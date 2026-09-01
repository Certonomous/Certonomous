# T23G — RESULTS. THE GRID TRIPLE AT (305 W, 20 m/s)

## RUNG VERDICT: **NOT A RESULT**

**All three graded quantities are `NOT A RESULT`.** Every level solved cleanly,
every level converged, every level plateaued, every reader was controlled, and
the ladder is exactly the ladder that was registered — **and the triple still
does not support a grid-convergence claim**, because the observed order of
convergence is **below 0.5 on all three quantities**, which
`scripts/roache_triple.py` classifies as `STAGNANT` and `CLAUDE.md` rule 5 makes
`NOT A RESULT` whatever the value says.

**This is a real graded outcome, not an instrument failure.** The comparator
exited 1, which is ambiguous by design, so the verdict was read from stdout: the
verdict block printed, and `grep -c Traceback` on the captured run returned **0**.

**Graded by `verification/runs/T-family/T23G_runs/analyse_t23g.py` and by nothing
else.** No value here was hand-read, no GCI was computed outside the comparator,
and the comparator was invoked with recognised flags only (`--json`).

| artifact | path |
|---|---|
| machine record | `verification/runs/T-family/T23G_runs/T23G_GRADED.json` |
| frozen registration | `docs/campaigns/T-family/T23G_PREREGISTRATION.md` |
| pre-flight referral | `docs/campaigns/T-family/T23G_PREFLIGHT_FINDINGS.md` |
| the §2d.1 ruling that unblocked grading | `DEAD_LEVER_AUDIT` §27, commit `af6af856` |

---

## 1. THE LADDER — AS REGISTERED, MEASURED FROM EACH LEVEL'S OWN `checkMesh` LOGS

| region | `T23G_C` | `T23G_M` | `T23G_F` | ratios |
|---|---|---|---|---|
| fluid | 8,800 | 35,200 | 140,800 | ×4, ×4 |
| housing | 280 | 1,120 | 4,480 | ×4, ×4 |
| core | 840 | 3,360 | 13,440 | ×4, ×4 |
| **total** | **9,920** | **39,680** | **158,720** | ×4, ×4 |

**Every region refines by exactly 4 at every step**, so `r21 = r32 = 2.000000` at
`dim = 2` — the case is a 5° wedge one cell thick circumferentially, so
refinement happens in two directions and a 4× cell count is r = 2, not r = 8.

**Level invariants byte-identical across all three levels:** `0.orig/` 12 files,
`constant/` 10 files, `system/` 8 files, and the `blockMeshDict` `vertices` block
— the geometry did not move. `cellToRegion` exempted by name (amendment A1).

---

## 2. RULE 5 STEP (1) — EVERY LEVEL CONVERGED AND PLATEAUED

| level | G-CONV | worst asserted residual | G-PLATEAU housing | G-PLATEAU core |
|---|---|---|---|---|
| `T23G_C` | **CONVERGED** | `p_rgh` 9.049e-09 | PLATEAUED, spread 0.000000 K | PLATEAUED, spread 0.000000 K |
| `T23G_M` | **CONVERGED** | `p_rgh` 9.923e-09 | PLATEAUED, spread 0.000000 K | PLATEAUED, spread 0.000000 K |
| `T23G_F` | **CONVERGED** | `p_rgh` 8.723e-09 | PLATEAUED, spread 0.000000 K | PLATEAUED, spread 0.000000 K |

All six asserted residuals (`Uy Uz h p_rgh k omega`) are ≤ 1e-8 against a 1e-6
tolerance on every level. `Ux` excluded by decision, justified by measurement
rather than asserted: max|Ux|/max|Uz| = 1.668e-17 (C), 1.832e-16 (M),
4.236e-16 (F).

**The plateau spreads are exact zeros, and this rung has independent evidence
that they are not blind zeros.** `plateau_state` carries no planted-zero control
of its own; one was supplied during the pre-flight, on a scratch copy: a +0.5 K
perturbation of the last `fieldMinMax` sample moved the reading to
`NOT PLATEAUED, spread 0.5`. The reader can see a non-zero, so the zeros mean
what they say (`T23G_PREFLIGHT_FINDINGS.md` §7).

**Rule 5 step (1) therefore did NOT fire.** The `NOT A RESULT` below comes from
step (2), and that distinction is the whole content of this rung.

