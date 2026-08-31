# D15 / D16 — THE FD STEP TABLE NEITHER ITEM PRINTED, AND WHAT IT SAYS ABOUT THE PLATEAU

**A NEW RECORD, 2026-08-31, by the dafoam team's D19 lane. ZERO SOLVER COMPUTE — this record reads five frozen JSON files and does arithmetic.**

**Nothing in this record is filed, sent, emailed, uploaded, registered, posted or commented outside this box. SUBMISSIONS ARE PARKED and sending is Sanaa's decision alone** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

> **THIS RECORD DOES NOT EDIT, REVISE, REGRADE OR CONTRADICT D15 OR D16.** Both items' documents are frozen and every verdict they recorded stands unchanged: `D15` item `GATE FAIL` (rows `SHIPPED` `GATE FAIL` / `PATCHED` `PASS`), `D16` item `GATE FAIL` (rows `SHIPPED` `GATE FAIL` / `PATCHED` `PASS`). This record reports the one thing their records left **unstated** — whether the graded step sits in a **two-sided** plateau — and it reports it from their own artefacts. **A dated addendum at the foot of `curriculum_D15/RESULTS.md` or `curriculum_D16/RESULTS.md` is the only legal touch on those files and it is the `dafoam-supervisor`'s call, not this lane's.**

---

## 0. WHY THIS RECORD EXISTS

`DAFOAM_CHARTER.md` §2 — *"No DAFoam gradient enters a record, a report or an optimisation without a finite-difference table beside it."* `VERIFICATION_CHARTER.md` §7 step 1 — *"Confirm the step sits in the well-converged plateau with a two or three point mini-sweep. Not assumed."* — and fixes the table's shape at `:885`:

    | step | rel err | rel err (excl. flagged) | cosine | status |

`DAFOAM_CHARTER.md` §3 adds the reading level: *"the plateau is read per component, not off the vector."*

**Neither `curriculum_D15/RESULTS.md` nor `curriculum_D16/RESULTS.md` publishes either table.** They publish the graded aggregate and the per-component relative error at one step; they publish **no step column and no cosine column**. The standard is not aspirational — `curriculum_D8R/RESULTS.md` prints its FD step columns — so these two items fall short of a standard the family already meets elsewhere.

**The data exists.** Three FD steps per component are in the frozen artefacts, under `rows[].fd`, and the grader's own plateau readings are in the graded JSONs under `gates.G5_{SHIPPED,PATCHED}.G5_{CD,CL}.components[].plateau_neighbour_pct`. This record turns that data into the required tables. It is the precondition evidence for `curriculum_D19` and it is why D19's optimisation phase is gated rather than launched.

**Artefacts, by absolute path — every number below is read from these and nothing else:**

| file | role |
|---|---|
| `/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic/{X-S,X-P}/d15_X.json` | D15 adjoint, shipped / patched |
| `/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic/{F-S,F-P}/d15_F.json` | D15 finite differences, shipped / patched |
| `/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic/D15_grade_20260827T114315Z.json` | D15 frozen grading output |
| `/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic/{X-S,X-P}/d16_X.json` | D16 adjoint, shipped / patched |
| `/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic/{F-S,F-P}/d16_F.json` | D16 finite differences, shipped / patched |
| `/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic/D16_grade_20260827T114714Z.json` | D16 frozen grading output |

**The instrument:** `cases/dafoam/ladder-a/A1/curriculum_D19/d19_step_table.py`. Read-only, launches nothing. `python3 d19_step_table.py` regenerates every table in §2 verbatim; `--selftest` runs the two controls alone.

---

## 1. THE ANSWER, FIRST — `NOT PROVED`, ON BOTH GROUNDS, ON OPPOSITE FUNCTIONS

> **The patched gradient a 2-D compressible optimisation would stand on does NOT have a proved plateau — on either ground. Each ground carries exactly ONE component whose plateau clears on ONE SIDE ONLY, and they sit on opposite functions: on D15 the failure is on the OBJECTIVE (`CD`), on D16 it is on the LIFT CONSTRAINT (`CL`).**

`PATCHED` rows only — the shipped rows are `GATE FAIL` on both items and nothing is proposed to stand on them:

| item | function | components with a **two-sided** plateau | the exception | plateau verdict |
|---|---|---|---|---|
| **D15** | **`CD`** | 4 of 5 | **`shape[7]`, one-sided — 1.1559 % coarse-side, 21.6299 % FINE-side** | **NOT PROVED** |
| **D15** | `CL` | **5 of 5**, worst neighbour 1.7174 % | — | **PROVED** |
| **D16** | **`CD`** | **5 of 5**, worst neighbour 1.6132 % | — | **PROVED** |
| **D16** | `CL` | 4 of 5 | **`shape[6]`, one-sided — 14.0978 % COARSE-side, 1.1268 % fine-side** | **NOT PROVED** |

