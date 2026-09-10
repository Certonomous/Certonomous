# A3FL2 — nd-only free-conditioning-lever arm for the rung-3 `-3` adjoint stagnation — PRE-REGISTRATION

**PERMISSION: NOT_FROZEN — DRAFT prepared by a dafoam lab-lane.** This file freezes nothing,
launches nothing, runs no solver. Every instrument md5 / image pin below is a **PLACEHOLDER**
(`<SET_AT_FREEZE>` / `<PLACEHOLDER_AT_FREEZE>`), and the launcher's G-FREEZE gate REFUSES to
launch while this reads NOT_FROZEN. The dafoam-supervisor performs the §3 check-1 review,
requires the **§13 pre-flight exercise to go GREEN**, and only then freezes (blob sha + grader
md5 + image digest pinned; PERMISSION flipped to `FROZEN`). Amendments before first compute are
legal and must state the condition and how it was checked (CLAUDE.md rule 2); after first
compute the gates, thresholds, caps and labels are closed.

Predecessor: curriculum_A3FL1 (NOT A RESULT | CONFOUNDED, config-install crash on invalid KSPCalcSingularVal daOption, 865e7c71)

Item id: `CURRICULUM-A3FL2-onera-m6-free-conditioning-levers`
Case dir: `/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A3/curriculum_A3FL2/`
Run root (created at launch, never before — the age guard, rule 4):
`/home/ubuntu/certonomous-runs/CURRICULUM-A3FL2-onera-m6-free-conditioning-levers/`
Pre-flight exercise root (measurement variant, SEPARATE from the graded run root):
`/home/ubuntu/certonomous-runs/A3FL2-PREFLIGHT-EXERCISE/`

---

## 0. Why A3FL2 exists — the A3FL1 confound, and the one-line fix

A3FL1 was a well-designed self-contained 3-leg arm that **froze and launched with an INVALID
daOption**. Its two delta functions injected `KSPCalcSingularVal 1` as a **top-level** daOption
to read the preconditioned condition number. That option is **not a valid PYDAFOAM option**:
all three legs died `rc=1` at pyDAFoam construction time on
`pyDAFoam Error: Option 'KSPCalcSingularVal' is not a valid PYDAFOAM option`, before any solver
iteration. The arm is therefore a **CONFOUNDED NOT A RESULT** — the intended `nd`-vs-`natural`
conditioning question was never tested, because the config never installed.

A3FL1 stays **FROZEN** as the confounded record (rule 6 — it is never edited). A3FL2 is its
fresh successor with exactly one change to the experiment and one change to the process:

1. **The `KSPCalcSingularVal` injection is DROPPED ENTIRELY** from both delta functions and from
   the grader's required proofs. The **ONLY** lever is `jacMatReOrdering: "natural" -> "nd"`
   **INSIDE `adjEqnOption`** — a placement confirmed valid (A3FL1's crash was solely the
   top-level `KSPCalcSingularVal` option; `nd` inside `adjEqnOption` is a standard DAFoam adjoint
   linear-solver option). The arm becomes a **clean single-variable experiment**:
   `jacMatReOrdering: natural -> nd`, nothing else moved.
2. **A MANDATORY pre-flight EXERCISE (§13) must go GREEN before the graded arm is frozen.** The
   A3FL1 lesson: a five-minute smoke — install the config, confirm the daOptions are ACCEPTED,
   reach the first solver iterations — would have caught the invalid option before the freeze
   and the ~4.2 core-min waste. A3FL2 makes that smoke a gate on the freeze itself.

Because the KSPCalcSingularVal diagnostic is gone, the arm **no longer measures an in-arm
condition number**. `sMax/sMin` is reported **NOT_MEASURED_THIS_ARM** (§5 G-DIAG), citing the
already-MEASURED historical natural-ordering value `9.57e+10` (rung 3, `PRIOR_WORK_INVENTORY.md`
119–120) as the reference. **Conditioning is adjudicated by CONVERGENCE (G-CONV), never by a
singular-value token.** This is a cleaner test than A3FL1's framing and it is the version
registered here.

---

## 1. The question, and why it is worth its cost

Rung 3 (79,560 cells) is the reopened A3 ladder's ceiling: its baseline adjoint stagnates at
`PetscConvergedReason: -3`, residual `2.121e-2 → 1.615e-2` (**1.31× total**, `3.79e-07` relative
change over the last 2,700 iterations = flat), peak memory **11.65 / 22 GiB** — a **conditioning**
wall, not a memory death (`A3_RUNG3_N52_RESULT.md`). Strengthening the preconditioner re-breaks it
to `-5` at the restart boundary (stage-0 L3, `A3_TRIAGE_LEVERS_PREREGISTRATION.md:164`). Twelve
levers are already eliminated at this rung (`PRIOR_WORK_INVENTORY.md:117-127`).

