# T23G2R — PRE-REGISTRATION (DRAFT). NEAR-WALL FIX-SUCCESSOR TO T23G2's G-YPLUS GATE FAIL

> ## ⚠ DRAFT — NOT FROZEN, NOT COMMITTED, NOTHING RUN
> This file is a **design draft** produced by a heat-transfer `lab-lane`. **No gate,
> threshold, band, cap or label in it is frozen.** No sha is claimed; no comparator
> or build script is written; **no solver has been launched.** The §3
> measurement-script diff-read and the sha-freeze are the **supervisor's** and are
> **non-delegable** — this lane stops before both. Every number below the "reused
> gates" line is a **DESIGN ESTIMATE**, not a measurement, and is labelled as such.

> ## ✅ FREEZE ADDENDUM — 2026-09-08 (SUPERSEDES THE ⚠ DRAFT STATUS ABOVE)
> **FROZEN by the commit that carries this amendment.** The build and comparator
> scripts are written and their bytes are final (§10 table); the supervisor's §3
> code diff-read of both — read as a diff against frozen `build_t23g2.py` /
> `analyse_t23g2.py` — is complete. **This freeze is BEFORE ANY SOLVER HAS
> ITERATED on any T23G2R case:** the run directory
> `verification/runs/T-family/T23G2R_runs` **does not exist** (checked on disk at
> freeze, 2026-09-08 — absent), so this is a legal pre-first-compute amendment
> (CLAUDE.md rule 2). **No gate, threshold, band, cap, label or prediction is
> altered by this amendment** — it pins grading-path blobs and records the freeze
> mechanism only. The §9 design-check sign-off below remains the accurate dated
> record of the 2026-09-07 design read (not frozen as of that date); §10 records
> the 2026-09-08 freeze that follows it. The §5.1 pre-flight and the graded launch
> remain OWED after this commit — see §10.

---

## 0. §2ay LINEAGE LINKAGE — the line the enforcement instrument reads

**Predecessor: `T23G2` (explicit, for §2ay linkage).** This registration is the
active, dated fix-successor to **T23G2**'s **`G-YPLUS` `GATE FAIL`** — max y+ on
`centrebody_up` reaches **1.8245 / 1.3539 / 1.0047** at L1 / L2 / L3, above the
registered ≤ 1.0 gate on the finest level included
(`docs/campaigns/T-family/T23G2_RESULTS.md:146-148`, independent field reader;
primary log instrument `1.8245835202 / 1.3540190129 / 1.0047773564`). T23G2R
**changes what failed — the near-wall first-cell spacing of the inner boundary-layer
band, which `centrebody_up` shares — and re-runs the full three-level ladder**,
re-grading against **every T23G2 gate, threshold and band UNCHANGED**. Under
`VERIFICATION_CHARTER.md` §2ay.2(b) this makes T23G2 a fail **carrying an active
fix-successor**; **T23G2 keeps its `NOT A RESULT` verdict** (`§2an.2`) — this linkage
**moves no verdict**, and this successor **creates no gate, threshold, band, cap or
label of its own; it reuses T23G2's**. The one net-new registration is a strictly
*stricter* prospective closure of an OWED item (`R6`, §5.2 below), which can only
add a refusal.

