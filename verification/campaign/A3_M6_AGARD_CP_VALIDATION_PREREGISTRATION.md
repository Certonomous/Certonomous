# A3-M6-AGARD — ONERA M6 Cp AND SHOCK LOCATION vs AGARD AR-138, PRE-REGISTRATION

**Item:** `A3_M6_AGARD_CP`
**Team:** dafoam. **Lane:** `lab-lane`. **Supervisor:** `dafoam-supervisor`.
**Authority:** Sanaa, `docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md:7` —
*"For M6: Cp at the AGARD span stations (the standard six) and shock location at
η = 0.65 and 0.90, with the tolerance written down first — otherwise it's a
post-hoc match, which your own doctrine doesn't accept."*

**STATUS: FROZEN AT THE COMMIT THAT INTRODUCES THIS FILE.**
No comparison number exists at the moment of the freeze. The grading script
`scripts/grade_m6_agard_cp.py` is committed **in the same commit** and is the only
admissible grading path. Rule 2.

**THIS IS A VALIDATION COMPARISON ON A SINGLE GRID. IT IS NOT A VERIFICATION.**
No grid triple, therefore **no observed order and no GCI may be computed, quoted or
implied under this document** (rule 5 has nothing to gate here; there is no triple).
The certificate slot is honest as: *single grid, band taken from the reference.*

**NO SOLVER RUNS UNDER THIS DOCUMENT.** It grades fields that already exist on disk.
Item 19 of the directive: the runner is the only launcher; nothing here launches.

---

## 1. THE REFERENCE, AND HOW IT WAS VERIFIED (rule 15)

**AGARD Advisory Report No. 138, "Experimental Data Base for Computer Program
Assessment", Report of the Fluid Dynamics Panel Working Group 04, published May 1979,
ISBN 92-835-1323-1.** Appendix B1 is V. Schmitt and F. Charpin (ONERA), ONERA M6 wing,
ONERA S2MA tunnel, Modane-Avrieux.

File: `docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf`

**Title-page verification, performed by this lane, 2026-09-12.** The title page was
read from the PDF itself with `pdftotext -f 1 -l 3` — i.e. from the document's own
first pages, **not** from the filename, not from the `.txt` sidecar, and not from any
hash. It returns, in order: *"NORTH ATLANTIC TREATY ORGANIZATION"*, *"AGARD Advisory
Report No. 138"*, *"EXPERIMENTAL DATA BASE FOR COMPUTER PROGRAM ASSESSMENT"*,
*"REPORT OF THE FLUID DYNAMICS PANEL / WORKING GROUP 04"*, *"Published May 1979"*,
*"ISBN 92-835-1323-1"*. This is the document it claims to be. L-144 satisfied.

**The data table.** `models/onera_m6/agard_ar138_table_b1_14_test2308_cp.dat`,
271 rows, TABLE B1-14, **TEST 2308: M0 = 0.8395, ALPHA = 3.06 deg, REC = 11.72e6**,
every one of those four read from the printed page header. Its own header block records
that it was read **from the page image** (1648x2330 1-bit 200 dpi scan) because the
PDF's OCR text layer for that page carries the header and no table body; that every
`x_over_c` and `Cp` was read twice independently and adjudicated; and that every
`(x_over_c, Z/L)` pair was checked against the independently committed section-coordinate
table `models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat` with **median
residual 6.8e-05 and maximum 5.9e-04 over all 271 rows.** Provenance:
`models/onera_m6/PROVENANCE.md`.

### 1.1 What the reference says about its own accuracy — including what it does NOT say

Read by this lane from the AR-138 PDF, `pdftotext -layout`, pages 330-336 (the B1
facility/instrumentation/data form), 2026-09-12, **before any CFD number was opened**:

| AR-138 clause | What it states |
|---|---|
| §5.1.1 | *"271 pressure orifices divided in 7 sections (y/b = 0.20/0.44/0.65/0.80/0.90/0.96 and 0.99)"* |
| §5.1.5 | pressure transducers **CEC 4312, ±12.5 PSID, Accuracy: ±0.012 PSI**; 6 scanivalves type D |
| §3.8.2 | angle determination accuracy **0.03 degree** |
| §4.2 | wing semispan to tunnel width **0.7** |
| §6.1.1 | **Pressure coefficients — BLANK. The report states NO Cp accuracy.** |
| §6.1.2 | **Aerodynamic coefficients — BLANK.** |
| §6.1.4 | Repeatability: *"see tables B1-2 and B1-3 or B1-10 and B1-11"* |
| §6.2 | Wall interference corrections: **"no corrections"** |

