# COVERAGE_ROWS — ansys-verification team's feed to the lab coverage matrix

**NOT FILED ANYWHERE. Nothing in this document leaves this box** (CLAUDE.md rules 7,
8). The manual is proprietary Ansys documentation. **SUBMISSIONS PARKED.**

**Zero compute.** This is a reading of committed artifacts (register HEAD blob, the
RESULTS records, the grading JSONs). No solver was started to produce it.

**What this file is, and is not.** `docs/COVERAGE_MATRIX.md` is **owned by the
verification team**, not by this team. This file is **our FEED to it** — draft rows
for the three cases this team has actually run, each scored on the matrix's three
columns and tiered with the matrix's five words, with the number and file path that
earns every claim. This lane does **not** edit `docs/COVERAGE_MATRIX.md`.

**Caveat carried at the top, as instructed.** CONSOLIDATION WEEK and the three-column
/ five-word scoring scheme reach this team as the **chief's own reconstruction of
Sanaa's instruction, NOT her verbatim words.** It is recorded and acted on as a
reconstruction, and is labelled as such wherever this team writes it. Nothing here is
a scoring-call authorisation (reserved to Sanaa, CLAUDE.md).

Drafted by `ansys-lane-opus48` (running as `claude-opus-4-8[1m]`) for the
`ansys-verification-supervisor`, 2026-08-25. Tiers on rows #1–#3 are the supervisor's
ruling of 2026-08-24 (VMFL001-R2 = HOLDS, VMFL005 = GATE REACHED, VMFL001 run 1 =
NOT HELD), applied here with the earning numbers verified from the artifacts.

---

## The scoring scheme (as relayed)

- **V** — code verification: `exact` / `manufactured` / `correlation`.
- **G** — a CONVERGING Roache triple + GCI + an observed order.
- **P** — validation against a public primary source, with a pre-registration on disk.
- **Tier**, exactly one of: **HOLDS / GATE REACHED / SURVEYED / NOT HELD / NEVER RUN**.

---

## LEAD FINDING — a small GCI does NOT license the V column (N-AV7)

**Read this before scoring any V column from a GCI, on any team.** This team has run
two cases that are, on their face, identical strength: both `PASS`, both grid triples
`CONVERGING`, both observed order p ≈ 2, both GCI_fine ≈ 0.05 %. They score
**differently** on the coverage matrix, and the reason is the single most transferable
thing this team currently has to give consolidation week:

- **VMFL001-R2** — Richardson extrapolation of the converging triple lands on the
  exact analytic value (White §3-2.3) to **3.7 ppm**, without the solver ever seeing
  the closed form (`docs/NUMERICS_KNOWLEDGE.md` N-AV6). The code demonstrably
  converges to the exact solution as h → 0. **The V column is real.**
- **VMFL005** — the same machinery gives a clean `CONVERGING` triple at p = 1.9341,
  GCI_fine 0.0502 %, and the grid sequence extrapolates to **10.2951 Pa, not to the
  exact 10.24 Pa**. The extrapolate is **0.5383 %** from exact — *further* from the
  analytic value than the finest grid (0.4979 %). The deviation from the reference is
  **9.92×** the fine-grid discretisation uncertainty. About **90 %** of the residual
  deviation is **not** discretisation error; grid refinement does not close it.

**A team scoring the V column from GCI alone would score VMFL005 `HOLDS` and be
wrong.** A small GCI is a statement about **grid convergence only** — that the answer
has stopped moving with mesh. It does **not** license the claim that the remaining
deviation from a reference is numerical, nor that the code converges to the *exact*
solution. That claim needs the extrapolate to land on the reference (VMFL001-R2), and
here it is measured **not** to (VMFL005). This is recorded as N-AV7 in the VMFL005
record and is a warning to every other team scoring a V column off a small GCI.

---

## The rows

