# SUBOFF R1 — DARPA SUBOFF bare hull, zero incidence, total-drag parity — PRE-REGISTRATION

**STATUS: FROZEN 2026-09-10 by the cfd-supervisor (check-4). NO compute has run for this rung.**
The gate, threshold, cap and label below are CLOSED as of this commit. From here they change
only as dated addenda that cannot alter a gate, threshold, cap or label; originals are struck,
never rewritten (standing rule 2, rule 6). The grading path is pinned by blob sha in §11 —
verify the frozen file IS the file that ran by hashing it against the committed blob.
This document is drafted by a cfd lab-lane for the cfd supervisor. The **freeze
(sha) and any graded launch are the supervisor's check-4**; the grader diff-read is
the supervisor's check-1. Nothing below is graded, and no number here is a result.
Written before any solver launch, in the W3-Ahmed pre-registration pattern: if a
result later falsifies a prediction, the prediction stays as written and the result
says so.

Case family: Navier-class parity, `navier_class` convention.
- Campaign prose: `docs/campaigns/navier_class/SUBOFF/`
- Case inputs / grader: `cases/navier_class/SUBOFF/` (grader `grade_suboff.py`)
- Run outputs (none yet): `verification/runs/navier_class/SUBOFF/`
- Reference values: `verification/runs/navier_class/SUBOFF/suboff_reference_ReL1p2e7.json`

---

## 1. What this rung is, and what it is NOT

The DARPA SUBOFF ladder's full ambition (Case 1) is forces and moments through an
angle-of-attack / drift sweep, yielding the stability derivatives Z_w, M_w and the
neutral point (Roddy 1990 DTRC/SHD-1298-08; conventions Gertler & Hagen 1967 NSRDC
2510, Feldman 1979). **That is a LATER ladder step (§8), not this rung.** R1 is the
**cheapest defensible gate**: the **bare-hull, zero-incidence TOTAL DRAG (axial force)
coefficient at a single Reynolds number** — one scalar, one published reference class
(Crook 1990 drag-vs-speed; consolidated in Liu & Huang 1998), a fully attached
axisymmetric turbulent boundary layer that steady RANS handles well. The bare hull
is the axisymmetric Model 5470 body (Groves/Huang/Chang 1989), regenerable exactly
from the report equations.

Because the bare hull at zero incidence is **axisymmetric**, R1 is run as an
axisymmetric wedge. Under the reference-tier standard's dimension axis it is
therefore **not-applicable-dimension** and **must never appear in a 3-D reference-tier
listing** (`REFERENCE_TIER_STANDARD.md` §4). The 3-D reference-tier entry is earned by
the later at-incidence rung, not this one.

---

## 2. THE GATE — declared now, one-way

> **Gate D1.** The bare-hull zero-incidence total drag coefficient
> `CT = R_T / (½ ρ U² S_wetted)` at `Re_L = 1.2×10⁷`, taken from the finest grid of a
> **CONVERGING** Roache triple, is **PASS** iff `|CT_cfd − CT_ref| ≤ 0.10·CT_ref`
> (±10%), else **GATE FAIL**. A non-CONVERGING triple is **NOT A RESULT** whatever the
> value (rule 5). The band ±10% is the frozen threshold.

**Threshold band: ±10% relative.** Rationale, recorded in advance: bare-hull
straight-course RANS drag on an attached axisymmetric body is a case where published
RANS (Toxopeus 2008 is the closest analogue for expected accuracy) agrees with
measurement to a few percent; ±10% is a **conservative** first-rung band that a
correct solve should clear with margin, and it will not be tightened after the run.

**Reference value `CT_ref`.** Anchor **3.6×10⁻³ on wetted-surface area**, an ITTC-1957
friction-line + body-of-revolution form-factor engineering estimate
(`suboff_reference_ReL1p2e7.json`). This is a **MANIFEST / engineering anchor and it
STAYS one**: there is **no title-verified SUBOFF report PDF on disk** (the Crook 1990 /
Liu & Huang 1998 references are NTIS/TRID landing pages only, 2026-09-09), so the gate
is **BOUNDED-AGREEMENT against this manifest anchor and remains so until a real,
title-verified SUBOFF report PDF lands.** This is explicitly **NOT** a promise to
"replace the anchor with a title-verified value before freeze" — no such value is
retrievable today. If a title-verified SUBOFF report is obtained later, the anchor is
confirmed or corrected by a dated addendum then; the band shape (±10%) does not move.