---

## 3. THE NINE PLANTED-ZERO CONTROLS — ALL PASSED, ON REAL FIELDS

Nine controls (3 quantities × 3 levels), every one `PASSED`, floor 1e-06 K, read
at PLANT `1.234000e-03 K` against the relative predicate
`>= PLANT*(1-1e-9)`. Values planted: 1 for the two `max(T)` readers; **70 / 140 /
280 faces** for Q2, which plants into every face of the patch so the expected
shift is `mag` and not `mag/N`.

`PLANT` imported from `scripts/roache_triple.py`, never redefined.

---

## 4. THE THREE QUANTITIES — VALUES, TRIPLES AND ORDERS

Values in K (°C in parentheses); the triple is graded on ΔT = T − 288.0 K.

| | `T23G_C` | `T23G_M` | `T23G_F` |
|---|---|---|---|
| **Q1** max(T) housing | 343.910055617 (70.7601) | 342.159828932 (69.0098) | **340.814501134 (67.6645)** |
| **Q2** areaAvg(T) interface | 342.070481175 (68.9205) | 340.334602785 (67.1846) | **338.997500934 (65.8475)** |
| **Q3** max(T) core | 348.006105080 (74.8561) | 346.265640914 (73.1156) | **344.923014542 (71.7730)** |

| quantity | ΔT triple (C, M, F) | state | observed order p | band verdict | **VERDICT** |
|---|---|---|---|---|---|
| **Q1** | 55.91005562, 54.15982893, 52.81450113 | **STAGNANT** | **0.3796** | PASS | **NOT A RESULT** |
| **Q2** | 54.07048118, 52.33460278, 50.99750093 | **STAGNANT** | **0.3766** | PASS | **NOT A RESULT** |
| **Q3** | 60.00610508, 58.26564091, 56.92301454 | **STAGNANT** | **0.3744** | PASS | **NOT A RESULT** |

**NO GCI IS QUOTED FOR ANY QUANTITY, AND THAT IS NOT AN OMISSION.** Rule 5
forbids a GCI beside a non-`CONVERGING` triple, and `roache_triple._seal` enforces
it structurally rather than by convention.

**The band verdict was computed first and unconditionally, and it was `PASS` on
all three** — every value sits inside the registered band [−14.85, 185.15] K on
ΔT. The gate then turned `PASS` into `NOT A RESULT`, which is **the only
direction rule 5 permits**. Nothing here was turned the other way.

**`G-ORDER`, `G-GCI-DISPLAY` and `G-GCI-LEGACY` are `NOT EVALUATED`** on all
three quantities, because rule 5 step (2) fired first. They are recorded as not
reached rather than as passed, and never replaced by a nearer gate that was
(`VERIFICATION_CHARTER.md` §2, the M6 row).

> **The registered expectation that `G-GCI-DISPLAY` would `GATE FAIL` was never
> tested.** It was not reached. A gate that was not reached has not failed and
> has not passed, and this record does not convert one into the other.

### 4.1 THE REGISTERED PREDICTION ABOUT p IS FALSIFIED, IN THE UNEXPECTED DIRECTION

`T23G_PREREGISTRATION.md` §6.2 registered **p ≈ 1.0**, on the ground that
`div(phi,h) = bounded Gauss upwind` is first order and rate-limiting, and the
comparator prints that a measured p > 1.5 would falsify that reading.

**The measurement went the other way: p ≈ 0.375, less than half the registered
prediction**, and it is not scatter — the three quantities agree to within 0.005
(0.3744, 0.3766, 0.3796) across two different readers on two different regions
and one boundary patch. **That consistency is what makes it a finding about the
discretisation rather than noise in one column.**

**This record does not explain it, and will not guess.** §5 states the one
instrument that would have borne on it and was unavailable.

---

## 5. G-REPRO — PASS, AND EXACTLY ZERO

| gate | measured | threshold | outcome |
|---|---|---|---|
| **G-REPRO** | \|Q1(`T23G_M`) − 342.1598289320 K\| = **0.000e+00 K** | ≤ 1e-06 K | **PASS** |