**The registered rule is what lets a one-sided plateau through.** `d15_grade.py:75` sets `PLATEAU_TOL_PCT = 10.0`, and `:356-358` refuses only when **both** neighbours miss:

    nb = [abs(d[0] - ref) / abs(ref) * 100.0, abs(d[2] - ref) / abs(ref) * 100.0]
    if min(nb) > PLATEAU_TOL_PCT:
        c.update({"verdict": "NOT A RESULT", "reason": "NO_PLATEAU"})

`min`, not `max`. **A component agreeing with one neighbour and missing the other by any margin whatever passes this rule.** That is not a defect in the grader — it graded exactly what its own pre-registration froze, and changing it after the answer is known is precisely what rule 2 forbids. It is a statement about **what the registered rule is entitled to conclude**, and the answer is: it is entitled to conclude the step is not *isolated*, and it is **not** entitled to conclude the step is in a *plateau*. A plateau is flat on both sides; a one-sided agreement is a boundary.

**A lift-constrained drag minimisation follows BOTH functions**, `dCD/dx` as the objective and `dCL/dx` as the constraint Jacobian. So neither ground clears §7 step 1 as it stands, and the exposure is symmetric.

### 1.1 What the brief anticipated, and where the measurement went the other way

The brief that commissioned this record named D15's `CD` `shape[7]` as the weak point and it is **right** — 21.6299 % on one side, on the component carrying that row's headline 1.6573 % FD error. What it could not anticipate is the other half: **D16's `CD` — the objective the transonic optimiser would follow — is the ONLY one of the four patched functions with a fully two-sided plateau on all five components**, worst neighbour 1.6132 %. The transonic ground has the better-proved objective gradient and the worse-proved constraint gradient; the subsonic ground has it the other way round. **The plateau finding therefore does not select a ground, and §3 below does not pretend it does.**

### 1.2 Two mechanisms, opposite in step, one diagnosable and one not

Read from the raw `CD_plus` / `CD_minus` and `CL_plus` / `CL_minus` values, against each item's own baseline repeatability (`CD_baseline` vs `CD_baseline_repeat`):

| component | step where it breaks | differenced signal at that step | S/N vs baseline bit-repeatability | direction | signature |
|---|---|---|---|---|---|
| **D15 `PATCHED` `CD` `shape[7]`** | **fine, 1e-4** | `-3.237083e-08` | **248.8** | breaks as the step **shrinks** | subtractive cancellation |
| D15 `PATCHED` `CD` `shape[6]` (for contrast) | — | `-2.836048e-06` at 1e-4 | 21,798 | flat | — |
| **D16 `PATCHED` `CL` `shape[6]`** | **coarse, 1e-2** | `+6.744144e-03` | **901,738** | breaks as the step **grows** | truncation / nonlinearity |
| D16 `PATCHED` `CD` `shape[7]` (for contrast) | — | `+2.202322e-06` at 1e-4 | 13,238 | flat | — |

**D16's `CL` `shape[6]` is diagnosed.** At the step where it breaks the signal-to-noise is 900,000 to one — noise is not remotely the story. The deviation **grows with step**, which is truncation error, and on a transonic section a 1e-2 shape perturbation moves the shock. Its plateau lies at 1e-3 and finer, and 1e-2 is simply outside it. **This is the textbook signature and it needs one extra decade to confirm, not an investigation.**

**D15's `CD` `shape[7]` is NOT diagnosed, and this record will not pretend it is.** The indication is strong — it is the smallest-magnitude component in the set (**1.135 %** of the `CD` gradient's norm, against `shape[6]`'s 76.414 %), and its fine-step S/N of **248.8** is two to four orders below every other fine-step S/N measured here (next lowest 7,992; highest 2.1 × 10⁶). That is exactly where subtractive cancellation appears first. **But the arithmetic does not close.** An S/N of 248.8 bounds the induced error near **0.4 %**, and the observed break is **21.6299 %** — roughly **50× larger than that bound explains**. The bound is the weakest one available: `CD_baseline` versus `CD_baseline_repeat` measures *rerun determinism on the same mesh*, not the *convergence-tolerance scatter of a primal restarted on a perturbed mesh*, which is the noise that actually matters and which **these artefacts do not measure at all**. **Cancellation is therefore a hypothesis with a gap in it, and a hypothesis with a gap is what a sweep is for.**

### 1.3 Two further readings, both of which change how the existing tables should be read

**(a) The fine step is outside the charter's own sanctioned range.** `VERIFICATION_CHARTER.md` §7 step 5 fixes *"Central differences, `step_calc=abs`, step between 1e-3 and 1e-2."* Both items registered the sweep `{1e-2, 1e-3, 1e-4}`, which puts **one of its three points a decade below the range §7 sanctions for grading.** The 21.6299 % is measured there. Inside §7's range D15's `CD` `shape[7]` agrees to **1.1559 %**.