**The one untried configuration lever is the Jacobian reordering.** M6 has only ever run
`natural` (and `rcm` on the hump family). Nested-dissection (`nd`) reordering produces a
different ILU(0) factorization and hence a different preconditioned spectrum. The question:
**does `nd` reordering clear the `-3` stagnation of the rung-3 adjoint operator?** The convergence
gate (G-CONV) answers it. A3FL2 does not attempt to read the condition number directly (that was
A3FL1's invalid diagnostic); if `nd` does not clear the wall, the honest deliverable is the
measured statement that the last untried free reordering does not help, benchmarked against the
historical `9.57e+10` conditioning reference.

This is a zero-rental, on-box experiment. If `nd` clears it, the ladder gains a rung for free
(pending the FD bright line, §3). If it does not, we have a measured conditioning finding that
closes the on-box question honestly and tells Sanaa whether renting is necessary.

---

## 2. Three legs, one self-contained arm — ALL under the ONE pinned image `dafoam-subpclu:v1`

**Why three legs, and why self-contained.** The rung-3 baseline's historical adjoint image was
**NOT preserved** (inferred `subpclu:v1`, not a surviving launch artifact). Rather than *argue*
the historical image, this arm is made **self-contained by measurement** (Sanaa's exhaustion
rule: measured, not argued): it carries its **own** rung-3 NATURAL baseline leg (`BASELINE_R3`)
under the **same** pinned image the `nd` test leg uses. The historical unpinned image is
therefore **IRRELEVANT** — the `nd` attribution is §11-clean *by measurement*, because the fresh
natural reference and the `nd` test both run under one identical, digest-pinned toolchain
(`dafoam-subpclu:v1` @ `sha256:ba2d16ab…`, MEASURED as the rung-1/rung-2 ladder image; present on
the host). All three legs run under **THIS ONE image**, so DAFOAM_CHARTER §11 toolchain identity
holds trivially.

All three legs use `-task compute_totals` (one primal + one adjoint solve, then print totals).
They run **SEQUENTIALLY** (CONTROL → BASELINE_R3 → TEST_R3), each fully completing before the next.

### Leg 1 — CONTROL — rung 2 (42,120 cells), KNOWN to converge, + the `nd` lever
- Source mesh / baseline runScript: `A3-rung2-n28-tpc1/` (`runScript_tpc1.py`; baseline CD **987** /
  CL **1171**, both `PetscConvergedReason: 2`, rc=0, wall 452 s = **30.13 core-min**; on disk).
- **Delta applied (`apply_delta`):** `jacMatReOrdering natural→nd` **ONLY** (no KSPCalcSingularVal).
- **Prediction (frozen):** the control **MUST still converge** — `PetscConvergedReason: 2` on BOTH
  CD and CL before the `gmresMaxIters 2000` cap. Iteration count vs the baseline (987/1171) is
  REPORTED, **not** gated.
- **Purpose:** proves `nd` does not BREAK a working solve (the stage-0 lesson: L3 Richardson looked
  good at rung 1 and collapsed the rung-2 control to double `-5`). Runs **first** (cheap).
- **If the control fails to converge** → `nd` is **harmful**; the arm is inconclusive → item
  verdict **NOT A RESULT** ("nd harmful").

### Leg 2 — BASELINE_R3 — rung 3 (79,560 cells), NATURAL ordering UNCHANGED (NO `nd`)
- Source mesh / baseline runScript: `A3-rung3-n52/runScript_rung3.py` (the SAME rung-3 source as
  TEST_R3; baseline stagnation `-3` at 4000 iters, wall 1426 s = **95.07 core-min**, peak
  11.65/22 GiB, historical `sMax/sMin = 9.57e+10`).
- **Delta applied (`apply_delta_baseline`):** a **PURE COPY** of the baseline runScript —
  `jacMatReOrdering` **STAYS `natural`**, and **NOTHING is added** (no KSPCalcSingularVal, no `nd`).
  The launcher asserts natural PRESENT and `nd` ABSENT. This is the single load-bearing difference
  from the two `nd` legs.
- **Prediction (frozen):** the natural baseline **REPRODUCES the `-3` stagnation** (flat tail
  `< THETA_STAG`) under the arm's OWN pinned image. This fresh natural reference is what makes the
  `nd` attribution §11-clean by measurement.
- **If BASELINE_R3 does NOT reproduce the stagnation** (converges, budget-limited, crashes) → the
  premise/toolchain is **not validated** → item verdict **NOT A RESULT**.

### Leg 3 — TEST_R3 — rung 3 (79,560 cells), + the `nd` lever
- Source mesh / baseline runScript: `A3-rung3-n52/runScript_rung3.py` (SAME source as BASELINE_R3).
- **Delta applied (`apply_delta`):** `jacMatReOrdering natural→nd` **ONLY**.
- Baseline config otherwise bit-identical: `transonicPCOption 1`, `pcFillLevel 0`, `gmresRestart 200`,
  `gmresMaxIters 4000`, `gmresRelTol 1e-4`, `normalizeStates` unchanged, `adjStateOrdering cell`
  unchanged. **The only variable between the two rung-3 legs is `jacMatReOrdering: natural
  (BASELINE_R3) → nd (TEST_R3)`.** That single-variable contrast, both under the ONE pinned image,
  is the arm's §11-clean measurement.

---

## 3. The bright line — convergence ALONE is never a PASS (DAFOAM_CHARTER §2) [INHERITED FROM A3FL1, VERBATIM]

> A DAFoam gradient is not a result until a finite-difference table stands beside it at a graded
> band (DAFOAM_CHARTER §2, the bright line; VERIFICATION_CHARTER §7 fixes the band).

**A PASS requires BOTH** the TEST_R3 adjoint to converge AND an endpoint FD table to verify the
gradient. Therefore, and frozen here:

- **IF and only if the TEST_R3 adjoint converges**, a **mandatory FD-verification leg** runs before
  any PASS is declared. A converged-but-not-yet-FD-verified test is **PENDING (FD owed)**, never PASS.
- If the TEST_R3 adjoint does **not** converge, there is no gradient to verify → the FD leg does not
  run, and the verdict is a **measured conditioning finding** reported with the historical
  `sMax/sMin` reference (§4). This is **not a PASS and not a hidden failure** — it is a GATE FAIL on
  the convergence gate stated openly (§7 verdict map).

---

## 4. Configuration and required proofs (the ONLY-variable-changed diff — check-1 reads this)

Each leg is staged by copying its **pinned baseline runScript** and applying **exactly** the delta
below — a single documented patch, so the baseline stays the single source of truth.

**Pinned baseline inputs (md5, real — these are inputs, not the freeze pin):**
- Rung-3 baseline runScript (BASELINE_R3 **and** TEST_R3): `A3-rung3-n52/runScript_rung3.py`
  md5 `1ec70293a56a2cf5a30a889a96832c06`
- CONTROL baseline runScript: `A3-rung2-n28-tpc1/runScript_tpc1.py` md5 `edc9e14be7297a442e16f43fdda94fcc`

**Two deltas, applied leg-specifically (and NOTHING else):**

- **`apply_delta` (the `nd` delta — CONTROL and TEST_R3):** `jacMatReOrdering "natural" -> "nd"`
  INSIDE `adjEqnOption`, **ONLY**. Asserts `nd` applied and no `natural` survived. **No
  KSPCalcSingularVal — the A3FL1 confound is dropped.**
- **`apply_delta_baseline` (BASELINE_R3):** a **PURE COPY** — `jacMatReOrdering` STAYS `natural`,
  NOTHING added. Asserts `natural` PRESENT and `nd` ABSENT.

| key | baseline value (on disk) | CONTROL / TEST_R3 (`nd` delta) | BASELINE_R3 (pure copy) |
|---|---|---|---|
| `adjEqnOption.jacMatReOrdering` | `"natural"` | **`"nd"`** — the genuinely-new lever | **`"natural"`** — UNCHANGED (load-bearing) |
| `transonicPCOption` (top-level daOption) | `1` | `1` | `1` |
| `adjStateOrdering` | `"cell"` | `"cell"` (held) | `"cell"` (held) |
| `adjEqnOption.pcFillLevel` | `0` | `0` | `0` |
| `adjEqnOption.gmresRestart` | `200` | `200` | `200` |
| `adjEqnOption.gmresMaxIters` | rung-3 `4000` / CONTROL `2000` | same | same (`4000`) |
| `adjEqnOption.gmresRelTol` | `1e-4` | `1e-4` | `1e-4` |
| ~~`KSPCalcSingularVal`~~ | `0` (baseline; UNTOUCHED) | **NOT injected (A3FL1 confound dropped)** | **NOT injected** |

**Required proofs in every leg's log before any number counts (L-40):**
1. `transonicPCOption 1;` in the DAOption dump.
2. **The leg's EXACT ordering** in BOTH the DAOption dump (`jacMatReOrdering <ord>;`) AND the KSP
   echo (`Mat ReOrdering: <ord>`): **`nd`** for CONTROL and TEST_R3 (a leg whose dump still reads
   `natural` did NOT apply the lever → REFUSE); **`natural`** for BASELINE_R3 (a BASELINE_R3 log
   reading `nd` is NOT the natural baseline → REFUSE). The grader keys the expected ordering on the
   leg name (`ND_LEGS = (CONTROL, TEST_R3)`).
3. `adjStateOrdering cell;` in the DAOption dump (unchanged — asserted present to prove no drift).
4. `ILU PC Fill Level: 0`, `GMRES Restart: 200` in the KSP echo.
5. **No** sub-LU banner (`DAFOAM_SUBPC_TYPE` unset).

**NOTE — no KSPCalcSingularVal proof.** A3FL1's grader REQUIRED `KSPCalcSingularVal 1;` in every
leg's dump; A3FL2's grader does NOT check it at all. A log reading `KSPCalcSingularVal 0` (the
untouched baseline value) is ACCEPTED. This is the load-bearing grader change and is self-tested
(§10, unit U15).

The launcher writes a per-leg `lever_echo.txt` **declaring** the intended config; the solver's own
DAOption dump is what **confirms** it (declaration is never proof).

---

## 5. Frozen gates, thresholds, caps and labels (prediction-first) [INHERITED FROM A3FL1, VERBATIM except G-DIAG]

### G-CONV — the convergence gate (frozen)
From the raw log's residual trace `Main iteration N KSP Residual norm r_N ... s.` and the terminal
`**Completed**! Total iterations: T. PetscConvergedReason: R. <wall> s`:
- **CONVERGED** = `PetscConvergedReason == 2` (KSP_CONVERGED_RTOL, i.e. `gmresRelTol 1e-4` reached)
  AND `Total iterations T < cap`, on the graded objective(s). CONTROL requires this on **both** CD
  and CL; BASELINE_R3 and TEST_R3 key on the first (CD) solve.
- **STAGNATION** = a negative reason (`-3`) at exactly the cap **with a flat tail**: the relative
  residual change over the last `N_TAIL = 1000` iterations `|r_{T-1000} - r_T| / |r_T| < THETA_STAG`,
  with **`THETA_STAG = 1.0e-3`** (frozen). The rung-3 baseline gave `3.79e-07` — far below
  `THETA_STAG` — so it is unambiguously flat by this rule.
- **BUDGET-LIMITED (not a wall)** = a negative reason at the cap but the tail is **still descending**
  (`relative change ≥ THETA_STAG` and monotone) — reported as budget-limited, cap too small to
  decide. This is **NOT** a stagnation verdict.
- **NOT EVALUABLE** = crash / OOM / memory guard trip before a reason is printed (§6).

### G-CTRL — the control-validity gate (frozen)
The CONTROL leg CONVERGED (both CD and CL, `reason 2`, before the `2000` cap). If not, `nd` broke a
converging solve → item **NOT A RESULT** ("nd harmful"). Iteration count vs baseline (987/1171) is
reported, not gated.

### G-BASE — the baseline-reproduction gate (frozen; the §11-clean-by-measurement gate)
The BASELINE_R3 leg (rung-3, NATURAL, no `nd`) must **REPRODUCE the `-3` stagnation** — leg state
`STAGNATION` (a negative reason at the `4000` cap with a flat tail `< THETA_STAG`) — under the arm's
OWN pinned image. This validates the premise and the toolchain. **If BASELINE_R3 does NOT stagnate**
→ the premise is **not validated** → item verdict **NOT A RESULT**. This gate is read **before**
TEST_R3 is composed (§7).

### G-DIAG — the condition-number reference (reported, never a gate) [CHANGED FROM A3FL1]
A3FL2 **DROPS** the in-arm `KSPCalcSingularVal` diagnostic (it was A3FL1's invalid daOption).
`sMax/sMin` is therefore **NOT_MEASURED_THIS_ARM** and is reported so, citing the historical
MEASURED natural-ordering value **`9.57e+10`** (rung 3, `PRIOR_WORK_INVENTORY.md` 119–120) as the
reference. **The grader does NOT require any in-arm singular-value token** and never composes one
into a verdict. Conditioning is adjudicated by convergence (G-CONV); the historical reference is
carried as context beside the outcome.

### G-FD — the bright-line finite-difference gate (frozen; CONDITIONAL on TEST convergence) [INHERITED VERBATIM]
Runs **only if** the TEST adjoint converged. Reuses the A3 family's validated FD protocol
(DAFOAM_CHARTER §7; `A3_RUNG3_N52_PREREGISTRATION.md` §5) and the `d8r_grade.py` band machinery:
- `primalMinResTol 1e-8`, `primalMinResTolDiff 1e4`; central differences; **registered steps
  `[5.0e-4, 1.0e-3, 2.0e-3]`**, middle step `1.0e-3` the reference.
- **PLATEAU**: the middle step agrees with at least one neighbour to `PLATEAU_TOL = 10%`, else that
  component is NOT A RESULT.
- **Band D (per component)**: `|d_FD − J_adj| / |d_FD| ≤ FD_BAND = 5.0%` **AND** same sign — a sign
  flip is GATE FAIL whatever the magnitude.
- **Band E (aggregate)**: vector-relative error `≤ AGG_BAND = 5.0%`.
- **Registered components**: `patchV[1]`, `twist[1]`, `shape[115]`; `of = CD`, `wrt = patchV`
  (+ twist, shape). **`MIN_GRADED = 2`** evaluable components; fewer → NOT A RESULT.
- Arm FD PASS = every evaluable component PASS with ≥ 2 evaluable.

### Caps (frozen; rule 12) — see §6 cost table for the derivation
- CONTROL per-leg cap **45 core-min**; BASELINE_R3 per-leg cap **130 core-min**; TEST_R3 per-leg cap
  **130 core-min**; FD-leg cap (conditional) **90 core-min**; item ceiling **395 core-min** (sum of
  the per-leg caps — the hard stop; predicted spend ~220, +FD ~60–70 conditional). A crossing STOPS
  the leg (overrun stops the run, rule 12) and is a G-CAP GATE FAIL, reported.
- **PRE-FLIGHT EXERCISE ceiling (§13, MEASUREMENT, separate from the graded item ceiling): 48
  core-min cumulative** (AMENDMENT A1, 2026-09-10, pre-compute; ~~36~~). It is **not** a graded row
  and is **not** inside the 395 item ceiling. A crossing is a **budget cap-stop** enforced by
  `a3fl2_exercise.sh` — it aborts the remaining legs and is recorded with its own distinct markers;
  it is **not** a G-CAP GATE FAIL, because the exercise declares no gate verdict (§13).

---

## 6. Memory guard and cost (rule 12)

**Memory guard:** record rung-3 peak 11.65 GiB. Container cap **`--memory=22g` — DOCKER-ENFORCED**
(`docker run --memory=22g --memory-swap=22g --oom-score-adj=500`), plus a host floor **6 GB**.
`nd` reordering changes the fill pattern of ILU(0) only marginally, so a large memory jump is not
expected; but the leg **STOPS** if the container hits the cap. **A memory death is NOT a
conditioning verdict** → reported as NOT EVALUABLE / **BLOCKED** with the memory numbers.

**Cost table (all figures per-leg; core-min = wall_s × ranks ÷ 60; np = 4):**

| leg | basis (measured, on disk) | predicted core-min | cap core-min | incurred when |
|---|---|---|---|---|
| CONTROL (rung 2 + `nd`) | rung-2 converged baseline 452 s = 30.13 core-min | **~30** (30–40) | 45 | always |
| BASELINE_R3 (rung 3, natural pure copy) | rung-3 baseline 1426 s = 95.07 core-min | **~95** (95–110) | 130 | always |
| TEST_R3 (rung 3 + `nd`) | rung-3 baseline 1426 s = 95.07 core-min | **~95** (95–110) | 130 | always |
| FD leg (conditional) | A3 family FD arm ~60–70 core-min | **60–70** | 90 | **only if TEST_R3 converges** |
| **PRE-FLIGHT EXERCISE (§13, MEASUREMENT, always, PRE-FREEZE)** — **AMENDED 2026-09-10, AMENDMENT A1 (pre-compute)** | rung-3 source case, 4 ranks: primal ends `ExecutionTime = 30.97 s`, dRdWTPC assembly `49.24 s` → `149.84 s` (`/home/ubuntu/certonomous-runs/A3-rung3-n52/rung3_stage1.log`, lines 809 / 847 / 861) **+** measured 21 s/leg container-start + decomposePar + pyDAFoam staging (all three A3FL1 legs, `/home/ubuntu/certonomous-runs/CURRICULUM-A3FL1-onera-m6-free-conditioning-levers/ledger.txt`) | **~34** (~5 CONTROL + ~13.4 × 2 R3 legs at the deadline) — ~~**~10–15**~~ | **48** = ⌈3 × (180 + 30 + 21) × 4 ÷ 60 = 46.2⌉ — ~~36 (3 × 12)~~ | always, before freeze |

- **Graded total, three legs always incurred** (pessimistic, most-likely path where TEST_R3 does not
  converge): ~30 + ~95 + ~95 = **~220 core-min** (chief-approved ~220; range 155–260).
- **Graded total if TEST_R3 converges and FD runs**: + 60–70 = **~280–290 core-min** (item ceiling
  395 — the sum of per-leg caps, the hard stop).
- **Pre-flight exercise adds ~34 core-min most-likely under a hard ceiling of 48 core-min**
  (~~"adds ~10–15 core-min"~~ — struck and replaced by **AMENDMENT A1, 2026-09-10, pre-compute**;
  derivation and the condition-check in that amendment), spent BEFORE the freeze; it is measurement,
  not a graded row (§13). The ceiling is **ENFORCED inside `a3fl2_exercise.sh`** — it was not before.
  Total campaign-to-verdict cost ≈ **254 core-min** (exercise most-likely + graded, no FD;
  ~~230–235~~) or ≈ **314–324 core-min** (with FD; ~~295–305~~). At the exercise **ceiling** rather
  than its most-likely: **268** (no FD) / **328–338** (with FD).
- **Derived $** at the reported-by-owner rate $0.0513/core-h (DERIVED, not measured — the box cannot
  read its own billing, COMPUTE_BUDGET §5): 220 core-min → 3.67 core-h → **$0.188**;
  **324 core-min → 5.40 core-h → $0.277** (~~305 core-min → 5.08 core-h → $0.261~~, AMENDMENT A1).
  The **exercise alone**: ~34 core-min → 0.567 core-h → **$0.029**; at its 48 core-min ceiling →
  0.800 core-h → **$0.041**. Every figure here is **DERIVED, NOT MEASURED**. All far under the
  $25/run pre-authorization.
- **A3FL1's ~4.2 core-min waste is recorded SEPARATELY** (rule 12, §6 of COMPUTE_BUDGET: waste is
  named, never absorbed): the three A3FL1 legs each died `rc=1` at config-install on the invalid
  option, spending ~4.2 core-min total that produced no result. That is a **waste row against
  A3FL1**, not a cost of A3FL2, and is not folded into A3FL2's estimate/actual ratio.
- **Estimate-vs-actual calibration (rule 12):** on completion the team appends a row to
  `docs/COST_CALIBRATION.md` — ratio actual/predicted per leg, gap attributed (contention / waste /
  misprediction, waste named separately), dollars derived and labelled derived.

---

## 7. Verdict map (frozen; vocabulary strictly PASS / GATE FAIL / NOT A RESULT / BLOCKED / PENDING) [INHERITED FROM A3FL1, VERBATIM except the G-DIAG wording]

Read in order; the first matching row is the item verdict.

| condition | item verdict | content reported beside it |
|---|---|---|
| CONTROL memory death / crash before a reason | **BLOCKED** | memory numbers; conditioning question open |
| CONTROL does not converge (any negative reason / collapse) | **NOT A RESULT** | "nd harmful" — it breaks a converging solve (stage-0 precedent) |
| CONTROL converged; **BASELINE_R3 does NOT reproduce the `-3` stagnation** | **NOT A RESULT** | the premise/toolchain is **not validated**; BASELINE_R3 leg state |
| CONTROL converged; BASELINE_R3 STAGNATION; TEST_R3 memory death / crash before a reason | **BLOCKED** | memory numbers |
| CONTROL converged; BASELINE_R3 STAGNATION; TEST_R3 `-3` at cap, **budget-limited** (tail still descending) | **NOT A RESULT** | cap too small to decide; residual trend; recommend a re-cap arm |
| CONTROL converged; BASELINE_R3 STAGNATION; TEST_R3 **STAGNATION** (`-3` at cap, flat tail `< THETA_STAG`), memory comfortable | **GATE FAIL** (on G-CONV) | **the measured conditioning finding**: "Free conditioning exhausted: `nd` does not clear the rung-3 wall, MEASURED under a §11-clean self-contained baseline." Historical `sMax/sMin 9.57e+10` reference reported beside it (NOT measured this arm). NOT a hidden failure. |
| CONTROL converged; BASELINE_R3 STAGNATION; TEST_R3 converged; FD leg **not yet run** | **PENDING** (FD owed) | `PENDING: <FD run path>`; never reported as PASS |
| CONTROL converged; BASELINE_R3 STAGNATION; TEST_R3 converged; FD leg run, FD **fails band or sign flip** | **GATE FAIL** (on G-FD, the bright line) | the FD table; the failing component(s) |
| CONTROL converged; BASELINE_R3 STAGNATION; TEST_R3 converged; FD leg run, FD **passes** (≥2 evaluable, all PASS, band E ≤ 5%) | **PASS** | the FD table; a new verified rung on the A3 ladder |
| any G-CAP crossing | folds to **GATE FAIL** unless a higher NOT A RESULT / BLOCKED row already fired | the core-min overrun |

Rows are read **in order**; the first match is the item verdict (the grader's `compose_item`
implements exactly this order).

---

## 8. §2bb pre-flight — applicability of `check_ladder_preflight.py`, and the evidence used instead

`scripts/check_ladder_preflight.py` does NOT structurally fit this arm (its manifest models a
time-marched primal ladder; the graded quantity here is a capped-iteration adjoint KSP solve). The
mapping is disclosed in `LADDER_PREFLIGHT.json`'s `_note`. The §2bb **principle** — a deadline SIZED
from a measured sample with the 1.25× margin, each distinct solver path shown to run cleanly once —
is met in the arm's own terms:

1. **Deadline sizing (measured + 1.25× margin):** BASELINE_R3 and TEST_R3 `1426 s × 1.25 = 1782.5 s
   → 1800 s`; CONTROL `452 s × 1.25 = 565 s → 600 s`.
2. **Distinct solver-path coverage:** `DARhoSimpleCFoam | compute_totals | np=4 | scotch` is the
   SAME path that ran rungs 1, 2 and 3 to completion (rung 2 rc=0). The `nd` lever is an
   adjoint-linear-solver option downstream of decomposition; it introduces no new path.
3. **THE MANDATORY §13 EXERCISE** additionally proves, PRE-FREEZE, that the actual `nd` / natural
   configs INSTALL and are ACCEPTED under the pinned image — the exact confound A3FL1 missed.

`LADDER_PREFLIGHT.json` (all three rungs, one distinct path) runs clean through the checker.
**Result verbatim (run by this lane):**
`PASS: ladder A3FL2 pre-flight complete (3 rungs, 1 distinct paths)` — `EXIT=0`
(`python3 scripts/check_ladder_preflight.py cases/dafoam/ladder-a/A3/curriculum_A3FL2/LADDER_PREFLIGHT.json`).

---

## 9. §2ba — the launcher, the G-FREEZE gate, and the detached autograder

- **Launcher** `a3fl2_launcher.sh`: stages each of the **three** legs (copy the pinned baseline
  runScript; apply the leg's §4 delta — `apply_delta` (`nd`) for CONTROL and TEST_R3,
  `apply_delta_baseline` (pure copy) for BASELINE_R3; write a per-leg `lever_echo.txt`), then runs
  each leg **inside a DAFoam Docker container** under the ONE pinned image (`docker run -d`,
  `--memory=22g` DOCKER-enforced, `timeout -k` deadline inside the container, rc from `docker inspect
  .State.ExitCode`). Legs run **sequentially in the detached orchestrator's foreground** (CONTROL →
  BASELINE_R3 → TEST_R3); `A3FL2_LADDER_DONE` is written **only after all three finish**. It carries
  a **G-FREEZE gate**: it REFUSES to launch unless the prereg `PERMISSION:` reads `FROZEN`, and it
  verifies the grader md5, both baseline-runScript md5s, and the §11 image digest against the pins,
  refusing on any drift.
