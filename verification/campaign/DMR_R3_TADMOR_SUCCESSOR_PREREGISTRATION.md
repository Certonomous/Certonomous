# DMR TADMOR-FLUX SUCCESSOR — a new numerics family — PRE-REGISTRATION

> **STATUS: NOT AUTHORISED — NOT FROZEN — NO CHECK-4 TAKEN — NO COMPUTE LAUNCHED.**
> Authored to completion by cfd `lab-lane`, 2026-09-07, from the DRAFT skeleton
> `DMR_R3_TADMOR_SUCCESSOR_PREREGISTRATION_DRAFT.md` and the lever analysis
> `DMR_R3_NUMERICS_ROBUSTNESS_LEVER_ANALYSIS.md`. The generator, both drivers and
> the STEP-0 reader are now ON DISK and self-tested (§9); the reused grader identity
> is confirmed on disk. **This becomes a frozen pre-registration only when the cfd
> supervisor takes check-1 (STEP-0 reader) and check-4 (generator/driver/prereg
> gates) PERSONALLY and freezes it by sha — none of which has happened here.** Gate
> V' tol 0.0231 and all bands are held BYTE-IDENTICAL to the parent; only the flux
> scheme changes. Heeds L-501: STEP 0 (§1a) MEASURES the failing field/site
> answer-blind; a crash of this family is a MEASURED negative result, never a
> capability inference from one/two SIGFPEs.

---

## 0. §2ay classification

Parent of THIS successor: the **DMR positivity successor** (freeze `08efee1a`,
`DMR_R3_POSITIVITY_SUCCESSOR_PREREGISTRATION.md`), verdict **NOT A RESULT** — R1p
(1/60) and R2p (1/120) graded **Gate V' PASS** (position errors 0.01082 → 0.006081
vs tol 0.0231, converging), **R3p (1/240) SIGFPE rc=136** in `Foam::sqrt(...)` at
t = 0.11648 of 0.2 (58 %) inside the `rhoCentralFoam` solve, triple therefore
incomplete. That successor had **already** applied Minmod reconstruction + maxCo 0.1;
both were live in the crash. This is **not** a capability gap (state a): the mechanism
is a reconstructed-state / updated-energy excursion into a negative temperature at the
flux level, and a **more diffusive but still-available in-solver flux scheme
(Tadmor)** is a standard our-side lever confirmed present in this build
(`readFluxScheme.H`, `rhoCentralFoam.C:167`). §2ay state **(b) NUMERICS-ROBUSTNESS**:
"if it's the numerics, change the numerics." This is that successor.

## 1. WHY A NEW FAMILY, NOT A RE-RUN

The parent DMR triple prereg names as a **disqualifier** "any difference in scheme,
constants, boundary conditions, maxCo, write times or rank count between rungs — the
triple requires one numerics family and a difference invalidates it." Therefore the
flux-scheme change is applied **uniformly to all three levels** of a **fresh,
self-contained three-level family** — R1t (1/60, 240×60), R2t (1/120, 480×120), R3t
(1/240, 960×240), nested exactly 2:1 — graded as its OWN Gate V' and its OWN
grid-convergence triple. The original `vanLeer` two-rung pair (2026-08-07) and the
Minmod positivity successor are both **untouched**.

### 1a. STEP 0 diagnostic (MANDATORY FIRST, answer-blind — L-501)

Before this family's verdict is trusted, MEASURE which field goes negative and where.
`run_dmr_step0_diagnostic.sh` restarts R3p from t = 0.10 (decomposed fields on disk,
copied read-only into a fresh root) with `writeControl timeStep`, `writeInterval 25`,
and a `fieldMinMax` functionObject on `(T e p rho U)` with `location yes`, **NO
numerics change** (Minmod + maxCo 0.1 + Kurganov all retained). Its output is read by
`step0_negativity_reader.py`, which reports which physical scalar field FIRST goes
negative, at what time, and WHERE:

- `min(T)`/`min(e)` (cell centre) crossing zero at a locatable cell before the crash →
  FPE at `rhoCentralFoam.C:136`, a **post-update energy/positivity** failure → the
  Courant / flux-diffusion / bounded-energy levers are relevant.
- cell `min(T)` strictly positive to the last written step yet the run still SIGFPEs →
  the negative lives on a **reconstructed face** (`rhoCentralFoam.C:137/143`) → the
  **reconstruction / flux-scheme diffusion** lever is relevant.

