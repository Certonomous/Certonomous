# A2-B2R2 — independent lift-trim of the twist+shape wing, graded on a REGISTERED PLATEAU of the graded quantity

**PERMISSION: NOT_FROZEN.**
**STATUS: DRAFT.** Nothing here is frozen, launched, enqueued or costed against a
live budget. No solver, no container and no `mpirun` was run to produce this
document. **SUBMISSIONS PARKED** (`CLAUDE.md` rule 7).

**Do not launch while `D6RF10 R3` is live.** At the time of drafting the box read
`/proc/loadavg` **22.81** on **16** cores with five solver processes live,
including the `D6RF10 R3` `np = 4` container. A launch into that is not a
measurement of this rung, it is a measurement of the queue.

**Predecessor:** `cases/dafoam/A2_B2R_INDEPENDENT_TRIM_PREREGISTRATION.md`
(frozen; **gates CLOSED at first compute 2026-09-10T04:18:34Z**, `CLAUDE.md`
rule 2). That document is **NOT edited by this one** (rule 6). Its item verdict
**`NOT A RESULT`** stands and is **not** overturned here — a gate can only turn a
`PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse (rule 5). This
is a **successor**, which is the only legal route to a re-cost and a re-grade.

---

## 1. What A2-B2R measured, and what killed it

Every figure in this section was read from the run's own artifacts by the dafoam
lab-lane on 2026-09-10. The run root is
`/home/ubuntu/certonomous-runs/A2B2R-independent-trim/` (outside git).

**It was not a crash and it was not a cap-stop.** `cost.txt` reads
`wall_s=49 ranks=4 core_min=3.27 cap_core_min=40.00` — 8.2 % of a 600 s
container timeout. `AGE_GUARD.txt` reads
`AGE_GUARD_OK pinned_names_verified=25 processor_zero_seen=28 processor_zero_rewritten_late=0 artifacts=2`,
both instrument `sha256`s matched frozen, and the driver's planted-zero
design-variable readback printed
`DECOMP_SETCHECK R1_A4_anchor_cold twist 0.000e+00 shape 0.000e+00 patchV 0.000e+00`
(`decomp.log:684`). The infrastructure did its job.

**The primal converged and went bit-stable.** `decomp.log` prints a force and
residual block every 100 outer iterations to `endTime = 1000`:

| outer iteration | `CD` | `CL` | `p` first `initRes` | `nuTilda` `initRes` |
|---|---|---|---|---|
| 400 | 0.0212483171 | 0.4998839135 | 8.5189214e-06 | 1.042101769e-05 |
| 500 | 0.0212479675 | 0.4999452034 | 6.380833282e-06 | **1.041476221e-05** *(the run's lowest printed sample)* |
| 600 | 0.02124797345 | 0.499946515 | 5.76983993e-06 | 1.042261103e-05 |
| 700 | 0.02124797332 | 0.4999465178 | 5.765918063e-06 | 1.042366023e-05 |
| 800 | 0.0212479734 | 0.4999465157 | 5.765828589e-06 | 1.042375386e-05 |
| 900 | 0.02124797341 | 0.4999465153 | 5.765825951e-06 | 1.042376187e-05 |
| **1000 = `endTime`** | **0.02124797341** | **0.4999465153** | **5.765826264e-06** | **1.042376255e-05** |

`CD` and `CL` are **bit-identical between `Time = 900` and `Time = 1000`** to
every printed digit. Worst per-equation `finalRes` at `Time = 1000` is
**4.652519276e-07** (`nuTilda`), i.e. **inside `G4R`'s registered `1e-6`
completion threshold** (`grade_a2b2r.py:55`, `RESID_MAX = 1e-6`). `yPlus`
min/max/mean = 70.59611759 / 1062.892237 / 321.4843296.

**The registered anchor gate would have passed on those numbers.** `G1R`
(predecessor `:163`) reads
`|CD(R1) − 0.02124478277| / 0.02124478277 ≤ 0.5 %` **and**
`|CL(R1) − 0.49994884178| ≤ 5e-4`. Measured:

* `CD` relative error **1.501846e-04 = 0.015018 %** — inside the 0.5 % band by a
  factor of **33.3**;
* `CL` absolute error **2.326480e-06** — inside the 5e-4 allowance by a factor of
  **214.9**.

**What discarded it.** After the solver's `End` line, DAFoam printed
(`decomp.log:892-895`):

> `Primal min residual 1.042376255e-05` / `did not satisfy the prescribed
> tolerance 1e-08` / `Primal solution failed!`

and raised `AnalysisError` from `mphys_dafoam.py:345`. OpenMDAO propagated it
through the **unguarded** `prob.run_model()` at
`a2_decomposition_driver.py:313`, so the `DECOMP_RESULT` write at `:324` never
ran, no row line reached the grader, and the frozen grader correctly recorded all
four rows as `NO VALUE -- NOT A RESULT (row did not complete)` and `G1R` as
`ANCHOR ROW ABSENT -> whole rung NOT A RESULT`. `RUN_RC.txt` reads `INNER_RC=1`.

**The whole rung's verdict therefore rested on a quantity the pre-registration
had already declined to grade on.** The predecessor's own §6.2 (`:173-183`) says
so in terms: `primalMinResTol` acts on DAFoam's **normalised total** residual,
the log prints **per-equation `finalRes`**, *"the two are not comparable"*, and
`G4R` was **deliberately** registered on the per-equation quantity instead. The
document disclaimed the tolerance as a grading criterion — and the harness then
let it abort the run anyway.

---

## 2. Which residual actually refused the run, and why it matters

The refused value `1.042376255e-05` is **byte-identical to `nuTilda`'s `initRes`
at `Time = 1000`** and to no other residual printed anywhere in the log. The
accept floor is `primalMinResTol 1e-08 × primalMinResTolDiff 1000 = 1.0e-05`
(**N-D43**: the floor is the **product**, never the tolerance alone; recorded at
`cases/dafoam/ladder-a/A2/curriculum_D6RF10/PREREGISTRATION.md:89-90`), and this
case sets `primalMinResTol 1.0e-8`, `primalMinResTolDiff 1e3` in all three of its
scripts. So the run plateaued **4.2376 %** above the floor.

Two consequences, both measured:

1. **More iterations would not have helped.** `nuTilda`'s `initRes` **bottoms at
   `1.041476221e-05` at `Time = 500`** — still **4.1476 %** above the floor — and
   then *rises* monotonically to `1.042376255e-05` at `endTime`. This is a
   shallow asymptote or weak limit cycle sitting just above the floor, not a
   descent that a longer horizon reaches. Raising `endTime` is refused as a
   route: it is unregistered spend against a measured non-descent.

2. **The binding field here is the SA turbulence residual, NOT pressure.** The
   `p` first-uncorrected `initRes` at `endTime` is **5.765826264e-06** — already
   **below** the `1.0e-05` floor. Only one `p initRes` line is printed per outer
   iteration in this case, so that value **is** the first/uncorrected p-solve and
   is directly comparable to `D6RF10`'s binding field.

**NOT VERIFIED, and stated as such:** this lane did **not** read DAFoam's own
definition of *"min residual"* from source. The `dafoam` package lives inside the
container image; a peer lane's extracted copy sits under a scratch path, and
`CLAUDE.md` rule 13 forbids a repository document citing one. The byte-identity
with `nuTilda`'s `initRes` is strong circumstantial evidence and is **not** a
source-level proof. **PF-3** in §7 makes reading that definition inside the
container a mandatory pre-flight before freeze.

---

## 3. The bright line — what this successor does NOT do

* **It does not relax `primalMinResTol`.** It stays `1.0e-8`.
* **It does not raise `primalMinResTolDiff`.** It stays `1e3`.
* **It does not move the `1.0e-05` accept floor**, which is `D6RF10`'s registered
  gate and not this rung's to touch (N-D43, the bright line).
* **It does not change one solver setting.** Scheme, relaxation, `endTime = 1000`,
  `nNonOrthogonalCorrectors`, mesh, decomposition, ranks — every one identical to
  A2-B2R. This rung is not a numerics experiment.
* **It does not re-grade A2-B2R's existing log.** Grading a log that has already
  been read would be choosing the grading path after seeing the data. The
  successor **re-runs** under its own freeze, and the numbers in §1 are the
  *motivation* for its design, never its result.
* **It does not suppress the DAFoam refusal.** The refusal is a mandatory printed
  field on every row that carries one, is printed beside every verdict, and is
  carried into the results record and the rung label.

**What changes is the harness, and only the harness.** A2-B2R's verdict was
decided by an **unregistered** gate — DAFoam's accept floor — firing before any
**registered** gate could be evaluated. Removing an unregistered gate is not
moving a gate to fit an answer. The registered gates get **stricter**, not
looser: `G4R` is kept verbatim and a numerically pre-registered plateau
requirement is added on top of it.

---

## 4. Routes considered, with costs, and the recommendation

### Route (a) — adopt `D6RF10 R3`'s numerics (SIMPLEC, `nNonOrth 12`, relax 0.70). **NOT AVAILABLE TODAY.**

**Conditional on a verdict that does not exist.** `D6RF10 R3` is *live* at the
time of drafting: its ladder file
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF10-a2-wing-convergence-probe/ledger.txt`
carries `D6RF10_RUNG_BEGIN rung=R3 cap_core_min=1133 deadline_s=16905` with **no
`D6RF10_RUNG_GRADED` line**, and its leg log was 0 bytes when the leg opened at
2026-09-10T03:12:09Z. R1 graded `GATE FAIL` and R2 `NOT A RESULT`. **There is no
R3 verdict, and this route must not be presented as available.**