**This does not rescue the plateau, and the record says so rather than banking the charitable reading.** 1e-2 and 1e-3 are the two **endpoints** of §7's range; the graded step 1e-3 therefore sits at an edge with its only in-range neighbour on one side. §7 step 1 asks that the step *"sits in"* the plateau, which a boundary point does not demonstrate. **Two points at the ends of a range bound a flat; they do not bracket one.**

**(b) The fine-step degradation is not confined to the flagged component.** On D15 `PATCHED` `CD` the vector aggregate goes **2.6021 % → 0.0474 % → 0.5087 %** across coarse/mid/fine, and **excluding `shape[7]` it still goes 2.6023 % → 0.0436 % → 0.4375 %** — a tenfold degradation at the fine step with the suspect component already removed. **1e-4 is a poor step for the whole D15 vector, not only for `shape[7]`.** D16 `PATCHED` `CD` does the opposite: **1.4760 % → 0.1460 % → 0.0289 %**, monotone toward the fine step, cosine climbing to 0.99999998 — no round-off floor reached anywhere in its registered range. **The two grounds behave oppositely in step, which is on its own sufficient reason that a sweep established on one does not transfer to the other.**

**(c) §7 step 3's flag is a different instrument from the items' 10 % rule, and neither component trips it.** §7 step 3 flags a component *"moving by more than 50 percent of its own magnitude across one decade of step."* `shape[7]`'s 21.6299 % and `shape[6]`'s 14.0978 % are both **under** that threshold. **Neither component is "flagged" in §7 step 3's sense.** What they fail is each item's **own registered 10 % plateau rule**, on one side. Two thresholds, two instruments, and this record does not merge them.

### 1.4 The consequence, stated as the operative sentence

> **An optimisation on either ground would be standing on a gradient whose step placement has not been demonstrated, on at least one of the two functions it follows.** `DAFOAM_CHARTER.md` §3 forbids *"Quoting an FD number from a single step"* and *"Selecting the step after seeing which one agrees"*; the second is the live risk here, because 1e-3 is the step that agrees best on D15 and the record that would justify it does not exist yet. **The honest first move is a cheap FD step-sweep that establishes the plateau BEFORE any optimiser runs, and the optimisation is gated behind it.** That is `cases/dafoam/ladder-a/A1/curriculum_D19/PREREGISTRATION.md`, phase 1 gating phase 2.

---

## 2. THE TABLES

Generated verbatim by `d19_step_table.py`. `share of |J_adj|` is the component's fraction of the five-component adjoint vector norm — it is how much of the optimiser's search direction that component actually carries, and it is not in either item's record.

<!-- GENERATED BY d19_step_table.py -- do not hand-edit the tables below. -->

## D15 -- run root `/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic`

Graded JSON: `D15_grade_20260827T114315Z.json`.  Item verdict `GATE FAIL`; rows {"SHIPPED": "GATE FAIL", "PATCHED": "PASS"}.

### D15 / PATCHED row / objective `CD`

**Per-component step table** (`DAFOAM_CHARTER.md` sec3: the plateau is read per component). `nb` = deviation of that step from the graded middle step, as percent of the middle step. Registered plateau tolerance 10.0 %.

| dv | idx | share of \|J_adj\| | J_adj | FD @ coarse | FD @ mid (graded) | FD @ fine | nb coarse | nb fine | plateau | rel err vs adjoint | sign match | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `shape` | 0 | 39.044 % | -7.221767e-03 | -7.228472e-03 | -7.216985e-03 | -7.175070e-03 | 0.1592 % | 0.5808 % | TWO-SIDED | 0.0662 % | yes | PASS |
| `shape` | 3 | 50.229 % | +9.290536e-03 | +9.321031e-03 | +9.296948e-03 | +9.337640e-03 | 0.2590 % | 0.4377 % | TWO-SIDED | 0.0690 % | yes | PASS |
| `shape` | 6 | 76.414 % | -1.413381e-02 | -1.366238e-02 | -1.413279e-02 | -1.418024e-02 | 3.3285 % | 0.3357 % | TWO-SIDED | 0.0072 % | yes | PASS |
| `shape` | 7 | 1.135 % | -2.099480e-04 | -2.089125e-04 | -2.065253e-04 | -1.618542e-04 | 1.1559 % | 21.6299 % | **ONE-SIDED** (fails fine 0.0001) | 1.6573 % | yes | PASS |
| `patchV` | 1 | 10.594 % | +1.959450e-03 | +1.959704e-03 | +1.959854e-03 | +1.964311e-03 | 0.0076 % | 0.2274 % | TWO-SIDED | 0.0206 % | yes | PASS |

Steps: coarse/mid/fine = 0.01 / 0.001 / 0.0001.  \|J_adj\| over the five registered components = 1.849638e-02.