**Reference constants (frozen into the forceCoeffs block; the grader asserts them on
disk and refuses on mismatch):** `magUInf = 2.893 m/s` (so `Re_L = U·L/ν = 1.2×10⁷`
with `L = 4.356 m`, `ν = 1.05×10⁻⁶ m²/s`), `lRef = 4.356 m`, `rhoInf = 1000 kg/m³`,
`Aref = S_wetted` **read back from the built hull patch area** and cross-checked
(±3%) against the analytic Groves/Huang/Chang 1989 hull surface area.

---

## 3. REFERENCE TIER — manifest-only, stated honestly

Applying `verification/credibility/REFERENCE_TIER_STANDARD.md`:

- **Tier: BOUNDED-AGREEMENT (rank 3) at best, against MANIFEST VALUES ONLY.** The
  SUBOFF drag references (Crook 1990, Liu & Huang 1998) are **NTIS/TRID landing pages
  only; no free title-verified PDF is on disk** as of 2026-09-09 (peer retrieval lane
  `a8dea886569cec3a3`). **This rung is NOT experiment-validated and may not be shown as
  such** until a real SUBOFF report PDF is title-page verified (rule 15). Any page
  showing D1 against the experiment must carry the ±10% band.
- If the solve reproduces only the ITTC engineering anchor (not a title-verified
  experiment), the honest tier is **CODE-VERIFIED (rank 2)** with the disavowal
  "NOT experiment-validated", and the tier is **upgraded to bounded-agreement once the
  title-verified Crook/Liu-Huang value lands.**
- **Registry action is deferred to completion.** `reference_tier_registry.json` is the
  frozen registry of *completed 3-D cases*; R1 is neither completed nor 3-D, so it is
  **not** added now (adding an uncompleted/axisymmetric case would be a dimension leak
  / registry drift). The tier is pre-declared here; the verification team registers it
  at completion of the 3-D at-incidence rung. `scripts/check_reference_tier.py
  --selftest` was confirmed green by this lane (all four RED-plant arms flip).

---

## 4. MESH PLAN (per `docs/standards/MESH_STANDARD.md`)

**Topology.** Axisymmetric wedge (single cell in azimuth, `wedge` patches),
`blockMesh`-generated in the (x, r) plane over the analytic hull profile. If
`blockMesh` refuses the topology, **the topology is redesigned, not bypassed by
hand-writing polyMesh** (§8.2).

**Three-level family (rule 5; §9.1 three levels is the gate standard).** Geometric
similarity is mandatory: first-cell height and expansion ratio **scale with the mesh**,
recipe otherwise fixed (§9.2). Target ~40k / 90k / 202.5k cells (2.25× per level ⇒
`r ≈ 1.5` in `h ~ 1/√N` for a 2-D-like refinement); the grader treats SUBOFF as
`dim = 2`. **Per-level graded values (first-cell, expansion) are read back from the
built mesh** and recorded in each level's birth certificate (§9.2), never from the
requested parameter.

**Admission gates (§3), and BUILD-BEFORE-FREEZE (§8.1).** Each level must be built,
`checkMesh`'d and **shown admissible** before this pre-registration is frozen: max
non-orthogonality **≤ 70°**, max skewness **≤ 4**; aspect ratio and whole-mesh
cell-volume ratio **recorded** in the birth certificate (§11 — recorded, not gated).
A `birth_certificate.json` sits beside each `polyMesh`.

**Wall treatment.** First rung uses **kOmegaSST with wall functions**, target
`y⁺ ≈ 30–100` (cheapest defensible; wall-resolved `y⁺ < 1` is a later rung). The
achieved `y⁺` band is read back and recorded; Menter/Kuntz/Langtry 2003 is the
wall-function-vs-wall-resolved basis.