**Scope boundary, stated plainly (the §2ay.3 discipline).** The T23G2 rung was
`NOT A RESULT` on **three** independent grounds — `G-CONV` (T23G2_L2 not iteratively
converged, `T23G2_RESULTS.md:126`), `G-YPLUS` (this file's primary target), and
`Q3`'s band (`Q3` fine value 56.708 K vs [46.0, 56.0] K, `:178`). The §2ay flag this
file discharges is the **`G-YPLUS`** rows (`:146-148`). Because a fix-successor that
reuses **every** gate unchanged must clear **all** of them to become a RESULT rather
than repeat `NOT A RESULT`, §2.3 and §4 below also carry the convergence margin for
T23G2_L2 and re-register `Q3`'s band unchanged. **These are bundled for honesty;**
the supervisor may split them into a separate successor. Nothing here relaxes any
gate.

---

## 1. THE DIAGNOSIS THIS FIX RESTS ON — near-wall resolution, confirmed from the frozen record

**The failure is genuinely first-cell wall spacing too large on `centrebody_up`,
not a gate defect, not a wall-function model choice, and not an unrefinable
geometry.** Confirmed from the frozen T23G2 record without re-running anything:

1. **`centrebody_up` shares its first-cell height with a patch that PASSES.**
   `T23G2_PREREGISTRATION.md:368` registers ONE inner-BL first-cell height —
   **2.306800e-05 / 1.537867e-05 / 1.025245e-05 m** (ratio 1.5) — for the band
   containing `fluid_to_housing`, `centrebody_up` and `centrebody_down`. At that
   identical height, `fluid_to_housing` reads y+ **0.751 / 0.505 / 0.339** (PASS)
   while `centrebody_up` reads **1.8245 / 1.3539 / 1.0047** (FAIL)
   (`T23G2_RESULTS.md:146-152`). The ~2.4× ratio is a property of the **local
   friction velocity** on `centrebody_up` (a higher-shear wall), not of any cell
   count or gate — the near-wall cell is simply too tall **there**.

2. **y+ resolves DOWN with refinement — it is not a singularity.** As the inner-BL
   first cell shrinks ×(1/1.5) per level, `centrebody_up` max y+ falls
   1.8245 → 1.3539 → 1.0047, a ratio of ~1.348 per step. The peak is being
   **resolved**, not blown up; there is no evidence of a corner singularity that
   refinement cannot lift. Reducing the first-cell height lowers the max.

3. **The gate is correct for the model and cannot be the fix.** The wall treatment
   is `nutLowReWallFunction` on all four patches (`T23G2_PREREGISTRATION.md:415-416`)
   — a low-Re treatment that **requires** y+ ≲ 1. The gate max y+ ≤ 1.0 is Sanaa's
   §0 point 1 for a wall-resolved case (`:1120-1126`), frozen under rule 2 and not
   this lane's to move.

4. **It IS refinable within the growth cap.** A uniform inner-BL first-cell
   reduction of ×0.4682 (§2.2) brings the estimated worst-case (coarsest-level)
   `centrebody_up` y+ to ~0.85 and keeps the per-cell growth ratio ≈ 1.13 / 1.08 /
   1.05 — under the `G-MESHSIM` ≤ 1.25 cap (`:613`) — at **unchanged cell counts**.

**Verdict of the diagnosis: a clean near-wall-refinement fix.** This is the
textbook, non-fabricated repair, and it is what `T23G2_RESULTS.md:681-683`
("WHAT WOULD TURN THIS INTO A RESULT", item 2) itself prescribes: *"It needs
first-cell refinement on that patch specifically, not another uniform level."*

---

## 2. THE CHANGES — mesh near-wall spacing (primary) + convergence margin (bundled)

### 2.1 What is held BYTE-INVARIANT from T23G2

Everything except the two items in §2.2 and §2.3. Re-asserted, not assumed:
geometry (5° wedge, `dim = 2`, 6 mm bore, 3.9962 mm housing wall), operating point
(`P_LOSS = 305 W` sector share, `U_INF = 20 m/s`, `T_INF = 288 K`), properties (air
rho 1.2 / cp 1005 / k 0.026 / mu 1.8e-5; aluminium housing; core), turbulence model,
`nutLowReWallFunction` / `alphatWallFunction` Prt 0.85 / `noSlip`, the implicit
conjugate interface, the second-order energy convection scheme
(`bounded Gauss limitedLinear 1` on `div(phi,h/K/k/omega)`,
`T23G2_PREREGISTRATION.md:388-395`), `ranks = 1`, no `decomposePar`, the outer-BL
(`duct_wall`) first-cell heights **7.750800e-06 / 5.167200e-06 / 3.444800e-06 m**
(`:369`), and the **cell counts 40,320 / 90,720 / 204,120** (`:347`). Cell-count
ratio stays **exactly 2.250000** per region; refinement ratio r = 1.5000; NR_HOUS =
8 at the coarsest level. **Any file that differs and is not in §2.2 / §2.3 is a
REFUSAL, not a note.**

### 2.2 PRIMARY CHANGE — the inner-BL first-cell height, reduced (the G-YPLUS fix)

Only the **inner boundary-layer band's** registered first-cell height changes
(`fluid_to_housing`, `centrebody_up`, `centrebody_down`). It is reduced by a uniform
factor **0.4682** at every level, preserving the 1.5 inter-level ratio exactly and
leaving the layer count **NR_BL_IN = 40 / 60 / 90 UNCHANGED** (`:338`), so cell
counts and the 2.25 similarity are untouched:

| band | T23G2 (frozen) L1/L2/L3 [m] | **T23G2R (proposed)** L1/L2/L3 [m] | ratio |
|---|---|---|---|
| inner BL (`fluid_to_housing`, `centrebody_*`) | 2.306800e-05 / 1.537867e-05 / 1.025245e-05 | **1.080000e-05 / 7.200000e-06 / 4.800000e-06** | 1.500000 |
| outer BL (`duct_wall`) | 7.750800e-06 / 5.167200e-06 / 3.444800e-06 | **unchanged** | 1.500000 |

The build script derives the per-cell growth ratio `k` by bisection from
`(n, band length L, first-cell height d1)` exactly as `build_t23g2.py` does, and
**REFUSES** if any per-cell growth exceeds 1.25 or if the registered `d1` values do
not scale by 1.5 to within 0.5 % (`T23G2_PREREGISTRATION.md:1168-1170`). **None of
the arithmetic below is taken on the script's word — `G-MESHSIM` (§5.4) re-derives
it from the built `polyMesh`.**

### 2.3 BUNDLED CHANGE — convergence margin so the reused G-CONV gate is met on L2

T23G2_L2 failed `G-CONV` at `endTime = 12,000` (last `p_rgh` initial residual
**1.04122627289e-08** vs the reused ≤ 1e-8, `T23G2_RESULTS.md:126`), a 4.1 % miss on
one level. The finer near-wall mesh changes the convergence path, so the margin is
re-registered on **every** level. `endTime` (SIMPLE iteration count for
`chtMultiRegionSimpleFoam`) is raised **6,000 → 8,000 / 12,000 → 16,000 / 24,000 →
28,000**. **`G-CONV`'s thresholds are UNCHANGED** (§3): raising the iteration budget
is a run-config change to *meet* a frozen gate, never a change to the gate. The
strict-completion rule 4 (`rc = 0`; one `End`; last time == `endTime`; fields
present; `ExecutionTime` count == `endTime`; **age guard** — every field at `endTime`
newer than the case's own `0/T`) is enforced by
`verification/runs/T-family/T23_runs/mark_done_t23.py` exactly as the parent
(`T23G2_PREREGISTRATION.md:523-524, 539-541`), including the guard's refusal of a
case where `0` or a time dir already exists.

---

## 3. THE REUSED GATES — VERBATIM FROM T23G2, UNCHANGED (the fix is the MESH, never a gate)

**Every gate, threshold and band below is reused BYTE-FOR-INTENT from the frozen
T23G2 registration. Not one is relaxed. The successor freezes these before its
refined mesh runs (prediction-first).**

- **`G-YPLUS` (the failing gate) — REUSED UNCHANGED:** *max y+ ≤ **1.0** on EVERY
  wall patch, on EVERY level. Gated, not reported.* (`T23G2_PREREGISTRATION.md:1117-1118`,
  amendment A2.2.) Primary instrument
  `chtMultiRegionSimpleFoam -postProcess -func yPlus -region fluid -latestTime`
  (`:594-595`); independent cross-check reader from `U`, `nut`, `polyMesh` that
  **plants a perturbation, reads it back, and refuses if it cannot see it** (rule 3,
  `:598-602`); the two must agree to within **2 %** or it is a REFUSAL; a perfect
  zero from either is REFUSED.
- **`G-CONV` — REUSED UNCHANGED:** at `endTime`, on every level, **`h` ≤ 1e-9**, and
  `Uy Uz p_rgh k omega` initial residual **≤ 1e-8** at the last iteration; `Ux`
  excluded with the exclusion itself measured
  (`T23G2_PREREGISTRATION.md:559`, `T23G2_RESULTS.md:117-127`).
- **`G-MESHSIM` — REUSED UNCHANGED** (`:604-616`): cell-count ratio exactly
  **2.250000** per region; **first-cell wall-normal height ratio 1.500 ± 0.005** on
  every patch; **per-cell growth ratio ≤ 1.25** in every band on every level;
  housing wall cells **≥ 8** at the coarsest level; `checkMesh` OK on all regions of
  all levels; `blockMeshDict` `vertices` byte-identical across levels. A failure
  **stops the rung before any solver launches** (`:618`).
- **Roache triple gating — REUSED UNCHANGED:** `Fs = 1.25`, graded by
  `scripts/roache_triple.py` under `CLAUDE.md` rule 5 ordering — any level not
  iteratively converged/plateaued → `NOT A RESULT`; a non-`CONVERGING` triple →
  `NOT A RESULT` with values, both triples and orders printed; `CONVERGING` → `PASS`
  inside band else `GATE FAIL`, GCI at Fs = 1.25 and never quoted off a non-monotone
  triple.
- **`G-ORDER` band — REUSED UNCHANGED:** p(`Q4`) in **[0.5, 1.5]**
  (`T23G2_PREREGISTRATION.md:833-834`, A2.3), with the **`R7`/`R3`** repair in place
  so the gate consults `iterative_convergence` and prints `NOT A RESULT` when rule 5
  step (1) has voided the triple (`T23G2_RESULTS.md` §14, §17).
- **`Q3` band — REUSED UNCHANGED:** ΔT = T − 288.0 K in **[46.0, 56.0] K**
  (`Q3` receives `Q4`'s registered band, `T23G2_PREREGISTRATION.md:453`,
  `T23G2_RESULTS.md:176`). **The band is NOT moved** (rule 2 forbids it, and this
  file does not); whether the finer mesh brings `Q3` inside is an **open outcome**,
  registered as a prediction in §4, not a gate change.
- **The five graded quantities and roles — REUSED UNCHANGED:** `Q4` core vol-avg T
  (PRIMARY ORDER), `Q5` `housing_to_fluid` surface heat flux (REPORTED, NEVER
  GATED), `Q1` housing max T, `Q3` core max T, `Q2` interface areaAvg T, `Q6`
  housing vol-avg T (`:448-455`); graded on ΔT = T − 288.0 K.
- **Planted-zero controls — REUSED UNCHANGED:** 6 quantities × 3 levels + 2 y+
  readers = **20**, each asserted by `RT.assert_plant_control`, refusing on a
  control that does not read its plant back (`:624-625`, §5.6; the `R5` repair that
  built all 18 quantity controls and made the exact-zero `G-RATIO` licence
  executable is retained, `T23G2_RESULTS.md` §7).

**No gate value, threshold or band above differs from T23G2 by any amount. The
only physical change is the inner-BL first-cell height (§2.2); the only run-config
change is the endTime margin (§2.3).**

---

## 4. PREDICTIONS — prediction-first, frozen before the refined mesh runs

DESIGN ESTIMATES. y+ predictions use the near-wall relation y+ ∝ first-cell
centroid distance at each level's own (fixed) friction velocity, scaling each
patch's measured T23G2 value by the 0.4682 first-cell factor.

| id | prediction | basis |
|---|---|---|
| **P-Y1** | max y+ on `centrebody_up` = **0.854 / 0.634 / 0.470** at L1/L2/L3, each ≤ 1.0 with ≥ 15 % margin, coarsest binding | 1.8245/1.3539/1.0047 × 0.4682 |
| **P-Y2** | max y+ on `fluid_to_housing` = **0.352 / 0.237 / 0.159**; `centrebody_down` **0.343 / 0.231 / 0.155**; `duct_wall` UNCHANGED **0.618 / 0.457 / 0.339** | parent × 0.4682 (inner band); outer band unchanged |
| **P-Y3** | ALL four patches clear y+ ≤ 1.0 on ALL three levels → **`G-YPLUS` PASS** | P-Y1 + P-Y2 |
| **P-G** | per-cell growth ratio inner band ≈ **1.13 / 1.08 / 1.05**, all ≤ 1.25 → `G-MESHSIM` PASS | bisection on (n, L≈9.94 mm, new d1) |
| **P-C** | `G-CONV` met on ALL levels including L2 at the raised endTimes | L2 missed by 4.1 % at 12,000; +33 % iterations |
| **P-Q3** | directional: `Q3` fine value continues its monotone descent (58.238 → 57.379 → 56.708) below its L3 value; **may or may not enter [46.0, 56.0] K** — registered as an open outcome that can lose | monotone series in `T23G2_RESULTS.md:684` |

**Registered loss modes.** If any patch exceeds y+ = 1.0 at any level, `G-YPLUS`
`GATE FAIL` and P-Y* lost — reported as exactly that. If `Q3` again lands above
56.0 K, `Q3` band `GATE FAIL` and the rung stays `NOT A RESULT` on that ground,
requiring a further successor — P-Q3's directional claim is honest that this can
happen. A near-wall reduction that stiffens the linear system and slows convergence
past the raised endTimes trips `G-CONV` — P-C lost.

---

## 5. THE PLANNED SCRIPTS — NAMED, NOT WRITTEN (written only after the supervisor's §3 diff-read)

**No comparator or build code is written by this draft** (the VF-sweep pattern: the
contract is registered; the executable path is authored and read as a diff by the
supervisor before any solver launches). To be written after the §3 design check:

1. **`docs/campaigns/T-family/build_t23g2r.py`** — a parametric edit of
   `build_t23g2.py`: the ONLY parameter change is the inner-BL `d1` table (§2.2) and
   the `endTime` table (§2.3); prints `L`, `n`, `d1`, `k`, the `simpleGrading`
   value, the band-length residual and the housing-wall cell count at every build,
   and **REFUSES** on growth > 1.25 or on `d1` not scaling by 1.5 within 0.5 %.
2. **`docs/campaigns/T-family/analyse_t23g2r.py`** — the comparator, reusing the
   T23G2 gate logic with the granted repairs already folded in (`R1`–`R5`, `R7`),
   **plus the prospective `R6` refusal below**. Grading path frozen at the
   pre-registration commit and verified by hashing against the committed blob.
3. **Reused unchanged, on the grading path:**
   `verification/runs/T-family/T23_runs/mark_done_t23.py` (rule 4 completion),
   `scripts/roache_triple.py` (triple gating + `PLANT`), and
   `docs/campaigns/T-family/t23g_readonly_diagnosis.py` (y+ / first-cell / mesh
   readers).

### 5.1 The required pre-flight (reused from T23G2 A2.5)

Before the graded launch, every function object must be shown to construct in a
**scratch copy** of a built case with **no graded artifact written**
(`T23G2_PREREGISTRATION.md:1183-1188`); the graded run is not launched until it
passes; the pre-flight's cost is reported separately and never folded into the
campaign ratio.

### 5.2 NET-NEW, STRICTLY STRICTER — prospective `R6` (the OWED item T23G2 could not fix)

`T23G2_RESULTS.md` §8 records that `gate_yplus`'s **"primary instrument ABSENT"**
branch continues to grade, that making it a **REFUSAL** (`R6`) was a good change,
and that `verification` refused it as a §2d.1 repair because *"a gap in a
registration is closed by the NEXT registration, not by repairing the rung that
revealed it"* (`:468-471`). **T23G2R is that next registration.** REGISTERED
PROSPECTIVELY: **if the primary y+ log instrument is ABSENT on any level, the
comparator REFUSES (exit 2), it does not fall through to the independent reader.**
This can only *add* a refusal; it relaxes nothing.

---

## 6. COST — rule 12, POINT + CAP in core-minutes, cost_basis honest

**DESIGN ESTIMATE. `cost_basis = REPORTED-BY-OWNER`:** the rate is owner-stated
($0.0513/core-h, 2026-08-21/22) and **the box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5), so no dollar figure here is a measurement. Basis:
T23G2's **MEASURED** per-iteration cost (`T23G2_RESULTS.md` §10 — L1 0.0029083, L2
0.0071083, L3 0.0180840 core-min/iter, `ranks = 1`), scaled by the raised endTimes
(§2.3) and by a **×1.05 near-wall-stiffening uplift (ASSUMED**, labelled as such —
a finer first cell can raise per-iteration cost slightly; cell counts are unchanged
so the dominant driver is unchanged).