`T23G_M` reproduces the already-solved `T23_P305_U20` **bit-identically**, not
merely inside tolerance. This is the determinism control, and it is a control
rather than an identity: a build differing in mesh, boundary condition or source
term would not reproduce it.

**The reference was corrected under a granted exception before this run**, and
its legality lives in its source: it was re-read from `T23_P305_U20`, an
independent prior case, **never from `T23G_M`, the case being graded** (§2d.1
grant, `DEAD_LEVER_AUDIT` §27.2; the struck constant and the whole argument are
carried in `analyse_t23g.py` at the `REPAIR R1` block). Had the pre-repair
constant stood, this gate would have read `GATE FAIL` at 1.514540e-02 K and
`min(verdicts)` would have propagated a bookkeeping artifact as a physics verdict.

---

## 6. ⚠ WHAT THIS RUNG COULD NOT MEASURE, AND WHY IT BEARS ON p

**y+ is `BLIND` on all three levels.** `log.yPlus.fluid` says on its own face
*"Unable to find turbulence model in the database: yPlus will not be
calculated"*, and then prints `min = 0, max = 0, average = 0` on all four
patches. The comparator **refuses those zeros rather than reading them**
(`CLAUDE.md` rule 3), which is the instrument working correctly.

**The consequence is specific and it is not cosmetic.** §7.4 exists to disclose
when y+ crosses 5, because that would mean the three levels **do not share one
wall treatment** and the measured order is **partly a wall-model artefact**. A
sub-first-order rate in a wall-bounded turbulent conjugate problem is exactly
the shape a changing wall treatment produces across a refining ladder.

> **So the single most likely instrumented explanation for p ≈ 0.375 is the one
> this rung has no instrument to test.** That is stated here as an unmeasured
> possibility and is NOT offered as the cause: no evidence in this rung
> distinguishes it from a genuine property of the discretisation. **What can be
> said is that the rung cannot tell, and that the gap is a build-side one — the
> `yPlus` function object ran without the turbulence model in the database.**

`Q2` has no `G-PLATEAU` at all: there is no `fieldMinMax` series for a patch
area-average. A **registered instrument gap** (§7.5), reported as absent, never
as a pass.

---

## 7. AN INSTRUMENT FINDING FROM THIS RUN — A JUSTIFICATION THAT CONTRADICTS ITS OWN RECORD

`roache_triple`'s `why` string, printed for all three quantities and stored in
the json, ends:

> *"…and NO GCI is quoted because the three values are not monotone"*

**The three values ARE monotone.** They descend cleanly on every quantity, and
**the same json record carries `monotone: true` for Q1, Q2 and Q3.** The printed
justification contradicts the computed field beside it.

**The ACTION is correct and is not in question** — no GCI may be quoted here,
because the state is not `CONVERGING`, which is the binding reason under rule 5.
**Only the stated reason is wrong.** It matters because this is the sentence a
reader will quote when asking why there is no GCI, and it would lead them to
believe the values oscillate when in fact they descend at a low order.

**NOT REPAIRED.** `scripts/roache_triple.py` is on the grading path of a rung
whose compute has run; no exception has been granted for it, and none is
requested by this record. **Referred, not fixed.**

---

## 8. COST CALIBRATION — RULE 12

Actuals are `core-min = wall_s × ranks / 60`, read from each level's own
`STATUS.<case>`; all three ran at `ranks = 1` with `capped = 0`.

| level | POINT (registered) | **actual** | ratio | cap | cap used |
|---|---|---|---|---|---|
| `T23G_C` | 7.56 | **6.0667** | **0.803** | 25.0 | 24.3 % |
| `T23G_M` | 30.22 | **27.8167** | **0.921** | 100.0 | 27.8 % |
| `T23G_F` | 120.88 | **145.7500** | **1.206** | 400.0 | 36.4 % |
| **CAMPAIGN** | **158.65** | **179.6334** | **1.132** | **525.0** | **34.2 %** |

**No level was capped and no level overran.** `T23G_F` ran 8,745 wall s against
a 24,000 s timeout.

**ATTRIBUTION: MISPREDICTION — SPECIFICALLY, A LINEAR COST MODEL ANCHORED
MID-LADDER AGAINST A SUPERLINEAR REALITY. NOT CONTENTION, AND NOT WASTE.**