| # | Case (manual p.) | V | G | P | **Tier** | The number that earns the tier |
|---|---|---|---|---|---|---|
| 1 | VMFL001 run 1 (pp. 15–16) | `exact` target (F. M. White, *Viscous Fluid Flow* §3-2.3) — **but not verified**: the run produced no number | **none** — no triple; L3 not iteratively converged | frozen prereg on disk — **but no PASS** | **NOT HELD** | L3 final Ux/Uy initial residual **1.19876e-06** vs frozen **< 1e-6**, and plateau ptp **2.77178e-05 m/s** vs **< 1e-6** → `NOT A RESULT` under CLAUDE.md rule 5 step 1; comparator also refused (exit 2) on a reader/writer filename mismatch. `NOT A RESULT`, so no column is earned |
| 2 | VMFL001-R2 (pp. 15–16) | `exact` — White §3-2.3, and the code **converges to it** (Richardson extrapolate 3.7 ppm from exact, N-AV6) | **CONVERGING** — v_θ(35 mm), ratio 2.0, p = **2.0102**, GCI_fine = **0.0563 %**, monotone | frozen prereg on disk, before compute; PASS at all four radii inside 2 % | **HOLDS** | Extrapolate **0.004547826544889741 m/s** vs exact **0.00454781** → **3.7 ppm**; GCI_fine **5.63283924506965e-04** = 0.0563 %; four-radii deviations vs the manual 0.0803 / 0.2742 / 0.2285 / 1.1787 %, all inside frozen 2 % |
| 3 | VMFL005 (p. 25) | `exact` target (Hagen–Poiseuille) — **but the code is measured NOT to converge to it** | **CONVERGING** — dP, ratio 2.0, p = **1.9341**, GCI_fine = **0.0502 %**, monotone, planted-zero fired | frozen prereg on disk, before compute; PASS at 0.4979 % inside 2 % | **GATE REACHED** | deviation/GCI = **9.92**; Richardson extrapolate **10.29511921046 Pa** is **0.5383 %** from exact 10.24 Pa — *further* than the fine grid's 0.4979 %. The gate is genuinely met and stays a credential; the exact-solution limb is measured not to close |

**Column detail and provenance:**

**Row 1 — VMFL001 run 1 — `NOT HELD`.**
- V: the manual's target is `exact` — F. M. White, *Viscous Fluid Flow* §3-2.3
  (analytical), reprinted in the manual's "Target, m/s" column, **manual pp. 15–16**.
  The target *type* is exact, but this row **verifies nothing** because the run
  produced `NOT A RESULT`.
- G: no triple. L1/L2 converged (Ux 4.69e-14 / 1.49e-12) but **L3 did not** (final
  Ux/Uy 1.19876e-06 vs frozen < 1e-6; plateau ptp 2.77178e-05 vs < 1e-6), so under
  CLAUDE.md rule 5 step 1 the rung is `NOT A RESULT` before a triple is even
  classified. Independently the frozen comparator refused (exit 2): it expected
  `U_gateAxis.*` with a header, v2606 wrote header-less `gateAxis_p_U.xy` (N-AV4).
- P: prereg frozen and committed before compute (blob `d6ea5de9…` as amended and as
  it ran; original freeze `e0afc259…`, commit `ffeed580`) — but there is no `PASS` to
  validate.
- **Tier NOT HELD.** A run that returned `NOT A RESULT`; it stays in the register
  honestly as row #1. Artifacts: `cases/ansys_verification/VMFL001/RESULTS.md`;
  `verification/runs/ansys_verification/VMFL001/` (committed `ae30f914`).

**Row 2 — VMFL001-R2 — `HOLDS`.**
- V: `exact`. White §3-2.3, and — decisively — the code is measured to converge to
  the exact value: the CONVERGING triple's Richardson extrapolate is
  `0.004547826544889741` m/s against the exact `0.00454781`, i.e. **3.7 ppm**, with
  the formula never given to the solver (N-AV6).
- G: **CONVERGING**. Roache triple on v_θ(35 mm), ratio 2.0, Fs 1.25: R =
  `0.2482365981669591`, p = `2.010212263457908`, GCI_fine = `5.63283924506965e-04`
  (0.0563 %); f_coarse/med/fine `0.00451458402376` / `0.00453957453453` /
  `0.00454577809391` — monotone, GCI quotable. **Verified from**
  `verification/runs/ansys_verification/VMFL001/R2/GRADING_VMFL001_R2.json`.
- P: prereg blob `c6b4a7c4fd09d2286a30440f5090116a7dae0eea`, commit `4507fc66`,
  frozen before compute and re-read by the run script at launch; PASS — four-radii
  deviations 0.0803 / 0.2742 / 0.2285 / 1.1787 % vs the manual, all inside frozen
  2 %. Reference is the manual's printed analytical target (public-primary judgement
  flagged below).
- **Tier HOLDS.** V exact and converged-to (3.7 ppm), G converging at p = 2.01, P
  frozen prereg on disk with a PASS. Artifacts:
  `cases/ansys_verification/VMFL001/R2/RESULTS.md`;
  `verification/runs/ansys_verification/VMFL001/R2/` (committed `fd2321ef`).

