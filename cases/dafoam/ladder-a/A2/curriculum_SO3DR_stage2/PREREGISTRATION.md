DRAFT — NOT FROZEN — awaiting supervisor check-1 read and freeze

# CURRICULUM SO-3D-R — STAGE 2. THE cl04-STANDALONE DISCRIMINATION EXPERIMENT. PRE-REGISTRATION (DRAFT).

**Version 0.9 DRAFT. NOT FROZEN. NOT ENQUEUED. NOT LAUNCHED. ZERO SOLVER CORE-MINUTES SPENT.**
Dated **2026-09-07**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.

**This document is a draft awaiting the `dafoam-supervisor`'s personal `SUPERVISION_CHARTER.md` §3
checks** — check 1 (the changed grading/rig code read as a diff) and check 4 (pre-registration
**committed before compute**). Neither is discharged here; the freeze is the supervisor's and **is
NOT taken by this draft.** `CLAUDE.md` rule 2: the gate, threshold, cap and label below are committed
**before** any Stage-2 solver starts; nothing here has run.

**Every decision below is `[lab-attributed]`.** `CLAUDE.md` rule 9: no agent message is Sanaa's
consent. **SUBMISSIONS PARKED** — nothing in this item is filed, sent, emailed, uploaded, registered,
posted or commented outside this box, now or on completion (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md`
§10).

**This item is DIRECTED by `../curriculum_SO3DR/RESULTS.md` §9 (RULING 3, the `dafoam-supervisor`
personally, under Sanaa 4ae4b33, 2026-09-06T23:29:23Z).** RULING 3 §9.2 specifies the experiment and
its gate; this draft registers them and does not redesign the question.

> ### ⚠ PRESERVED VERBATIM FROM RULING 2 — BINDING ON THIS DOCUMENT AND EVERY READER OF IT
> `cl04` fails at **88.29 %** against the `D4` single-point control's **2.222 %** on the same base
> mesh, solver, image digest and identical `primalMinResTol`/`primalMinResTolDiff` — a **39.7×**
> elevation. **THIS RATIO WAS NOT A REGISTERED GATE, WAS NEVER SCORED, AND MAY NOT BE QUOTED AS A
> VERDICT — anywhere, by anyone, at any later date.** It is a **DATUM**. Quoting it as a verdict
> would be choosing the statistic after seeing the answer. Stage-2 does not gate on it, does not
> "confirm" it, and does not convert it into anything.

**Stage-1 stands untouched.** SO-3D's `NOT A RESULT` stands; SO-3D-R's Stage-1 verdicts stand as
emitted; §5's frozen contradiction stays **disclosed, not repaired** (rule 2 gates closed, rule 6
forbids the edit). This document does **not** reopen or re-grade Stage-1.

**Toolchain row** (`DAFOAM_CHARTER.md` §6): every Stage-2 leg runs on the **PATCHED** row — image
`dafoam-idwarp-rot:v1`, digest
`sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`, `libidwarp.so` md5
`85f59e87253e0a71a813f64ca6e4c425` — the same row the D6R multipoint, D4/D5 controls and D6RF4
ran on. **There is no shipped row for the multipoint pathology and this stage does not manufacture
one.**

---

## 0. WHAT STAGE-2 ANSWERS, AND WHY G-SO3D-3 STRUCTURALLY COULD NOT

**The one question.** Is `cl04`'s elevated per-primal failure rate **INTRINSIC to `cl04`'s own
primal** (the A2-wing convergence pathology D6RF4 measured — `maxNonOrth 71.48 > 70`, p first-solve
at ~1.66× the 1e-05 floor), or an **ARTEFACT of the multipoint aborted-trial coupling** (one
scenario's boolean `primalFail` abandons the whole trial; §3.3, and the field-reuse / warm-start the
assembly carries across IPOPT iterates)?

**Why Stage-1's G-SO3D-3 could not answer it.** G-SO3D-3's registered statistic is
`min(r)` over the three scenarios `cl04`/`cl05`/`cl06`. RULING 2 recorded that this statistic is
**driven to zero by the aborted-trial mechanism regardless of whether `cl05`/`cl06` are healthy** —
they are barely evaluated (89 starts vs `cl04`'s 760) and never reached in a failing trial. It is one
of the family's "statistics that cannot answer their own question." More fundamentally: **every
scenario G-SO3D-3 compares lives INSIDE the same multipoint assembly**, so no contrast among them can
separate "`cl04`'s own primal" from "the assembly context" — both are properties measured *within*
the assembly. The comparison Stage-1 structurally cannot make is **inside-assembly vs
outside-assembly on the same design.**

**How Stage-2 makes exactly that comparison.** It takes the **exact `cl04` design vectors the D6R
multipoint actually evaluated** and re-runs a registered, stratified sample of them as **standalone
single-point primals, outside the mphys/OpenMDAO multipoint assembly.** Design is held perfectly
fixed (same shape, twist and patchV vectors, same base mesh, solver, image digest, tolerances); the
**only** thing that changes is the assembly context. This is the property G-SO3D-3 and PLANT-B's
degeneracy both lacked (RULING 2): **the gate answers its own question.**

---

## 1. THE STANDALONE SINGLE-POINT RIG, AND THE REGISTERED STRATIFIED SAMPLE

### 1.1 The rig — how `cl04` runs OUTSIDE the multipoint assembly

**The rig MUST BE BUILT — it does not exist on disk.** The D6R multipoint runscript
(`../curriculum_D6R/d6r_opt_runScript.py`) instantiates `Top(Multipoint)` with three
`ScenarioAerodynamic` scenarios, shared `shape`/`twist` DVs connected to three geometries, per-scenario
`patchV`, an **`om.ExecComp`** objective coupling `CD04`/`CD05`/`CD06`, and `findFeasibleDesign` +
`run_driver`. No existing rig runs a single bare `cl04` primal from an externally supplied design
vector. The Stage-2 rig (`so3dr_stage2_standalone_runScript.py`, to be written and pinned at freeze)
is derived from `d6r_opt_runScript.py` by:

1. **One scenario only** — a single `cl04` geometry + mesh + `ScenarioAerodynamic`; **the `obj`
   `om.ExecComp`, the `cl05`/`cl06` subsystems, and all cross-scenario connects are removed.**
2. **No optimiser, no trim** — `pyOptSparseDriver`, `findFeasibleDesign` and `run_driver` are removed.
   The registered `patchV_cl04 = [100, AoA]` from the D6R block is set directly; **AoA is NOT
   re-trimmed** (using the exact evaluated AoA is what holds design fixed). The primal is run once via
   `prob.run_model()` (`task="run"`), not `run_driver`.
3. **Exact design injection** — `dvs.shape` (90 values), `dvs.twist` (7 values) and
   `dvs.patchV_cl04` ([100, AoA]) are set to the exact arrays parsed from the registered
   `dv_block_line` in the D6R log, then the mesh is warped by DVGeo/idwarp exactly as the multipoint
   would. The geometry is therefore the identical warped mesh the multipoint evaluated.
4. **Fresh start, isolated** — each leg starts from the case's own `0/` fields (no warm-start,
   no field reuse). This is deliberate: warm-start/field-reuse across IPOPT iterates is one component
   of "the assembly context" the experiment isolates (see §6 on what a LOW result may and may not
   attribute).
5. **Identical numerics, identical row** — `primalMinResTol = 1.0e-8`, `primalMinResTolDiff = 1e3`
   (accept floor `1e-05`, `N-D42`/`N-D43`), same base mesh, same solver `DARhoSimpleFoam`, same
   PATCHED image digest, `np = 4` — all matching the D6R multipoint and the D6RF4 measured basis. **No
   tolerance, solver, mesh or floor change is made** (that would be a remedy; Stage-2 registers none).

**Per-leg outcome.** A leg **fails** iff its own primal log carries the DAFoam
`Primal solution failed!` cutback banner (the same anchored banner Stage-1's reader counted,
`RE_FAIL_BANNER`, 671 of which populated `cl04` in D6R). `r_sa` is the fraction of registered legs
carrying it.

### 1.2 The registered stratified sample — frozen from the D6R log BEFORE compute

The sample is drawn from the **frozen** D6R log
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/O_mp_20260828T162849Z_1898072.log`,
**sha256 `394d9f5d8c59ea79602e678cec7a75915bef53a048b61e153d835fce57fc675d`** (264,607 lines,
unchanged since 2026-08-29). Design vectors are recovered from the `Driver debug print for iter
coord` blocks (768 in the log), each of which declares `dvs.patchV_cl04 = array([100, AoA])`,
`dvs.shape` (90), `dvs.twist` (7). Each `cl04` primal record is attributed and its banner status read
by the Stage-1 reader's **own** `parse_primal_records` (`../curriculum_SO3DR/so3dr_replay.py`), so the
FAILED/SUCCEEDED partition is byte-identical to the graded Stage-1 census
(`cl04`: 760 starts, 671 failed, 89 succeeded).

**Deterministic and reproducible.** The sample is produced by
`so3dr_stage2_build_sample.py` (md5 `89828c709c30b95205db0e37fd9dfc84`, seeded
`SEED = 20260907`), pinned here; its output `so3dr_stage2_registered_sample.json`
(md5 `55bf8e2dcc07fbe3197f2c53421ad019`) is the frozen sample. Re-running the builder against the
sha256-pinned log reproduces the table below exactly. **The sample is fixed before any Stage-2
compute, so no leg can be added, dropped or reweighted after seeing a Stage-2 result.**

**Stratification, and why 2:1 FAILED:SUCCEEDED.** N = 36: **24 designs that FAILED inside the
multipoint** + **12 designs that SUCCEEDED inside the multipoint** (populations 671 and 89). The
FAILED stratum is the discriminating one — *do the designs that failed in the assembly fail on their
own primal?* The SUCCEEDED stratum is a built-in rig-validity control — those designs converged in
the assembly and should converge standalone under **both** hypotheses. The 2:1 ratio makes the
pooled `r_sa` land near **24/36 ≈ 67 %** under the intrinsic hypothesis (clear HIGH) and near
**0 %** under the coupling hypothesis (clear LOW); see §2. The strata deliberately overlap in AoA
(both carry designs at AoA ≈ 0.57–0.93°), so the contrast is context, not angle.

| dv_block_line | record_start_line | ordinal | cl04 AoA (deg) | multipoint outcome |
|---|---|---|---|---|
| 10870 | 10911 | 39 | 2.93038337 | SUCCEEDED |
| 13801 | 13857 | 48 | 2.76545079 | SUCCEEDED |
| 19906 | 19964 | 72 | 2.40676146 | SUCCEEDED |
| 22078 | 22134 | 80 | 1.76225717 | SUCCEEDED |
| 22971 | 23027 | 83 | 1.73843295 | SUCCEEDED |
| 32169 | 32225 | 117 | 1.26074887 | SUCCEEDED |
| 33596 | 33652 | 122 | 1.13583455 | FAILED |
| 46954 | 47012 | 172 | 0.58721627 | FAILED |
| 47225 | 47283 | 173 | 0.56807238 | SUCCEEDED |
| 55343 | 55401 | 203 | 0.57832947 | FAILED |
| 57507 | 57565 | 211 | 0.59201742 | FAILED |
| 77546 | 77604 | 285 | 0.58489318 | FAILED |
| 78630 | 78688 | 289 | 0.57847025 | FAILED |
| 91630 | 91688 | 337 | 0.57817210 | FAILED |
| 98943 | 99001 | 364 | 0.57810201 | FAILED |
| 106650 | 106708 | 393 | 0.57800036 | FAILED |
| 110446 | 110504 | 407 | 0.58055234 | SUCCEEDED |
| 112068 | 112124 | 413 | 0.73362860 | FAILED |
| 116129 | 116187 | 428 | 0.58562294 | FAILED |
| 116671 | 116729 | 430 | 0.58540771 | SUCCEEDED |
| 118293 | 118349 | 436 | 0.62484450 | FAILED |
| 121539 | 121597 | 448 | 0.57579595 | FAILED |
| 125872 | 125928 | 464 | 0.88036416 | FAILED |
| 136369 | 136425 | 503 | 0.93168308 | FAILED |
| 157359 | 157415 | 581 | 0.93166260 | FAILED |
| 164898 | 164954 | 609 | 0.92455331 | FAILED |
| 165167 | 165223 | 610 | 0.92769749 | FAILED |
| 177820 | 177876 | 657 | 0.93000504 | FAILED |
| 187241 | 187297 | 692 | 0.93001713 | FAILED |
| 208578 | 208634 | 771 | 0.93046812 | FAILED |
| 214774 | 214830 | 794 | 0.95172222 | FAILED |
| 217735 | 217793 | 805 | 0.91930028 | SUCCEEDED |
| 218471 | 218529 | 808 | 0.91742064 | SUCCEEDED |
| 221452 | 221510 | 819 | 0.86854311 | SUCCEEDED |
| 235144 | 235200 | 869 | 0.88226794 | FAILED |
| 249576 | 249632 | 922 | 0.86290253 | FAILED |

The full design vectors (shape[90], twist[7], patchV_cl04) are recovered from each `dv_block_line`
at run time; only the block line and the corroborating AoA are tabulated here. Each leg's rig must
echo-check the injected vector against the block (F4, §4).

---

## 2. THE GATE — G-SA-DISCRIM (thresholds, prediction, controls) — REGISTERED BEFORE COMPUTE

> **G-SA-DISCRIM.** `r_sa` = fraction of the 36 registered standalone legs carrying the
> `Primal solution failed!` banner.
> - **`r_sa ≥ 50 %` (≥ 18/36) → HIGH → verdict: "cl04's OWN primal is the pathology"** — the A2-wing
>   convergence pathology; the D6RF5-class numerics/mesh fix is the **candidate** remedy (never
>   established by this stage). **This is a RESULT**: the hypothesis that the multipoint coupling is
>   primary is **REFUTED**.
> - **`r_sa ≤ 10 %` (≤ 3/36) → LOW → verdict: "the MULTIPOINT ABORTED-TRIAL COUPLING is the cause"**
>   — routed to the `om.ExecComp` propagation code-read that §3.3/§4 H5 leaves NOT DONE. **This is a
>   RESULT.**
> - **`10 % < r_sa < 50 %` (4–17 / 36) → NOT A RESULT** — indeterminate; the sample did not
>   discriminate.

**Boundary arithmetic, fixed now:** 18/36 = 50.0 % → HIGH; 17/36 = 47.2 % → NOT A RESULT;
3/36 = 8.33 % → LOW; 4/36 = 11.1 % → NOT A RESULT. `≥` and `≤` are inclusive at the bands.

**Controls already measured and on record** (SO3DR RESULTS §3.6, §3.2), which bracket the bands:
D4 single-point control **2.222 %**; D5 single-point control **1.1696 %**; multipoint `cl04`
**88.29 %**. The LOW band sits just above the single-point controls; the HIGH band sits far below the
multipoint rate. `r_sa` is not compared to the 39.7× datum and does not reconstruct it.

**REGISTERED PREDICTION — written so it can be wrong.** `r_sa` is predicted **below the 88.29 %
multipoint rate and in a low-to-moderate band — leaning LOW, possibly indeterminate; predicted NOT
HIGH.** Reasoning: the same-mesh single-point **D4 control fails at only 2.222 %**, and the A2-wing
primal carries a **real-but-mild** pathology (D6RF4: `maxNonOrth 71.48 > 70`, p first-solve at
~1.66× the `1e-05` floor), not a catastrophic one. If the 88 % multipoint rate were `cl04`'s own
primal, D4 would not sit at 2.2 %. The prediction therefore leans toward the **coupling /
warm-start** story with a mild-primal contribution. **The experiment can refute this either way: if
`r_sa ≥ 50 %`, the prediction is falsified and cl04's own primal is the pathology.**

**Binomial resolution — why N = 36 (24+12) resolves the 10 %/50 % bands.** Under the coupling
hypothesis, each leg's standalone failure probability is near the D4 control (~2.2 %): expected
failures ≈ 36 × 0.022 ≈ 0.8, and P(≤ 3 | n = 36, p = 0.022) ≈ 0.99 — a clean LOW. Under the intrinsic
hypothesis, the 24 FAILED-stratum designs fail near-certainly and the 12 SUCCEEDED-stratum designs
convert near-0, so expected ≈ 24 and P(≥ 18) ≈ 1.0 — a clean HIGH. The 40-point gap between the
bands far exceeds the ±1.96·√(p(1−p)/36) ≈ ±15 % sampling half-width at mid-range, so a rate near
either control lands cleanly in its band and only a genuinely moderate rate (4–17 failures,
11–47 %) is returned as NOT A RESULT — which is the honest outcome for an indeterminate rate.

**Diagnostic decomposition, NEVER gated.** The per-stratum standalone rates
`r_fail` (over the 24 FAILED designs) and `r_succ` (over the 12 SUCCEEDED designs) are reported
beside `r_sa` for mechanism, not scored. `r_succ` feeds the rig-confound falsifier F3 (§4).

---

## 3. CONTROLS, COMPLETION, DECOMPOSITION, MEMORY

### 3.1 Planted-zero control (`CLAUDE.md` rule 3) — the rate reader must be shown able to see a banner

The banner reader emits a zero only if it has first been shown able to see a non-zero. Before scoring,
the reader:
1. **PLANT-SA-BANNER** — takes a copy of a leg log **known to be clean** (0 banners), inserts one
   synthetic `Primal solution failed!` line at a registered offset, and requires the reader to report
   **exactly +1** on the planted copy. If the reader still reads 0, it **REFUSES (exit 2)** and no
   `r_sa` is emitted — a zero from a reader that cannot see a planted banner is not evidence.
2. **PLANT-SA-DECOY** — inserts a non-banner line containing the substring `failed` but not matching
   the anchored banner regex; the reader must **NOT** count it (guards over-counting; F2).
3. **Originals untouched** — the plant operates on copies; every original leg log's sha256 is
   unchanged after the plant pass, asserted by re-read (not by control flow).
The plant report (`so3dr_stage2_plant_report.json`) is written **incrementally**: a plant not yet
reached reads `NOT RUN`, never absent and never `PASS` (Stage-1's §2.2 disclosure repair, carried).

### 3.2 Strict completion + age guard (`CLAUDE.md` rule 4), per leg

A leg counts as a completed primal only if: `rc = 0`; an `End` line; **last time == `endTime`**;
the primal fields present; `ExecutionTime` count == `endTime`; and **every field at `endTime` NEWER
than that leg's own `0/` fields** (the age guard — `0/` is touched last at launch). A leg that fails
any clause is **NOT A RESULT for that leg**, not a silent success and not counted as a converged
(non-banner) leg. **A DAFoam acceptance refusal AFTER `End` (the `N-D42` mode D6RF4 hit) is exactly
the `Primal solution failed!` banner outcome and IS the failure `r_sa` counts** — it is a completed
primal that the acceptance bar rejected, not an infrastructure fault.

### 3.3 Infrastructure vs physics (`bookkeeping never voids physics`)

A leg stopped by **OOM, a watchdog, a container kill or a cost stop** is recorded **stopped-by-that-
cause and NOT A RESULT about convergence** (`DAFOAM_CHARTER.md` §7). Such a leg is **NOT** counted as
a `Primal solution failed!` banner — the reader distinguishes the solver-emitted cutback banner from
an infra kill by requiring the banner's exact anchored form to be present in the leg's own log. A leg
lost to infrastructure is re-run once under a repair note; it never silently inflates or deflates
`r_sa`.

### 3.4 Decomposition disclosure

`np = 4`, the decomposition of the D6R multipoint and the D6RF4 measured basis (D6R: "np=4 in a 20g
cgroup", `../curriculum_D6R/d6r_grade.py:1064`). Method = the A2-wing case's own `decomposeParDict`
(to be confirmed at rig build; the D6R/D6RF4 A2 system is carried unchanged). All 36 legs run at the
identical `np` so per-leg cost is comparable to the D6RF4 measurement.

### 3.5 Memory prediction (`DAFOAM_CHARTER.md` §7)

**Stage-2 launches NO adjoint — primal only.** §7's incidents (A3/A6/NASA-hump) concern the
mesh-sized reverse-sweep matrix OpenMDAO builds for adjoint total derivatives; **that structure does
not arise here** (no `compute_totals`, no `run_driver`). The D6R multipoint — three geometries and
three scenarios — was shown memory-feasible at `np = 4` inside a **20 GiB cgroup**
(`d6r_grade.py:1064`). A single standalone `cl04` primal carries ~one-third of that state, so
**predicted peak is well under the 20 GiB cgroup (estimate ~5–8 GiB) against the box's headroom.**
A leg that nonetheless stops on memory is recorded **stopped-by-memory, NOT A RESULT about
convergence** (§3.3), never a banner.

---

## 4. FALSIFIERS — EACH NAMES ITS GATE WITH ARITHMETIC

- **F1 — a banner-blind reader miscounts and reports zero.** Guarded by **PLANT-SA-BANNER** (§3.1):
  plant exactly one banner into a clean leg copy; the reader must report the count moving by
  **exactly +1** (0 → 1). A reader that stays at 0 (wrong regex, wrong file, silent skip) **REFUSES
  (exit 2)** and `r_sa` is not emitted. Arithmetic: reported Δ ≠ +1 → REFUSE.
- **F2 — a reader over-counts `failed`.** A reader counting every line containing "failed" would
  inflate `r_sa`. Guarded by **PLANT-SA-DECOY** (§3.1) and by counting only the anchored banner
  (Stage-1's `RE_FAIL_BANNER`): a leg's banner count is **0 or 1**; a reader returning > 1 on a leg
  the log shows one banner **REFUSES**. Arithmetic: per-leg count ∉ {0,1} against the log's own
  anchored-banner count → REFUSE.
- **F3 — rig confound (fresh-start instability).** If the SUCCEEDED stratum fails standalone at a
  high rate, the standalone rig itself introduces failures the multipoint did not have, and a HIGH
  `r_sa` cannot be cleanly attributed to intrinsic design pathology. Arithmetic: if
  **`r_succ > 10 %` (≥ 2/12) AND `r_sa ≥ 50 %`**, the HIGH reading is **downgraded to NOT A RESULT
  (rig confound)**. (A LOW `r_sa` with high `r_succ` is contradictory and also → NOT A RESULT.)
- **F4 — wrong design injected.** A rig bug that injects the wrong shape/twist/patchV makes the leg a
  different design. Guarded by an **echo check**: the leg's own log must print
  `Setting UMag = 100 AoA = <aoa>` matching the registered `cl04 AoA` to `|Δ| ≤ 1e-6`, **and** the
  md5 of the injected shape[90]+twist[7] arrays must equal the md5 of the arrays parsed from the
  registered `dv_block_line`. Any mismatch **REFUSES that leg** (NOT A RESULT for the leg), never a
  silent count. Arithmetic: |AoA_log − AoA_registered| > 1e-6 OR shape/twist md5 mismatch → REFUSE.
- **F5 — indeterminate-band honesty.** A rate between the bands is not rounded into one.
  Arithmetic: r_sa ∈ (10 %, 50 %) ⇔ failures ∈ {4,…,17} → **NOT A RESULT**; only failures ≤ 3 → LOW,
  only failures ≥ 18 → HIGH.
- **F6 — sample tampering.** The reader recomputes the registered sample from the sha256-pinned D6R
  log and seed and requires it to equal the frozen `so3dr_stage2_registered_sample.json`
  (md5 `55bf8e2dcc07fbe3197f2c53421ad019`); any drift in the log sha256 or the sample **REFUSES**
  the whole run. Arithmetic: recomputed sample md5 ≠ frozen md5 → REFUSE.

---

## 5. COST (`CLAUDE.md` rule 12) — CORE-MINUTES, GROUNDED IN A MEASURED PER-PRIMAL BASIS

**Per-leg basis, MEASURED.** D6RF4 ran a single A2-wing primal to `endTime 1000` at `np = 4`:
**solve ≈ 3.83 core-min** (`ExecutionTime 57.43 s` × 4 ÷ 60) and **≈ 5.4 core-min gross** including
container spin-up and mesh setup (`../curriculum_D6RF4/RESULTS.md` §7, `ledger.txt`
`container_wall_s = 75`, `delivered_cores_mean 3.3475`). The gross figure is used per leg — it already
includes per-leg container + DVGeo warp overhead.

| field | value |
|---|---|
| unit | **core-minutes** = wall s × ranks ÷ 60 |
| ranks | **4** (per leg; same decomposition as the D6RF4 measured basis) |
| per-leg basis | **5.4 core-min gross** [MEASURED, D6RF4 §7] (solve component ≈ 3.83 core-min) |
| N legs | **36** (24 FAILED-stratum + 12 SUCCEEDED-stratum) |
| primal subtotal | 36 × 5.4 = **194.4 core-min** |
| host frame | sample rebuild + 36-log banner census + plant control at ranks 1 ≈ **0.6 core-min** |
| **point estimate** | **≈ 195 core-min** [PREDICTION, not measurement] |
| **cap (family MAX form)** | max(3.0 × 195, 1.25 × (4/3) × 195) = max(**585**, 325) = **585 core-min** |
| **stop rule** | at 585 core-min the campaign **stops**; an overrun gets no new budget. A leg whose wall exceeds ~3× the measured per-leg envelope (> ~16 core-min) or 3600 wall s (rule-12 stall) is stopped and recorded, not absorbed |
| solver core-min | the whole 195 IS solver time (36 real primals); this is not a host-only reader |
| dollars | **DERIVED, NOT MEASURED, REPORTED-BY-OWNER** at $0.0513/core-h (`COMPUTE_BUDGET_CHARTER.md` §5): estimate 195 core-min = 3.25 core-h → **$0.167**; cap 585 core-min = 9.75 core-h → **$0.500**. **Both well under $25.** |
| pre-authorisation | under $25, inside the standing pre-authorisation; **a blanket is not a per-item read** (rule 9) — costed here on its own terms |
| rule-12 calibration | on completion, predicted vs measured (ratio + attribution) as a row in `docs/COST_CALIBRATION.md`, naming D6RF4's measured per-primal row as the basis it continues. A completion report without it is incomplete |

---

## 6. WHAT STAGE-2 MAY NOT CONCLUDE

- **It fixes nothing.** No tolerance, solver, `max_iter`, mesh or accept-floor change is made or
  proposed. Stage-2 **discriminates**; it does not remedy. The accept floor stays `1e-05` (`N-D43`;
  the floor is never widened to fit).
- **A HIGH result does not establish the D6RF5 remedy.** It identifies cl04's own primal as the
  pathology and makes the D6RF5-class numerics/mesh fix the **candidate**; whether that fix brings the
  case under `1e-05` is **D6RF5's own gated test**, not this one.
- **A LOW result does not prove the `om.ExecComp` path.** "The assembly context" it indicts is
  broad — the aborted-trial `failFlag` coupling **and** the warm-start / field-reuse across IPOPT
  iterates. A LOW `r_sa` **routes** to the `om.ExecComp` propagation code-read (§3.3/§4 H5, still NOT
  DONE); it does not by itself isolate that path from warm-start effects. The code-read stays owed.
- **It establishes nothing about the shipped toolchain.** Every leg runs on the **PATCHED** row
  (`dafoam-idwarp-rot:v1`, digest `sha256:2927768a…`). This is a **one-row PATCHED** outcome, **not**
  a `DAFOAM_CHARTER.md` §6 two-row verdict about DAFoam.
- **The 39.7× stays a DATUM.** RULING 2's bar is preserved verbatim (front matter): it is not a
  verdict, is not scored, is not "confirmed" by any Stage-2 outcome, and may not be quoted as a
  verdict by anyone at any later date.
- **Stage-1 is not reopened.** SO-3D's `NOT A RESULT` stands; SO-3D-R's Stage-1 verdicts stand;
  §5's frozen contradiction stays disclosed-not-repaired. Stage-2 does not re-grade, convert or edit
  any of them.
- **Stage-3** (the incompressible transfer test) remains unfrozen.

---

## 7. GRADING PATH AND FROZEN ARTIFACT NAMES (to be fixed at the supervisor's freeze)

| file | role | status |
|---|---|---|
| `so3dr_stage2_standalone_runScript.py` | the standalone single-point rig | **TO BE BUILT**, pinned at freeze |
| `so3dr_stage2_grade.py` | the banner reader / `r_sa` grader + F1–F6 controls | **TO BE BUILT**, pinned at freeze |
| `so3dr_stage2_build_sample.py` | deterministic sample builder | present, md5 `89828c709c30b95205db0e37fd9dfc84` |
| `so3dr_stage2_registered_sample.json` | the frozen 36-leg sample | present, md5 `55bf8e2dcc07fbe3197f2c53421ad019` |
| `so3dr_stage2_replay.json`, `so3dr_stage2_plant_report.json`, `RESULTS.md` | outputs | produced at run |

All under this case directory. **No repository document produced by this item may cite a scratchpad
path** (`CLAUDE.md` rule 13). The launcher will hash the rig and grader against their committed blobs
before invoking, and verify the frozen files are the files that ran.

---

## 8. FREEZE STATEMENT — NOT YET TAKEN

This document is a **DRAFT**. Its gate (`G-SA-DISCRIM`), thresholds (HIGH ≥ 50 %, LOW ≤ 10 %),
prediction (leaning LOW, NOT HIGH), registered sample (36 legs, md5
`55bf8e2dcc07fbe3197f2c53421ad019`), cap (585 core-min) and labels are set out **before any Stage-2
compute** so the freeze can bind them. **The freeze itself, and the `SUPERVISION_CHARTER.md` §3
check-1 read of the rig/grader diff and check-4 committed-before-compute, are the `dafoam-supervisor`'s
and are NOT discharged here.**

**NOT FROZEN. NOT ENQUEUED. NO QUEUE ENTRY. NOT LAUNCHED. ZERO SOLVER CORE-MINUTES. SUBMISSIONS
PARKED.**