The evidence is in the *shape* of the error, not its size. The registered points
scale by exactly the cell ratio — predicted M/C = 3.997, predicted F/M = 4.000 —
because §8.2 derived wall time from cell-iterations. **The measured scalings are
both larger and they grow: actual M/C = 4.585, actual F/M = 5.240.** Cost per
cell rises with mesh size, as linear-solver iteration counts and cache behaviour
degrade. The per-level ratio therefore drifts monotonically upward — 0.803,
0.921, 1.206 — and passes through ≈1 at the **medium** level, which is precisely
where §8.3 anchored the model on a measured 1,813 s prior run.

**That is the signature of an anchored linear model, not of machine contention**:
contention inflates every level, and here the two smaller levels came in *under*
their points. **The campaign ratio of 1.132 understates the modelling error and
is not the honest headline; the per-level drift from 0.803 to 1.206 is.**

**WASTE, NAMED SEPARATELY AND NOT ABSORBED INTO THE RATIO ABOVE:** one comparator
run was wasted earlier tonight, when `analyse_t23g.py` was invoked with a
`--selftest` flag it does not implement and `main()` silently fell through to a
full `grade()` against the live tree. **It consumed no solver compute** — it
refused at `require_done` — but it wrote `DONE.T23G_C` and `DONE.T23G_M` early,
at 06:01:19.98Z and 06:01:20.12Z. The markers' content is not false: rule 4's six
clauses were genuinely evaluated. **The flag-handling defect is a real finding and
is recorded, not hidden.**

**Comparator cost:** under one minute, single-rank Python, bounded from the
artifact timestamps (`DONE.T23G_F` 06:27:34.16Z → `T23G_GRADED.json`
06:27:35.89Z). It is **not** solver compute and does not enter the ratios above.

**USD, DERIVED AND NEVER MEASURED** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5) — at the owner-stated c7a.4xlarge rate of
$0.0513/core-h: campaign actual **$0.1536** against a registered point of
$0.1357.

---

## 9. WHAT THIS RUNG DOES NOT LICENSE

- **It does not move the G column.** The tiering directive requires a
  `CONVERGING` triple with every level plateaued. Every level plateaued; the
  triple is `STAGNANT`. **The G column does not move for (305 W, 20 m/s).**
- **It never could have moved the P column.** A grid triple is code-and-grid
  convergence evidence, not validation against a physical experiment, and there
  is no primary experimental source for this geometry.
- **It licenses no display precision.** `G-GCI-DISPLAY` was not reached, so
  **nothing here authorises Act A to print 0.1 °C significant figures for any of
  these quantities**, and nothing here forbids it either — the gate that decides
  it was not evaluated.
- **No value in §4 may be quoted as a converged answer.** Rule 5 makes a
  non-`CONVERGING` triple `NOT A RESULT` whatever the number, and the fine-level
  values are printed here as the graded inputs to that verdict, not as results.
- **Nothing transfers to any other point of the T23 map.**

---

## 10. WHAT WOULD BE NEEDED TO TURN THIS INTO A RESULT

Recorded as an open question for the campaign, **not** as a proposal, a plan or a
compute request — no compute is requested by this record and none is authorised
by it.

The triple is clean in every respect except the rate. Any future rung would have
to establish **why p ≈ 0.375**, and the first instrument to restore is the one
§6 names as missing: **a working y+ measurement**, so the ladder can be shown to
share one wall treatment or shown not to. Until that is measured, the
distinction between a wall-model artefact and a genuine sub-first-order
discretisation rate is **not decidable from this rung's artifacts.**

---

*Graded 2026-09-01T06:27Z. Verdict read from stdout, not from the exit code
(exit 1 is ambiguous by design; zero tracebacks in the captured run). Grading
path shas as recorded on the artifact's own face: `analyse_t23g.py`
`9e4a5f2eb5cc1290da231bb8245d35101f0bfb31`, `scripts/roache_triple.py`
`78e56a3bc2c2a07571db1cf3c91f4c2c31f246b8`, `analyse_t23.py`
`314a2b82b85cd1c620f26d37c1a2613cf76838d6`, `mark_done_t23.py`
`ecd457ac87dbdab83498c6a9c0334226c3e66863` — the fourth entry recorded for the
first time by REPAIR R2 under the §2d.1 grant.*