**Step-size sweep, `VERIFICATION_CHARTER.md` sec7 shape.** `rel err` is the vector-relative aggregate over the five registered components AT THAT STEP; `excl. flagged` drops the components whose plateau is not two-sided (`shape`[7]).

| step | rel err | rel err (excl. flagged) | cosine | status |
|---|---|---|---|---|
| 0.01 (shape) / 0.1 (patchV) | 2.6021 % | 2.6023 % | 0.99983913 | coarse |
| 0.001 (shape) / 0.01 (patchV) | 0.0474 % | 0.0436 % | 0.99999989 | mid (registered) |
| 0.0001 (shape) / 0.001 (patchV) | 0.5087 % | 0.4375 % | 0.99998949 | fine -- **OUTSIDE sec7 step-5 range 1e-3..1e-2** |

Grader's published aggregate at the graded (mid) step: **0.047405 %** -- reproduced by this reader to 1e-9 (CONTROL A).

### D15 / PATCHED row / objective `CL`

**Per-component step table** (`DAFOAM_CHARTER.md` sec3: the plateau is read per component). `nb` = deviation of that step from the graded middle step, as percent of the middle step. Registered plateau tolerance 10.0 %.

| dv | idx | share of \|J_adj\| | J_adj | FD @ coarse | FD @ mid (graded) | FD @ fine | nb coarse | nb fine | plateau | rel err vs adjoint | sign match | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `shape` | 0 | 58.748 % | +1.073592e+00 | +1.073859e+00 | +1.073506e+00 | +1.072540e+00 | 0.0329 % | 0.0900 % | TWO-SIDED | 0.0080 % | yes | PASS |
| `shape` | 3 | 74.888 % | +1.368550e+00 | +1.368433e+00 | +1.368456e+00 | +1.367485e+00 | 0.0017 % | 0.0709 % | TWO-SIDED | 0.0069 % | yes | PASS |
| `shape` | 6 | 13.961 % | -2.551356e-01 | -2.595290e-01 | -2.551470e-01 | -2.539956e-01 | 1.7174 % | 0.4513 % | TWO-SIDED | 0.0045 % | yes | PASS |
| `shape` | 7 | 26.751 % | +4.888695e-01 | +4.888842e-01 | +4.887417e-01 | +4.877749e-01 | 0.0291 % | 0.1978 % | TWO-SIDED | 0.0262 % | yes | PASS |
| `patchV` | 1 | 5.467 % | +9.990780e-02 | +9.990378e-02 | +9.989824e-02 | +9.979007e-02 | 0.0055 % | 0.1083 % | TWO-SIDED | 0.0096 % | yes | PASS |

Steps: coarse/mid/fine = 0.01 / 0.001 / 0.0001.  \|J_adj\| over the five registered components = 1.827457e+00.

**Step-size sweep, `VERIFICATION_CHARTER.md` sec7 shape.** `rel err` is the vector-relative aggregate over the five registered components AT THAT STEP; `excl. flagged` drops the components whose plateau is not two-sided.

| step | rel err | rel err (excl. flagged) | cosine | status |
|---|---|---|---|---|
| 0.01 (shape) / 0.1 (patchV) | 0.2408 % | 0.2408 % | 0.99999717 | coarse |
| 0.001 (shape) / 0.01 (patchV) | 0.0099 % | 0.0099 % | 1.00000000 | mid (registered) |
| 0.0001 (shape) / 0.001 (patchV) | 0.1194 % | 0.1194 % | 0.99999981 | fine -- **OUTSIDE sec7 step-5 range 1e-3..1e-2** |

### D15 / SHIPPED row / objective `CD`

**Per-component step table** (`DAFOAM_CHARTER.md` sec3: the plateau is read per component). `nb` = deviation of that step from the graded middle step, as percent of the middle step. Registered plateau tolerance 10.0 %.

| dv | idx | share of \|J_adj\| | J_adj | FD @ coarse | FD @ mid (graded) | FD @ fine | nb coarse | nb fine | plateau | rel err vs adjoint | sign match | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `shape` | 0 | 55.945 % | -8.102837e-03 | -7.228472e-03 | -7.216985e-03 | -7.175070e-03 | 0.1592 % | 0.5808 % | TWO-SIDED | 12.2745 % | yes | GATE FAIL |
| `shape` | 3 | 61.568 % | +8.917268e-03 | +9.321031e-03 | +9.296948e-03 | +9.337640e-03 | 0.2590 % | 0.4377 % | TWO-SIDED | 4.0839 % | yes | PASS |
| `shape` | 6 | 53.791 % | -7.790869e-03 | -1.366238e-02 | -1.413279e-02 | -1.418024e-02 | 3.3285 % | 0.3357 % | TWO-SIDED | 44.8738 % | yes | GATE FAIL |
| `shape` | 7 | 1.717 % | -2.487026e-04 | -2.089125e-04 | -2.065253e-04 | -1.618542e-04 | 1.1559 % | 21.6299 % | **ONE-SIDED** (fails fine 0.0001) | 20.4223 % | yes | GATE FAIL |
| `patchV` | 1 | 13.529 % | +1.959450e-03 | +1.959704e-03 | +1.959854e-03 | +1.964311e-03 | 0.0076 % | 0.2274 % | TWO-SIDED | 0.0206 % | yes | PASS |