- **Detached autograder** `a3fl2_autograde.sh`: runs under `setsid` (PPID=1), polls for the
  `A3FL2_LADDER_DONE` marker (CEIL 12000 s), md5-verifies the frozen grader and REFUSES (exit 2) on a
  placeholder or drift, grades each leg log, writes per-leg JSON + a single `A3FL2_AUTOGRADE_DONE.txt`.
  It **declares no verdict** — that is the supervisor's call.

**FREEZE PINS (PLACEHOLDERS — the dafoam-supervisor sets these at freeze, after a GREEN §13 exercise):**
- This file's committed blob sha: `<SET_AT_FREEZE>` (the grading path is fixed at the commit, rule 2).
- Grader `a3fl2_grade.py` md5: `<SET_AT_FREEZE>` — launcher and autograder both pin this; the
  md5-drift limb REFUSES while it is the placeholder.
- **§11 toolchain image (ONE image, all three legs)** — intended `IMG` = `dafoam-subpclu:v1`,
  `IMG_DIGEST` = `sha256:ba2d16ab9d575ed3167abe31344aa58fb42fef1a8b27db60baeb505ab9413517` (MEASURED
  as the rung-1/rung-2 ladder image; present on host). Both fields are `<SET_AT_FREEZE>` /
  `<PLACEHOLDER_AT_FREEZE>` placeholders in the launcher; the digest-verify gate REFUSES until the
  supervisor pins them and reads the host image's real digest, refusing on drift.