🔴 **Two of these are load-bearing against us and are registered as such.**

1. **§6.1.1 is blank.** AR-138 does not publish a Cp accuracy. Any Cp tolerance
   therefore cannot be read off the reference, and this document will not pretend it was.
2. **§6.1.4's repeatability pairs are at other conditions.** Read by this lane from the
   table headers: TABLE B1-2 is **TEST 2309**, TABLE B1-10 is **TEST 2385 at M0 ≈ 0.459,
   ALPHA ≈ −0.04**. Neither pair sits at the transonic test-2308 condition being graded.
   **The reference supplies no repeatability at the graded condition.**
3. **§6.2: no wall-interference correction was applied**, at a semispan/tunnel-width
   ratio of 0.7 (§4.2), at M0 = 0.84. The blockage and wall-interference bias in these
   Cp values is real, is not removed, and is **not quantified by the reference.**

**Derived instrument floor, arithmetic registered here so it can be checked:**
From §5.1.5, δ(Δp) = 0.012 PSI = 82.74 Pa. The experiment's dynamic pressure q0 is not
printed on the table page; it is derived from the header's own M0 = 0.8395,
REC = 11.72e6 and T0 = 300 K with c = MAC = 0.64607 m:
T_static = 300/(1+0.2·0.8395²) = 262.94 K; a = 325.0 m/s; U = 272.8 m/s;
μ(Sutherland) = 1.6646e-5 Pa·s; ρ = Re·μ/(U·c) = 1.107 kg/m³; **q0 ≈ 41.2 kPa**.
Hence **δCp(instrument) ≈ 82.74/41200 = 0.0020.**
This is the *instrument floor only*. It is not the tolerance, and §6.2 is the reason.

---

## 2. WHICH SIX STATIONS, AND WHY — stated because the reference has SEVEN

AR-138 §5.1.1 instruments **seven** sections: y/b = 0.20, 0.44, 0.65, 0.80, 0.90,
**0.96**, 0.99. There is no "six" in the reference; "the standard six" is the CFD
community's convention, not AGARD's.

**REGISTERED SET, the six graded:  η = 0.20, 0.44, 0.65, 0.80, 0.90, 0.96.**
**EXCLUDED:  η = 0.99.**

Reason, fixed before any CFD number was read: η = 0.99 lies 1% of semispan (≈12 mm)
from the tip edge, inside the tip-vortex roll-up, where the local chord and surface
normal used to form x/c and to place a cutting plane are least well defined, and where
a spanwise cut is most sensitive to tip geometry on both the experimental and the CFD
side. The six retained are simply the six inboard of it. The exclusion is geometric and
was chosen without reference to any deviation.

🔴 **A correction that travels with this document:** the community's "0.95" station is a
**mis-citation of AR-138's actual 0.96**. AR-138 §5.1.1 reads 0.96. Our own data file
already flags this (`NOTE 0.96, NOT 0.95`). This document grades **0.96**, the value the
reference prints.

---

## 3. THE GRADED QUANTITIES

**Q1 — Cp at the six registered stations**, upper and lower surface graded separately
(12 rows), on the **off-shock** orifices only (§4 defines the shock zone from the
experiment alone).

**Q2 — upper-surface shock location at η = 0.65 and η = 0.90**, as x/c.

---

## 4. DEFINITIONS, FIXED HERE SO NEITHER SIDE CAN MOVE THEM

**D1 — the experimental shock location.** On the upper surface of a station, take the
experimental orifices sorted by x/c, restricted to x/c ≥ 0.20. The shock interval is the
adjacent orifice pair `(x_i, x_{i+1})` with the largest **Cp rise** `Cp_{i+1} − Cp_i`.
`x_shock_exp` is the midpoint of that interval. `Δ_local` is that interval's width.

**D2 — the CFD shock location, on the SAME resolution.** The CFD Cp curve is linearly
resampled onto the **experimental** upper-surface x/c locations of that station, and D1
is then applied to the resampled curve. Both sides are therefore read at the
experiment's own orifice resolution and neither is given an advantage. The CFD's native
136-point resolution is **not** used for Q2.