| level | cells | `endTime` | per-iter [core-min] (measured × 1.05) | **POINT** | **CAP** | timeout [s] |
|---|---|---|---|---|---|---|
| `T23G2R_L1` | 40,320 | 8,000 | 0.0030537 | **24.5** | **49.0** | 2,940 |
| `T23G2R_L2` | 90,720 | 16,000 | 0.0074637 | **119.5** | **239.0** | 14,340 |
| `T23G2R_L3` | 204,120 | 28,000 | 0.0189882 | **531.7** | **1,063.4** | 63,840 |
| **CAMPAIGN** | | | | **675.7** | **1,351** | |

**The timeout IS the cap. An overrun STOPS the run; a capped level is not restarted
with a bigger number** (rule 12). **USD — DERIVED, NEVER MEASURED:** POINT 11.26
core-h × $0.0513 = **$0.578**; CAP 22.5 core-h = **$1.155**. Under the $25/run
pre-authorisation, and still costed here per rule 12. Ranks = 1 on every level,
three cores, one per level, concurrent. **Estimate-versus-actual calibration
(rule 12) is owed at completion**: a row in `docs/COST_CALIBRATION.md` comparing
this POINT against the measured actual, gap attributed, waste named separately.

---

## 7. WHAT THIS DRAFT DELIBERATELY DOES NOT DO

