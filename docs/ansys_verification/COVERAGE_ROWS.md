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