**STEP 0 is a DIAGNOSTIC PROBE, not a graded triple member.** A SIGFPE during it
(rc 136, expected ~t=0.116) is THE MEASUREMENT; the driver records the rc and runs the
reader regardless. Because it restarts (startFrom latestTime) it necessarily writes
into a case carrying the t=0..0.10 seed, so the rule-4 graded-run age guard does not
apply; the guard the probe DOES enforce is: refuse if its own root exists (never
overwrite a prior diagnostic). This family may be run in parallel with the probe since
Tadmor is the cheapest robust standard lever regardless — but the probe's location
result is what tells us whether L2/L5 must be reached should Tadmor prove insufficient.

## 2. WHAT FAILED, MEASURED

From `verification/runs/DMR_R3_POSITIVITY_SUCCESSOR_runs/R3p/`:
- rc 136 SIGFPE, deepest frame `Foam::sqrt(Field<double>&, UList<double> const&)`,
  trapped (`sigFpe::sigHandler`), at t = 0.11648 (58 %).
- dt Courant-limited: `deltaT` constant 2.318e-5, max Courant pinned 0.1001 == maxCo.
- Partial solver cost 1100 core-s = 18.3 core-min to 58 % → ~31.5 core-min to complete.
- Last written field t = 0.10 healthy; failing-step field never written (STEP 0 fixes
  the blind spot with `writeControl timeStep`).

## 3. THE SPECIFIC NUMERICS CHANGE, AND WHY IT SHOULD RECOVER

**Single lever, uniform across R1t/R2t/R3t:** `system/fvSchemes`
`fluxScheme Kurganov;` → `fluxScheme Tadmor;`. Everything else is byte-identical to the
positivity successor: Minmod / MinmodV reconstruction RETAINED, maxCo 0.1 RETAINED,
Euler ddt, `div(tauMC) Gauss linear`, all BCs, write times and 4-rank layout unchanged.
**Proven exactly one line** (§5, §9): the Tadmor generator's N=60 output tree differs
from the Minmod generator's N=60 output tree by EXACTLY `system/fvSchemes` line 6
(`fluxScheme Kurganov;` → `fluxScheme Tadmor;`) and nothing else.

**Why it should recover:** `readFluxScheme.H` in v2606 accepts only `Tadmor` or
`Kurganov` (Tadmor is a valid choice, confirmed). `rhoCentralFoam.C:167` — for Tadmor
the interface diffusion becomes `aSf = -0.5*amaxSf` with `a_pos = 0.5` (symmetric split
on the single local max wave speed), strictly **more numerical diffusion** at the
interface than Kurganov's wave-speed-weighted split. That damps the interface-state
excursion driving the negative temperature, at no dt cost.

**Honest caveat, stated before the run (rule 2):** Tadmor is **more diffusive** than
Kurganov. This family may **run to completion and then GATE FAIL on accuracy** — the
shock could smear past tol 0.0231, or the triple could STAGNATE as added diffusion masks
the formal order. That is a legitimate robustness/accuracy trade finding, still state
(b), NOT a widening of the gate: the tolerance is held (§4). And R3t may **still SIGFPE**
— then the flux-diffusion lever is MEASURED insufficient (a negative result), which
under fix-until-runs CONTINUES the ladder as a further dated successor (L2 Courant, L3
combined, or L5 bounded-energy solver build), reported not softened — **never a
capability finding from one or two SIGFPEs (L-501).**

## 4. GATES — NO THRESHOLD WIDENED

- **Gate V' (kinematics vs exact theory):** PASS iff
  `|x_measured − x_exact_at_row| ≤ **0.0231**`, applied at each of R1t/R2t/R3t.
  **BYTE-IDENTICAL to the parent** — asserted (§9): `GATEV_TOL = 0.0231`
  (`dmr_locator_v2.py:69`) equals the literal `0.0231` in the parent
  `DMR_PREREGISTRATION.md` and the positivity successor prereg. No band moved.
- **Gate T' (grid-convergence triple, rule 5 in full):** self-convergence triple of the
  Gate V position error across R1t/R2t/R3t (Roache no-exact form, exact 2:1 nesting). A
  non-CONVERGING triple is **NOT A RESULT**; a CONVERGING triple is graded against its
  band; no GCI on a non-monotone triple. No band loosened.