**Farfield / blockage.** Free-stream (free-air) external domain with Spalart-Rumsey
2007 effective inflow turbulence values and placement: radial farfield ≥ 10·L,
inlet ≥ 5·L upstream, outlet ≥ 10·L downstream (domain blockage negligible). The
Crook 1990 reference is a **towing-tank** resistance measurement whose tank blockage
is small, so free-air CFD is the correct comparison for D1. **Note for a later
Cp-vs-Huang-1992 rung:** Huang's data is **wind-tunnel**, so a Barlow-Rae-Pope 1999
solid+wake blockage correction is required there before comparing tunnel-patched CFD
to that reference — it does NOT apply to this towing-tank drag gate.

**GCI.** Celik 2008 `Fs = 1.25`, computed by the shared instrument
`scripts/roache_triple.py`; never quoted for a non-monotone triple.

### 4a. THE THREE REGISTERED GRADED RUN ROOTS (pre-compute registration, 2026-09-10)

§4 named only the parent `verification/runs/navier_class/SUBOFF/`. **The graded triple
runs in exactly these three directories, coarse → fine, and in no others.** A number
taken from any other directory under that parent is not a graded R1 number.

| level | registered run root | cells (`checkMesh`, MEASURED) | maxNonOrtho (≤70) | maxSkew (≤4) | `checkMesh` |
|---|---|---|---|---|---|
| coarse | `verification/runs/navier_class/SUBOFF/reg_coarse` | 39,904 | 57.4051 | 1.6538 | Mesh OK |
| medium | `verification/runs/navier_class/SUBOFF/reg_medium` | 89,784 | 63.6022 | 1.9002 | Mesh OK |
| fine   | `verification/runs/navier_class/SUBOFF/reg_fine`   | 202,014 | 68.7055 | 2.1226 | Mesh OK |

Cell-count nesting is exactly 2.25× per level (89,784/39,904 = 2.25; 202,014/89,784 =
2.25), i.e. a per-direction refinement of 1.5 for the `dim = 2` wedge; radial resolution
is 344 → 516 → 774 and axial 116 → 174 → 261. The §4 admission gates are cleared at all
three levels by the lines above, each read back from that level's own `MESH_LINE.txt`
beside its `birth_certificate.json`.

**NOT graded, and named here so nobody grades a sibling by accident:**
`smoke_coarse` (the §6 exercise smoke, a 7,600-cell wedge, already run, `Cd`
sanity-only), `mesh_medium` and `mesh_fine` (superseded mesh-only builds), and
`diag_medium_wp16` (a wall-treatment diagnostic). None of these is an R1 level.

**PRE-COMPUTE CONDITION, and how it was checked (rule 2).** Checked 2026-09-10T04:33Z by
a cfd lab-lane, directly on disk, per directory: `reg_coarse`, `reg_medium` and
`reg_fine` each hold **no `0/`**, **no numeric time directory** (`find -maxdepth 1 -type
d -regex '.*/[0-9]+(\.[0-9]*)?'` returns zero rows in each), **no `rc` sidecar**, **no
`log.simpleFoam`** and **no `postProcessing/`**. The directories that do not exist are
therefore `reg_coarse/0`, `reg_medium/0`, `reg_fine/0` and any `reg_*/<time>`; **no
compute has run for this rung**, so §4a and §5a below are legal pre-compute
registrations and not post-hoc addenda. Each holds only `0.orig/`, `constant/`,
`system/`, `birth_certificate.json`, `MESH_LINE.txt`, `AREF_PIN.txt`, `log.blockMesh`,
`log.checkMesh` and the build stdout/stderr.

---

## 5. THE GRADER — `cases/navier_class/SUBOFF/grade_suboff.py`

Diff-read is the supervisor's check-1. Built-in non-negotiables:

- **Live planted-zero controls (rule 3) — TWO, and the gate reader has its own.**
  (i) **Gate-reader control (primary):** PLANT `CT = 1.234×10⁻³` into the last row of a
  COPY of the finest `coefficient.dat` and re-read it through `read_CT` — **the same
  parser the verdict comes from** — refusing (exit 2) unless the returned value moves by
  the plant. This is the control the graded number needs, because `CT` is read from
  `coefficient.dat`, not from the field. (ii) **Field control (secondary):** PLANT
  `500 Pa` into ONE hull owner-cell of a COPY of the finest `p` field, re-read the hull
  mean-surface-pressure through the same reader, refuse unless it moves by `PLANT/n_hull`.
  A zero from a reader not shown able to see a non-zero is not evidence.