Steps: coarse/mid/fine = 0.01 / 0.001 / 0.0001.  \|J_adj\| over the five registered components = 1.448353e-02.

**Step-size sweep, `VERIFICATION_CHARTER.md` sec7 shape.** `rel err` is the vector-relative aggregate over the five registered components AT THAT STEP; `excl. flagged` drops the components whose plateau is not two-sided (`shape`[7]).

| step | rel err | rel err (excl. flagged) | cosine | status |
|---|---|---|---|---|
| 0.01 (shape) / 0.1 (patchV) | 32.7703 % | 32.7717 % | 0.95834391 | coarse |
| 0.001 (shape) / 0.01 (patchV) | 34.6807 % | 34.6821 % | 0.95326078 | mid (registered) |
| 0.0001 (shape) / 0.001 (patchV) | 34.9057 % | 34.9039 % | 0.95263323 | fine -- **OUTSIDE sec7 step-5 range 1e-3..1e-2** |

Grader's published aggregate at the graded (mid) step: **34.680703 %** -- reproduced by this reader to 1e-9 (CONTROL A).

### D15 / SHIPPED row / objective `CL`

**Per-component step table** (`DAFOAM_CHARTER.md` sec3: the plateau is read per component). `nb` = deviation of that step from the graded middle step, as percent of the middle step. Registered plateau tolerance 10.0 %.

| dv | idx | share of \|J_adj\| | J_adj | FD @ coarse | FD @ mid (graded) | FD @ fine | nb coarse | nb fine | plateau | rel err vs adjoint | sign match | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `shape` | 0 | 58.777 % | +1.079738e+00 | +1.073859e+00 | +1.073506e+00 | +1.072540e+00 | 0.0329 % | 0.0900 % | TWO-SIDED | 0.5806 % | yes | PASS |
| `shape` | 3 | 74.153 % | +1.362200e+00 | +1.368433e+00 | +1.368456e+00 | +1.367485e+00 | 0.0017 % | 0.0709 % | TWO-SIDED | 0.4572 % | yes | PASS |
| `shape` | 6 | 18.066 % | -3.318760e-01 | -2.595290e-01 | -2.551470e-01 | -2.539956e-01 | 1.7174 % | 0.4513 % | TWO-SIDED | 30.0724 % | yes | GATE FAIL |
| `shape` | 7 | 26.279 % | +4.827504e-01 | +4.888842e-01 | +4.887417e-01 | +4.877749e-01 | 0.0291 % | 0.1978 % | TWO-SIDED | 1.2259 % | yes | PASS |
| `patchV` | 1 | 5.439 % | +9.990780e-02 | +9.990378e-02 | +9.989824e-02 | +9.979007e-02 | 0.0055 % | 0.1083 % | TWO-SIDED | 0.0096 % | yes | PASS |

Steps: coarse/mid/fine = 0.01 / 0.001 / 0.0001.  \|J_adj\| over the five registered components = 1.837007e+00.

**Step-size sweep, `VERIFICATION_CHARTER.md` sec7 shape.** `rel err` is the vector-relative aggregate over the five registered components AT THAT STEP; `excl. flagged` drops the components whose plateau is not two-sided.

| step | rel err | rel err (excl. flagged) | cosine | status |
|---|---|---|---|---|
| 0.01 (shape) / 0.1 (patchV) | 3.9992 % | 3.9992 % | 0.99921588 | coarse |
| 0.001 (shape) / 0.01 (patchV) | 4.2394 % | 4.2394 % | 0.99912013 | mid (registered) |
| 0.0001 (shape) / 0.001 (patchV) | 4.3028 % | 4.3028 % | 0.99909950 | fine -- **OUTSIDE sec7 step-5 range 1e-3..1e-2** |

## D16 -- run root `/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic`

Graded JSON: `D16_grade_20260827T114714Z.json`.  Item verdict `GATE FAIL`; rows {"SHIPPED": "GATE FAIL", "PATCHED": "PASS"}.

### D16 / PATCHED row / objective `CD`

**Per-component step table** (`DAFOAM_CHARTER.md` sec3: the plateau is read per component). `nb` = deviation of that step from the graded middle step, as percent of the middle step. Registered plateau tolerance 10.0 %.