- **It does not edit the frozen T23G2 registration** (rule 6). T23G2 keeps its
  bytes and its `NOT A RESULT` verdict.
- **It does not commit anything, freeze any sha, or run any solve.**
- **It does not write comparator or build code** — §5 names the scripts; they are
  authored only after the supervisor's §3 diff-read.
- **It does not move, widen or relax any gate, threshold, band or label.** The only
  physical change is the inner-BL first-cell height; the only run-config change is
  the endTime margin; the only net-new registration is a strictly stricter refusal.

---

## 8. OPEN ITEMS THIS LANE IS NOT CERTAIN OF (for the supervisor's read)

1. **y+ linearity in first-cell height.** P-Y* assume y+ ∝ first-cell centroid
   distance at fixed per-level friction velocity. Refining the near-wall cell can
   slightly change the resolved u_tau (T23G2's inter-level data show u_tau falling
   ~10 %/level as the mesh refines). The direction is favourable (u_tau tends to
   *drop* on finer near-wall meshes, lowering y+ further), so the ~0.85 coarsest
   estimate is conservative — but it is an ESTIMATE, and the coarsest level is the
   binding one. Margin (0.854 vs 1.0) is 15 %; the supervisor may prefer a larger
   reduction factor.
2. **Inner-band length L.** The parent's stated growth ratios (1.099/1.070/1.043)
   do not reproduce a single band length across levels when back-solved (9.94 /
   12.51 / 10.30 mm), i.e. those `k` values are rounded. The growth estimates in
   §4/§6 use L ≈ 9.94 mm; the build script derives `k` from the actual band length
   and `G-MESHSIM` re-checks ≤ 1.25 from the built mesh, so the true `k` is gated
   regardless — but the exact figure should be read off the build, not this draft.