- **Refuse-not-degrade.** `exit 2` on any missing/malformed/unreadable input or a
  control that misbehaves; `exit 70` only for an internal grader defect; `exit 0` only
  when a verdict was produced.
- **Rule-4 strict completion, per level.** `rc==0` **read from an rc sidecar / DONE
  marker written INSIDE the detached wrapper** — never inferred from an `End` line (the
  setsid-parent-returns-zero lesson: a `setsid`/`timeout` parent exits 0 for every
  outcome); an `End` line in the log is also required; last time == `endTime`;
  **ExecutionTime count == `round(endTime/deltaT)`** (rule-4 clause 5; the run took the
  registered number of steps); **incompressible-RANS field set `p U k omega nut phi`**
  present at endTime and every field **newer than `0/`** (age guard). The thermal-family
  set (T, p_rgh, alphat) does not apply — simpleFoam incompressible has no energy
  equation; the enforced set is stated in the grader header. **This requires the R1 run
  to write an rc sidecar** (a freeze precondition on the launcher).
- **forceCoeffs normalisation asserted on disk.** `magUInf/lRef/rhoInf` must equal the
  registered values and `Aref` must match the reference wetted area (±3%) or the grader
  refuses — a coefficient on the wrong normalisation is not the gated quantity.
- **Rule-5 Roache triple via the shared instrument** (`grade_ladder`, `dim=2`), so no
  `P_MIN`/`STAGNANT_FLOOR` symbol is redefined (MESH_STANDARD §10.5). Order: iterative
  convergence + plateau first (a level not plateaued ⇒ NOT A RESULT), then the triple
  (DIVERGENT/STAGNANT/OSCILLATORY/EXACT ⇒ NOT A RESULT), then CONVERGING ⇒ band verdict
  with GCI printed. **Fixed verdict vocabulary only.**
- **Iterative convergence READ, never defaulted (rule-5 clause 1).** Per-level iterative
  state comes from `read_iterative_state`, which reads `log.simpleFoam`: CONVERGED iff
  the solver printed "SIMPLE solution converged" OR every monitored field's **final
  Initial residual** (`p Ux Uy k omega`) is below the registered `RES_TOL = 1×10⁻⁴`
  (Initial, not Final — the W3 gate-(b) test). A level that is not iteratively converged
  makes the whole triple **NOT A RESULT** before the triple is even read. Plateau of `CT`
  is measured separately here.
- **Solver-config requirement (so `last == endTime` is reachable AND iterative
  convergence is judged).** R1 runs to a **fixed iteration count `endTime` with
  `deltaT = 1` as a HARD stop and NO `residualControl` early-exit**, so every level ends
  at exactly `endTime` and the ExecutionTime count equals `round(endTime/deltaT)`.
  Iterative convergence is then the final-Initial-residual test above (residuals below
  `RES_TOL` at `endTime`), not an early "converged" stop. This is a freeze precondition
  on the case's `system/controlDict` and `fvSolution`.

Selftest (`--selftest`) confirmed green by this lane: CONVERGING-in-band → PASS,
OSCILLATORY → NOT A RESULT, not-plateaued → NOT A RESULT, missing control → refuse.

### 5a. THE REGISTERED SOLVER LENGTH — `endTime`, and why this number (pre-compute registration, 2026-09-10)

§5's last bullet **requires** a fixed iteration count with `deltaT = 1` as a hard stop
and no `residualControl` early-exit, but **never stated the number**. That is a rule-2
trap: the three built levels carried the builder's smoke default `endTime 50`, which is
not a graded length, and a graded run at 50 SIMPLE iterations would return
`NOT_CONVERGED` from `read_iterative_state` and make the whole triple **NOT A RESULT**
before the triple was read — a truncation artifact wearing a verdict's clothes. The
number is registered here, **before any compute**, on a basis that is stated in advance
and contains no residual reading.

