# DRIVAER — GRADES FOR THE THREE COMPLETED RERUNS (`_R2` arms), 2026-09-12

**Filed by a cfd `lab-lane`. No solver was launched by this lane. No gate, threshold,
cap or label is altered by this file. Submissions parked.**

Graded against the **frozen** registrations, not against gates composed now:

| run | registration | freeze |
|---|---|---|
| `r2_coarse_R2` | `DRIVAER_R2_LAYERED_PREREGISTRATION.md` (+ Addendum 1) | gates M1/M2/M2c/M3/Y1/Y2/S1/S2/S3, Gate G registered ABSENT |
| `r2c_coarse_blended_R2` | `DRIVAER_R2C_BLENDED_WALL_TREATMENT_PREREGISTRATION.md` | gates B1/B2/B3 on top of the R2 gates |
| `r2c_medium_blended_R2` | `DRIVAER_R2C_BLENDED_WALL_TREATMENT_PREREGISTRATION.md` | same |

## 0. INSTRUMENT HASHES — VERIFIED BEFORE ANY VERDICT WAS BELIEVED (rule 2)

Every instrument re-hashed and compared against **its committed blob at HEAD
`381228464`**, and against the literal sha256 table in the R2c registration §8.
**All four match exactly; no mismatch, no refusal.**

| instrument | sha256 | vs committed blob | vs prereg §8 table |
|---|---|---|---|
| `cases/navier_class/DRIVAER/grade_drivaer.py` | `6106cf6d…83c26d7` | MATCH | MATCH |
| `cases/navier_class/DRIVAER/mesh/stage_r2_measure.py` | `c86a8ea4…40bb0e` | MATCH | (not in §8; R2 §6 names it as THE R2 instrument) |
| `cases/navier_class/DRIVAER/mesh/launch_r2_solve.sh` | `60074739…2bfb668d` | MATCH | MATCH |
| `cases/navier_class/DRIVAER/mesh/watch_grade_r2.sh` | `aaa727ab…8460156d` | MATCH | MATCH |
| `verification/runs/.../drivaer_reference_notchback.json` | `bb504af3…cfa72238c72` | MATCH | MATCH |

## 1. PLANTED-ZERO CONTROLS (rule 3) — ALL FIRED, NONE SKIPPED

* `grade_drivaer.py --selftest` → **SELFTEST OK**, rc 0. Includes ARMING PROOFS 1–5:
  a null reference REFUSES rather than disarming a gate; the Cl gate FIRES on a planted
  wrong value; the claim cap cannot be emitted unmeasured; the windowed-plateau limb is
  driven in BOTH directions; and the p-field control is driven on meshes of known
  multiplicity with the superseded formula's false-refusal DEMONSTRATED, not described.
* Per run, `grade_drivaer.py` drove three unconditional controls: **p-field plant
  PASSED, `coefficient.dat` Cd gate-reader plant PASSED, Cl gate-reader plant PASSED**
  on all three runs.
* Per run, `stage_r2_measure.py` drove **four plants (P1 checkMesh, P2 layer-table
  scope, P3 mesh index, P5 Cd window) — `all_plants_passed: true` on all three.**
* The solved-y⁺ probe on the medium arm returned **non-zero on 52 of 52 patches**
  (`YPLUS_PROBE/r2c_medium_blended_R2/log.yPlus`). The method's own positive control —
  that generic `postProcess -func yPlus` returns an identically-zero false reading and
  only `simpleFoam -postProcess -func yPlus` is live — was established at
  `DRIVAER_SOLVED_YPLUS_2026-09-12.md` §0 and is honoured here: the solver-mode form
  was used, and the reading is non-zero everywhere.