| dv | idx | share of \|J_adj\| | J_adj | FD @ coarse | FD @ mid (graded) | FD @ fine | nb coarse | nb fine | plateau | rel err vs adjoint | sign match | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `shape` | 0 | 8.428 % | +2.362931e-02 | +2.370209e-02 | +2.354560e-02 | +2.366286e-02 | 0.6646 % | 0.4980 % | TWO-SIDED | 0.3555 % | yes | PASS |
| `shape` | 3 | 18.523 % | -5.193531e-02 | -5.135651e-02 | -5.198730e-02 | -5.190153e-02 | 1.2134 % | 0.1650 % | TWO-SIDED | 0.1000 % | yes | PASS |
| `shape` | 6 | 97.808 % | -2.742312e-01 | -2.701944e-01 | -2.746247e-01 | -2.741764e-01 | 1.6132 % | 0.1633 % | TWO-SIDED | 0.1433 % | yes | PASS |
| `shape` | 7 | 3.915 % | +1.097599e-02 | +1.098099e-02 | +1.091837e-02 | +1.101161e-02 | 0.5735 % | 0.8540 % | TWO-SIDED | 0.5278 % | yes | PASS |
| `patchV` | 1 | 2.053 % | +5.755234e-03 | +5.760814e-03 | +5.743948e-03 | +5.758701e-03 | 0.2936 % | 0.2568 % | TWO-SIDED | 0.1965 % | yes | PASS |

Steps: coarse/mid/fine = 0.01 / 0.001 / 0.0001.  \|J_adj\| over the five registered components = 2.803782e-01.

**Step-size sweep, `VERIFICATION_CHARTER.md` sec7 shape.** `rel err` is the vector-relative aggregate over the five registered components AT THAT STEP; `excl. flagged` drops the components whose plateau is not two-sided.

| step | rel err | rel err (excl. flagged) | cosine | status |
|---|---|---|---|---|
| 0.01 (shape) / 0.1 (patchV) | 1.4760 % | 1.4760 % | 0.99999842 | coarse |
| 0.001 (shape) / 0.01 (patchV) | 0.1460 % | 0.1460 % | 0.99999987 | mid (registered) |
| 0.0001 (shape) / 0.001 (patchV) | 0.0289 % | 0.0289 % | 0.99999998 | fine -- **OUTSIDE sec7 step-5 range 1e-3..1e-2** |

Grader's published aggregate at the graded (mid) step: **0.146003 %** -- reproduced by this reader to 1e-9 (CONTROL A).

### D16 / PATCHED row / objective `CL`

**Per-component step table** (`DAFOAM_CHARTER.md` sec3: the plateau is read per component). `nb` = deviation of that step from the graded middle step, as percent of the middle step. Registered plateau tolerance 10.0 %.

| dv | idx | share of \|J_adj\| | J_adj | FD @ coarse | FD @ mid (graded) | FD @ fine | nb coarse | nb fine | plateau | rel err vs adjoint | sign match | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `shape` | 0 | 52.583 % | +1.449893e+00 | +1.451591e+00 | +1.449806e+00 | +1.448340e+00 | 0.1231 % | 0.1011 % | TWO-SIDED | 0.0060 % | yes | PASS |
| `shape` | 3 | 80.020 % | +2.206433e+00 | +2.209653e+00 | +2.205988e+00 | +2.204851e+00 | 0.1662 % | 0.0515 % | TWO-SIDED | 0.0202 % | yes | PASS |
| `shape` | 6 | 10.893 % | +3.003604e-01 | +3.372072e-01 | +2.955423e-01 | +2.988725e-01 | 14.0978 % | 1.1268 % | **ONE-SIDED** (fails coarse 0.01) | 1.6303 % | yes | PASS |
| `shape` | 7 | 26.212 % | +7.227502e-01 | +7.219084e-01 | +7.225232e-01 | +7.211748e-01 | 0.0851 % | 0.1866 % | TWO-SIDED | 0.0314 % | yes | PASS |
| `patchV` | 1 | 5.104 % | +1.407479e-01 | +1.403232e-01 | +1.407690e-01 | +1.405904e-01 | 0.3167 % | 0.1269 % | TWO-SIDED | 0.0150 % | yes | PASS |

Steps: coarse/mid/fine = 0.01 / 0.001 / 0.0001.  \|J_adj\| over the five registered components = 2.757342e+00.

**Step-size sweep, `VERIFICATION_CHARTER.md` sec7 shape.** `rel err` is the vector-relative aggregate over the five registered components AT THAT STEP; `excl. flagged` drops the components whose plateau is not two-sided (`shape`[6]).

| step | rel err | rel err (excl. flagged) | cosine | status |
|---|---|---|---|---|
| 0.01 (shape) / 0.1 (patchV) | 1.3396 % | 0.1370 % | 0.99991370 | coarse |
| 0.001 (shape) / 0.01 (patchV) | 0.1758 % | 0.0185 % | 0.99999852 | mid (registered) |
| 0.0001 (shape) / 0.001 (patchV) | 0.1127 % | 0.0995 % | 0.99999983 | fine -- **OUTSIDE sec7 step-5 range 1e-3..1e-2** |