- Baseline runScript md5s (real, pinned now): rung-3 `1ec70293a56a2cf5a30a889a96832c06`, CONTROL
  `edc9e14be7297a442e16f43fdda94fcc`.

---

## 10. Planted-zero control (rule 3)

The grader plants a known perturbation and refuses if the reader cannot see it — two controls:
1. **Residual-trace / convergence reader:** a fixture log carries a planted converging trace
   (`reason 2`, iterations below cap) and a planted stagnant trace (`-3`, flat tail); the grader's
   selftest asserts G-CONV reads CONVERGED and STAGNATION respectively.
2. **FD-table reader:** a copy of each FD table with a known `PLANT` (`1.234e-03`) added to every
   physical derivative is re-read; the grade REFUSES unless every value moved by exactly `PLANT`.

The grader carries **no `assert`** (L-332; it counts `ast.Assert` nodes in its own source and
refuses on any) and **REFUSES (exit 2) rather than degrade** on any missing/garbage field.
`--selftest` / `--drive` runs the planted fixtures against a frozen expected-unit count
(**36 units, PASS, verified by this lane**). Unit **U15** specifically verifies A3FL2's dropped
requirement: a dump reading `KSPCalcSingularVal 0` is now **ACCEPTED**, not refused.

---

## 11. §11 completion rule and toolchain identity (rule 4)