**Row 3 — VMFL005 — `GATE REACHED`.**
- V: the manual's target is `exact` (Hagen–Poiseuille, 8·μ·L·V_avg/R² = 10.240000 Pa,
  cross-checked via 8·μ·L·Q/(πR⁴); White, *Fluid Mechanics* 3rd ed., **manual p. 25**).
  **But the code is measured NOT to converge to it** — the grid sequence extrapolates
  to 10.2951 Pa, and 10.2951 is 0.5383 % from 10.24, so the exact-solution limb does
  not close. V is *not* earned as "converges to exact".
- G: **CONVERGING — earned outright.** Roache triple on dP, ratio 2.0, Fs 1.25: R =
  `0.26169092088`, p = `1.9340642225610707`, GCI_fine = `5.021172780104668e-04`
  (0.0502 %); f_coarse/med/fine `10.23475565622` / `10.27932261636` / `10.2909853852`
  — monotone, GCI quotable; planted-zero fired (planted 1.234, read_back_delta 1.234).
  **Verified from** `verification/runs/ansys_verification/VMFL005/GRADING_VMFL005.json`.
- P: prereg blob `43aaf6bf5c5f1189495e1460e5de415e56860447`, commit `2d54a629`, frozen
  `2026-08-24T18:42:07Z` — **before** the first run artifact (18:45:32Z, 3 min 25 s
  later); PASS at 0.4979 % inside frozen 2 % (factor 4.0 of margin). Public-primary
  judgement flagged below.
- **Tier GATE REACHED.** The `PASS` is real, defensible and stays a credential — a
  frozen 2 % gate met at 0.4979 % with a converging triple. It is **not** HOLDS
  because the exact-solution limb is measured not to close: deviation/GCI = **9.92**
  and the Richardson extrapolate is **0.5383 %** from exact, further than the finest
  grid. Artifacts: `cases/ansys_verification/VMFL005/RESULTS.md`;
  `verification/runs/ansys_verification/VMFL005/` (committed `90ee8d80`).

---

## VMFL005's answer to the chief's explicit question

**Does VMFL005 have its own converging Roache triple? — YES.** Verified this session
directly from `verification/runs/ansys_verification/VMFL005/GRADING_VMFL005.json`:
`triple.state = CONVERGING`, `triple.ratio = 2.0`, `triple.p = 1.9340642225610707`,
`triple.gci_fine = 5.021172780104668e-04`, `triple.R = 0.26169092088`, f_coarse <
f_med < f_fine (monotone), and `planted_zero.passed = True`. VMFL005 earns the **G**
column outright.

**Why VMFL005 is still `GATE REACHED`, not `HOLDS`, and what it would take to lift
it.** The brief's contingency ("if VMFL005 lacks a converging triple, state which
extra grid levels would lift it") does **not** apply — it does not lack one. The block
on HOLDS is **not** grid resolution and **cannot be fixed by more grid levels**: the
triple already extrapolates cleanly at second order, and it extrapolates to 10.2951 Pa
(0.5383 % from exact), *away* from 10.24. Adding L4/L5 would tighten the GCI further
and move the extrapolate no closer to the reference — it would sharpen, not close, the
finding. Lifting VMFL005 to HOLDS requires removing the ~90 % **modelling/setup**
residual, not discretisation error. The one arithmetically-checkable candidate is
quantified in the next section; the mechanism as a whole is unresolved and is not
claimed (docket-tracked; see the D510 citation note below). **No grid spend is
recommended for VMFL005** — it would buy a smaller GCI and the same gap.

---

## The planar-wedge geometry candidate — checked arithmetically, no solve (supervisor instruction 1)

VMFL005's RESULTS §5.3 lists candidate mechanisms and correctly refuses to assert
one. Candidate 2 — the planar-wedge geometry — is arithmetically checkable **without
any solve**, and it bears on **every future axisymmetric case this team runs**, so it
is checked here.

An OpenFOAM axisymmetric wedge cell is a **flat-sided triangle**, not a circular
sector. For total included angle `t`, the triangle cross-section area is
`½ R² sin(t)` against the true sector's `½ R² t`, so the modelled cross-section is
short by the factor **sin(t)/t**. Read from the case (`constant/polyMesh/boundary`:
`wedge1`/`wedge2` both `type wedge`; half-angle 2.5°, total t = 5°):