3. **Whether to bundle the L2 convergence fix and the Q3 band.** §2.3 raises endTime
   so the reused `G-CONV` is met on L2, and §3 reuses `Q3`'s band; both are needed
   for the re-run to be a RESULT rather than another `NOT A RESULT`, but the
   supervisor may prefer to split the pure y+ fix from the convergence/Q3 work.
4. **The near-wall-stiffening cost uplift (×1.05) is ASSUMED**, not measured. If the
   finer first cell slows convergence more than that, the L2/L3 caps bind first.
5. **`Q3` may still fail its band.** P-Q3 is directional only; the mesh may not bring
   `Q3` inside [46.0, 56.0] K, in which case the rung stays `NOT A RESULT` on that
   ground and needs a further successor. This is registered honestly, not waved.

---

---

## 9. SUPERVISOR §3 DESIGN CHECK — ratified 2026-09-07 (heat-transfer supervisor)

*This is the supervisor's personal design read (non-delegable), recorded before any
script is written or committed. It ratifies the DESIGN; it does NOT freeze — the
freeze follows the §3 diff-read of the build + comparator code (§5), which are not
yet written.*

- **Design SOUND. No gate, threshold, band, cap or label is moved.** Every gate is
  reused verbatim from frozen T23G2; the only physical change is the inner-BL
  first-cell height (§2.2), the only run-config change is the endTime margin (§2.3,
  raising the iteration budget to MEET a frozen `G-CONV`, never to move it), and the
  one net-new item (prospective `R6`, §5.2) is strictly STRICTER — it can only add a
  refusal. Confirmed against the frozen record: rule-2 clean.