- Controls carried over from the grader: planted 7-whole-cell density displacement
  (rule 3), planted-absence refusal, and the regression reproducing the 2026-08-07
  R1/R2 Gate V positions to 1e-12.
- STEP-0 diagnostic control: `step0_negativity_reader.py` carries a **two-sided
  planted-zero control** (rule 3): a known negative extremum is planted into a copy and
  read back through the same parse+detect path; the reader REFUSES (exit 2) if it cannot
  see it. Fires both ways in selftest (§9): exit 0 SEEN, exit 2 when blinded.

## 5. GRADING PATH — FIXED AT FREEZE, INSTRUMENTS ON DISK

Grading is by the frozen method-agnostic
`verification/runs/DMR_runs/dmr_locator_v2.py` (git blob
`52aacf9669bcf23e88a0bf7984b299fa8aaf286e`, `GATEV_TOL = 0.0231` at :69) — it grades
shock POSITION and reads NO scheme file, so it grades the Tadmor family unchanged; the
driver **hashes it against the frozen blob before grading each level and refuses on
mismatch** (rule 2). The planted-zero controls of §4 are mandated before any verdict
(rule 3). The grader is REUSED UNCHANGED and is NOT edited (rule 6).

**Instruments authored and self-tested (on disk), cited by sha256:**

| instrument | path | sha256 | git blob |
|---|---|---|---|
| Tadmor generator | `verification/runs/DMR_runs/make_case_tadmor.py` | `f08ddd6884f16ef89146723ba2ae79ba8efff639935b0a0dc1ac5b29b23bb0bc` | `8b43f6cd846cb2301e6ce181b16726248537dd1e` |
| L1 family driver | `verification/runs/DMR_runs/run_dmr_tadmor_successor.sh` | `fe822fc4e6d9df37111833c52566885827491e288a9a26f3b233ce9286aa872c` | `119f09ffe3ed2a9c2302e4f7df343933eae4032b` |
| STEP-0 diagnostic driver | `verification/runs/DMR_runs/run_dmr_step0_diagnostic.sh` | `e3f1c44ea51f0b4a6f7f0fe3b85a7a1f6a7b9ecd9508fa29b4e1a5e21b6fc262` | `0a5cd05f4dd2a824c752f7b53a929257df8dd8e8` |
| STEP-0 reader (MEASUREMENT SCRIPT — check-1) | `verification/runs/DMR_runs/step0_negativity_reader.py` | `c7da80cee99b5d7143d28beb8af51e02d819e67050c8dbc730a244e3db1e02e3` | `61da49fe9375d2ba2cb4f9e8a1fd406f5ad45636` |
| reused grader (UNCHANGED) | `verification/runs/DMR_runs/dmr_locator_v2.py` | — | `52aacf9669bcf23e88a0bf7984b299fa8aaf286e` |

> **The sha256 values above are frozen at the pre-registration commit.** The supervisor
> verifies at check-4 that these are the files that will run; the driver re-hashes the
> grader against its blob at grade time (rule 2).

## 6. COST — rule 12 (measured anchors from this session's R1p/R2p and the R3p partial)

4 ranks; anchors: R1p 0.83 core-min, R2p 4.30 core-min (both measured this session,
`PROGRESS.txt`); R3p partial 18.3 core-min @ 58 % → ~31.5 core-min to complete at
maxCo 0.1. Tadmor is the same step count (dt unchanged), if anything marginally cheaper
per step.

| item | h | grid | basis | core-min |
|---|---|---|---|---|
| STEP-0 diagnostic (restart 0.10→crash, dense writes) | 1/240 | 960×240 | ~0.016 endTime × ~157 cm/unit | **~3 DIAGNOSTIC (own cap, not graded)** |
| R1t | 1/60 | 240×60 | measured R1p 0.83 | ~0.85 MEASURED-ANCHORED |
| R2t | 1/120 | 480×120 | measured R2p 4.30 | ~4.3 MEASURED-ANCHORED |
| R3t | 1/240 | 960×240 | 18.3 cm @ 58 % → 100 % | ~32 MEASURED-ANCHORED |
| mesh/init/reconstruct/locator overhead | | | | ~1.0 |
| **L1 family estimate total (excl. STEP 0)** | | | | **≈ 38 core-min** |
| **grand estimate total (incl. STEP 0)** | | | | **≈ 41 core-min** |
| **L1 HARD CAP (the ONE registered family cap)** | | | | **60 core-min** |
| **STEP-0 HARD CAP (separate)** | | | | **5 core-min** |

