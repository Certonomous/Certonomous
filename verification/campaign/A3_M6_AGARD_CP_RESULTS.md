# A3-M6-AGARD — RESULTS. **`GATE FAIL`**

Graded 2026-09-12 by a `lab-lane` of the dafoam team against
`A3_M6_AGARD_CP_VALIDATION_PREREGISTRATION.md`, **frozen at `4c931d97c`,
2026-09-12T18:37:51Z, before the grader was run even once.**

Grading path `scripts/grade_m6_agard_cp.py`, blob
`e9d5c04b420b99201ab19e694b76d1b9eda62443`, **verified identical to its committed blob
at the freeze commit** in the same invocation that graded (rule 2).
Pre-registration blob `9667e0e584d6c4f5fe21f0ab8b57626b34fe0020`, likewise verified.

Output: `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/m6_agard_grade_20260912.json`
Primal: `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic`, time 6000.
**SUBMISSIONS PARKED** (rule 7).

---

## 1. VERDICT

**`GATE FAIL`** — the primal is admissible under §6 of the pre-registration, and
**6 of the 14 graded bands are missed**:

- **B1 (Cp RMS ≤ 0.050): 7 of 12 rows inside.** All six **lower** surfaces pass.
  **Five of six upper surfaces fail**; only η = 0.96 upper passes.
- **B2 (shock within one local orifice interval): 1 of 2 inside.**
  η = 0.90 **inside**; η = 0.65 **outside**.

**The planted control was seen** (rule 3): planting `1.234e-01` into the η = 0.44 lower
branch moved that row's RMS from `0.036637` to `0.140970`, i.e. by `0.104333` against a
required response of `0.061700`. The reader can see a non-zero, so its zeros mean
something.

---

## 2. THE BANDS AS GRADED

| station | surface | n graded | RMS dev | max abs dev | mean bias | band | |
|---|---|---|---|---|---|---|---|
| 0.20 | lower | 11 | **0.0415** | 0.1084 | +0.0217 | 0.050 | inside |
| 0.20 | upper | 19 | **0.0693** | 0.1661 | −0.0141 | 0.050 | **miss** |
| 0.44 | lower | 11 | **0.0366** | 0.0898 | +0.0134 | 0.050 | inside |
| 0.44 | upper | 19 | **0.0699** | 0.1681 | +0.0074 | 0.050 | **miss** |
| 0.65 | lower | 11 | **0.0211** | 0.0453 | −0.0013 | 0.050 | inside |
| 0.65 | upper | 19 | **0.0718** | 0.2577 | +0.0004 | 0.050 | **miss** |
| 0.80 | lower | 11 | **0.0201** | 0.0434 | −0.0022 | 0.050 | inside |
| 0.80 | upper | 19 | **0.0728** | 0.2756 | +0.0084 | 0.050 | **miss** |
| 0.90 | lower | 14 | **0.0296** | 0.0767 | +0.0035 | 0.050 | inside |
| 0.90 | upper | 27 | **0.1160** | 0.5477 | +0.0421 | 0.050 | **miss** |
| 0.96 | lower | 14 | **0.0221** | 0.0458 | +0.0010 | 0.050 | inside |
| 0.96 | upper | 27 | **0.0479** | 0.1308 | +0.0225 | 0.050 | inside |

**Shock location, upper surface, both sides read at the experiment's own orifice
resolution (definition D2):**

| station | x_shock EXP | x_shock CFD | Δx | band (one local orifice interval) | |
|---|---|---|---|---|---|
| **0.65** | 0.47517 | 0.52533 | **+0.05016** | 0.05014 | **miss** |
| **0.90** | 0.27976 | 0.31987 | **+0.04011** | 0.04024 | inside |

🔴 **Both misses are reported at their true margin and neither is softened.** The
η = 0.65 shock misses its band by **2.0×10⁻⁵ of chord** — it sits essentially exactly on
the band edge, and η = 0.90 clears its band by **1.3×10⁻⁴**. **A band edge is a band
edge: η = 0.65 is a `GATE FAIL` limb and is recorded as one.** But a reader who takes
"one inside, one outside" as a contrast between the two stations would be reading noise:
**the two shocks are displaced by very nearly the same distance, and that distance is
almost exactly one orifice interval at each station.**

---

## 3. WHAT THE NUMBERS ACTUALLY SAY — the physics, stated once

**The CFD shock sits AFT of the experiment at both stations, by +0.050 c and +0.040 c,
and it is roughly HALF as strong:** Cp rise across the shock interval is
**0.227 (CFD) vs 0.424 (EXP)** at η = 0.65, and **0.335 (CFD) vs 0.640 (EXP)** at
η = 0.90. A shock that is too far aft and too weak is the classic under-resolved /
over-diffused transonic signature, and it is the same direction the DPW-8 working group
reports for SA-based models — *"predict the shock much further downstream as compared to
the experiments"* (`sansica_2025_dpw8_aepw4_buffet_workinggroup.txt:~630`). **That
citation is context, not corroboration: it is a 2D airfoil study and carries no weight
in this verdict.**

**The failure is on the upper surface only.** Every lower surface is inside band, most
of them comfortably (0.020–0.042). The suction side — shock, supersonic plateau,
leading-edge peak — is where this solution parts company with the tunnel.

### 3.1 🔴 A diagnostic that kills the convenient explanation

The tempting story is *"it is all the leading edge"*. **It is not, and the measurement
says so.** Recomputing the upper-surface RMS with the leading-edge orifices (x/c < 0.01)
dropped — **a diagnostic only; it moves no band and changes no verdict**:

| station | RMS, all off-shock | RMS, excl. x/c < 0.01 | would that alone clear 0.050? |
|---|---|---|---|
| 0.20 | 0.0693 | **0.0739** | no — it gets **worse** |
| 0.44 | 0.0699 | 0.0573 | no |
| 0.65 | 0.0718 | **0.0749** | no — **worse** |
| 0.80 | 0.0728 | **0.0784** | no — **worse** |
| 0.90 | 0.1160 | 0.0419 | yes |
| 0.96 | 0.0479 | 0.0363 | (already inside) |

**Only η = 0.90's outlying 0.1160 is leading-edge-driven** (its +0.548 max deviation sits
at x/c = 0.002). **At η = 0.20, 0.65 and 0.80 the disagreement is distributed along the
chord and removing the leading edge makes it worse.** Three of the five failing stations
are not a leading-edge story, and this record refuses to tell one.

### 3.2 Caveats that travel with the numbers

- **yPlus at the graded time: min 5.577, max 103.518, mean 33.748** — wall-function
  regime, **not** wall-resolved. Stated as a caveat, not as an excuse.
- **AGARD AR-138 applies no wall-interference correction** (§6.2) at semispan/tunnel
  width 0.7 (§4.2) at M0 = 0.84; the CFD is free-air. A disclosed bias on the reference
  side, not a removed one.
- **The B1 threshold of 0.050 is the lab's declared allowance, labelled judgement**,
  because AR-138 §6.1.1 is blank and its repeatability pairs are at M0 ≈ 0.459. **The B2
  shock band is reference-derived with no judgement in it.** A reader may disagree with
  0.050; they cannot claim it was chosen after the fact.
- **Single grid. No observed order, no GCI, and none is implied.**
- **`A3GC-AR1` is graded `NOT A RESULT` on an internal nuTilda convergence gate.** Its
  CD 0.02300300328 / CL 0.3131159742 sat inside their ±2 % band and that does not lift
  the verdict. An internal convergence verdict does not bar this external comparison; it
  never leaves the report.

---

## 4. 🔴 PRECONDITION P5 — A DEFECT IN MY OWN INSTRUMENT, DISCLOSED RATHER THAN REPAIRED

**The pre-registration's §6 registers FIVE preconditions. The committed grader implements
FOUR.** P1, P2, P3 and P4 are coded and were checked. **P5 — iterative convergence — is
registered as a refusing check and is NOT implemented in `grade_m6_agard_cp.py`.**

This is the same disease as D8G's defect 5: a registration gating on something the
instrument does not check. **It is disclosed here, in the record the verdict travels in,
and the script is NOT edited to hide it** — gates are closed post-compute (rule 2) and a
frozen file is not rewritten (rule 6).

**P5 was therefore established by direct reading of the run's own log, and it PASSES.**
From `run_model_run3.log` at the graded step `Time = 6000`:

| equation | initial residual at the last steps |
|---|---|
| U0 / U1 / U2 | 1.046e-07 / 6.889e-08 / 8.712e-08 |
| he | 2.635e-07 |
| p | 3.744e-07 |
| nuTilda | 8.903e-07 |
| continuity | sum local 1.405e-07, global −1.248e-10, cumulative −4.200e-08 |

and the graded functionals are plateaued to the ninth significant figure across the final
prints — CD 0.02299552 / 0.02299541 / 0.02299546 / 0.02299556, CL 0.31311590 ±3e-08.

**Also recorded because it is true and unflattering: the case declares no convergence
criterion at all** — `"SIMPLE: no convergence criteria found. Calculations will run for
3000 steps."` It stopped on iteration count, not on a met criterion. The residuals happen
to be at 1e-7, far past any normal production threshold, so **P5 passes on the evidence
and not on the case's intent.** Rule 5 clause 1 is satisfied; the verdict stays
`GATE FAIL` and does not become `NOT A RESULT`.

**Named for the successor registration, and NOT applied here:** implement P5 in the
instrument, and define the shock-exclusion zone from the union of the experimental and
CFD shock intervals rather than the experimental one alone — at η = 0.80 the displaced
CFD shock leaves 79.9 % of that row's squared deviation in the two points adjacent to the
zone edge. **Neither change may touch this document's gates.**

---

## 5. COST (rule 12)

| | core-minutes |
|---|---|
| predicted (prereg §10) | < 1.0, cap 3.0 |
| **actual, MEASURED** | **8.214e-05** (4.93e-03 wall s × 1 rank ÷ 60) |
| ratio actual/predicted | **< 1e-4** — over-predicted by four orders |

**No solver ran.** Attribution: the prediction priced a file-walking comparator at a
round "under a minute"; it reads a 271-row table and one JSON and finishes in five
milliseconds. **Waste: 0.000 core-min** — no rerun, no crash, no relaunch; the grader ran
once and returned rc = 0. **Contention: none measurable at this duration.** Dollars are
**derived, not measured** at the owner-stated $0.0513/core-h and round to $0.00.
A row lands in `docs/COST_CALIBRATION.md`.

---

## 6. WHAT THIS RESULT IS, IN ONE LINE

**The first external-reference validation this territory has produced: an ONERA M6 primal
graded against AGARD AR-138 tunnel data on a band frozen before any CFD number was
opened, and it is a `GATE FAIL` on the suction side with the shock 0.04–0.05 c too far
aft and about half as strong.**