- **Lineage RATIFIED.** `Predecessor: T23G2` (§0) is the §2ay.2(b) form; T23G2 keeps
  its `NOT A RESULT` verdict; this linkage moves no verdict. It discharges the
  `G-YPLUS` rows (`T23G2_RESULTS.md:146-148`) as an active dated fix-successor.
- **Diagnosis VERIFIED by the supervisor from the frozen record** (not merely
  relayed): `centrebody_up` shares the one inner-BL first-cell height with
  `fluid_to_housing`, which PASSES at that identical spacing (y+ 0.751/0.505/0.339),
  while `centrebody_up` fails (1.8245/1.3539/1.0047) — the excess is local friction
  velocity, not a gate/geometry defect; and y+ resolves DOWN with refinement
  (not a singularity). A clean near-wall-refinement fix.
- **RULING — bundling (open item #3): APPROVED.** T23G2 was `NOT A RESULT` on three
  grounds (`G-CONV` L2, `G-YPLUS`, `Q3`). A successor reusing every gate must clear
  ALL of them to yield a RESULT rather than repeat `NOT A RESULT`; a y+-only fix
  would discharge nothing. Bundling the endTime margin and the reused (unchanged)
  `Q3` band is the honest design and relaxes nothing.
- **RULING — reduction factor ×0.4682 / 15 % coarsest margin (open item #1):
  ACCEPTED.** The P-Y* estimate is directionally CONSERVATIVE (u_tau drops on finer
  near-wall meshes → real y+ lower than predicted), the inner-band growth ratio
  ≈1.13 sits well under the 1.25 `G-MESHSIM` cap, and a y+ overshoot is registered
  as an honest `GATE FAIL` loss mode. Tightening the factor toward the growth cap
  for second-order margin is not warranted.
- **Open items #2/#4/#5 — accepted as registered:** #2 (band length `L` back-solves
  to rounded `k`) is gated at build by `G-MESHSIM` re-deriving growth from the built
  `polyMesh` and refusing >1.25, so the exact `k` is measured, not asserted; #4 (×1.05
  cost uplift ASSUMED) and #5 (`Q3` may still fail its band → rung stays `NOT A
  RESULT`, owes a further successor) are honestly registered loss modes, not defects.
- **STILL OWED before freeze (NEXT lane cycle → supervisor's §3 diff-read → freeze):**
  the build (`build_t23g2r.py`) and comparator (`analyse_t23g2r.py`) scripts of §5,
  read by the supervisor AS A DIFF against the frozen `build_t23g2.py` /
  `analyse_t23g2.py` before any solver launches; then the sha-freeze with the §2au
  `FREEZE-PIN`. No compute launches until the pre-registration is frozen and
  committed (personal check 4).

*Drafted 2026-09-07 by a heat-transfer `lab-lane`; DESIGN ratified by the
heat-transfer supervisor 2026-09-07 (§9). NOT FROZEN — the build/comparator code is
not yet written; the §3 code diff-read and the freeze are the supervisor's.*

---

## 10. FREEZE — 2026-09-08 (pre-first-compute amendment, CLAUDE.md rule 2)

*The build and comparator scripts named in §5 are now written and diff-read; this
section freezes the grading path. **Condition, checked at freeze:** nothing has run
— `verification/runs/T-family/T23G2R_runs` is ABSENT on disk (checked 2026-09-08),
so no gate, threshold, band, cap, label or prediction may be — or is — altered here.
This amendment pins blobs and records the freeze mechanism ONLY.*

### 10.1 FREEZE TABLE — NON-SELF grading-path files, pinned by git blob

These are pinned to the blobs below. `build_t23g2r.py` enters the tree **in this
freeze commit** (its on-disk `git hash-object`); the four reused frozen instruments
are pinned at their committed HEAD blobs (each verified byte-identical on disk at
freeze). `print_grading_path_shas` in the comparator rev-parses these members
against `GRADING_PATH_FREEZE_COMMIT` at grade time.

| grading-path member | role | pinned git blob | source |
|---|---|---|---|
| `docs/campaigns/T-family/build_t23g2r.py` | mesh/case build (§5.1) | `63a7e5aa9f96c917d4f65d027ee84918c8288b6d` | on-disk, enters tree at freeze commit |
| `verification/runs/T-family/T23_runs/mark_done_t23.py` | rule-4 completion (§5.3) | `37165979fafbe3c87921dab05b51e984878d90dc` | HEAD (unchanged on disk) |
| `scripts/roache_triple.py` | triple gating + `PLANT` (rule 5/rule 14) | `78e56a3bc2c2a07571db1cf3c91f4c2c31f246b8` | HEAD (unchanged on disk) |
| `docs/campaigns/T-family/t23g_readonly_diagnosis.py` | y+ / first-cell / mesh readers | `73804c02d2f1ebbb2cd2ad63796f4b5cfb4d7067` | HEAD (unchanged on disk) |
| `docs/campaigns/T-family/analyse_t23g2.py` | PREDECESSOR comparator (diff base) | `72357dad2bfb39ca74b78ad253cdbca1545d6534` | HEAD (unchanged on disk) |

### 10.2 THE SELF MEMBER — `analyse_t23g2r.py` is NOT pinned in the table above (§2au.2)

The comparator's own blob (on-disk `7f7786a0dd3ce2ea8ea47756db5550584214bb43`) is
**deliberately absent from §10.1**. A self-referential "IDENTICAL vs its own freeze
commit" pin is a **git pre-image**: the freeze sha would have to live inside the
hashed file, so writing it changes the blob and hence the commit (established
empirically by a heat-transfer lane, 2026-09-08; pinning to a predecessor commit
fails the same way, because writing any pin moves the blob off every prior committed
one). The SELF member is instead anchored, per `VERIFICATION_CHARTER.md` §2au.2, by
**three things**:

1. **`EXPECTED_SELF_BLOB = None`** in `analyse_t23g2r.py` — the self-hash is
   **PRINT-ONLY** (`verify_self` prints the running blob as provenance and does not
   refuse on it; it asserts only if `EXPECTED_SELF_BLOB` is ever set).
2. **A `FREEZE-PIN: analyse_t23g2r.py@7f7786a0dd3ce2ea8ea47756db5550584214bb43`
   line in the freeze commit message** — the blob recorded outside the hashed
   content, where hashing cannot perturb it.
3. **Grade-time byte-identity** of the on-disk `analyse_t23g2r.py` against that
   recorded blob (the supervisor's non-delegable check before launch).

Precedent: `analyse_t10avf2_sweep.py`, frozen at `5fb1d8a9` with
`EXPECTED_SELF_BLOB = None` (its SELF member is print-only; its one asserted blob is
a *different*, non-self-referential file). The DRAFT guard is retained: while
`GRADING_PATH_FREEZE_COMMIT == "PIN-AT-FREEZE"`, `verify_self` REFUSES to grade.

### 10.3 THE TWO-COMMIT FREEZE — one freeze operation, not an edit of a frozen file

1. **Freeze commit (commit 1):** this pre-registration amendment + `build_t23g2r.py`
   + `analyse_t23g2r.py` (still carrying the `PIN-AT-FREEZE` placeholder), with the
   §10.2 `FREEZE-PIN` line in its message. This commit CONTAINS `build_t23g2r.py`,
   so its tree can be rev-parsed for every §10.1 member.
2. **Pin commit (commit 2):** set `GRADING_PATH_FREEZE_COMMIT` in
   `analyse_t23g2r.py` to commit 1's sha, so `print_grading_path_shas` resolves the
   non-self members. This is **the same freeze operation completed**, NOT an edit of
   a frozen file: the comparator was `PIN-AT-FREEZE` (an explicitly unfrozen DRAFT)
   until commit 2 sets its pin. Writing the pin re-blobs the comparator — expected,
   and exactly why the SELF member is anchored by commit message + byte-check
   (§10.2), never by a table entry.

### 10.4 STILL OWED AFTER THIS COMMIT — the §5.1 pre-flight and personal check 4

The **§5.1 pre-flight** (every function object shown to construct in a scratch copy
of a built case, **no graded artifact written**,
`T23G2_PREREGISTRATION.md:1183-1188`) is **OWED before the graded launch** and its
cost is reported separately, never folded into the campaign ratio. **NO SOLVER
LAUNCHES until the freeze is committed** (personal check 4, non-delegable): the
graded run on `verification/runs/T-family/T23G2R_runs` begins only after commit 2
and the pre-flight pass.

*Freeze section authored 2026-09-08 by a heat-transfer `lab-lane`; the §3 code
diff-read, the blob pins and the freeze commit are the supervisor's (non-delegable).
Nothing is committed by this lane.*