**And a clean R3 `PASS` may not even address this failure.** `D6RF10`'s binding
field is `p_first_uncorrected` (its `PREREGISTRATION.md:92`), and in A2-B2R that
field is **already below** the `1.0e-05` floor at `5.765826264e-06`. The refusal
here is driven by `nuTilda`, which `D6RF10` does not gate on and has not measured
on this configuration. The pre-flight exercise's `p_first_uncorrected@300 =
6.306e-6` for R3 (recorded in that document's AMENDMENT A2, `:399`) is a
**pressure** measurement from a **pre-flight exercise**, not from the live graded
leg, and it says nothing measured about the SA residual.

**Cost, if it ever became available:** it is not a drop-in. Changing the
pressure–velocity coupling changes the fixed point the anchor is reproduced
against, so `G1R`'s anchor `CD = 0.02124478277` — measured under SIMPLE — would
have to be re-established under SIMPLEC before any `G5` falsifier meant anything.
That is an extra anchor rung on top of this one, and its precondition (`R3`)
carries a **1133 core-min** cap of its own. **Held in reserve, not recommended,
not costed into this document.**

### Route (b) — register a PLATEAU criterion on the graded quantity itself. **RECOMMENDED.**

The graded quantity is `CD` at fixed `CL`. Its convergence claim should be a claim
about **its own plateau**, not about a solver-internal residual the
pre-registration already declared non-comparable (§6.2 of the predecessor).
Registered numerically and in advance in §5.3 below.

**This is the route that answers the design question**, because it makes the
verdict depend on the stability of the number being graded, while the DAFoam
refusal is recorded rather than obeyed or hidden.

### Route (c) — catch the `AnalysisError` so the row is written with a refusal flag. **RECOMMENDED, in the form (c′).**

**(c) as literally posed — catch the error and read `CD`/`CL` back from the
OpenMDAO vector — rests on a premise this lane cannot verify without compute:**
that `prob.get_val("scenario1.aero_post.CD")` returns the *fresh* post-solve value
after `solve_nonlinear` has raised, rather than a stale or unset one. The log
shows DAFoam evaluating and printing the functions *before* raising, which is
suggestive, but whether the OpenMDAO outputs vector was populated before the
raise is **NOT VERIFIED**. A reader that silently returns a stale value is
exactly the failure `CLAUDE.md` rule 3 exists to catch.

**(c′), which is what is registered:** the row's `CD`/`CL` are parsed from the
**solver log's own final `Time = <endTime>` block**, which is unambiguously on
disk, instead of from the OpenMDAO vector. The `AnalysisError` is caught, the row
line is still written, and it carries an explicit refusal field. This removes the
unverified premise entirely rather than testing it with compute.

### Recommendation

**(b) + (c′) together, with (a) held in reserve and explicitly unavailable.**

They are complementary and neither is sufficient alone. (c′) makes the row *exist*;
(b) decides whether the row's number may be *believed*. (c′) without (b) would
write a value with nothing but the DAFoam refusal standing against it and no
registered criterion for accepting it — which is the "pretend the refusal did not
happen" failure. (b) without (c′) cannot be evaluated at all, because the process
dies before any row is written.

---

## 5. The registered design

### 5.1 Rows — unchanged from A2-B2R

Four rows, identical twist/shape/`patchV` vectors, identical order, carried
byte-for-byte from `cases/dafoam/a2b2r_rows.json` into `a2b2r2_rows.json` with the
`sha256` of the source recorded in the freeze block: `R1_A4_anchor_cold`,
`R2_trim_from_below` (`patchV` AoA 0.2, `trim_to_CL` 0.5),
`R3_A4_anchor_warm`, `R4_trim_from_above` (`patchV` AoA 2.48, `trim_to_CL` 0.5).

### 5.2 Gates — the predecessor's, kept verbatim, plus one

`G1R`, `G2R`, `G3R`, `G4R`, `G5-R2`, `G5-R4`, `G6R`, `G7R` are carried over
**unchanged**, thresholds byte-identical to the predecessor's §6.1 table. `G4R`
in particular keeps `worst per-equation finalRes ≤ 1e-6` and `DV set/readback
≤ 1e-12`.

One gate is **added**, and it can only make a verdict stricter:

| id | gate | threshold | on failure |
|---|---|---|---|
| **G8R** | **plateau of the graded quantity**, per row | §5.3 | that row **NOT A RESULT** |

### 5.3 `G8R` — the plateau criterion, NUMERIC AND FIXED HERE, BEFORE ANY RUN

For a row to be graded at all, **all four** must hold on its **final** primal
(for a trim row, the confirming primal after the trim, not any primal inside the
search):

1. **Window — fixed:** outer iterations **[600, 1000]**, i.e. the last **five**
   printed blocks at `printInterval = 100` ending exactly at `endTime = 1000`.
   The window is defined by iteration number, not by "the last N samples of
   whatever was printed"; if `printInterval` or `endTime` differ from 100 and
   1000 the row is **NOT A RESULT**.
2. **Minimum sample count — fixed at 5.** Fewer than five `CD`/`CL` blocks inside
   the window → **NOT A RESULT**. Never graded on fewer, never on a widened
   window.
3. **`CD` plateau — fixed:** relative spread `(max − min) / |mean|` over the
   window **≤ 1.0e-4**.
4. **`CL` plateau — fixed:** absolute spread `(max − min)` over the window
   **≤ 1.0e-5**.

**Where the two numbers come from, and why they are not fitted to A2-B2R's data.**
Each is **the registered gate it protects, divided by 50** — both divisors and
both parent thresholds were frozen before A2-B2R ran:

* `G5`'s falsifier band is **0.5 %** relative in `CD`; 0.5 % / 50 = **1.0e-4**.
* `G3R`'s trim tolerance is **5e-4** absolute in `CL`; 5e-4 / 50 = **1.0e-5**.

The 50× factor is the design requirement that residual drift inside the graded
window can never be large enough to manufacture or destroy a `G5` or `G3R`
verdict. **The bar is derived from the gates, not from the observations.**

**Achievability, and the fact that this gate has teeth.** A2-B2R's measured
values are reported here as evidence the bar is *reachable* — explicitly **not**
as its basis:

| window | `CD` relative spread | vs 1.0e-4 bar | `CL` absolute spread | vs 1.0e-5 bar |
|---|---|---|---|---|
| **[600, 1000]** — the registered window | **6.118e-09** | inside by 16 345× | **2.8e-09** | inside by 3 571× |
| [500, 1000] | 2.800e-07 | inside | 1.3144e-06 | inside |
| [400, 1000] | 1.645e-05 | inside | **6.2604e-05** | **FAILS by 6.3×** |

The last row is the point: at a window that reaches back to iteration 400 this
criterion **refuses**. It is a gate that can fail, not a formality.

### 5.4 The DAFoam refusal is recorded, never suppressed

Mandatory, on every graded row:

* the driver prints
  `DECOMP_PRIMAL_REFUSED <row_id> minres <value> tol <value> floor <value>`
  whenever the final primal raised `AnalysisError`, and
  `DECOMP_PRIMAL_ACCEPTED <row_id> minres <value>` whenever it did not;
* the `DECOMP_RESULT` line carries an added terminal field
  `primal_refused 0|1`;
* the grader prints the refusal flag **in the row table and beside every gate
  verdict** for that row, and a rung any of whose graded rows carried a refusal
  is labelled **`PRIMAL-REFUSED`** in its results record and in the ledger. That
  label does not change the verdict; it travels with it.
* **Falsifier F4, registered:** if any row is `PRIMAL-REFUSED` **and** fails
  `G8R`, the harness change itself is falsified — the refusal would then be
  tracking a real non-convergence of the graded quantity, and the rung is
  **NOT A RESULT** with that finding stated as the item's result.

### 5.5 The trim search moves into the driver, and is registered

`optFuncs.findFeasibleDesign` cannot be used: its internal primals go through the
same DAFoam accept path, so an `AnalysisError` inside the search kills `R2`/`R4`
before any confirming primal exists, and (c′) cannot rescue what it cannot see.
The driver implements its **own** secant trim, registered numerically here:

* variable: `patchV[1]` (AoA, deg); target `CL = 0.5`.
* initial slope `dCL/dα = 0.068972407` per deg (carried from
  `a2b2r_rows.json`), thereafter the secant of the two most recent
  `(AoA, CL)` pairs.
* convergence: `|CL − 0.5| ≤ 5e-4` — **`G3R`'s own threshold, unchanged**.
* **maximum 8 primals per trim**, fixed here. On exhaustion the row is
  **`BLOCKED`** and reported as such, **never estimated** — the predecessor's
  `BLOCKED-TRIM` branch, unchanged.
* `CL` for each secant step is read from that primal's own final `Time = 1000`
  log block, so a refused primal advances the search instead of aborting it.
* every trim primal prints `DECOMP_TRIM_STEP <row_id> k <n> AoA <..> CL <..>
  primal_refused 0|1`, so the search is auditable line by line.

### 5.6 Branch table

| branch | condition | row verdict | gate verdict |
|---|---|---|---|
| `TRIMMED` | row completes, `G3R` met, `G4R` met, `G8R` met | graded | `PASS` or `GATE FAIL` on `G5` |
| `TRIMMED-REFUSED` | as above **and** `primal_refused 1` | graded, labelled `PRIMAL-REFUSED` | as above, label carried |
| `NOT-PLATEAUED` | `G8R` fails | **NOT A RESULT** | `G5` **NOT A RESULT** |
| `UNCONVERGED` | `G4R` fails | **NOT A RESULT** | `G5` **NOT A RESULT** |
| `BLOCKED-TRIM` | 8 primals exhausted, `G3R` not met | **BLOCKED** | `G5` **NOT A RESULT** |
| `DIVERGED` | the driver's own trim loop or `run_model` raises anything other than `AnalysisError`, or the DV readback refuses | **NOT A RESULT** | `G5` **NOT A RESULT** |
| `CAP-STOPPED` | the 750 s cap fired | rows not reached are **PENDING** | — |

Rung verdict mapping is the predecessor's §6.4, carried unchanged.

### 5.7 Instruments to be written before freeze — named, not yet written

None of these exist yet; writing them is the next step and each is hashed into
the freeze block.

| file | role |
|---|---|
| `cases/dafoam/a2b2r2_rows.json` | rows, byte-carried from `a2b2r_rows.json` |
| `cases/dafoam/a2_decomposition_driver_b2r2.py` | driver: guarded `run_model`, log-sourced `CD`/`CL`, registered secant trim, refusal fields |
| `cases/dafoam/grade_a2b2r2.py` | comparator: `G1R`–`G8R`, planted controls, refuses (exit 2) rather than degrading |
| `cases/dafoam/run_a2b2r2.sh` | grading path, `timeout 750s`, cost and age-guard capture |
| `cases/dafoam/a2b2r2_age_guard.py` | age guard, carried from `a2b2r_age_guard.py` |

---

## 6. Planted-zero controls (`CLAUDE.md` rule 3)

Carried from the predecessor, plus one the new read path requires:

1. **DV set/readback**, unchanged: every row writes `twist`/`shape`/`patchV`, reads
   them back, and **refuses** on any component differing by more than `1e-12`.
2. **`thickcon` geometry witness**, unchanged: reads exactly `1.0` on the baseline
   and spans `[0.500101, 1.727944]` on the final geometry, so a shape vector that
   never reached the mesh is visible.
3. **NEW — the log reader's own plant.** The `CD`/`CL` log parser is the new
   single point of failure, so its selftest plants a known perturbation
   `PLANT = 1.234e-03` into a **copy** of a real log's final block, asserts the
   parser returns the perturbed value, and **refuses the grading (exit 2)** if it
   does not. A zero from a reader not shown able to see a non-zero is not
   evidence.
4. **NEW — the plateau reader's plant.** The `G8R` window reader is driven twice
   in selftest: once over a synthetic five-sample window at spread `0`, which must
   pass, and once over the same window with one sample displaced by `2.0e-4`
   relative in `CD`, which **must** be refused. A criterion that cannot be made to
   fail has not been shown to work.

---

## 7. Pre-flight checks, mandatory, before freeze — all zero-compute

| id | check | why |
|---|---|---|
| **PF-1** | `sha256` of every instrument recorded in the freeze block, and the frozen file hashed against its committed blob at grading time | rule 2: verify the frozen file **is** the file that ran |
| **PF-2** | the illustrative command block in this document executed once, dry | the calibration lesson already paid for once in this ledger: a path bug in a pre-registration's own commands is cheap at 0.2 core-min and would not be cheap in a line that gated a launch |
| **PF-3** | read DAFoam's definition of *"min residual"* **from the package source inside the container** and record it in the freeze block | §2's identification of `nuTilda` as the refusing field is circumstantial and is **NOT** source-verified |
| **PF-4** | confirm `D6RF10 R3` has ended and the box load has returned before any launch | a launch into a saturated box measures the queue, not the rung |

---

## 8. Cost — pre-registered per `CLAUDE.md` rule 12

**Basis, and it is a NEW one, measured on the predecessor.** A2-B2R's `R1` anchor
primal took **`ExecutionTime = 27.11 s`** at `Time = 1000` on a **saturated** box
(`/proc/loadavg` 22.81 on 16 cores; five co-tenant solvers, all with elapsed times
pre-dating the 04:18:34Z launch). That is **1.76×** the predecessor's registered
15.38 s first-row line and **1.99×** its 13.65 s mean plain-primal basis. **The
predecessor's per-row basis carried no load figure and is not reused as a point
estimate.** This document registers the load its basis was measured at, which is
the calibration lesson this ledger has now recorded twice.

| item | count | basis | wall s | core-min |
|---|---|---|---|---|
| container start + mesh + OpenMDAO setup | 1 | measured ≈ 21.9 s on the predecessor | 22.0 | 1.47 |
| `R1` anchor primal | 1 | 27.11 s measured, saturated box | 27.1 | 1.81 |
| `R2` secant trim | 5 primals | 5 × 27.11 s | 135.6 | 9.04 |
| `R2` confirm primal | 1 | 27.11 s | 27.1 | 1.81 |
| `R3` warm anchor primal | 1 | 27.11 s | 27.1 | 1.81 |
| `R4` secant trim | 6 primals | 6 × 27.11 s, highest-risk row | 162.7 | 10.85 |
| `R4` confirm primal | 1 | 27.11 s | 27.1 | 1.81 |
| chown + cost + guard + grade | 1 | — | 5.0 | 0.33 |
| **REGISTERED POINT** | | | **433.7** | **28.9** |

**Band.** Low **12.6** core-min (a quiet box at the 13.65 s basis with both trims
converging in 4 primals). High **38.5** core-min (both trims at the registered
8-primal maximum, 30 s setup, saturated basis).

**HARD CAP: 50.0 core-min = 750 s wall at 4 ranks**, enforced by `timeout 750s`
inside the container. That is **1.30×** the top of the band. **An overrun stops
the run; it does not get a new budget.** Rows completed before the cap are graded
on their own gates; rows not reached are **PENDING**, never estimated.

**Memory.** Container capped at `--memory=12g`, unchanged; the predecessor
completed its anchor row under that cap with no OOM, kill or memory error
anywhere in its log — a demonstrated **upper bound**, explicitly not a peak-RSS
measurement, because none was taken.

**Dollars, DERIVED NOT MEASURED.** Point 28.9 core-min = 0.4817 core-h →
**$0.0247**; at the cap 0.8333 core-h → **$0.0428**. Rate **$0.0513/core-h,
c7a.4xlarge, reported-by-owner (Sanaa 2026-08-21/22), never measured — this box
cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). Three orders of
magnitude under the $25 pre-authorisation; **a blanket is not a per-item read**
(rule 9), and this is the per-item read.

**Calibration, owed at completion (rule 12).** The completion report will carry
actual core-minutes from this run's own `t0`/`t1` ledger against the **28.9**
predicted here, with the ratio, its attribution, waste named separately, **and the
box load average at launch**, and it will land as a row in
`docs/COST_CALIBRATION.md`. The predecessor's own calibration row is already in
that ledger and records **0.184×** as a **truncation, not a saving** — that row
is the reason this document's basis is 27.11 s and not 15.38 s.

---

## 9. Predictions — to be committed before the solver starts

| # | prediction | band | reasoning |
|---|---|---|---|
| Q1 | `R1` reproduces the anchor | `CD` within **0.5 %** of 0.02124478277 | nothing about the solver configuration changed |
| Q2 | `R1`'s final primal is **refused** by DAFoam again | **stated as LIKELY, ~90 %** | not one solver setting moved, and the `nuTilda` residual's own history shows it bottoming 4.15 % above the floor and rising |
| Q3 | `R1` meets `G8R` | **stated as LIKELY** | its measured window spread is far inside the bar — reported as a prediction, and a miss is reported as a miss |
| Q4 | `R2`'s trim converges within **5** primals | point 5, band 4–8 | B1's converged trim was 4.99 primal-equivalents |
| Q5 | `R4`'s trim converges within 8 primals | **stated as UNCERTAIN, ~60 %** | same direction as the only *diverging* observation, at 0.426× its magnitude |
| Q6 | `|CD(R2) − CD(R1)|/CD(R1)` | ≤ **0.1 %** — five times tighter than `G5` | as the predecessor's P5; a value between 0.1 % and 0.5 % passes `G5` and is still reported as a missed prediction |
| Q7 | `|CD(R4) − CD(R1)|/CD(R1)` | ≤ **0.1 %** | as Q6 |
| Q8 | gross cost | **28.9** core-min, band 12.6–38.5 | §8 |
| Q9 | at least one row is labelled `PRIMAL-REFUSED` | **stated as LIKELY** | follows Q2; if **no** row is refused, that is itself a finding and goes on the page |

**If the measurement contradicts these, the measurement is the finding and it
goes on the page.**

---

## 10. What this document does not know

* **`D6RF10 R3` has no verdict.** Route (a) is conditional on a result that does
  not exist, and nothing here may be read as it being available.
* **DAFoam's internal *"min residual"* definition is not source-verified** by this
  lane (§2). PF-3 discharges it before freeze.
* **Whether `prob.get_val` returns fresh values after `AnalysisError` is
  unverified** — route (c′) is designed so the answer does not matter.
* **Whether the trim's internal primals will be refused too is unmeasured.** §5.5
  is designed for the case that they are; if they are not, the registered secant
  loop costs the same and the search is simply auditable.
* **The 27.11 s basis is a single observation on a saturated box.** It is the best
  measurement available and is registered with its load; it is not a distribution.

---

## 11. Freeze block — EMPTY, to be completed at freeze

`PERMISSION: NOT_FROZEN`. No `sha256`, no commit, no grading-path hash is recorded
here yet, because nothing is frozen. This document may still be amended freely
under rule 2's pre-first-compute clause, **and the condition is checked and stated
here: the graded run root `/home/ubuntu/certonomous-runs/A2B2R2-trim-plateau`
DOES NOT EXIST** (verified on disk 2026-09-10 by the drafting lane). At freeze,
this section takes the instrument/grading-path hash table, the freeze commit sha,
and the `PERMISSION` sha, in the predecessor's format.

**SUBMISSIONS PARKED.**