A leg is done only if: rc = 0 (from the ledger, captured inside the detached wrapper); the log carries
a `**Completed**! Total iterations: ... PetscConvergedReason: ...` terminal line; the age guard holds
(the totals artifact / log is NEWER than the leg's own `0/` datum, and the run root did not exist
before launch); the required-proof tokens of §4 are present. A leg failing any clause is NOT a result
for grading and the grader REFUSES. **ONE image, all three legs** — `dafoam-subpclu:v1` @
`sha256:ba2d16ab…`; because the arm is self-contained (its own natural baseline under this image),
the unpreserved historical rung-3 image is irrelevant and §11 holds under this ONE pinned image.
(For an adjoint `compute_totals` leg the "fields present" clause is substituted by the totals print /
terminal `Completed` line and the age-guarded log — disclosed, not silent.)

---

## 12. Provenance and reading list
- Predecessor: `cases/dafoam/ladder-a/A3/curriculum_A3FL1/` (A3FL1, FROZEN 865e7c71, CONFOUNDED).
- Baselines & prior work: `A3_RUNG3_N52_RESULT.md`, `A3_RUNG3_N52_PREREGISTRATION.md`,
  `A3_TRIAGE_LEVERS_PREREGISTRATION.md`, `A3_NONNORMALITY_DIAGNOSTIC_PREREGISTRATION.md`,
  `docs/dafoam/PRIOR_WORK_INVENTORY.md` (§1e / lines 100-127).