**REGISTERED, for all three levels of §4a, and one-way:**

```
endTime         2500;   // SIMPLE iterations; HARD stop
deltaT          1;      // unit step, so rule-4 clause 5 reads ExecutionTime count == 2500
writeInterval   2500;   // one field write, at endTime
purgeWrite      0;
```

`system/fvSolution` at every level **omits `residualControl`** (confirmed on disk at all
three levels, 2026-09-10), so no early exit can make `last < endTime`.

**HOW 2500 WAS CHOSEN — the basis, stated in advance, and what is NOT in it.** It was
**not** chosen by running the case and reading where the residuals flattened; no graded
solve has run and none was run to pick this number (rule 2). The basis is four things
that all existed before it:

1. **The registered cap binds it from above.** §7's frozen 150 core-minute cap covers
   the triple + the §6 smoke + one rerun allowance. At the rate registered below and
   with one **fine-level** rerun (the most expensive single level) held in reserve, the
   cap admits at most `N = 2892`. With no rerun reserved the cap would admit 4653, and
   with a whole-triple rerun reserved only 2327; the fine-level reading is the one
   registered, and 2500 sits under its bound with 13.5% of the cap unspent.
2. **Lab precedent for this exact solver pattern.** `MRF_R1_PREREGISTRATION.md`
   registered **4000** fixed iterations, hard stop, no `residualControl`, for a steady
   segregated-SIMPLE incompressible RANS case that is strictly *harder* to converge than
   this one (rotating frame, blade–baffle interaction, trailing vortices).
   `W1_HUMP_CHALLENGE_PREREGISTRATION.md` registered a **5000** cap for a *separating*
   hump. SUBOFF R1 is a fully attached, zero-incidence, axisymmetric turbulent boundary
   layer — the easiest steady-RANS convergence class in this ladder — so a number of the
   same order but **below** MRF's is the precedent-consistent choice, not a novel one.
3. **The lab's nearest measured convergence count, on a harder case.** F6a's kOmegaSST
   `simpleFoam` leg printed *"SIMPLE solution converged in 1772 iterations"*
   (`verification/campaign/F6a_epistemic_band.md:254`, checked 2026-07-29) on a
   51,626-cell separating-hump mesh against `endTime 2000`. 2500 is **1.41×** that count
   on a case with no separation. This is a *precedent from another case's record*, not a
   residual reading from this one.
4. **The grader's own test decides convergence, not this number.** `endTime` is a HARD
   STOP; `read_iterative_state` judges convergence at that stop against `RES_TOL = 1e-4`
   on the final **Initial** residuals of `p Ux Uy k omega`, and `CT` plateau is measured
   separately (`PLATEAU_TOL_REL = 5e-3`). 2500 is therefore sized to be *generous enough
   that a `NOT_CONVERGED` is a finding rather than a truncation*, not sized to be the
   convergence point.

**NAMED RISK, recorded in advance so it is reported as a result if it happens.** The
per-direction refinement between levels is 1.5, and the outer-iteration count a
segregated SIMPLE solve needs to reach a fixed residual scales roughly with linear cell
count [INFERRED, standard segregated-solver behaviour — not measured on this case]. The
**fine** level (774 radial × 261 axial) is therefore the level most at risk of not
reaching `RES_TOL` by 2500. If the fine level returns `NOT_CONVERGED` at 2500 with
residuals still falling monotonically, that outcome is **NOT A RESULT** and is reported
as a **truncation finding** — the honest response is a re-registered successor rung with
a larger cap and its own pre-registration, **never a quiet extension of this `endTime`
after seeing the residuals**. The opposite outcome — residuals stalled above `RES_TOL`
on a flat plateau — is a numerics/model finding and is likewise reported, not fixed by
adding iterations.

**CONSIDERED AND REJECTED: a per-level `endTime` scaled by the 1.5 refinement ratio**
(e.g. 1600 / 2400 / 3600). The grader reads `endTime` per case so it would work
mechanically, and it equalises convergence state rather than iteration count. It is
rejected because it does not fit the §7 cap with a rerun reserved (97.6 core-min for the
triple + 70.5 for a fine rerun = 168 > 150), and because it introduces a degree of
freedom the uniform MRF_R1 precedent does not have. Recorded so the choice is visible,
not silent.