**ONE ARTIFACT WAS SUPPLIED, AND IT IS DISCLOSED RATHER THAN LEFT TO BE INFERRED.**
`grade_drivaer.py` REFUSED (exit 2) on all three runs for an absent `log.checkMeshFull`:
the rerun roots carry `constant/polyMesh` as a **symlink** to the mesh owner
(`r2_coarse` / `r2_medium`) and no checkMesh log of their own. The mesh owner's
`log.checkMeshFull` was symlinked into each rerun root **after proving it is the log of
that mesh**: all four header counts match the `polyMesh/owner` note exactly —
coarse `nPoints 221464 / nCells 186709 / nFaces 592877 / nInternalFaces 564186`,
medium `1100653 / 983106 / 3060269 / 2959169`. No script was edited; no gate moved.

## 2. THE FAMILY IS **TWO LEVELS**, AND NO ROACHE TRIPLE IS CLAIMED

Sanaa, ~21:00Z 2026-09-12, byte-exact: *"for Drivaer, we can keep the level up to
medium (no fine mesh), if the results are good."*

**DrivAer is a TWO-LEVEL family: coarse + medium. There is no third level and none is
owed, costed or queued.** A Roache triple needs three levels, so:

* **NO observed order of accuracy exists for this family.**
* **NO GCI is computed and none may be quoted** — CLAUDE.md rule 5 forbids quoting a
  GCI where the three values are not monotone, and here there are not three values at all.
* This is **also** independently forbidden by **Gate G of the R2 registration**, which
  was registered **ABSENT AND FORBIDDEN before any compute**, with the reason given in
  advance: under `relativeSizes true` the first-layer thickness scales with `h`, so the
  wall model is a different model on each level and a Roache order from it measures the
  closure changing, not the grid.
* **Disclosed here on the record rather than papered over by an absent row.**

Delivered refinement ratio, measured from BUILT cell counts, reported not gated:
186,709 → 983,106 cells, linear r = **1.7397**.

## 3. COMPLETION — GATE S1, RULE 4, ALL-OR-NOTHING

| clause | `r2_coarse_R2` | `r2c_coarse_blended_R2` | `r2c_medium_blended_R2` |
|---|---|---|---|
| rc = 0 from the sidecar written INSIDE the wrapper | PASS | PASS | PASS |
| `End` line in `log.simpleFoam` | PASS | PASS | PASS |
| last time == `endTime` 2000 | PASS | PASS | PASS |
| fields `p U k omega nut phi` at `endTime` | PASS | PASS | PASS |
| `ExecutionTime` count == round(endTime/deltaT) = 2000 | PASS | PASS | PASS |
| age guard — every field at 2000 NEWER than `0/` | PASS | PASS | PASS |

**GATE S1: PASS on all three runs, 6/6 clauses each.** `grade_drivaer.py`'s
`check_completion` did not refuse on any clause on any run.

## 4. FORCES — MEASURED, WITH THE CAP STATED BEFORE THE NUMBER

🔴 **EVERY `Cd` BELOW IS A MIXED-WALL-TREATMENT `Cd` (Gate Y2 claim cap) AND MUST NOT BE
CITED AS A `Cd` ON A FULLY LAYERED DRIVAER BODY.** On the medium level 16 patches
carry fewer than one prismatic layer — 12,106 faces, **6.518 m² = 19.65 % of the
wetted area** — and are resolved by the bare snapped cell. Y1 passing on the medium
level speaks for the **LAYERED PATCH GROUP ONLY** and **does not lift the Y2 cap.**

| arm | mesh | wall function | `Cd` window mean (1000,2000] | `Cd` last | `Cl` window mean | `Cl` last |
|---|---|---|---:|---:|---:|---:|
| `r2_coarse_R2` (control) | coarse 186,709 | `nutkWallFunction` | **0.357938** | 0.35525032 | 0.009618 | 0.00507984 |
| `r2c_coarse_blended_R2` | coarse 186,709 | `nutUSpaldingWallFunction` | **0.352801** | 0.35516290 | 0.013309 | 0.01397983 |
| `r2c_medium_blended_R2` | medium 983,106 | `nutUSpaldingWallFunction` | **0.315107** | 0.31507318 | 0.019961 | 0.02152462 |