- `t = 5° = 0.08726646259971647 rad`; `sin(t) = 0.08715574274765817`.
- **`sin(t)/t = 0.9987312439537492`** → area deficit **0.1268756 %**.
- Modelled patch area `½ R² sin(t) = 6.809042402160794e-08 m²`, matching the L3 inlet
  monitor's own header (`6.809042402188e-08 m²`) to eleven significant figures — so
  the deficit is a property of the *actual mesh that ran*, not an assumption.
- True sector area `½ R² t = 6.81769239060285e-08 m²`.

**Effect on dP.** Under the supervisor's stated model — Poiseuille at fixed
volumetric flow, dP ∝ R⁻⁴, an effective-area deficit read as an effective-radius
deficit `√(sin t/t)` — the dP inflation is `(sin t/t)⁻²`:

- **dP high by `(0.9987312439537492)⁻² − 1 = +0.2542349500671337 %`.**
- Against the measured deviation **0.49790415 %**, this is **51.06 %** — **near
  half**, and it is reported as near half, **not** rounded up into "the mechanism is
  explained."

**Honesty on the model, so the arithmetic does not over-claim.** The VMFL005 inlet
imposes the velocity *profile* pointwise (fixed V_avg), and the wall is at the exact
radius R; the deficit is in the azimuthal area metric, not in R. A fixed-V_avg reading
(dP ∝ R⁻² → inflation `(sin t/t)⁻¹`) gives **+0.1270 %**, i.e. **25.51 %** of the
deviation. So the wedge-geometry candidate accounts for **somewhere between ~a quarter
and ~a half** of the 0.4979 %, depending on which invariant the effective-radius
heuristic is anchored to. **In either reading it is a substantial but partial
contributor and does not close the gap.** It remains a candidate; the docket keeps the
question. This is the source of the numerics candidate drafted in `RECORDS_DRAFTS.md`.

---

## FLAG TO THE SUPERVISOR — the P column and "public primary" (a judgement, not decided here)