**RANKS: 1 (serial), per level.** These are ~40k–202k-cell axisymmetric wedges; a 16-way
decomposition would leave ~2.5k cells per rank and be communication-bound, and
core-minutes = wall-s × ranks, so serial is the *cheapest* option in the lab's own unit.
No level has a `decomposeParDict` and none is registered. The three levels may run
concurrently (3 cores total) to compress wall time; that does not change core-minutes.

**COST — MEASURED-ANCHORED RATE, and exactly what is being borrowed.**

The rate is **NOT borrowed from M6.** `M6SR_PREREGISTRATION.md:462` registers
**3.40e-8 core-min/cell/iteration**, measured on an ONERA M6 **`rhoSimpleFoam`**
(compressible) run — a different solver, and this registration does not rest on it. A
**SUBOFF-specific rate** is available on disk instead and is used:

> `verification/runs/navier_class/SUBOFF/smoke_coarse` — the §6 exercise smoke, already
> run, `rc=0`, 7,600 cells, `Time = 1 → 50`, 50 `ExecutionTime` lines, last line
> `ExecutionTime = 2.21 s`, serial (no `processor*` directories). Its `system/fvSolution`
> and `system/fvSchemes` are **byte-identical** (`diff` clean, 2026-09-10) to those of
> all three §4a levels, so the rate transfers within one solver configuration.
>
> **Rate = 2.21 s × 1 rank ÷ 60 ÷ (7,600 cells × 50 iterations) = 9.693e-8
> core-min/cell/iteration.** MEASURED on this case family and this exact solver config;
> the derived-not-measured label applies to the *dollars*, not to this rate.

**This rate is a deliberate upper bound and the confidence cost is stated.** It is
2.85× the M6 figure, because a 7,600-cell serial run pays per-iteration fixed costs
(GAMG setup, the `forceCoeffs` function object writing `coefficient.dat` every
iteration, I/O and bookkeeping) over very few cells; per-cell cost normally **falls** as
the mesh grows through this range [INFERRED]. Using it therefore over-estimates the
graded triple, which is the safe direction against a cap whose overrun stops the run.
At the M6 rate the triple would cost 28.2 core-min instead of 80.4 — the spread between
the two rates is the honest width of this estimate.

| item | cells | iterations | ranks | est. core-min | per-level sub-cap |
|---|---|---|---|---|---|
| coarse `reg_coarse` | 39,904 | 2500 | 1 | **9.67** | 15 |
| medium `reg_medium` | 89,784 | 2500 | 1 | **21.76** | 33 |
| fine `reg_fine` | 202,014 | 2500 | 1 | **48.95** | 74 |
| **graded triple** | | | | **80.38** | |
| §6 exercise smoke (coarse mesh, ≤100 it) | 39,904 | 100 | 1 | **0.39** | 2 |
| one rerun allowance (= one FINE level) | 202,014 | 2500 | 1 | **48.95** | 74 |
| **TOTAL against the §7 cap** | | | | **129.72** | **cap 150 (unchanged)** |

Headroom **20.28 core-min (13.5%)**. Derived dollars at the recorded c7a.4xlarge rate
$0.0513/core-h: 129.72/60 × 0.0513 = **$0.111 — DERIVED, NOT MEASURED** (the box cannot
read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5). **§7's 150 core-minute cap is
unchanged and is the binding total**; the per-level sub-caps above are 1.5× the estimate,
rounded up, and are stop-that-level figures in the MRF_R1 pattern — they may individually
sum above the total, and **the total is what stops the rung. An overrun stops the run; it
does not get a new budget.** "One rerun allowance" is registered here as **one rerun of
the fine level**, not a second triple.

**Launcher wall timeouts derive from these sub-caps, shown as arithmetic:**
`wall_s = sub_cap_core_min × 60 ÷ ranks`, ranks = 1 ⇒ coarse `15 × 60 = 900 s`,
medium `33 × 60 = 1980 s`, fine `74 × 60 = 4440 s`.