`Cm` is **not registered** in this family and is therefore neither read nor graded.

## 5. GATE-BY-GATE

### Gate S2 — ITERATIVE STATIONARITY (the R2 family's OWN frozen gate)
Window (1000,2000], four blocks of 250. STATIONARY iff block-mean span < 3.0 % **and**
|half-to-half drift| < 2.0 %. Read by `stage_r2_measure.py`, the instrument R2 §6 names.

| arm | block span % | limit | half drift % | limit | verdict |
|---|---:|---:|---:|---:|---|
| `r2_coarse_R2` | 0.0320 | 3.0 | −0.0196 | 2.0 | **STATIONARY** |
| `r2c_coarse_blended_R2` | 0.0745 | 3.0 | −0.0297 | 2.0 | **STATIONARY** |
| `r2c_medium_blended_R2` | 0.7718 | 3.0 | −0.3216 | 2.0 | **STATIONARY** |

### 🔴 AN INSTRUMENT CONFLICT, DISCLOSED AND NOT RESOLVED BY THIS LANE
`grade_drivaer.py`'s **windowed plateau limb** (trailing 200 samples, tolerance 0.5 %
excursion — the **R1 Stage-A** instrument, named in the R2c §8 hash table) reads
**`NOT_PLATEAUED` on all three arms**: Cd excursion **1.648 % / 2.029 % / 0.958 %**
against a 0.5 % tolerance. The R2 registration created Gate S2 **specifically** to
supersede that test, and said so in advance: *"a pointwise plateau test applied to a
quantity that is physically an oscillation, not a fixed point."*

**Two registered instruments give opposite readings of the same trace.** This lane is
not entitled to rule between them. **The conservative direction governs until
verification rules**: the one that yields `NOT A RESULT` is taken, per rule 5's
one-way direction (a gate may turn a result INTO `NOT A RESULT`, never the reverse).
Both readings are printed above so the ruling can be made on the numbers.

### Gate S3 — Cd DIAGNOSTIC BAND (explicitly NOT a validation gate)
0.20 ≤ Cd ≤ 0.40: **IN BAND** on all three (0.357938 / 0.352801 / 0.315107).
Gross-error bands A2 (0.15–0.60) and A3: **PASS** on all three.
**An in-band value is NOT agreement with any reference and is not cited as one.**

### Gate Y1 — y⁺ ADMISSIBILITY, area-weighted median over LAYERED vehicle wall faces, band [30, 300]

| level | layered patches | layered faces | layered area | **layered median y⁺** | verdict |
|---|---:|---:|---:|---:|---|
| coarse (both arms) | 27 | 14,057 | 24.959 m² | **481.565** | **GATE FAIL — NOT WALL-FUNCTION ADMISSIBLE** |
| medium | 31 | 52,489 | 26.647 m² | **232.027** | **PASS — WALL-FUNCTION ADMISSIBLE (layered group only)** |

The coarse failure was **predicted in the frozen registration before a core-minute was
spent** ("median layered y⁺ coarse 400–800, PREDICTED NOT ADMISSIBLE"). The gate has a
failing branch and it fired where it was said it would.

### Gate Y2 — MIXED-WALL-TREATMENT DISCLOSURE (claim cap, not pass/fail)

| level | unlayered patches | unlayered faces | unlayered area | share of wetted area | **unlayered median y⁺** | ratio to layered |
|---|---:|---:|---:|---:|---:|---:|
| coarse | 20 | 3,803 | 5.931 m² | 19.19 % | **1940.998** | 4.03× |
| medium | 16 | 12,106 | 6.518 m² | **19.65 %** | **556.556** | **2.40×** |

**The y⁺ per patch, for every patch of every run, is in the artifacts named in §8** —
47 vehicle patches per level, layered and unlayered groups separated with face count,
area and median y⁺ stated for each, exactly as Y2 requires.