- Charters: `DAFOAM_CHARTER.md` §2 (bright line), §7-referenced band, §11 (toolchain identity);
  `VERIFICATION_CHARTER.md` §2/§2b/§2bb/§2ba/§7; `COMPUTE_BUDGET_CHARTER.md` §5/§6; CLAUDE.md rules
  2, 3, 4, 5, 6, 12.
- Instrument reused: `cases/dafoam/ladder-a/A6/curriculum_D8R/d8r_grade.py` (FD band machinery),
  the A3FL1 launcher/grader/autograder as templates, and `curriculum_D6RF10/d6rf10_preflight_exercise.sh`
  as the pre-flight-exercise pattern (§13).

---

## 13. THE MANDATORY PRE-FLIGHT EXERCISE — the graded arm is frozen ONLY on a GREEN smoke (the A3FL1 lesson)

**This is the process fix that A3FL1 paid for.** The graded arm (§9) is **NOT frozen** until the
pre-flight exercise `a3fl2_exercise.sh` reports **GREEN**.

- **What it is:** a SHORT, MEASUREMENT-ONLY smoke — no grader staged, no freeze, no G-FREEZE limb,
  a SEPARATE exercise run root (`/home/ubuntu/certonomous-runs/A3FL2-PREFLIGHT-EXERCISE/`, NOT the
  graded run root, so the graded age guard stays clean). It stages each of the three legs with the
  **SAME nd / natural ordering deltas** the graded launcher applies (nd-only, no KSPCalcSingularVal),
  applies a **smoke override** (`gmresMaxIters → 30`, primal `controlDict endTime → 25`), and runs
  each leg in the ONE pinned container with a **short 180 s per-leg deadline**.
- **What it proves:** (a) the config INSTALLS (decomposePar + pyDAFoam construction), (b) the
  daOptions are **ACCEPTED** — no `not a valid PYDAFOAM option` (the exact A3FL1 crash string), and
  (c) the first solver iterations are reached (primal + adjoint start). It writes an
  `A3FL2_EXERCISE_DONE.txt` marker + per-leg `rc` + a grep for `not a valid PYDAFOAM option` /
  `Traceback`.
