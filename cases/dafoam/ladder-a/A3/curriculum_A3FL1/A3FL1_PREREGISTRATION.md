# A3FL1 — Free-conditioning-levers arm for the rung-3 `-3` adjoint stagnation — PRE-REGISTRATION

**PERMISSION: NOT_FROZEN — DRAFT.** This file is a draft prepared by a dafoam lab-lane.
It freezes nothing, launches nothing, runs no solver. The dafoam-supervisor performs the
§3 check-1 review and only then freezes (blob sha + grader md5 pinned; PERMISSION line flipped
to `FROZEN`). Until then every instrument md5 below is a **PLACEHOLDER** and the launcher's
G-FREEZE gate REFUSES to launch (see §9). Amendments before first compute are legal and must
state the condition and how it was checked (CLAUDE.md rule 2); after first compute the gates,
thresholds, caps and labels are closed.

Item id: `CURRICULUM-A3FL1-onera-m6-free-conditioning-levers`
Case dir: `/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A3/curriculum_A3FL1/`
Run root (created at launch, never before — the age guard, rule 4):
`/home/ubuntu/certonomous-runs/CURRICULUM-A3FL1-onera-m6-free-conditioning-levers/`

---

## 0. Check-1 honesty preface — the brief's three-lever premise is corrected against the run configs on disk

The dispatch brief named three "genuinely untried" free levers. Reading the actual A3 run
configs and logs on disk (not the brief), **one of the three is already spent and a second is a
re-measurement, not a new lever**. This arm is registered on the truthful reading, and the
supervisor must read this section as part of check-1 before freezing:

| brief's claim | on-disk reality (artifact) | status in this arm |
|---|---|---|
| `jacMatReOrdering: nd` — "M6 only ever ran natural/rcm" | **TRUE.** Every A3 rung ran `jacMatReOrdering natural` (`A3-rung3-n52/rung3_stage1.log:449`, `A3-rung2-n28-tpc1/runScript_tpc1.py:101`). `nd` never ran on M6. | **THE one genuinely-untried configuration lever. Applied.** |
| `adjStateOrdering: cell` — "M6 defaults to state" | **FALSE.** `adjStateOrdering cell` is **already the baseline** on rungs 1, 2 AND the stagnating rung 3 (`rung3_stage1.log:508`; `runScript_rung3.py:95`; every converging rung). It is not a change. | **NOT a lever. Held at the baseline value `cell`, unchanged.** Registered explicitly so the check-1 diff shows zero movement on this key. |
| `KSPCalcSingularVal: 1` — "off everywhere; would finally MEASURE the condition number" | **PARTLY.** The option is off in every logged run (`KSPCalcSingularVal 0`, e.g. `rung3_stage1.log:465`) — but the rung-3 **preconditioned** condition number `sMax/sMin = 9.57e+10` was **already measured** via `KSPComputeExtremeSingularValues` in `A3_NONNORMALITY_DIAGNOSTIC_PREREGISTRATION.md` (§1e / `PRIOR_WORK_INVENTORY.md:119-120`) under the *natural-ordering* baseline. | **Diagnostic applied. Its NEW information is conditional on the `nd` lever: it measures whether `nd` changes the 9.57e+10 baseline condition number.** Not a redundant re-measurement — it reads out the `nd` lever's spectral effect. |

**Net:** this arm is, honestly, a **one genuinely-new-variable experiment** — `jacMatReOrdering: nd`
— instrumented by `KSPCalcSingularVal: 1` to read the conditioning change, benchmarked against the
already-measured baseline `sMax/sMin = 9.57e+10` (natural ordering). `adjStateOrdering` stays at its
baseline `cell`. This is a cleaner single-variable test than the brief's framing, and it is the
version registered here. (`DAFOAM_SUBPC_TYPE=lu` is a SEPARATE later registration, per the brief;
NOT in this arm.)

Prior expectation is **pessimistic** (`LAB_STATE` dafoam board, 2026-09-09): the most-recommended
free remedy (`renumberMesh`) is already spent on every rung, so this arm's most likely value is a
**measured conditioning finding** — does `nd` move the condition number, and does that (or does it
not) translate into convergence — rather than a production fix. A NULL (levers do not clear it,
condition number stays ~1e11) is a valuable, honest result and is registered as such below.

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
**does `nd` reordering change the preconditioned condition number of the rung-3 adjoint operator,
and does any such change clear the `-3` stagnation?** `KSPCalcSingularVal: 1` measures the answer's
first half directly (`sMax/sMin` under `nd` vs the baseline `9.57e+10`); the convergence gate
measures the second half.