**A SECOND, MORE PHYSICAL READING OF THE MEDIUM ARM, AND IT MOVES ONE NUMBER — SAID
PLAINLY RATHER THAN BURIED.** Gate Y1's registered basis is **mesh-derived**: a flat-plate
`u_tau` (y⁺ = 90,623 per metre of wall distance) applied uniformly, so the estimate
scales purely with first-cell distance. The **SOLVED** field from the converged medium
blended run reads, area-weighted over the same groups:

| medium blended, solved y⁺ | layered | unlayered | ratio |
|---|---:|---:|---:|
| area-weighted average | **203.94** | **261.74** | **1.28×** |
| mesh-derived estimate (the gate's basis) | 232.027 | 556.556 | 2.40× |

**The gate verdict stands on 232.027 — the registered basis is the registered basis.**
But the honest reading is that the unlayered group's *actual* y⁺ on the medium blended
arm is **261.74, not 556.6**, because the local wall shear on wheels, rims, brake discs
and wheel supports is far below flat-plate. **THIS DOES NOT SHRINK THE Y2 CAP.** The cap
is about **layers**, not about a ratio: 16 patches at under one prismatic layer over
19.65 % of the wetted area are still resolved by a bare snapped cell, and a `Cd` from
this family is still a **MIXED-WALL-TREATMENT `Cd`**. Also measured and reported against
us: the solved layered minimum is **1.92**, i.e. part of the layered group sits in the
viscous sublayer — admissible under Spalding blending, and **not** admissible under the
`nutkWallFunction` the control arm uses.

### Gate M-series — MESH (per level, from `stage_r2_measure.py`, all plants passed)

| gate | coarse | medium |
|---|---|---|
| M1 index integrity | **PASS** | **PASS** |
| M2 solvability (0 negative-volume cells) | **PASS** | **PASS** |
| M2c MESH_STANDARD conformance | **NON-CONFORMING** — max skewness **4.782** vs 4.0, 1 face | **NON-CONFORMING** — max skewness **5.450** vs 4.0, 2 faces |
| M3 layer coverage | **GATE FAIL (MIDDLE band)** | **GATE FAIL (MIDDLE band)** |

**M2c ⇒ `credential_eligible: false` on all three runs.** Every result here is a
**STATED LIMITATION** row — not `HOLDS`, not `GATE REACHED`, not a credential.

### Gate B2 — IS BLENDING ACTIVE? (the clean discriminator: same mesh, one line apart)
Threshold: 2 × the control's own trailing-200 excursion at `endTime` 2000 =
2 × 1.6476 % = **3.2952 %**.

| reading | |ΔCd|/Cd_control | verdict |
|---|---:|---|
| window means (1000,2000] | **1.4351 %** | **INACTIVE** (2.30× below threshold) |
| last values at 2000 | **0.0246 %** | **INACTIVE** (134× below threshold) |

**INACTIVE on both readings — the verdict is robust to the choice.** Mechanism,
measured independently: layered-group y⁺ minimum **34.235** and unlayered minimum
**56.062** on the coarse mesh — the whole body sits above the y⁺ ≈ 30 crossover where
the two wall functions coincide, so **there was no buffer-layer region for blending to
act on.** A registered null with its cause measured.

### Gate B1 — y⁺ INSENSITIVITY (R2c PRIMARY)
`|Cd_coarse − Cd_medium| / mean(Cd) ≤ 0.10`.
Measured: |0.352801 − 0.315107| / 0.333954 = **0.112872 = 11.287 %**, against ≤ 10.0 %.

**VERDICT: `NOT A RESULT`.** The threshold is exceeded, but B1's **coarse input is
itself `NOT A RESULT`** (Gate Y1 GATE FAIL on the coarse mesh; the R2c registration §0
states in its own words that *"`r2_coarse`'s Cd stays `NOT A RESULT`"*). Rule 5 runs one
way: a gate may turn a result INTO `NOT A RESULT` and never the reverse, so B1 cannot be
reported as a `GATE FAIL`. **The measured 11.287 % is printed beside it, not suppressed.**

The registration's **outcome 3**, written before either number existed, reads: *"B1
disagrees → blending does not rescue this geometry at these y⁺. The 19.65 % of wetted
area on 16 unlayered patches at y⁺ 556.6 is then the binding problem and the mesh route
is the only route."* **That is the direction the measurement points**, and it is
consistent with B2's INACTIVE. It is a **supported reading, not a gate-certified one.**
The registration also fixed in advance that a B1 failure cannot separate y⁺ sensitivity
from grid error on two levels — and with no third level, it never will here.

### Gate B3 — REFERENCE AGREEMENT (REPORTED, NEVER PRIMARY)
Band `|Cd − 0.2758368| ≤ 0.10 × 0.2758368` = **[0.2482531, 0.3034205]**. DrivAerML is a
**CODE reference (rank 2), NOT experiment**; the disavowal applies to every row.

| arm | Cd | deviation | drag counts vs 2758.4 | band |
|---|---:|---:|---:|---|
| `r2_coarse_R2` | 0.357938 | **+29.76 %** | **+821.0** | **OUTSIDE** |
| `r2c_coarse_blended_R2` | 0.352801 | **+27.90 %** | **+769.6** | **OUTSIDE** |
| `r2c_medium_blended_R2` | 0.315107 | **+14.24 %** | **+392.7** | **OUTSIDE** |

**REPORTED, not a verdict** — a `NOT A RESULT` cannot also be a `GATE FAIL` against a
reference (rule 5). The medium level **halves the gap** (from +794 to +393 drag counts),
which is the one genuinely encouraging number in this record, and it is **still 1.42×
outside the band** on a body with a fifth of its wetted area unlayered — exactly what
the Y1/Y2 caps predict.

## 6. VERDICTS — FIXED VOCABULARY ONLY

| run | verdict on `Cd` | basis |
|---|---|---|
| `r2_coarse_R2` | **NOT A RESULT** | Gate Y1 **GATE FAIL** (layered median y⁺ 481.565, outside [30,300]) — the coarse mesh is not wall-function admissible and the R2c registration already fixed this verdict. Stage-A plateau limb `NOT_PLATEAUED` independently. S1 PASS, S2 STATIONARY, S3 IN BAND. |
| `r2c_coarse_blended_R2` | **NOT A RESULT** | Same Y1 GATE FAIL on the same mesh; blending measured **INACTIVE** (B2) so it does not relieve the cap. S1 PASS, S2 STATIONARY, S3 IN BAND. |
| `r2c_medium_blended_R2` | **NOT A RESULT** | S1 **PASS**, S2 **STATIONARY**, S3 **IN BAND**, Y1 **PASS (layered group only)** — this level clears every gate the registration puts on a single level. It is `NOT A RESULT` on the **conservative side of the §5 instrument conflict alone** (Stage-A plateau limb `NOT_PLATEAUED` 0.958 % vs 0.5 %). **Were S2 ruled to govern — as the R2 registration's own text argues — this level's `Cd` would stand as a MIXED-WALL-TREATMENT diagnostic `Cd` of 0.315107, still not validated, still not a credential.** A verification ruling on the two instruments is what decides it, and this lane does not make it. |
| family gate **B1** | **NOT A RESULT** | 11.287 % measured against ≤ 10 %; the coarse input is `NOT A RESULT` and rule 5 runs one way. |
| family gate **B2** | **INACTIVE** (registered null, mechanism measured) | 1.4351 % / 0.0246 % against a 3.2952 % threshold. |
| family **Roache triple / GCI / observed order** | **none exists** | Two-level family per Sanaa ~21:00Z; Gate G registered ABSENT AND FORBIDDEN before compute. |
| **credential eligibility, all three** | **NOT ELIGIBLE** | M2c non-conformance (max skewness 4.782 / 5.450 vs 4.0). STATED LIMITATION rows. |

## 7. COST — core-minutes measured from each run's own `RUN_META.txt`

Rate **$0.0513/core-h, c7a.4xlarge, owner-stated 2026-08-21/22**.
`cost_basis` = **reported-by-owner, NOT measured** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). Every dollar figure below is **DERIVED**.

