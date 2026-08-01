# R7 — is the cylinder ladder's Strouhal gate soft at every rung: pre-registration

**Written 2026-08-01 14:40 UTC, before the twin was meshed or launched.** No
cell of the twin mesh exists when this file is written. The baseline it is
compared against was solved on 2026-07-2x and is already on the record, so
every number that decides this test is either already published or still
unmeasured.

Item: `r7-strouhal-mesh-sensitivity-across-the-ladder`, approved,
`est_core_min` 45.0, cost basis "measured, from the low rung's own
2,417-second single-core solve, which a twin reproduces at the same cost".

---

## 1. What is already measured, and what is not

At the ladder's **top** rung, Re 3900, a matched pair exists. The two members
differ in first-cell height alone, 0.0022646 against 0.0035167, a **55.29%
coarsening**, at the same 44,000 cells. Measured
(`F5a_cylinder_reynolds_ladder.md`, matched-pair section, runs finished
20260729T233155Z and 20260730T025040Z):

| quantity | fine spacing | coarse spacing | change |
| --- | --- | --- | --- |
| Cd mean | 1.5806 | 1.7547 | 11.0% |
| Cl rms | 1.3292 | 1.4133 | 6.3% |
| **Strouhal** | **0.1564** | **0.2409** | **35.1%** |

The Strouhal shift is large enough to cross the 3D reference band 0.210-0.220
from below to above, so at that rung the gate flips sign on a mesh parameter
nobody varied deliberately. **The lower rungs have no twins at all.** The
ladder nonetheless reports a Strouhal *trend across rungs* — 0.2343 at Re 1000,
0.2421 at Re 2000, 0.1564 at Re 3900 — and the sensitivity of that trend is
unquantified at every point but one.

## 2. The prediction being tested, and it is the proposal's own

The proposal's stated reading is that the sensitivity belongs to a
chaotic-dynamics regime in which a finite window no longer holds one robust
dominant frequency. **That reading predicts the low rung will be robust.** It is
falsifiable in both directions and the directions are pre-committed here:

* **Strouhal moves comparably at Re 1000 (say, more than 15%)** — the
  sensitivity is not regime-related, there is no onset, and **every Strouhal
  gate on this ladder is soft**, including the two the ladder currently reports
  as its cleanest.
* **Strouhal holds within a few percent (say, under 5%)** — the sensitivity has
  an onset somewhere between Re 1000 and Re 3900, the lower gates stand, and
  the chaotic-regime explanation survives a prediction it made rather than the
  observation that motivated it.
* **Between 5% and 15%** — no verdict; the test reports the number and says the
  design cannot separate the two readings.

## 3. The design decision this test turns on, stated before it is run

The twin must change **first-cell height and nothing else**, and it must change
it by **the same amount the Re 3900 pair changed it**. That is not the same as
running the low rung through the other branch of the sizing formula, and the
difference is large enough to ruin the comparison:

| | laminar branch | turbulent branch | ratio |
| --- | --- | --- | --- |
| Re 1000 | 0.0044721 | 0.0097596 | **2.1823** |
| Re 2000 | 0.0031623 | 0.0058031 | 1.8351 |
| Re 3900 | 0.0022646 | 0.0035167 | **1.5529** |

The two branches converge as Reynolds rises, so reproducing the Re 3900
*mistake* at Re 1000 would coarsen by **118%** where the top rung was coarsened
by **55%**. A larger response would then be uninterpretable: it would confound
"the low rung is more sensitive" with "the low rung was perturbed twice as
hard". **The twin therefore takes the ratio, not the formula.**

Baseline first-cell height, read from the stored record rather than recomputed:
**0.00447** (`F5_runs/re1000/record.json`; note this is the value the run was
launched with, not the formula's 0.004472136). Twin first-cell height:
0.00447 x 1.5529226 = **0.0069416**, an achieved ratio of 1.552931, within
0.001% of the Re 3900 pair's.

Everything else is held at the baseline's stored values: Re 1000, laminar,
n_radial 80, n_tangential 70, **22,400 cells in both members**, farfield 20
diameters, end time 90, dt0 0.005, max Courant 1.5. Only the near-wall grading
changes, which is exactly how the Re 3900 pair differed.

## 4. Gates

**G1** — the twin's mesh clears the same checks the baseline did, and its cell
count is 22,400. A twin that is not the same mesh apart from grading is not a
twin and the comparison is void.

**G2** — stationarity: `halves_drift` on Cd over t = 45 to 90 resolves, and the
run is judged on the same second-half window the baseline used. If drift is
undecidable the run reports UNKNOWN and no Strouhal comparison is made.

**G3** — the Strouhal comparison against the thresholds in section 2.

**G4** — Cd mean, Cl rms and base suction are reported alongside, against the
Re 3900 pair's 11.0%, 6.3% and 6.9%, so the answer says whether Strouhal is
special at this rung or whether everything moves.

## 5. Cost, pre-committed with its rank count

Baseline measured: **2417.17 s at 1 rank**, 22,400 cells, 8,511 steps
(`F5_runs/re1000/record.json`).

The twin is launched at **4 MPI ranks**, not serially. On this lab's own
measurement four ranks ran 4.71x faster than serial while costing 15% fewer
core-minutes, and running serial out of caution was measured to cost more of
both.

* **Estimate at 4 ranks: 2417 / 4.71 = 513 s wall, 34.2 core-minutes.**
* Serial equivalent for comparison: 2417 s wall, 40.3 core-minutes.
* Docket `est_core_min`: 45.0.

5,600 cells per rank is a thin decomposition and the 4.71x figure was not
measured on this case, so the wall time is the number most likely to miss. It
is recorded here so the miss is measurable rather than retrofitted.