**PRE-COMPUTE CONDITION for §5a, and how it was checked (rule 2).** Same check as §4a,
same timestamp: none of `reg_coarse`, `reg_medium`, `reg_fine` holds a `0/`, a numeric
time directory, an `rc` sidecar or a `log.simpleFoam`. The run directories that do not
exist are `reg_coarse/0`, `reg_medium/0`, `reg_fine/0`. **No gate, band, threshold,
reference value, `Aref` or cap is altered by §4a or §5a**; they register a length, three
directory names and a cost that §5 and §7 required and did not state.

**Applied to disk 2026-09-10 by `build_suboff.py --set-endtime --dir <level>`**, which
rewrites ONLY the `endTime` and `writeInterval` entries of an already-built
`system/controlDict` and **refuses** on a case holding a numeric time directory or an
`rc` sidecar — the same surgical, no-rebuild path as `--repin-aref`, chosen because a
rebuild would destroy each level's `checkMesh` log and birth certificate.

---

## 6. EXERCISE-SMOKE PLAN (A3FL1 lesson — a real run, not static checks)

Before the graded freeze, and because R1 carries a **new solver config** (first
SUBOFF case in the lab), run a real EXERCISE smoke:

1. Regenerate the analytic hull profile; `blockMesh` the **coarse** wedge; `checkMesh`
   and confirm §3 admissibility (this is the BUILD-BEFORE-FREEZE mesh line, §8.1).
2. Launch `simpleFoam` for **~50–100 iterations** on the coarse level with the R1
   config (kOmegaSST, wall functions, the registered inlet/farfield BCs, the
   forceCoeffs block). **Assert `rc == 0`**, residuals decreasing, no unbounded
   turbulence-field messages, and that `postProcessing/forceCoeffs*/…/coefficient.dat`
   is being written with a parseable `Cd` column.
3. Run `grade_suboff.py --selftest --smoke <coarse-smoke-dir>` so the **planted-zero
   control fires on a real on-disk field** before any graded run.

The smoke is a prerequisite to freeze; a smoke that does not reach `rc==0` blocks the
rung. The smoke run is EXERCISE, not graded, and its `Cd` is sanity-only.

---

## 7. COST (rule 12 — core-minutes; c7a.4xlarge $0.0513/core-h, derived-not-measured)

Compute cap, **frozen**: **150 core-minutes** for the whole rung (coarse + medium +
fine graded triple + the exercise smoke + one rerun allowance). Basis: an axisymmetric
wedge simpleFoam solve to steady convergence is minutes of wall time on 16 ranks;
40k/90k/202.5k cells scale roughly linearly. Derived dollar cost at the recorded rate:
150/60 core-h × $0.0513 = **≈ $0.13, derived not measured** (the box cannot read its
own billing). Well under the $25 pre-authorised tier. **Overrun stops the run; it does
not get a new budget.** Estimate-vs-actual calibration lands in `docs/COST_CALIBRATION.md`
at rung completion (rule 12).

---

## 8. LATER LADDER STEPS (named, not registered here)

- **R2 — bare-hull surface Cp at zero incidence** vs Huang 1992 / Liu & Huang 1998
  (wind-tunnel ⇒ Barlow-Rae-Pope blockage correction applies; distributional gate).
- **R3 — bare-hull at incidence**, AoA/drift sweep → forces & moments → derivatives
  Z_w, M_w and neutral point (Roddy 1990; conventions Gertler & Hagen 1967, Feldman
  1979). This is the **3-D** rung that earns a reference-tier registry entry. Toxopeus
  2008 sets the expected-accuracy band.
- **R4 — wall-resolved (`y⁺ < 1`) re-grade** of D1 for a tighter numerical channel.

---

---

## 11. FREEZE BLOCK — pinned 2026-09-10 by the cfd-supervisor (check-4)

**Grading path, pinned by blob sha (standing rule 2).** Each was verified `disk == HEAD` at the
moment of freezing. Before any grade, re-hash the file and refuse on drift:

| blob sha | path |
|---|---|
| `9ab71b156d395d1e040851c524f0b81bb0e82ae1` | `cases/navier_class/SUBOFF/grade_suboff.py` |
| `dcddfe727ea9b85109f2000ea674add80de256c5` | `cases/navier_class/SUBOFF/build_suboff.py` |
| `ebc0a65f948d5bd47d144cd2ffa82649391f39f8` | `cases/navier_class/SUBOFF/run_suboff_r1_triple.sh` |
| `d893378817c823605c793e849d2800a1f4a28b5a` | `verification/runs/navier_class/SUBOFF/suboff_reference_ReL1p2e7.json` |
| `ca5c9554ea807207c9b9bc3955d0ef9c81ed21b0` | `system/controlDict`, IDENTICAL in all three levels |

That the three `controlDict`s share ONE blob is the mechanical proof of the pinned-`Aref` ruling:
every level normalises on the same `Aref 0.08317033628` and runs the same `endTime 2500`.

**FREEZE PRECONDITIONS, each verified BY ME first-hand, not relayed:**

| precondition | evidence |
|---|---|
| §8.1 build-before-freeze: 3 levels built, `checkMesh`'d, admissible | non-orth **57.405 / 63.602 / 68.706** (< 70), skew 1.654 / 1.900 / 2.123 (< 4), `Mesh OK`, 0 severe faces, 0 neg-vol |
| §4 registered family actually built | 39,904 / 89,784 / 202,014 cells vs target 40k/90k/202.5k (−0.24%), ratio **exactly 2.25000** |
| §4 geometric similarity read back from the mesh | first cell 1.0000e-3 / 6.6667e-4 / 4.4444e-4 m (ratios exactly 1.5000); max AR invariant to **8 s.f.** |
| §5 graded `endTime` registered, `deltaT`=1, no `residualControl` | `endTime 2500; deltaT 1;` verified in all three; builder refuses if `residualControl` present |
| `reference.Aref` pinned, not null | **0.0831703362813915 m²** (sector) = analytic 5.988264212260189 / 72, ratio verified 72.000000000 |
| launcher exists and writes an rc sidecar (§ launcher precondition) | rc capture proven on a **planted failure** and a forced cap-stop, not on success alone |
| run roots registered by name and launch-clean | `reg_coarse` / `reg_medium` / `reg_fine`: no `0/`, no numeric time dir, no `rc`, no `log.simpleFoam`, no `postProcessing/` — a launch ADDS, it does not overwrite |
| grading path present, committed, `disk == HEAD` | all five blobs above |

**WHAT THIS FREEZE DOES NOT CLAIM.** (a) That `endTime 2500` is *enough*: it is defensible on
its stated prior basis and is **not** a prediction that convergence happens by 2500. If the fine
level returns `NOT_CONVERGED` with residuals still falling, that is **`NOT A RESULT` reported as
a truncation finding**, answered by a re-registered successor — **never** by extending this
`endTime` after seeing residuals, which is the precise thing rule 2 forbids. (b) That the cost
estimate is tight: the 80.38 core-min triple rests on a deliberately conservative
within-configuration rate (9.693e-8 core-min/cell/iteration, measured on `smoke_coarse`, whose
`fvSolution`/`fvSchemes` are byte-identical to the graded levels); at the M6 rate the triple
would be 28.2 core-min, and **that spread is the honest width of the estimate**. (c) That D1 is
experiment-validated: the CT anchor 3.6e-3 remains a **MANIFEST / engineering** value
(ITTC-1957 + form factor), so this rung is **CODE-VERIFIED / BOUNDED-AGREEMENT**, not validation,
and stays so until a title-verified SUBOFF report lands.

**LAUNCH AUTHORISED** by the cfd-supervisor under this freeze, via the queue (the detached runner
schedules against box occupancy; this rung is **not** hand-launched). Whole-rung cost 129.72
core-min against the frozen **150** cap — overrun stops the run and does not get a new budget.

*Results, when they exist, land in `verification/campaign/SUBOFF_R1_RESULTS.md` citing this file
by commit hash. This file is now FROZEN: it is never edited, only appended to as dated addenda.*