**D3 — the shock zone, defined from the EXPERIMENT only.** For every station and the
upper surface, the shock zone is the closed x/c window
`[x_shock_exp − 2·Δ_local, x_shock_exp + 2·Δ_local]`. Orifices inside it are excluded
from Q1. The lower surface has no shock zone (no shock; all orifices graded).
The zone is built from experimental Cp alone, so no CFD value can widen or move it.

**D4 — pairing.** For Q1 the CFD Cp is linearly interpolated onto each experimental
orifice x/c of the same station and surface. An experimental orifice outside the CFD
x/c span is **dropped and counted**, never extrapolated.

**D5 — the residual.** `dev_j = Cp_cfd(x_j) − Cp_exp(x_j)`; the row statistic is
`RMS = sqrt(mean(dev_j²))` over the graded orifices of that station/surface.

---

## 5. 🔴 THE BAND — WRITTEN DOWN NOW, BEFORE ANY CFD Cp HAS BEEN OPENED

### B1 — Cp, per station per surface, off-shock

**`RMS(Cp_cfd − Cp_exp) ≤ 0.050`  for each of the 12 station/surface rows.**

**Honest derivation, and the part of it that is judgement is labelled judgement.**
- The reference's instrument floor is **0.0020** (§1.1, derived above).
- The reference publishes **no Cp accuracy** (§6.1.1 blank) and **no repeatability at
  this condition** (§6.1.4 pairs are at M0 ≈ 0.459 and test 2309).
- The reference applies **no wall-interference correction** (§6.2) at semispan/width 0.7
  (§4.2) at M0 = 0.84. In a solid/slotted transonic tunnel at that span ratio this bias
  dominates the transducer floor by more than an order of magnitude, and AR-138 declines
  to quantify it.

**Therefore 0.050 is NOT derived from AR-138 arithmetic, and this document says so
rather than dressing a judgement as a derivation.** It is the lab's declared allowance,
set at 25× the reference's instrument floor, anchored on the reference's own disclosure
that its dominant error source is present and uncorrected. It is chosen before any CFD
Cp is read and it is frozen by this commit. **If a later reader wants a reference-derived
Cp band, the named route is §8's future work: transcribe TABLE B1-2 and B1-3 and measure
the repeatability directly. That has not been done and this band does not claim it.**

### B2 — shock location, η = 0.65 and η = 0.90

**`|x_shock_cfd − x_shock_exp| ≤ Δ_local`, one local orifice interval.**

**This band IS derived from the reference, with no judgement in it.** The experiment
localises the shock only to the interval between two adjacent orifices; it cannot
resolve any finer. Agreement to within one interval is the finest distinction AR-138 is
capable of making. Measured by this lane from the reference file itself (experimental
x/c only, no CFD touched), upper surface, aft of x/c = 0.30:

| station | upper-surface orifices | local orifice interval Δ | **REGISTERED BAND** |
|---|---|---|---|
| **η = 0.65** | 23 | 0.0500 c (0.30→0.65), widening to 0.060–0.070 c aft of 0.65 | **± 0.0500 c** (± Δ at the interval found by D1; if D1 lands aft of 0.65, the wider local Δ applies and is printed) |
| **η = 0.90** | 31 | 0.0400 c, uniform across 0.34→0.90 | **± 0.0400 c** |

The band is **the D1 interval width at the interval D1 actually selects**, printed beside
the result. The table above records what that is across the plausible range so that the
number cannot be chosen after the fact.

### B3 — verdict rule, fixed

- **`PASS`** — all 12 rows satisfy B1 **and** both stations satisfy B2.
- **`GATE FAIL`** — the primal is admissible under §6 but any row misses B1 or B2.
  The failing rows are named and their values printed.
- **`NOT A RESULT`** — any §6 precondition fails, or the §7 planted control fails.
  This verdict overrides PASS and GATE FAIL and is never overridden by them.

**Partial credit is registered explicitly:** B1 and B2 are reported per row. A run that
meets B2 and misses B1 is `GATE FAIL` overall and says which. No row-level verdict is
promoted to the overall verdict.

---

## 6. PRECONDITIONS ON THE PRIMAL — checked before any deviation is printed

The graded primal is named in §9. Before Q1 or Q2 is computed the grader checks, and
**refuses with `NOT A RESULT` (exit 2) rather than degrading** if any fails:

- **P1** the CFD extraction file exists and its `freestream` block is present;
- **P2** the CFD freestream Mach is within **±0.005** of the reference's M0 = 0.8395,
  and the CFD angle of attack equals the reference's ALPHA = 3.06 to within **0.05 deg**.
  A mismatch beyond either is a **condition mismatch** and the comparison is refused,
  not forced;