### D16 / SHIPPED row / objective `CD`

**Per-component step table** (`DAFOAM_CHARTER.md` sec3: the plateau is read per component). `nb` = deviation of that step from the graded middle step, as percent of the middle step. Registered plateau tolerance 10.0 %.

| dv | idx | share of \|J_adj\| | J_adj | FD @ coarse | FD @ mid (graded) | FD @ fine | nb coarse | nb fine | plateau | rel err vs adjoint | sign match | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `shape` | 0 | 8.105 % | +2.233273e-02 | +2.370209e-02 | +2.354560e-02 | +2.366286e-02 | 0.6646 % | 0.4980 % | TWO-SIDED | 5.1511 % | yes | GATE FAIL |
| `shape` | 3 | 19.061 % | -5.251876e-02 | -5.135651e-02 | -5.198730e-02 | -5.190153e-02 | 1.2134 % | 0.1650 % | TWO-SIDED | 1.0223 % | yes | PASS |
| `shape` | 6 | 97.729 % | -2.692698e-01 | -2.701944e-01 | -2.746247e-01 | -2.741764e-01 | 1.6132 % | 0.1633 % | TWO-SIDED | 1.9499 % | yes | PASS |
| `shape` | 7 | 3.948 % | +1.087707e-02 | +1.098099e-02 | +1.091837e-02 | +1.101161e-02 | 0.5735 % | 0.8540 % | TWO-SIDED | 0.3783 % | yes | PASS |
| `patchV` | 1 | 2.089 % | +5.755234e-03 | +5.760814e-03 | +5.743948e-03 | +5.758701e-03 | 0.2936 % | 0.2568 % | TWO-SIDED | 0.1965 % | yes | PASS |

Steps: coarse/mid/fine = 0.01 / 0.001 / 0.0001.  \|J_adj\| over the five registered components = 2.755261e-01.

**Step-size sweep, `VERIFICATION_CHARTER.md` sec7 shape.** `rel err` is the vector-relative aggregate over the five registered components AT THAT STEP; `excl. flagged` drops the components whose plateau is not two-sided.

| step | rel err | rel err (excl. flagged) | cosine | status |
|---|---|---|---|---|
| 0.01 (shape) / 0.1 (patchV) | 0.7320 % | 0.7320 % | 0.99997737 | coarse |
| 0.001 (shape) / 0.01 (patchV) | 1.9648 % | 1.9648 % | 0.99998059 | mid (registered) |
| 0.0001 (shape) / 0.001 (patchV) | 1.8275 % | 1.8275 % | 0.99997905 | fine -- **OUTSIDE sec7 step-5 range 1e-3..1e-2** |

Grader's published aggregate at the graded (mid) step: **1.964796 %** -- reproduced by this reader to 1e-9 (CONTROL A).

### D16 / SHIPPED row / objective `CL`

**Per-component step table** (`DAFOAM_CHARTER.md` sec3: the plateau is read per component). `nb` = deviation of that step from the graded middle step, as percent of the middle step. Registered plateau tolerance 10.0 %.

| dv | idx | share of \|J_adj\| | J_adj | FD @ coarse | FD @ mid (graded) | FD @ fine | nb coarse | nb fine | plateau | rel err vs adjoint | sign match | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `shape` | 0 | 53.511 % | +1.474937e+00 | +1.451591e+00 | +1.449806e+00 | +1.448340e+00 | 0.1231 % | 0.1011 % | TWO-SIDED | 1.7334 % | yes | PASS |
| `shape` | 3 | 79.975 % | +2.204393e+00 | +2.209653e+00 | +2.205988e+00 | +2.204851e+00 | 0.1662 % | 0.0515 % | TWO-SIDED | 0.0723 % | yes | PASS |
| `shape` | 6 | 6.240 % | +1.719991e-01 | +3.372072e-01 | +2.955423e-01 | +2.988725e-01 | 14.0978 % | 1.1268 % | **ONE-SIDED** (fails coarse 0.01) | 41.8022 % | yes | GATE FAIL |
| `shape` | 7 | 25.991 % | +7.163859e-01 | +7.219084e-01 | +7.225232e-01 | +7.211748e-01 | 0.0851 % | 0.1866 % | TWO-SIDED | 0.8494 % | yes | PASS |
| `patchV` | 1 | 5.106 % | +1.407479e-01 | +1.403232e-01 | +1.407690e-01 | +1.405904e-01 | 0.3167 % | 0.1269 % | TWO-SIDED | 0.0150 % | yes | PASS |

Steps: coarse/mid/fine = 0.01 / 0.001 / 0.0001.  \|J_adj\| over the five registered components = 2.756337e+00.