| run | wall s | ranks | **core-min** | **$ derived** | pre-registered estimate | ratio actual/predicted |
|---|---:|---:|---:|---:|---:|---:|
| `r2_coarse_R2` | 881 | 4 | **58.73** | **$0.0502** | 121 core-min (R2 §4) | **0.485** |
| `r2c_coarse_blended_R2` | 950 | 4 | **63.33** | **$0.0541** | 254 core-min CPU-held (R2c §6) | **0.249** |
| `r2c_medium_blended_R2` | 5,625 | 4 | **375.00** | **$0.3206** | 810 core-min CPU-held (R2c §6) | **0.463** |
| **total** | | | **497.06 core-min = 8.28 core-h** | **$0.425 DERIVED** | | |

**Gap attribution — misprediction, and the gap is named, not absorbed.** The R2c §6
basis (1.904 and 6.073 CPU s/iter/rank) was measured from logs taken **under heavy fleet
contention on the 16-core box**, so it is a contention-inflated basis used as a clean
one. Achieved after the 17:36Z resize and reboot, on a quiet box: **0.4405 / 0.4750 /
2.8125 wall s/iter**, i.e. **4.0×–4.3× faster** than the registered basis on the coarse
level. **No waste to name on any of the three runs** — no stall row (every run under
3,600 s except the medium, which ran 5,625 s continuously and is not a stall), no
restart, no re-mesh, no discarded compute.