This is a zero-rental, on-box experiment. If `nd` clears it, the ladder gains a rung for free. If
it does not, we have a measured statement — the condition number under the last untried reordering —
that closes the on-box conditioning question honestly and tells Sanaa whether renting is
necessary-but-not-sufficient.

---

## 2. Three legs, one self-contained arm — ALL under the ONE pinned image `dafoam-subpclu:v1`

**Why three legs, and why self-contained.** The rung-3 baseline's historical adjoint image was
**NOT preserved** (inferred `subpclu:v1`, not a surviving launch artifact). Rather than *argue* the
historical image, this arm is made **self-contained by measurement** (Sanaa's exhaustion rule:
measured, not argued): it carries its **own** rung-3 NATURAL baseline leg (`BASELINE_R3`) under the
**same** pinned image the `nd` test leg uses. The historical unpinned image is therefore
**IRRELEVANT** — the `nd` attribution is §11-clean *by measurement*, because the fresh natural
reference and the `nd` test both run under one identical, digest-pinned toolchain
(`dafoam-subpclu:v1` @ `sha256:ba2d16ab…`, MEASURED as the rung-1/rung-2 ladder image; present on
the host; named explicitly by the CONTROL baseline's own `lever_echo.txt`). All three legs run
under **THIS ONE image**, so DAFOAM_CHARTER §11 toolchain identity holds trivially.

All three legs use `-task compute_totals` (one primal + one adjoint solve, then print totals) — the
same task the triage and stage-0 arms used. They run **SEQUENTIALLY** (CONTROL → BASELINE_R3 →
TEST_R3), each fully completing before the next starts.

### Leg 1 — CONTROL — rung 2 (42,120 cells), KNOWN to converge, + the `nd` lever set
- Source mesh / baseline runScript: `A3-rung2-n28-tpc1/` (`runScript_tpc1.py`; baseline CD **987** /
  CL **1171**, both `PetscConvergedReason: 2`, rc=0, wall 452 s = **30.13 core-min**; on disk).
- **Delta applied (`apply_delta`):** `jacMatReOrdering natural→nd` + `KSPCalcSingularVal 0→1`.
- **Prediction (frozen):** the control **MUST still converge** — `PetscConvergedReason: 2` on BOTH
  CD and CL before the `gmresMaxIters 2000` cap. Iteration count vs the baseline (987/1171) is
  REPORTED, **not** gated.
- **Purpose:** proves `nd` does not BREAK a working solve (the stage-0 lesson: L3 Richardson looked
  good at rung 1 and collapsed the rung-2 control to double `-5`). Runs **first** (cheap), and
  confirms the `KSPCalcSingularVal` print-token format on a converging solve for the grader's
  diagnostic regex (§4, §8).
- **If the control fails to converge** (any negative reason / collapse) → `nd` is **harmful**; the
  arm is inconclusive → item verdict **NOT A RESULT** ("nd harmful"), mirroring the stage-0 L3
  withdrawal.

### Leg 2 — BASELINE_R3 — rung 3 (79,560 cells), NATURAL ordering UNCHANGED (NO `nd`)
- Source mesh / baseline runScript: `A3-rung3-n52/runScript_rung3.py` (the SAME rung-3 source as
  TEST_R3; baseline stagnation `-3` at 4000 iters, wall 1426 s = **95.07 core-min**, peak
  11.65/22 GiB, historical `sMax/sMin = 9.57e+10`).
- **Delta applied (`apply_delta_baseline`):** `KSPCalcSingularVal 0→1` **ONLY** — `jacMatReOrdering`
  **STAYS `natural`** (the baseline lever config is UNCHANGED). This is the single load-bearing
  difference from the two `nd` legs.
- **Prediction (frozen):** the natural baseline **REPRODUCES the `-3` stagnation** (flat tail
  `< THETA_STAG`) under the arm's OWN pinned image. This fresh natural reference is what makes the
  `nd` attribution §11-clean by measurement.
- **Purpose:** establishes, *under the same pinned image the `nd` test uses*, that the rung-3 wall is
  real. The in-arm natural `sMax/sMin` (G-DIAG) is the **primary** comparator for TEST_R3's `nd`
  reading; the historical `9.57e+10` is the secondary check.
- **If BASELINE_R3 does NOT reproduce the stagnation** (it converges, is budget-limited, or
  crashes/not-evaluable) → the premise/toolchain is **not validated**; `nd`'s effect cannot be
  attributed without a confirmed natural baseline under this image → item verdict **NOT A RESULT**.

### Leg 3 — TEST_R3 — rung 3 (79,560 cells), + the `nd` lever set
- Source mesh / baseline runScript: `A3-rung3-n52/runScript_rung3.py` (SAME source as BASELINE_R3).
- **Delta applied (`apply_delta`):** `jacMatReOrdering natural→nd` + `KSPCalcSingularVal 0→1`.
- Baseline config otherwise bit-identical: `transonicPCOption 1`, `pcFillLevel 0`, `gmresRestart 200`,
  `gmresMaxIters 4000`, `gmresRelTol 1e-4`, `normalizeStates` unchanged, `adjStateOrdering cell`
  unchanged. **Everything except the §4 lever set is identical to BASELINE_R3**, so the only
  variables between the two rung-3 legs are `jacMatReOrdering: natural→nd` (`KSPCalcSingularVal 1` is
  common to both). **The question:** does `nd` clear the `-3` stagnation BASELINE_R3 reproduced?

---

## 3. The bright line — convergence ALONE is never a PASS (DAFOAM_CHARTER §2)

> A DAFoam gradient is not a result until a finite-difference table stands beside it at a graded
> band (DAFOAM_CHARTER §2, the bright line; VERIFICATION_CHARTER §7 fixes the band).

**A PASS requires BOTH** the TEST_R3 adjoint to converge AND an endpoint FD table to verify the
gradient. Therefore, and frozen here:

- **IF and only if the TEST_R3 adjoint converges**, a **mandatory FD-verification leg** runs before
  any PASS is declared. A converged-but-not-yet-FD-verified test is **PENDING (FD owed)**, never PASS.
- If the TEST_R3 adjoint does **not** converge, there is no gradient to verify → the FD leg does not
  run, and the verdict is a **measured conditioning finding** reported with the `sMax/sMin` reading (§4).
  This is **not a PASS and not a hidden failure** — it is a GATE FAIL on the convergence gate stated
  openly, carrying the condition-number measurement as its physics content (§7 verdict map).

---

## 4. Configuration and required proofs (the ONLY-variables-changed diff — check-1 reads this)

Each leg is staged by copying its **pinned baseline runScript** and applying **exactly** the delta
below — a single documented patch, so the baseline stays the single source of truth (never a
hand-retyped second copy).

**Pinned baseline inputs (md5, real — these are inputs, not the freeze pin):**
- Rung-3 baseline runScript (BASELINE_R3 **and** TEST_R3): `A3-rung3-n52/runScript_rung3.py`
  md5 `1ec70293a56a2cf5a30a889a96832c06`
- CONTROL baseline runScript: `A3-rung2-n28-tpc1/runScript_tpc1.py` md5 `edc9e14be7297a442e16f43fdda94fcc`

**Two deltas, applied leg-specifically (and NOTHING else):**

- **`apply_delta` (the `nd` delta — CONTROL and TEST_R3):** `jacMatReOrdering natural→nd` **plus**
  `KSPCalcSingularVal 0→1`.
- **`apply_delta_baseline` (the NATURAL delta — BASELINE_R3):** `KSPCalcSingularVal 0→1` **ONLY** —
  `jacMatReOrdering` **STAYS `natural`**. The launcher asserts natural SURVIVES and `nd` is ABSENT.

| key | baseline value (on disk) | CONTROL / TEST_R3 (`nd` delta) | BASELINE_R3 (natural delta) |
|---|---|---|---|
| `adjEqnOption.jacMatReOrdering` | `"natural"` | **`"nd"`** — the genuinely-new lever | **`"natural"`** — UNCHANGED (load-bearing) |
| `KSPCalcSingularVal` (top-level daOption) | `0` (dump reads `KSPCalcSingularVal 0`) | **`1`** | **`1`** |
| `adjStateOrdering` | `"cell"` | `"cell"` (held) | `"cell"` (held) |
| `adjEqnOption.pcFillLevel` | `0` | `0` | `0` |
| `adjEqnOption.gmresRestart` | `200` | `200` | `200` |
| `adjEqnOption.gmresMaxIters` | rung-3 `4000` / CONTROL `2000` | same | same (`4000`) |
| `adjEqnOption.gmresRelTol` | `1e-4` | `1e-4` | `1e-4` |
| `transonicPCOption` | `1` | `1` | `1` |
| `normalizeStates` | (baseline dict) | same | same |

The **only** variable between the two rung-3 legs is `jacMatReOrdering: natural (BASELINE_R3) →
nd (TEST_R3)`; `KSPCalcSingularVal 1` is common to all three legs. That single-variable contrast,
both under the ONE pinned image, is the arm's §11-clean measurement.

**Required proofs in every leg's log before any number counts (L-40; reuse the triage §4 pattern):**
1. `transonicPCOption 1;` in the DAOption dump (record logs of the negative control read `2;`).
2. **The leg's EXACT ordering** in BOTH the DAOption dump (`jacMatReOrdering <ord>;`) AND the KSP
   echo (`Mat ReOrdering: <ord>`): **`nd`** for CONTROL and TEST_R3 (a leg whose dump still reads
   `natural` did NOT apply the lever → REFUSE); **`natural`** for BASELINE_R3 (a BASELINE_R3 log
   reading `nd` is NOT the natural baseline → REFUSE). The grader keys the expected ordering on the
   leg name (`ND_LEGS = (CONTROL, TEST_R3)`).
3. **`KSPCalcSingularVal 1;`** in the DAOption dump of **all three** legs (baseline reads `0`).
4. `adjStateOrdering cell;` in the DAOption dump (unchanged — asserted present to prove no drift).
5. `ILU PC Fill Level: 0`, `GMRES Restart: 200`, `GMRES Max Iterations: <cap>` in the KSP echo.
6. **No** sub-LU banner (`DAFOAM_SUBPC_TYPE` unset).
7. The cold-from-uniform continuity signature of the leg's own mesh, captured at that leg's launch
   and asserted for the leg (per the family's L-40 practice).

The launcher writes a per-leg `lever_echo.txt` **declaring** the intended config; the solver's own
DAOption dump is what **confirms** it (declaration is never proof — the triage §4 rule).

---

## 5. Frozen gates, thresholds, caps and labels (prediction-first)

### G-CONV — the convergence gate (frozen)
From the raw log's residual trace `Main iteration N KSP Residual norm r_N ... s.` and the terminal
`**Completed**! Total iterations: T. PetscConvergedReason: R. <wall> s`:
- **CONVERGED** = `PetscConvergedReason == 2` (KSP_CONVERGED_RTOL, i.e. `gmresRelTol 1e-4` reached)
  AND `Total iterations T < cap`, on the graded objective(s). CONTROL requires this on **both** CD
  and CL; BASELINE_R3 and TEST_R3 key on the first (CD) solve.
- **STAGNATION** = a negative reason (`-3`) at exactly the cap **with a flat tail**: the relative
  residual change over the last `N_TAIL = 1000` iterations `|r_{T-1000} - r_T| / |r_T| < THETA_STAG`,
  with **`THETA_STAG = 1.0e-3`** (frozen). The rung-3 baseline gave `3.79e-07` over its last 2,700
  iterations — far below `THETA_STAG` — so it is unambiguously flat by this rule.
- **BUDGET-LIMITED (not a wall)** = a negative reason at the cap but the tail is **still descending**
  (`relative change ≥ THETA_STAG` and monotone) — reported as budget-limited, cap too small to
  decide (the rung-2 precedent, where the first `-3` was budget and converged at 1171 once the cap
  rose, reproducing to ten significant digits). This is **NOT** a stagnation verdict.
- **NOT EVALUABLE** = crash / OOM / memory guard trip before a reason is printed (§6).

### G-CTRL — the control-validity gate (frozen)
The CONTROL leg CONVERGED (both CD and CL, `reason 2`, before the `2000` cap). If not, `nd` broke a
converging solve → item **NOT A RESULT** ("nd harmful"). Iteration count vs baseline (987/1171) is
reported, not gated.

### G-BASE — the baseline-reproduction gate (frozen; the §11-clean-by-measurement gate)
The BASELINE_R3 leg (rung-3, NATURAL, no `nd`) must **REPRODUCE the `-3` stagnation** — leg state
`STAGNATION` (a negative reason at the `4000` cap with a flat tail `< THETA_STAG`) — under the arm's
OWN pinned image. This is what validates the premise and the toolchain: it proves, *under the same
image the `nd` test uses*, that the rung-3 wall is real and is not an artifact of the (unpreserved)
historical image. **If BASELINE_R3 does NOT stagnate** (it converges, is budget-limited, or crashes
/ is not evaluable), the premise is **not validated** → `nd`'s effect on TEST_R3 cannot be
attributed to conditioning without a confirmed natural baseline under this image → item verdict
**NOT A RESULT**. This gate is read **before** TEST_R3 is composed (§7).

### G-DIAG — the condition-number diagnostic (reported measurement, never a gate)
`sMax/sMin` from `KSPCalcSingularVal 1` at the last non-degenerate Krylov cycle (restart-boundary
`1./1.=1.` entries excluded, per `A3_NONNORMALITY_DIAGNOSTIC` §... ). Reported for **all three** legs.
The **primary** comparator for TEST_R3's `nd` reading is **BASELINE_R3's own in-arm natural reading**
(same image, same instrument) — that is the §11-clean-by-measurement contrast; the historical
natural baseline (rung 3: `9.57e+10`; rung 2: `~4.3e+10`–`9.6e+10` band) is the **secondary** check,
and BASELINE_R3 reproducing ~`9.57e+10` corroborates the toolchain. **If the solver does not emit a
singular-value token to the graded log**
(the exact DAFoam print format for `KSPCalcSingularVal 1` has never been observed on disk — every
prior reading came from the offline `KSPComputeExtremeSingularValues` diagnostic), the value is
reported **`NOT_MEASURED` and named**, never composed into a verdict. The CONTROL leg's log
establishes the token format; the grader's diagnostic regex is confirmed against it before the TEST
leg is graded (§8 pre-flight).

### G-FD — the bright-line finite-difference gate (frozen; CONDITIONAL on TEST convergence)
Runs **only if** the TEST adjoint converged. Reuses the A3 family's validated FD protocol
(DAFOAM_CHARTER §7; `A3_RUNG3_N52_PREREGISTRATION.md` §5) and the `d8r_grade.py` band machinery:
- `primalMinResTol 1e-8`, `primalMinResTolDiff 1e4`; central differences; **registered steps
  `[5.0e-4, 1.0e-3, 2.0e-3]`**, middle step `1.0e-3` the reference (the A3 family's used step).
- **PLATEAU**: the middle step agrees with at least one neighbour to `PLATEAU_TOL = 10%`, else that
  component is NOT A RESULT.
- **Band D (per component)**: `|d_FD − J_adj| / |d_FD| ≤ FD_BAND = 5.0%` **AND** same sign — a sign
  flip is GATE FAIL whatever the magnitude.
- **Band E (aggregate)**: vector-relative error `≤ AGG_BAND = 5.0%`.
- **Registered components**: the A3 family's FD-verified set — `patchV[1]`, `twist[1]`, `shape[115]`
  (rung-2 verified at 0.0077% / 0.2740% / 0.0172%); `of = CD`, `wrt = patchV` (+ twist, shape).
  **`MIN_GRADED = 2`** evaluable components (A3 family rule); fewer → the leg is NOT A RESULT.
- Arm FD PASS = every evaluable component PASS with ≥ 2 evaluable.

### Caps (frozen; rule 12) — see §6 cost table for the derivation
- CONTROL per-leg cap **45 core-min**; BASELINE_R3 per-leg cap **130 core-min**; TEST_R3 per-leg cap
  **130 core-min**; FD-leg cap (conditional) **90 core-min**; item ceiling **395 core-min** (sum of
  the per-leg caps — the hard stop; predicted spend ~220, +FD ~60–70 conditional). A crossing STOPS
  the leg (overrun stops the run, rule 12) and is a G-CAP GATE FAIL, reported.

---

## 6. Memory guard and cost (rule 12)

**Memory guard (the constraint most likely to end the two rung-3 legs):** record rung-3 peak
11.65 GiB (the baseline was memory-comfortable). Container cap **`--memory=22g` — now DOCKER-ENFORCED**
(`docker run --memory=22g --memory-swap=22g --oom-score-adj=500`, the D6RF10 pattern), plus a host
floor **6 GB** by inspection. `nd` reordering changes the fill pattern of ILU(0) only marginally
(ILU(0) has fixed sparsity ≈ the matrix graph), so a large memory jump is not expected; but the leg
**STOPS** if the container hits the cap (OOM-kill), host MemAvailable falls below 6 GB, or swap
grows. **A memory death is NOT a conditioning verdict** (standing precedent) → reported as NOT
EVALUABLE / **BLOCKED** with the memory numbers, conditioning question left open.

**Cost table (all figures per-leg; core-min = wall_s × ranks ÷ 60; np = 4):**

| leg | basis (measured, on disk) | predicted core-min | cap core-min | incurred when |
|---|---|---|---|---|
| CONTROL (rung 2 + `nd`) | rung-2 converged baseline 452 s = 30.13 core-min (`A3-rung2-n28-tpc1/.t0/.t1`) | **~30** (30–40) | 45 | always |
| BASELINE_R3 (rung 3, natural) | rung-3 baseline 1426 s = 95.07 core-min (`A3-rung3-n52` ledger) | **~95** (95–110) | 130 | always |
| TEST_R3 (rung 3 + `nd`) | rung-3 baseline 1426 s = 95.07 core-min (`A3-rung3-n52` ledger) | **~95** (95–110) | 130 | always |
| FD leg (conditional) | A3 family FD arm ~60–70 core-min (`A3_RUNG3_N52_PREREGISTRATION.md` §8 stage-2 basis) | **60–70** | 90 | **only if TEST_R3 converges** |

- **Total, three legs always incurred** (the pessimistic, most-likely path where TEST_R3 does not
  converge): ~30 + ~95 + ~95 = **~220 core-min** (chief-approved ~220; range 155–260).
- **Total if TEST_R3 converges and FD runs**: + 60–70 = **~280–290 core-min** (item ceiling 395 —
  the sum of per-leg caps, the hard stop).
- **Derived $** at the reported-by-owner rate $0.0513/core-h (DERIVED, not measured — the box
  cannot read its own billing, COMPUTE_BUDGET §5): 220 core-min → 3.67 core-h → **$0.188**; 290
  core-min → 4.83 core-h → **$0.248**. Both far under the $25/run pre-authorization.
- **The added leg vs the prior 2-leg draft:** the self-contained arm costs one extra rung-3 leg
  (BASELINE_R3, ~95 core-min) over the prior 2-leg design — the price of §11-cleanliness by
  measurement (a fresh natural baseline under the pinned image) rather than by argument. Chief
  approved ~220 core-min for this 3-leg arm.
- **Estimate-vs-actual calibration (rule 12):** on completion the team appends a row to
  `docs/COST_CALIBRATION.md` — ratio actual/predicted per leg, gap attributed (contention / waste /
  misprediction, waste named separately), dollars derived and labelled derived.

---

## 7. Verdict map (frozen; vocabulary strictly PASS / GATE FAIL / NOT A RESULT / BLOCKED / PENDING)

Read in order; the first matching row is the item verdict.

| condition | item verdict | content reported beside it |
|---|---|---|
| CONTROL memory death / crash before a reason | **BLOCKED** | memory numbers; conditioning question open |
| CONTROL does not converge (any negative reason / collapse) | **NOT A RESULT** | "nd harmful" — it breaks a converging solve; the arm cannot attribute a rung-3 stagnation to conditioning (stage-0 precedent) |
| CONTROL converged; **BASELINE_R3 does NOT reproduce the `-3` stagnation** (converges, budget-limited, crash / not-evaluable) | **NOT A RESULT** | the premise/toolchain is **not validated** — `nd`'s effect cannot be attributed without a confirmed natural baseline under this image; BASELINE_R3 leg state + `sMax/sMin` if emitted |
| CONTROL converged; BASELINE_R3 STAGNATION (`-3`, flat tail); TEST_R3 memory death / crash before a reason | **BLOCKED** | memory numbers; TEST_R3 `sMax/sMin` if emitted |
| CONTROL converged; BASELINE_R3 STAGNATION; TEST_R3 `-3` at cap, **budget-limited** (tail still descending) | **NOT A RESULT** | cap too small to decide; residual trend; recommend a re-cap arm |
| CONTROL converged; BASELINE_R3 STAGNATION; TEST_R3 **STAGNATION** (`-3` at cap, flat tail `< THETA_STAG`), memory comfortable | **GATE FAIL** (on G-CONV) | **the measured conditioning finding**: TEST_R3 `sMax/sMin` under `nd` vs **BASELINE_R3's in-arm natural** reading (primary) and historical `9.57e+10` (secondary); iteration count; flat-tail numbers. **"Free conditioning exhausted: `nd` does not clear the rung-3 wall, MEASURED under a §11-clean self-contained baseline."** NOT a hidden failure. |
| CONTROL converged; BASELINE_R3 STAGNATION; TEST_R3 converged; FD leg **not yet run** | **PENDING** (FD owed) | `PENDING: <FD run path>`; never reported as PASS |
| CONTROL converged; BASELINE_R3 STAGNATION; TEST_R3 converged; FD leg run, FD **fails band or sign flip** | **GATE FAIL** (on G-FD, the bright line) | the FD table; the failing component(s) |
| CONTROL converged; BASELINE_R3 STAGNATION; TEST_R3 converged; FD leg run, FD **passes** (≥2 evaluable, all PASS, band E ≤ 5%) | **PASS** | the FD table; a new verified rung on the A3 ladder |
| any G-CAP crossing | folds to **GATE FAIL** unless a higher NOT A RESULT / BLOCKED row already fired | the core-min overrun |

Rows are read **in order**; the first match is the item verdict (the grader's `compose_item`
implements exactly this order). `KSPCalcSingularVal` reading (G-DIAG) is REPORTED in every
non-BLOCKED outcome for all three legs; the TEST_R3-vs-BASELINE_R3 in-arm natural contrast is the
arm's durable deliverable even on a GATE FAIL.

---

## 8. §2bb pre-flight — applicability of `check_ladder_preflight.py`, and the evidence used instead

**`scripts/check_ladder_preflight.py` does NOT structurally fit this arm, and here is why.** Its
manifest models a **time-marched primal ladder**: `deadline_sizing` is
`measured_per_step_wall_s × steps_to_endTime`, i.e. a per-`deltaT`-timestep cost model, and
`solver_path` asserts a `decomposePar` reaches "first solve." The graded quantity here is a
**capped-iteration adjoint KSP solve** driven by DAFoam/OpenMDAO `compute_totals`; its wall is
governed by Krylov iteration count to the `gmresMaxIters` cap, not by `endTime` time steps. Forcing a
KSP-iterations-as-timesteps mapping through the checker would pass numerically but misrepresents the
model, so it is **disclosed here, not relied on as the primary instrument**.

The §2bb **principle** — a deadline SIZED from a measured sample with the 1.25× margin, and each
distinct solver path shown to run cleanly once on disk — is met in the arm's own terms, and this is
the pre-flight evidence of record:

1. **Deadline sizing (measured + 1.25× margin):**
   - BASELINE_R3 and TEST_R3 deadline `1426 s × 1.25 = 1782.5 s → 1800 s`, sized from the measured
     rung-3 baseline wall 1426 s at 4000 iters (`A3-rung3-n52` ledger `.t0`/`.t1`, on disk). n
     sampled = 4000 iterations — a measurement, not a two-step guess. (Both rung-3 legs share the
     source, the path and the deadline.)
   - CONTROL deadline `452 s × 1.25 = 565 s → 600 s`, sized from the measured rung-2 converged
     baseline wall 452 s (`A3-rung2-n28-tpc1/.t0/.t1`, on disk).
2. **Distinct solver-path coverage (cleanly exercised once, on disk):** the path
   `DARhoSimpleCFoam | compute_totals | np=4 | decomposePar` is the SAME path that ran rungs 1, 2 and
   3 to completion (rung 2 rc=0, `A3-rung2-n28-tpc1/.rc`; rung 1 PASS). It has demonstrably reached its
   first primal solve and decomposed cleanly — stronger evidence than a fresh smoke, because it is the
   completed converging run itself. No new decomposition method or solver is introduced by the lever
   set (`nd` and `KSPCalcSingularVal` are adjoint-linear-solver options, downstream of decomposition).
3. **Instrument-format pre-flight (specific to this arm):** the CONTROL leg's converging log
   establishes the `KSPCalcSingularVal 1` print-token format. The grader's `sMax/sMin` regex
   (`G-DIAG`) is confirmed to match the CONTROL log **before** the rung-3 legs (BASELINE_R3, TEST_R3)
   are graded; if the token is absent, `G-DIAG` is `NOT_MEASURED` and named (§5), never fabricated.

A `LADDER_PREFLIGHT.json` manifest with **all three rungs** (CONTROL smoke → clean rung-2
compute_totals log; BASELINE_R3 + TEST_R3 smoke → the rung-3 baseline stage-1 log; all one distinct
path `DARhoSimpleCFoam|scotch|4`) is provided in this dir, the KSP-iterations-as-steps mapping
disclosed in its own `_note` field. **Run through the checker by this lane, result verbatim:**
`PASS: ladder A3FL1 pre-flight complete (3 rungs, 1 distinct paths)` — `EXIT=0`
(`python3 scripts/check_ladder_preflight.py <this dir>/LADDER_PREFLIGHT.json`). Every rung's deadline
is arithmetically consistent with its measured sample and carries the 1.25× margin; the single
distinct path is covered by a passing smoke. The supervisor confirms at freeze; the in-arm evidence
above stands as the primary record.

---

## 9. §2ba — the launcher, the G-FREEZE gate, and the detached autograder

- **Launcher** `a3fl1_launcher.sh`: stages each of the **three** legs (copy the pinned baseline
  runScript; apply the leg's §4 delta — `apply_delta` (`nd`) for CONTROL and TEST_R3,
  `apply_delta_baseline` (natural + `KSPCalcSingularVal` only) for BASELINE_R3; write a per-leg
  `lever_echo.txt` naming the exact config), then runs each leg **inside a DAFoam Docker container**
  under the ONE pinned image (`docker run -d`, `--memory=22g` DOCKER-enforced, `timeout -k` deadline
  inside the container, rc from `docker inspect .State.ExitCode` — never `$?` of a setsid/timeout
  line). The three legs run **sequentially in the detached orchestrator's foreground** (CONTROL →
  BASELINE_R3 → TEST_R3); `A3FL1_LADDER_DONE` is written **only after all three finish**. It carries
  a **G-FREEZE gate**: it reads this file's `PERMISSION:` line and **REFUSES to launch** unless it
  reads `FROZEN`; while this draft reads `NOT_FROZEN` the launcher exits non-zero without staging
  anything. It also verifies the grader md5, both baseline-runScript md5s, and the **§11 image
  digest** (`IMG`/`IMG_DIGEST`, one image for all three legs) against the pins below and refuses on
  any drift.
- **Detached autograder** `a3fl1_autograde.sh` (mirrors `d6rf10_autograde.sh`): runs under `setsid`
  (PPID=1), polls the run-root ledger for the `A3FL1_LADDER_DONE` marker (CEIL sized to the arm's wall
  + margin), md5-verifies the frozen grader and REFUSES (exit 2) on drift, grades each leg log with the
  frozen grader, writes per-leg JSON + a single `A3FL1_AUTOGRADE_DONE.txt`. It **declares no verdict**
  and files no README / cost row — those are the supervisor's calls after reading the DONE file.

**FREEZE PINS (PLACEHOLDERS — the dafoam-supervisor sets these at freeze):**
- This file's committed blob sha: `<SET AT FREEZE>` (the grading path is fixed at the commit, rule 2).
- Grader `a3fl1_grade.py` md5: `<SET AT FREEZE>` — the launcher and autograder both pin this; the
  md5-drift limb REFUSES while it is the placeholder, so nothing grades with an unpinned instrument.
- **§11 toolchain image (ONE image, all three legs)** — `IMG` = `dafoam-subpclu:v1`, `IMG_DIGEST` =
  `sha256:ba2d16ab9d575ed3167abe31344aa58fb42fef1a8b27db60baeb505ab9413517` (MEASURED as the
  rung-1/rung-2 ladder image; present on host). Both fields are `<SET_AT_FREEZE>` /
  `<PLACEHOLDER_AT_FREEZE>` placeholders in the launcher; the digest-verify gate REFUSES until the
  supervisor pins them and reads the host image's real digest, refusing on drift. (Because the arm is
  self-contained — its own natural baseline under this image — the unpreserved historical rung-3
  image is irrelevant; §11 holds under this ONE pinned image.)
- Baseline runScript md5s (real, pinned now): rung-3 (BASELINE_R3 + TEST_R3)
  `1ec70293a56a2cf5a30a889a96832c06`, CONTROL `edc9e14be7297a442e16f43fdda94fcc`.

---

## 10. Planted-zero control (rule 3)

The grader plants a known perturbation and refuses if the reader cannot see it — two controls:
1. **Residual-trace / convergence reader:** a fixture log carries a planted converging trace
   (`reason 2`, iterations below cap) and a planted stagnant trace (`-3`, flat tail); the grader's
   selftest asserts G-CONV reads CONVERGED and STAGNATION respectively, and a mutated "flat but
   labelled converged" fixture is caught.
2. **FD-table reader:** mirrors `d8r_grade.py` — a copy of each FD table with a known `PLANT` added to
   every physical derivative is re-read through the same reader; the grade REFUSES unless every value
   moved by exactly `PLANT`. The instrument's own `CTRL` planted row is re-read and the grade refuses
   if the reader cannot see the planted non-zero.

The grader carries **no `assert`** (L-332; it counts `ast.Assert` nodes in its own source and refuses
on any) and **REFUSES (exit 2) rather than degrade** on any missing/garbage physics field (rule 4,
L-342). `--selftest` runs the planted fixtures against a frozen expected-unit count.

---

## 11. Completion rule (rule 4)

A leg is done only if: rc = 0 (from the ledger, captured inside the detached wrapper); the log carries
a `**Completed**! Total iterations: ... PetscConvergedReason: ...` terminal line; the age guard holds
(the totals artifact / log is NEWER than the leg's own `0/` datum, and the run root did not exist
before launch); the required-proof tokens of §4 are present. A leg failing any clause is NOT a result
for grading and the grader REFUSES. (For an adjoint `compute_totals` leg the "fields present" clause of
the thermal-family completion rule does not apply verbatim; the analogue is the totals print / terminal
`Completed` line and the age-guarded log — stated here so the substitution is disclosed, not silent.)

---

## 12. Provenance and reading list
- Baselines & prior work: `A3_RUNG3_N52_RESULT.md`, `A3_RUNG3_N52_PREREGISTRATION.md`,
  `A3_TRIAGE_LEVERS_PREREGISTRATION.md` (§8/§10), `A3_NONNORMALITY_DIAGNOSTIC_PREREGISTRATION.md`,
  `docs/dafoam/PRIOR_WORK_INVENTORY.md` (§1e / lines 100-127).
- Charters: `DAFOAM_CHARTER.md` §2 (bright line), §7-referenced band; `VERIFICATION_CHARTER.md`
  §2/§2b/§2bb/§2ba/§7; `COMPUTE_BUDGET_CHARTER.md` §5; CLAUDE.md rules 2, 3, 4, 5, 12.
- Instrument reused: `cases/dafoam/ladder-a/A6/curriculum_D8R/d8r_grade.py` (FD band machinery,
  planted controls, refuse-not-degrade, no-assert), `d6rf10_autograde.sh` (detached autograder).