- **GREEN criterion (frozen):** `rc = 0` on **all three** legs **AND** the invalid-option string
  absent from **every** leg log. **GREEN ⇒ config valid, `nd` accepted ⇒ the supervisor MAY freeze
  the graded arm.** If any leg trips (rc ≠ 0, or the invalid-option string present), the exercise is
  **NOT GREEN**, the config is **fixed PRE-FREEZE**, and the graded arm is **not frozen** until a
  re-run goes GREEN.
- **Cost (AMENDED 2026-09-10, AMENDMENT A1, pre-compute):** ~~~10–15 core-min (3 smokes × ~180 s
  wall × 4 ranks, capped at 12 core-min each)~~ → **most-likely ~34 core-min, HARD CEILING 48
  core-min** = ⌈3 × (deadline 180 s + kill grace 30 s + measured 21 s staging) × 4 ÷ 60 = 46.2⌉.
  Derived **$0.029** most-likely / **$0.041** at the ceiling at $0.0513/core-h — DERIVED, NOT
  MEASURED. Spent before the freeze; a measurement, not a graded row. Mirrors
  `d6rf10_preflight_exercise.sh`.
- **The ceiling is ENFORCED, not annotated** (rule 12; it was previously enforced by nothing).
  `a3fl2_exercise.sh` writes a per-leg `wall_s` → `core_min` row into the exercise ledger, keeps a
  running `cumulative_core_min`, stops a leg **in flight** when the remaining budget is exhausted
  (`A3FL2_EXERCISE_BUDGET_STOP`), and on a cumulative crossing sets a **cap-stop that ABORTS the
  legs that have not started** (`A3FL2_EXERCISE_CUMULATIVE_CAP_STOP`, mirroring
  `d6rf10_run_arm.sh`'s `D6RF10_CUMULATIVE_HARD_STOP`). An overrun **stops the exercise**; it does
  not get a new budget.
- **A budget abort is NEVER a config failure, and the record says which.** The GREEN criterion above
  is **unchanged**. A cap-stop writes its OWN distinct markers — `stop_cause=BUDGET_STOP` or
  `rc=CAP_STOP_NOT_RUN` per leg, `A3FL2_EXERCISE_CAP_STOP=yes`, and an explicit
  `A3FL2_EXERCISE_CAP_STOPPED -- BUDGET ABORT, NOT A CONFIG FAILURE` block in
  `A3FL2_EXERCISE_DONE.txt`. Config evidence remains `invalid_option=yes` **alone**. A cap-stopped
  exercise is NOT GREEN (a leg that never ran proved nothing), and the graded arm stays **unfrozen**
  — but it is **not** evidence against the daOptions, and must never be reported as such.

The freeze order is therefore, explicitly: (1) supervisor §3 check-1 review of this DRAFT; (2) run
`a3fl2_exercise.sh`, confirm **A3FL2_EXERCISE_VERDICT=GREEN**; (3) only then pin the freeze values
(§9) and flip PERMISSION to FROZEN; (4) launch the graded arm.

---

## AMENDMENT A1 — 2026-09-10 — the §13 exercise cost is re-registered (most-likely ~34, ceiling 48 core-min) AND the ceiling is given an enforcing instrument

**Condition, and how it was checked (CLAUDE.md rule 2, the pre-compute clause).** This amendment is
legal because **no compute has run** for A3FL2 and this file is **NOT_FROZEN**:

1. **The exercise run root does not exist.** `/home/ubuntu/certonomous-runs/A3FL2-PREFLIGHT-EXERCISE`
   was checked by direct `ls` of that path at **2026-09-10T03:52Z** and returned
   *No such file or directory*. `a3fl2_exercise.sh` refuses to start if that root already exists
   (its exercise-root guard), so its absence is proof the exercise has never run.
2. **The graded run root does not exist either.**
   `/home/ubuntu/certonomous-runs/CURRICULUM-A3FL2-onera-m6-free-conditioning-levers` is created at
   launch and never before (rule 4, the age guard); it is absent.
3. **PERMISSION reads `NOT_FROZEN`** (this file's opening line and its closing line), and the
   launcher's G-FREEZE gate refuses to launch while it does.

No gate, threshold or label is touched below. What changes is a **cost estimate and a cap** — both
of which rule 2 permits to move **before** first compute, and neither of which may move after it.

**Finding (a) — the registered ceiling of 36 core-min was mpirun-only, and therefore too low.**
`36 = 3 legs × 180 s deadline × 4 ranks ÷ 60` counts only the time inside the container's
`timeout … mpirun`. It excludes:
- the **30 s kill grace** (`a3fl2_exercise.sh`, `KILL_GRACE_S=30`), which a deadline trip actually
  spends; and
- the **~21 s per-leg container-start + `decomposePar` + pyDAFoam-staging span**, measured on all
  three A3FL1 legs — same image, same case, same 4 ranks — in
  `/home/ubuntu/certonomous-runs/CURRICULUM-A3FL1-onera-m6-free-conditioning-levers/ledger.txt`
  (each leg's `t1 − t0` = 21 s exactly).

True worst case per leg = `180 + 30 + 21 = 231 s`; three legs at 4 ranks =
`3 × 231 × 4 ÷ 60 = 46.2 core-min`. **REGISTERED HARD CEILING: 48 core-min** (46.2 rounded up).

**Finding (b) — the "~10–15 core-min" most-likely was understated.** Measured on the exercise's own
rung-3 source case at 4 ranks, `/home/ubuntu/certonomous-runs/A3-rung3-n52/rung3_stage1.log`:
- the primal stage ends at `ExecutionTime = 30.97 s` (line 809);
- the `dRdWTPC` preconditioner assembly runs from `dRdWTPC: 0 of 1355, ExecutionTime: 49.24 s`
  (line 847) to `dRdWTPC: 1354 of 1355, ExecutionTime: 149.84 s` (line 861).

That is **~119 s of adjoint setup + assembly which is MANDATORY before the first GMRES iteration**,
so the smoke's `gmresMaxIters → 30` cap cannot shorten it, and the smoke's
`primal endTime → 25` shortens only the (cheap) primal part. Against a 180 s deadline both R3 legs
are therefore expected to run **at or near the deadline**. **REGISTERED MOST-LIKELY: ~34 core-min**
= CONTROL ~5 + BASELINE_R3 ~13.4 + TEST_R3 ~13.4, where each R3 leg is
`(180 s deadline + 21 s staging) × 4 ÷ 60 = 13.4 core-min`.

**Finding (c) — nothing enforced any of it.** Before this amendment `a3fl2_exercise.sh` contained
**no core-minute accounting and no cap logic at all**; `DEADLINE_S=180` was the only limiter and it
is a per-leg wall deadline, not a cumulative budget. A cap that no instrument enforces is a number
annotated as non-binding, which this lab treats as worse than one never computed.

**What this amendment changes.**
1. §6 cost table exercise row, §6 cost prose, the §5 caps list and the §13 cost bullet:
   most-likely **~34 core-min**, hard ceiling **48 core-min**, derived **$0.029 / $0.041** at
   $0.0513/core-h — **DERIVED, NOT MEASURED** (the box cannot read its own billing,
   `COMPUTE_BUDGET_CHARTER` §5). Campaign totals folded: ≈ **254 core-min** (no FD) /
   ≈ **314–324 core-min** (with FD), and 268 / 328–338 at the exercise ceiling.
2. `a3fl2_exercise.sh` gains the **enforcing instrument**: per-leg `wall_s` → `core_min` ledger row,
   a running `cumulative_core_min`, an **in-leg budget stop** sized from the remaining budget
   (`A3FL2_EXERCISE_BUDGET_STOP` → `docker stop`), and a **cumulative cap-stop**
   (`A3FL2_EXERCISE_CUMULATIVE_CAP_STOP`) that **aborts the legs that have not started**. The shape
   is `d6rf10_run_arm.sh`'s `D6RF10_CUMULATIVE_HARD_STOP`, with one deliberate difference: the
   crossing test is `>=`, not `>`, so a leg stopped exactly at the ceiling does not hand the next
   leg a zero-second allowance. `python3` is now a hard dependency and the script **refuses before
   creating the exercise root** if it is absent — a run with no cost instrument is a run with an
   unenforced cap.

**What this amendment does NOT change — stated so the boundary is unmistakable.**
- **The §13 GREEN criterion is untouched**: `rc = 0` on all three legs **AND**
  `not a valid PYDAFOAM option` absent from every leg log. Not altered, not widened, not softened,
  nothing added. The enforcing line in `a3fl2_exercise.sh` is byte-for-byte the line that was there.
- **No gate, threshold, band, verdict-map row, `MIN_GRADED`, endTime, deadline, memory cap, image
  digest or graded per-leg cap moves.** `DEADLINE_S` stays 180 s; `KILL_GRACE_S` stays 30 s;
  `RANKS` stays 4. The graded item ceiling stays **395 core-min** and the exercise's 48 is **outside**
  it (the exercise is measurement, not a graded row).
- **PERMISSION stays `NOT_FROZEN`.** This amendment freezes nothing and launches nothing.
- **A budget cap-stop is not a config failure and can never be reported as one.** It writes its own
  distinct markers (`stop_cause=BUDGET_STOP`, `rc=CAP_STOP_NOT_RUN`, `A3FL2_EXERCISE_CAP_STOP=yes`,
  and an explicit `BUDGET ABORT, NOT A CONFIG FAILURE` block in `A3FL2_EXERCISE_DONE.txt`). Config
  evidence stays `invalid_option=yes` **alone**. A cap-stopped exercise is **NOT GREEN** — a leg that
  never ran proved nothing, so the graded arm stays unfrozen — but the record says the reason was
  budget, not an invalid daOption.

**What I could not verify (honest gaps in this amendment's own numbers).**
- The **CONTROL leg's ~5 core-min** is an **inference**, not a measurement: it scales the R3 legs by
  the rung-2 / rung-3 cell counts (42,120 vs 79,560) with no rung-2 smoke log on disk. If CONTROL
  runs to its own deadline instead, the most-likely rises to ~40 core-min — still inside the 48
  ceiling, which is why the ceiling is derived from the deadline, not from the most-likely.
- The **21 s anchor** measures the A3FL1 span from just before `docker run -d` to after
  `docker logs` + `chown`, and those legs **died at pyDAFoam construction**; it is a staging-overhead
  measure, not a full-leg measure. The new instrument takes its `T0` **earlier** (before the `cp -a`
  staging of the case), so it accounts slightly more than the anchor — conservative in the enforcing
  direction, and charged at 4 ranks even though staging is single-threaded.
- `rung3_stage1.log` was produced with `jacMatReOrdering natural` (line 449). The `nd` legs' assembly
  cost may differ from the 119 s measured there; the direction is not known in advance — that is
  precisely the question A3FL2 exists to answer.
- The box is **contended** (foreign solvers running at the time of writing). Contended wall times can
  exceed these figures; the in-leg budget stop is what keeps a contended leg from silently spending
  the whole budget.

**Verification of the instrument (no compute, no solver, no container).** The edited script passes
`bash -n`, and its control flow was exercised end-to-end against **stubbed** `docker`/`sudo` in the
lane scratchpad — never against the real image, the real cases or the real exercise root — over
three paths: (i) all legs rc=0 → `A3FL2_EXERCISE_VERDICT=GREEN` with the cost rows present and no
cap markers; (ii) a tiny cap → leg 1 budget-stopped in flight, legs 2 and 3 `rc=CAP_STOP_NOT_RUN`,
`NOT_GREEN` plus the `BUDGET ABORT, NOT A CONFIG FAILURE` block; (iii) the A3FL1 crash string in
every log → `invalid_option=yes`, `stop_cause=none`, `A3FL2_EXERCISE_CAP_STOP=no`, `NOT_GREEN`. The
three states are mutually distinguishable from the DONE file alone.

---

**PERMISSION: NOT_FROZEN — DRAFT. SUBMISSIONS PARKED (rule 7). Freeze happens only after a GREEN §13 pre-flight exercise (the A3FL1 lesson).**