**Step-size sweep, `VERIFICATION_CHARTER.md` sec7 shape.** `rel err` is the vector-relative aggregate over the five registered components AT THAT STEP; `excl. flagged` drops the components whose plateau is not two-sided (`shape`[6]).

| step | rel err | rel err (excl. flagged) | cosine | status |
|---|---|---|---|---|
| 0.01 (shape) / 0.1 (patchV) | 6.0411 % | 0.8951 % | 0.99817439 | coarse |
| 0.001 (shape) / 0.01 (patchV) | 4.5797 % | 0.9458 % | 0.99895131 | mid (registered) |
| 0.0001 (shape) / 0.001 (patchV) | 4.7091 % | 0.9871 % | 0.99889207 | fine -- **OUTSIDE sec7 step-5 range 1e-3..1e-2** |

---

## Controls

- **CONTROL A (same-data)** -- `OK`. **60** plateau and relative-error values recomputed from the raw `*_F.json` / `*_X.json` and asserted equal to 1e-9 against the frozen graded JSONs. This reader is reading what the grader read.
- **CONTROL B (planted)** -- `OK`. A perturbation of 1.618542e-05 (10 % of its own magnitude) was injected into D15/PATCHED/`CD` `shape[7]` at the fine step. The fine-side neighbour moved **21.6299 % -> 29.4669 %**, predicted **29.4669 %**, delta **7.8370 pp**. A reader that could not see this plant would not be trusted to report a plateau.

---

## 3. WHAT THIS RECORD DOES **NOT** CLAIM

1. **It does not regrade D15 or D16.** Every verdict those items recorded stands. The `PATCHED` rows are `PASS` under the rules those items registered before their compute, and that is the only thing a graded row can ever mean.
2. **It does not say the patched gradients are wrong.** It says one thing about them: on one function per ground, the **step placement** was demonstrated on one side only. A gradient agreeing with FD to 0.0474 % is not thereby suspect; it is insufficiently *bracketed*, which is a different and smaller claim.
3. **It does not release, weaken, satisfy or comment on SO-3b's gate.** SO-3b is Mach multipoint and Sanaa's 2026-08-31 ruling gates it behind the **`SHIPPED`** compressible gradient gate passing (`cases/dafoam/ladder-a/A1/SO3b_STUB.md` §3). Nothing here touches the shipped rows, which remain `GATE FAIL` on both items. **No such item exists on this box today and this record does not create one.**
4. **It does not propose amending `PLATEAU_TOL_PCT` or the `min`/`max` reading retrospectively.** Both were frozen before D15's and D16's compute and are unamendable now (`CLAUDE.md` rule 2). What a future item registers is a future item's business.
5. **It reads the `PATCHED` rows because those are what an optimisation would stand on.** The `SHIPPED` tables are printed in §2 for completeness and because §6 requires both rows; no design in this family proposes standing on them.

## 4. A STALENESS FINDING ON `docs/capability/dafoam_GRID.md`, REPORTED AND NOT ACTED ON

The grid's **2-D · steady · subsonic-compressible** and **2-D · steady · transonic** rows read `CAN NOT DO — not attempted` in **both** columns and cite `PENDING: …/curriculum_D15/PREREGISTRATION.md` and `…/curriculum_D16/PREREGISTRATION.md`.

- The **"gradients computed + FD-verified"** column is **STALE**. Both items have run and graded: D15 `PATCHED` `PASS` at aggregate 0.047405 % on `CD`, D16 `PATCHED` `PASS` at 0.146003 %, both `SHIPPED` rows `GATE FAIL`, both item verdicts `GATE FAIL`. The graded JSONs even carry `capability_grid_cell` strings naming the cell each was to move.
- The **"optimization converged"** column is **CORRECT**: *"D15 runs no optimiser"*, *"D16 runs no optimiser"*. **That column is the genuine, never-attempted gap**, and it is the one D19 is designed to move.

**Editing the grid is the `dafoam-supervisor`'s call and this lane has not touched it.** It is reported here because a design that cited the stale half as its own justification would be building on a false premise.

## 5. THE OPEN QUESTION THIS RECORD HANDS FORWARD

**Is a forward-AD or complex-step reference reachable on this ground?** `DAFOAM_CHARTER.md` §2 — *"where a complex-step or forward-AD reference is available, it is the reference"*, and *"a record that reports only an FD table where a forward-AD or complex-step reference was reachable states that it did not reach for it, and why."* Both images ship `libDASolverADF.so`, a forward-AD build (`docs/dafoam/TOOLCHAIN_INVENTORY.md` §6a). **This lane did not reach for it, and the reason is scope, not availability**: the brief commissioned a step table from existing artefacts under a no-compute constraint, and a forward-AD reference is a new run. **It is named here so the omission is on the record rather than invisible**, and D19's pre-registration carries it as a declared non-instrument. A forward-AD reference would settle §1.2's undiagnosed mechanism outright, because it has no step at all.