**Measured, and §6 said it would be reported as measured rather than assumed away:**
`nutUSpaldingWallFunction` costs **+7.83 %** over `nutkWallFunction` on the identical
coarse mesh (950 s vs 881 s wall, 2000 iterations each) — the Newton iteration on
Spalding's law per wall face, now a measured figure instead of an expectation.

Calibration rows: `r2_coarse_R2` and `r2c_coarse_blended_R2` were already landed at
20:29Z (`C-20260912T202941.451290Z-e54fb046`, `C-20260912T202941.451381Z-c98fdfee`).
**This lane appends the one row that was still owed: `r2c_medium_blended_R2`.**

## 8. ARTIFACTS EVERY NUMBER ABOVE CITES

| number | artifact |
|---|---|
| completion, Cd/Cl last values, Stage-A plateau limb, planted controls, M2c conformance | `verification/runs/navier_class/DRIVAER/<run>/GRADE_STAGE_A_<level>.json` |
| S2 / S3, window means, block means, M1/M2/M3, P1/P2/P3/P5 plants | `verification/runs/navier_class/DRIVAER/<run>/S2_S3_R2_INSTRUMENT.json` |
| y⁺ per patch, mesh-derived, 47 patches per level, layered/unlayered groups, P4 plant | `verification/runs/navier_class/DRIVAER/r2_coarse/R2_MEASURED.json`, `.../r2_medium/R2_MEASURED.json` |
| y⁺ per patch, SOLVED, medium blended arm, 52/52 patches non-zero | `verification/runs/navier_class/DRIVAER/YPLUS_PROBE/r2c_medium_blended_R2/postProcessing/yPlus/0/yPlus.dat` and `log.yPlus` |
| y⁺ per patch, SOLVED, both coarse arms | `verification/runs/navier_class/DRIVAER/YPLUS_PROBE/r2_coarse_R2/`, `.../r2c_coarse_blended_R2/` |
| cost | `verification/runs/navier_class/DRIVAER/<run>/RUN_META.txt` |
| earlier coarse-arm record, not superseded by this file | `verification/campaign/DRIVAER_COARSE_YPLUS_PER_PATCH_2026-09-12.md`, `DRIVAER_R2C_B2_RESULTS_2026-09-12.md` |

*Filed by a cfd `lab-lane`, 2026-09-12. Alters no gate, threshold, cap or label.
No agent's message is Sanaa's consent. Submissions parked.*