The scheme's **P** column asks for "validation against a **public primary source**".
The Ansys manual is a **published primary for the reference VALUE**, but it is
**proprietary vendor documentation, not open literature**. This affects how P should
read, and the judgement is flagged rather than made here (a scoring convention is the
supervisor's / verification team's to set, not this lane's):

- For **VMFL001** and **VMFL005**, the reference is **not internal to Ansys** — it is
  a **public textbook** (F. M. White, *Viscous Fluid Flow* §3-2.3; *Fluid Mechanics*
  3rd ed., Hagen–Poiseuille). This lab **re-derived both closed forms independently**
  (VMFL005's two algebraic forms cross-checked to 10.240000 Pa; VMFL001's exact v_θ(r)
  evaluated directly, N-AV2/N-AV3). So for these two rows the P reference is a genuine
  **public primary** (White), and the manual is only the transcription — P is on firm
  ground for both.
- The distinction that **does** bite is for future cases whose **only** reference is
  the manual's own `NUM`/benchmark number with no public-literature source behind it
  (CASE_MAP marks 19 such). There, P would rest on **proprietary vendor documentation
  alone**, which is a weaker P than a public primary. **Recommend** the matrix
  distinguish "P against a public primary the lab re-derived" (VMFL001/005) from "P
  against the manual's own internal number" (future NUM cases) — but this is your call
  and Sanaa's, not this lane's.

---

## Summary for relay

| Row | Tier | Earning number |
|---|---|---|
| VMFL001 run 1 | **NOT HELD** | `NOT A RESULT` — L3 residual 1.19876e-06 vs < 1e-6 |
| VMFL001-R2 | **HOLDS** | Richardson extrapolate 3.7 ppm from exact; p = 2.0102, GCI 0.0563 % |
| VMFL005 | **GATE REACHED** | PASS 0.4979 % inside 2 %, but deviation/GCI = 9.92, extrapolate 0.5383 % from exact |

VMFL005 has its own converging triple: **YES**. Wedge-geometry candidate: **~a
quarter to ~half** of the deviation (0.2542 % / 51 % under fixed-Q; 0.1270 % / 26 %
under fixed-V_avg) — does not close it.

---

## CAUSE CLASS — dated companion block, appended 2026-08-31 (Sanaa's GRADING TRANSPARENCY ORDER, item 2)

**Lines whose number changed above this section: 0** (append-only at the foot; the 237
lines above are a byte-for-byte prefix, pre-append SHA-256
`f0a7fe3f8349c58f60815f7410ff6c3f966a962cd063c8b068a8f0f136100b1e`).

**Authority & mechanics.** Sanaa's order `4116024a`
(`etc/sessions/2026-08-31T2055Z_sanaa_grading_transparency_order.md`), read at source
(rule 9). Class set, precedence and format are **verification's**, not this team's:
`VERIFICATION_CHARTER` §2n.1 (the closed eight, her verbatim text), **§2n.3 (precedence:
assign the LOWEST-NUMBERED class the grading record supports — `1 BUDGET/KILL` … `8
PHYSICS-FAIL` — you may not claim a physics cause until every referee cause is
excluded)**, §2n.4 (`UNCLASSED` is fail-closed, not a ninth class, never physics-adverse),
§2n.5 (headline split), **§2n.10/§2n.11 (the class lands as this APPENDED companion block
keyed by row id in the schema below — NOT a 14th register column, which would edit all 51
landed rows; this file is ansys's contribution file; `COVERAGE_MATRIX.md` carries the
census only)**, §2n.14/§2n.15 (`6fcc7fb6`: `GATE-DESIGN` joins the capability-exclusion
list). **Zero compute — a reading of committed records, no re-runs** (§2n.7). Row ids are
**references** into `ANSYS_VALIDATION_REGISTER.md` (never double-counted). "REGISTER L*n*"
below = `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` at that line, whose
verdict cell carries the grading record's own words and cites its artifacts.

**Row-count reconciliation (read cell-by-cell from each row's own verdict cell, never a
file-wide grep — a naive grep over backticked verdict words returns ~88 PASS from prose
and is nonsense).** 51 rows, ids 1–51 no gaps (43 in `**N**` form, 8 in `**#N**` form; the
five-column `#1`–`#4` at register L193–196 are the tier cross-reference table, told from
rows by COLUMN COUNT, and excluded): **PASS 10 · NOT A RESULT 28 · GATE REACHED 8 · GATE
FAIL 3 · BLOCKED 1 · PENDING 1 = 51 ✓**. Non-`PASS` = **41** (PASS carries no class, §2n.8).

| row | case | verdict (rule 1, unchanged) | CAUSE CLASS | citation resolving at HEAD |
|---|---|---|---|---|
| 1 | VMFL001 | `NOT A RESULT` | `INSTRUMENT` | REGISTER L24 — frozen comparator refused (exit 2): frozen to read `U_gateAxis.*`+header, v2606 writes header-less `gateAxis_p_U.xy`; reader defect, physics unjudged |
| 4 | VMFL051 | `NOT A RESULT` | `GATE-DESIGN` | REGISTER L27 — gate value inside band 2.14×, but rule-5 step-1 plateau clause disqualifies (L1&L2 fail); the registered plateau clause, not the solve |
| 5 | VMFL045 (run 1) | `NOT A RESULT` | `UNCLASSED` | REGISTER L28 — `rhoCentralFoam` crashed on 1st timestep (missing `e` energy-solver entry inherited from inviscid VMFL051); a fatal case-config crash, no gradeable answer, fits none of the eight (not a cap/external death, not a referee defect). Row 7 (`PASS`) carries VMFL045's capability |
| 6 | VMFL003 (run 1) | `NOT A RESULT` | `GATE-DESIGN` | REGISTER L29 — comparator applied rule 5; all levels miss the frozen residual floor (<1e-8) while Δp is plateaued; the registered residual clause is the disqualifier |
| 8 | VMFL007 (run 1) | `NOT A RESULT` | `UNCLASSED` | REGISTER L32 — case DIVERGED (p→9.45e144; L2 SIGFPE at iter 9065); solver-internal divergence, no cap/external death, no gradeable number; fits none of the eight |
| 9 | VMFL003-M2 arm A | `NOT A RESULT` | `GATE-DESIGN` | REGISTER L34 — same residual-floor clause; `gate_verdict_before_rule5=GATE FAIL` turned `NOT A RESULT` by rule 5 |
| 10 | VMFL003-M2 arm B | `NOT A RESULT` | `GATE-DESIGN` | REGISTER L36 — same residual clause. Prose (§2n.3): a latent physics signal (realizableKE Δp −6.95% vs Colebrook) is present but ranks class 7 `MODEL-LIMIT`; precedence takes 5 |
| 11 | VMFL003-M2 arm C | `NOT A RESULT` | `BUDGET/KILL` | REGISTER L37 — `PER_ARM_CAP=40` core-min fired (39.93/40), no `End` line, rule 4 fails; run did not finish |
| 12 | VMFL003-M2 arm D | `NOT A RESULT` | `BUDGET/KILL` | REGISTER L38 — cap fired to the second (rc=124, 39.99/40) |
| 14 | VMFL010 | `NOT A RESULT` | `GATE-DESIGN` | REGISTER L40 — Roache triple `OSCILLATORY` (rule 5 step 2); value 0.26% from ref but the refinement/triple cannot grade the flow-split quantity |
| 16 | VMFL059 | `NOT A RESULT` | `GATE-DESIGN` | REGISTER L42 — `rightWall` triple `EXACT` (378/378/378): mis-specified gate quantity pinned to a BC value; clean solve at all levels |
| 17 | VMFL022 | `NOT A RESULT` | `GATE-DESIGN` | REGISTER L43 — Roache triple `OSCILLATORY`; cavitation onset mesh-dependent (L1 stayed single-phase) so the triple crosses a regime boundary and cannot grade |
| 18 | VMFL021 | `NOT A RESULT` | `NAMING/PLUMBING` | REGISTER L44 — L3 killed by a run-dir collision (a rival lane dispatched onto the same case; ruled `docs/ansys_verification/VMFL021_022_COLLISION_RULING.md`). Precedence 2 over the also-present `writeInterval`>`endTime` no-field-written defect (class 3 `BOOKKEEPING`), narrated here in prose |
| 19 | VMFL017 | `PENDING` | `UNCLASSED` | REGISTER L45 — registered instrument `rhoSimpleFoam` diverges (`Negative initial temperature T0` at shock); solver-internal divergence, no fitting class; superseded by row 32 |
| 20 | VMFL036 | `GATE REACHED` | `REFERENT-CEILING` | REGISTER L433 — arm A Cd inside the registered Schiller–Naumann band; empirical-correlation reference caps the tier at `GATE REACHED` |
| 21 | VMFL033 | `NOT A RESULT` | `GATE-DESIGN` | REGISTER L460 — two levels not plateaued + Roache `OSCILLATORY` (R=−398.5); the registered settling clause refuses, named before compute |
| 22 | VMFL023 | `GATE REACHED` | `REFERENT-CEILING` | REGISTER L461 — St inside band, triple `CONVERGING`; experimental St–Re correlation caps the tier |
| 23 | VMFL021-R2 | `GATE REACHED` | `REFERENT-CEILING` | REGISTER L462 — Cd inside band, `CONVERGING`; Nurick (1976) experimental reference caps the tier |
| 24 | VMFL002 | `GATE REACHED` | `REFERENT-CEILING` | REGISTER L463 — dP & outlet-T inside band, both triples `CONVERGING`; textbook/correlation reference caps the tier |
| 25 | VMFL004 | `NOT A RESULT` | `INSTRUMENT` | REGISTER L464 — inherited iterative-convergence check (Uy/p<1e-7) mis-applied to a 1-D fully-developed flow (normalization noise); comparator defect; gate value is a textbook PASS |
| 26 | VMFL011 | `NOT A RESULT` | `INSTRUMENT` | REGISTER L465 — comparator refused (exit 2) on a mis-calibrated planted-zero control (single-point plant diluted ~1/√N by an averaging RMS reader) |
| 27 | VMFL076 | `NOT A RESULT` | `GATE-DESIGN` | REGISTER L466 — both gates met but rule 5 step 2 `OSCILLATORY` triple; family refined past its own asymptotic range |
| 29 | VMFL064 | `NOT A RESULT` | `INSTRUMENT` | REGISTER L468 — reader defect: took FIRST wall-shear sign change, refused when the profile did not start negative ("no reattachment found"); all levels ran clean |
| 30 | VMFL064-R2 | `GATE REACHED` | `REFERENT-CEILING` | REGISTER L513 — reader fixed (LAST crossing in window); LR/s inside band; experimental reattachment reference caps the tier |
| 31 | VMFL011-R2 | `NOT A RESULT` | `INSTRUMENT` | REGISTER L549 — same planted-zero mis-calibration as row 26 |
| 32 | VMFL017-R2 | `NOT A RESULT` | `BUDGET/KILL` | REGISTER L574 — registered per-level cap fired (rc=124); run did not finish |
| 33 | VMFLGPU001 | `NOT A RESULT` | `INSTRUMENT` | REGISTER L595 — null-range plateau guard refused a demonstrably-live channel (a dead field and a converged one look identical to the tolerance); guard defect, repaired in row 39 |
| 34 | VMFLGPU002 | `NOT A RESULT` | `GATE-DESIGN` | REGISTER L605 — GPU grid triple `OSCILLATORY` (R=−0.197); rule 5 step 2 |
| 35 | VMFL076-R2 | `GATE REACHED` | `REFERENT-CEILING` | REGISTER L609 — both gates met on a `CONVERGING` triple (repair of row 27); reference caps the tier |
| 36 | VMFL011-R3 | `GATE FAIL` | `PHYSICS-FAIL` | REGISTER L611 — `rms_vs_benchmark`=0.03409 vs 0.030 (+13.6%) at L3 on a `CONVERGING` triple whose GCI (~3.3%, row 38) is ≪ the miss; proven instrument (planted controls seen; GPU≡CPU to 12 digits); byte-identical gate (empty 77-line diff), prereg predicted the fail. The converged laminar triangular-cavity solution genuinely misses the Jyotsna–Vanka benchmark |
| 37 | VMFL007-R2 | `NOT A RESULT` | `INSTRUMENT` | REGISTER L613 — comparator refused (exit 2) on its planted-zero control (linear-solver/preconditioner screening slate; gate not applied) |
| 38 | VMFLGPU003 | `GATE FAIL` | `PHYSICS-FAIL` | REGISTER L615 — same physics as row 36 (GPU path): rms +13.6% at L3, `CONVERGING` (GCI 3.303% ≪ miss), limb A GPU verified, limb B GPU≡CPU 4.6e-12 |
| 39 | VMFLGPU001-R2 | `GATE REACHED` | `REFERENT-CEILING` | REGISTER L616 — both limbs held, `CONVERGING` (repair of row 33); Taylor–Couette exact-theory reference → `GATE REACHED` max |
| 40 | VMFLGPU007 | `NOT A RESULT` | `GATE-DESIGN` | REGISTER L624 — plateau clause IG3 refuses: wall-T channel still travelling at endTime (ptp 0.0238K > 0.0001K, monotone 238→36×); registered endTime/plateau spec inadequate for a slow-settling channel |
| 41 | VMFLGPU004 | `BLOCKED` | `REFERENT-CEILING` | REGISTER L626 — the manual's `Reference` cell is genuinely empty (read from PDF pp.233–234 under rule 15): the reference is not obtainable. Driving inputs also absent, narrated in prose |
| 42 | VMFLGPU005 | `NOT A RESULT` | `GATE-DESIGN` | REGISTER L628 — comparator GRADED (exit 0); rule 5 disqualified 4 of 7 channels (C1/C2 triples); limb B GPU verified. Prose: latent turbulent-cavity model context (declared modelling difference) ranks class 7; precedence takes 5 |
| 43 | VMFLGPU007-R2 | `GATE REACHED` | `REFERENT-CEILING` | REGISTER L662 — comparator GRADED, both gates met (repair of row 40); reference caps the tier |
| #44 | VMFL063 | `GATE FAIL` | `GATE-DESIGN` | REGISTER L725 — limb A LR/2t=5.60 vs 4.0 (+40%) at L3, but the triple's `GCI_fine`=120.62% (p=0.143) EXCEEDS the 40% deviation, so the miss cannot be attributed to physics vs under-resolution; the registered triple (P_MIN=0.05, no GCI ceiling) graded an unconverged result → ungradeable-as-registered. NOT `PHYSICS-FAIL` (fail-closed, §2n.3) — JUDGMENT, see note B |
| #45 | VMFL069 | `NOT A RESULT` | `UNCLASSED` | REGISTER L726 — solver died of SIGFPE at step 69 (rc=136); solver-internal crash (deltaT=1s in `interFoam`, a setup/numerics config), no gradeable answer, fits none of the eight |
| #47 | VMFL038 | `NOT A RESULT` | `GATE-DESIGN` | REGISTER L728 — triple `DIVERGENT` (R=9.05) on an ANISOTROPIC y-only refinement that violates the Richardson/Roache premise; gate quantity τ_w pinned by a discrete conservation identity — Sanaa's canonical `GATE-DESIGN` example |
| #49 | VMFL006 | `NOT A RESULT` | `GATE-DESIGN` | REGISTER L758 — jointly-unsatisfiable convergence clause: L1/L2 T-residual flat at the machine floor tripping a null-range refusal, L3 still descending (window max 6.18e-8 > 1e-9 floor) at endTime; no level satisfies both limbs; physics clean (every L3 station 10.9× inside band) |

### Census (this file's rows only; verification folds it into `COVERAGE_MATRIX.md`)

| class (precedence #) | count | rows |
|---|---|---|
| `BUDGET/KILL` (1) | 3 | 11, 12, 32 |
| `NAMING/PLUMBING` (2) | 1 | 18 |
| `BOOKKEEPING` (3) | 0 | — (row 18's bookkeeping defect subsumed under NAMING by precedence) |
| `INSTRUMENT` (4) | 7 | 1, 25, 26, 29, 31, 33, 37 |
| `GATE-DESIGN` (5) | 15 | 4, 6, 9, 10, 14, 16, 17, 21, 27, 34, 40, 42, #44, #47, #49 |
| `REFERENT-CEILING` (6) | 9 | 20, 22, 23, 24, 30, 35, 39, 41, 43 |
| `MODEL-LIMIT` (7) | 0 | — |
| `PHYSICS-FAIL` (8) | 2 | 36, 38 |
| `UNCLASSED` | 4 | 5, 8, 19, #45 |
| **total non-`PASS`** | **41** | (PASS: 10 rows carry no class — 2, 3, 7, 13, 15, 28, #46, #48, #50, #51) |

### Headline split (§2n.5)

**2 physics-adverse (`PHYSICS-FAIL`: #36 VMFL011-R3, #38 VMFLGPU003 — one physics, the
laminar triangular-cavity benchmark miss on CPU + GPU; `MODEL-LIMIT`: none) / 35
non-physics (`GATE-DESIGN` 15, `REFERENT-CEILING` 9, `INSTRUMENT` 7, `BUDGET/KILL` 3,
`NAMING/PLUMBING` 1, `BOOKKEEPING` 0) / `UNCLASSED` 4 (#5, #8, #19, #45).**

### Notes and findings

- **Note A — the two verified indications.** #49 → `GATE-DESIGN` and #47 → `GATE-DESIGN`
  were checked against their own records and confirmed (see table). #47 is Sanaa's own
  τ_w-conservation-identity example. **VMFL070 has NO register row** (grep of the register:
  zero hits) — so there is nothing to backfill and no class to assign; if it was retired it
  never landed as a credential.
- **Note B — #44 is the one genuine judgment call, flagged for overrule.** Its record labels
  it `GATE FAIL` (LR/2t +40%). I did **not** class it `PHYSICS-FAIL` because its own triple
  reports `GCI_fine`=120.62%, i.e. the numerical uncertainty EXCEEDS the 40% discrepancy —
  by Roache's own principle a physics attribution is unsupportable, and §2n.3 fail-closes
  away from physics. Classed `GATE-DESIGN` (the registered triple graded an unconverged
  result). Contrast rows 36/38, where GCI ~3.3% ≪ the 13.6% miss, which is what makes those
  a clean `PHYSICS-FAIL`. If Sanaa reads #44 as a physics failure the count becomes 3.
- **Note C — the `UNCLASSED` finding (§2n.7 expects some; a zero-`UNCLASSED` backfill should
  be disbelieved).** All 4 `UNCLASSED` rows share one gap: a run that produced **no gradeable
  answer** because the **solver crashed or diverged** (#8, #19 divergence; #5, #45 fatal
  crash) — which is neither a cap/external death (`BUDGET/KILL`'s verbatim definition) nor a
  referee defect. **The closed eight has no bucket for solver-internal divergence/crash.**
  Reported as a finding to verification/Sanaa: either widen `BUDGET/KILL` ("run did not
  finish" already its §2n.3 rationale) or add a class. These 4 are fail-closed OUT of
  physics-adverse and are the third headline figure.
- **Note D — capability (§2n.6, exclusions now 4 incl. `GATE-DESIGN`, `6fcc7fb6`).** Of the 41
  non-`PASS` rows, only rows 36/38 (`PHYSICS-FAIL`) bear on "can the lab do this physics";
  every other non-`PASS` row is referee trouble or `UNCLASSED`. `PASS`/`GATE REACHED` rows
  answer the capability question and are unaffected by this block.

Drafted by `ansys-lane-opus48` (`claude-opus-4-8[1m]`) for the
`ansys-verification-supervisor`, 2026-08-31. Classes are the grading records' assignments
read cell-by-cell (§2n.2), not recollection; the supervisor's read and verification's audit
govern. Overrulable.