- **P3** all six registered stations are present in the CFD file;
- **P4** the solver terminated: an `End` line in the run log;
- **P5** the run's iterative convergence status is **read and printed beside the result
  whatever it says.** A primal that is not converged makes the row `NOT A RESULT`
  (rule 5 clause 1), and the value is still printed beside the label.

🔴 **P5 is registered with its answer already partly known and disclosed here:** the
sibling run `A3GC-AR1` is graded **`NOT A RESULT` on an internal nuTilda convergence
gate**. That verdict travels with anything this document produces. §9 states which
primal is graded and repeats the disclosure.

---

## 7. THE PLANTED-ZERO CONTROL (rule 3) — the grader refuses without it

Before grading, `scripts/grade_m6_agard_cp.py` **plants a known perturbation**
`PLANT = 1.234e-01` into the CFD Cp array of a named station/surface **by index**,
re-runs the identical pairing and RMS path on the perturbed array, and requires the
recomputed RMS to move by at least `0.5 * PLANT`. If the reader cannot see the plant,
the grader **exits 2 with `NOT A RESULT — PLANTED CONTROL UNSEEN`** and prints no
deviation. A zero from a reader not shown able to see a non-zero is not evidence.

The plant is applied to a **copy**; the graded pass reads the unperturbed array.
Both the planted and the clean RMS are printed.

---

## 8. WHAT THIS DOCUMENT DOES NOT DO — named so nobody reports it as new

1. **No repeatability from the reference.** TABLE B1-2/B1-3 bodies are not transcribed
   on this box and were not transcribed here. The named future tightening of B1 is to
   transcribe them by the same page-image route `PROVENANCE.md` documents.
2. **No grid convergence, no observed order, no GCI.** Single grid.
3. **No force-coefficient gate.** CD and CL are not graded here; AR-138 §6.1.2 leaves
   the aerodynamic-coefficient accuracy blank and §6.3.1 gives no coefficient data.
4. **No wall-interference correction on either side.** The reference is uncorrected
   (§6.2) and the CFD is free-air. This is a disclosed bias, not a removed one.

---

## 9. THE PRIMAL GRADED, AND WHAT TRAVELS WITH IT

**Graded primal: `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic`**, fields at
time 6000, CFD Cp extraction `cp_extracted.json` produced by that case's own
`extract_cp.py` (a vtkCutter plane at z = η·b_semi, freestream taken from the case's own
BCs, not re-derived from the solution).

**Chosen over `A3GC-AR1` / `A3GC-AR1C` because** A3 is the only one of the three with a
committed surface-Cp extraction at the six stations on disk; AR1 and AR1C hold
decomposed processor fields at 0/2000/4000/6000 with no station extraction.

🔴 **DISCLOSURES THAT TRAVEL WITH EVERY NUMBER THIS DOCUMENT PRODUCES:**
- **`A3GC-AR1` is graded `NOT A RESULT` on an internal nuTilda convergence gate.** Its
  CD 0.02300300328 and CL 0.3131159742 sat inside their ±2% band, and that does not
  lift the verdict. An internal convergence verdict does **not** bar an external
  validation comparison, but it is never dropped from the report.
- **This is a single-grid comparison against an uncorrected tunnel dataset.**

---

## 10. COST (rule 12)

**No solver runs.** Desk work on existing fields.
- Predicted: grader wall time **< 60 s on 1 rank → < 1.0 core-minute**.
- Cap: **3× = 3.0 core-minutes.** A crossing is graded `NOT A RESULT` on cost and the
  cap is never raised (directive item 7). Nothing is killed on the cap (directive
  reading 1; Sanaa directive #17, 2026-09-12, no run stopped by a cap).
- `cost_basis`: **measured from the grader's own wall clock**, 1 rank. Dollars, if ever
  quoted, are **derived, not measured** at $0.0513/core-h (owner-stated); the box cannot
  read its own billing.
- Estimate-vs-actual lands in `docs/COST_CALIBRATION.md` at completion (rule 12).

---

## 11. FREEZE

This file and `scripts/grade_m6_agard_cp.py` are committed together. The grading path is
fixed at that commit. **No comparison number existed when it was made.** Changes after
first use land only as dated addenda that cannot alter a gate, threshold, cap or label
(rule 2); originals are struck, never rewritten.