**Two separate registered hard caps: the L1 family 60 core-min (one accumulator across
all steps of all three levels, `run_dmr_tadmor_successor.sh`), and the STEP-0 probe
5 core-min (`run_dmr_step0_diagnostic.sh`).** R3t dominates the family. An overrun of
either cap **STOPS that run** and writes `CAP_BREACH.txt`; no new budget (rule 12).
Per-level figures are advisory rule-12 watermarks, NOT per-level caps.

**Dollars — DERIVED, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5; the box cannot read
its own billing): at c7a.4xlarge $0.0513/core-h — grand total 41 core-min = 0.683 core-h
× $0.0513 = **$0.0350 DERIVED**; the 60-core-min L1 cap = 1.0 core-h = **$0.0513
DERIVED**; the 5-core-min STEP-0 cap = 0.0833 core-h = **$0.0043 DERIVED**. All well
under the $25 pre-authorised ceiling. A calibration row (estimate vs actual) is owed in
`docs/COST_CALIBRATION.md` at completion (rule 12).

## 7. DOES THE FINE LEVEL NEED ITS OWN ROBUSTNESS TREATMENT?

**Physically yes, procedurally no — within this family.** Only R3t (1/240) is at risk;
R1t/R2t completed clean at these numerics. But a graded Roache triple requires ONE
numerics family (parent disqualifier), so the fine level CANNOT carry a distinct
scheme/maxCo inside this triple. If Tadmor at uniform maxCo 0.1 still fails R3t, the
distinct fine-level treatment (maxCo 0.05, or first-order T reconstruction) is explored
as a **diagnostic probe** and then, if it works, graded as its own **uniform** family
under its own prereg and cap (lever analysis §2 L2/L3) — never spliced into this triple.

## 8. WHAT THIS SUCCESSOR CAN AND CANNOT SETTLE

- **Can:** whether a more diffusive but still-standard flux scheme (Tadmor) carries the
  DMR to t = 0.2 at 1/240 and yields a CONVERGING Gate V' triple; and quantify the
  robustness-vs-accuracy trade at Mach 10.
- **Cannot:** claim capability exhaustion — that requires the full lever-analysis §4
  measured chain (STEP-0 location + L1 + L2 + L3 measured insufficient). Cannot alter the
  original `vanLeer` or Minmod families' standing.

## 9. SELFTESTS RUN AT AUTHORING (recorded; the supervisor re-checks personally)

All run 2026-09-07 by the authoring lane; verdicts recorded, not the transcripts:
1. **STEP-0 reader two-sided planted control fires both ways.**
   `step0_negativity_reader.py --selftest` → planted negative **SEEN**, clean data no
   false negative, **exit 0**. `--selftest-blind` → detector blinded, planted negative
   **NOT SEEN**, control **CORRECTLY REFUSES, exit 2**. End-to-end on a synthetic
   parallel-format `.dat` with a planted negative-T at t=0.11648: control ran first, then
   located FIRST NEGATIVE `T = -3.14e-01` at the planted cell — the real measure path
   works. **(FLAGGED for the supervisor's §3 check-1.)**
2. **Generator change is exactly one line.** `diff -r` of the Tadmor generator's N=60
   output tree vs the Minmod generator's N=60 output tree returns EXACTLY:
   `system/fvSchemes` line 6 `fluxScheme Kurganov;` → `fluxScheme Tadmor;`, nothing else.
3. **Drivers `bash -n` clean** — both `run_dmr_tadmor_successor.sh` and
   `run_dmr_step0_diagnostic.sh`.
4. **Grader identity unchanged.** `git hash-object dmr_locator_v2.py` =
   `52aacf9669bcf23e88a0bf7984b299fa8aaf286e` (== frozen blob; grader NOT edited).
5. **Gate V' 0.0231 byte-identical** to the parent literal (asserted programmatically).
6. **Run roots ABSENT at authoring:** `DMR_R3_TADMOR_SUCCESSOR_runs` and
   `DMR_R3_STEP0_DIAG_runs` both confirmed to not exist.

---

**Nothing is sent, filed, uploaded, registered or posted (rule 7). NOT frozen, NOT
authorised, no compute launched. Freeze and launch are the cfd supervisor's, after
check-1 (STEP-0 reader) and check-4 (generator/driver/prereg gates) are taken
PERSONALLY.**
