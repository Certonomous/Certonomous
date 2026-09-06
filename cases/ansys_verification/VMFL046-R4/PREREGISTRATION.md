# VMFL046-R4 — PRE-REGISTRATION

**Supersonic flow with a normal shock in a converging–diverging nozzle.**
Ansys Fluid Dynamics Verification Manual, Release 2026 R1, **p. 155 (VMFL046)**.

> **THIS IS A COST FIX AND A READER-WINDOW FIX. IT IS NOT A PHYSICS FIX AND IT IS NOT A
> NUMERICS FIX.**
> All **eleven** `case/` inputs are **BYTE-IDENTICAL to R3's** and the driver **ABORTS** if
> any one of them differs. `x_shock` against **1.250 m**, band **5 %**, plateau
> **`DELTA_X = 6.250e-04 m`**, `endTime = 0.080 s`, `maxCo 0.5`, `maxDeltaT 1.0e-04`,
> `ddtSchemes Euler`, `Gauss vanLeer(V) 1` — every one carried forward **unchanged, not
> re-derived, not re-rounded, not moved**.

---

## 1. WHY THIS DOCUMENT EXISTS — **R3's NUMERICS CHANGE WORKED AND ITS COST ESTIMATE KILLED IT**

VMFL046-R3 (freeze `91f62d73`, register row **#60**) graded **`NOT A RESULT`**. Read from
its three logs, and every figure below was re-derived by this lane from the raw
`Time = ` / `ExecutionTime = ` lines rather than taken from a brief:

| level | `RUN_RC` | `End` lines | last `Time` | as a fraction of `endTime` | `ExecutionTime` | core-min |
|---|---|---|---|---|---|---|
| **L1** | **0** | **1** | **0.08** | **100.0000 %** | 482.71 s | **8.0452** |
| L2 | **124** | 0 | 0.0731877615 | 91.4847 % | 2 991.96 s | 49.8660 |
| L3 | **124** | 0 | 0.0793715355 | **99.2144 %** | 25 190.36 s | 419.8393 |

**L1 COMPLETED.** `rc = 0`, one `End`, last `Time` exactly `endTime`, `Time` strictly
increasing over all 34 694 steps. The route chosen in R3 §5 — `rhoPimpleFoam` with
`ddtSchemes Euler` and TVD `vanLeer` — **integrates this case in physical time, which is
the thing twelve first-order-upwind configurations could not do, including one at
`maxCo 0.05`.** That finding stands and **this document does not reopen it.**

**L2 AND L3 DIED ON THEIR OWN CAPS.** Both were killed by `timeout`, not by the solver:
`rc 124`, no `End`, the log ending mid-step. **L3 was killed at 99.2144 % of `endTime`
after seven hours**, having consumed 419.84 of its 420 core-min cap.

> **That is charter `§26.2` verbatim, and `§27` sharpened it:** *"AN OPTIMISTIC ESTIMATE IS
> NOT A CHEAP MISTAKE THAT COSTS A LITTLE MONEY. IT IS AN EXPENSIVE ONE THAT COSTS THE
> ENTIRE RUN, AND IT COSTS IT AT THE END, AFTER ALL THE COMPUTE HAS BEEN SPENT."* R3 filed
> 162.08 core-min and consumed 477.75 before both caps fired. **Nothing about the physics
> was wrong. The number in front of the physics was.**

**`§26.2`'s cap rule is not relaxed by one core-minute here.** Caps stay at **~3×** and the
repair is made **entirely inside the estimate**, which is where `§27` says the defect lives.

---

## 2. WHAT BROKE THE R3 ESTIMATE — **`deltaT` IS NOT STATIONARY, AND THE PROBES SAT IN THE ONE PLACE WHERE THAT MATTERS**

R3 §8 costed from three probes: **L1 to 20 ms (25 % of the graded clock), L2 and L3 to
8 ms (10 %)**. Its method — per-cell-step rate × `endTime` ÷ an equilibrium `deltaT` — is
sound arithmetic fed a wrong input, because **an adaptive-timestep transient's `deltaT` has
not settled after 10 % of the clock.**

Measured on R3's own logs, mean `deltaT` in the probe's tail as a multiple of the
**run-settled** `deltaT`:

| fraction of the clock the probe covers | L1 | L2 | L3 |
|---|---|---|---|
| 0.050 | 5.84 | 5.34 | 4.57 |
| **0.100 ← R3's L2/L3 probes** | **4.70** | **4.46** | **3.89** |
| 0.150 | 2.09 | 2.34 | 2.41 |
| 0.175 | 1.07 | 1.15 | 1.09 |
| 0.200 | 1.03 | 1.09 | 1.00 |
| **0.250 ← R3's L1 probe** | **1.03** | **1.03** | **0.95** |

**The mechanism closes the whole miss.** R3's L3 probe read an equilibrium `deltaT` of
1.8921e-06 s and projected 42 282 steps; the run took **144 041 steps to reach 99.2 % of
`endTime`**, a mean `deltaT` of 5.5e-07 s. The probe's `deltaT` was **3.4× too coarse**, and
the filed 136.97 core-min was **3.09× low** against a measured 423.63. The same arithmetic
at L2: **3.55× low**. **This is not a decomposition that closes by construction —
`§27.3` bans citing one of those — it is an independently measured `deltaT` ratio predicting
an independently measured cost ratio.**

**AND THE POSITIVE CONTROL IS INSIDE THE SAME CAMPAIGN.** L1's probe covered 25 %, its
`deltaT` had settled (1.03× the run value), and L1 came in at **0.845×** filed.

### 2.1 DOES THE PER-STEP COST RISE THROUGH THE RUN? **NO — IT FALLS.**

The question decides whether extrapolating from 99.2 % is still slightly low. Per-step
cost, first decile of the clock → last decile:

| level | s/step at the first decile | s/step at the last decile | change |
|---|---|---|---|
| L1 | 0.01472 | 0.01405 | **−4.6 %** |
| L2 | 0.04783 | 0.04480 | **−6.3 %** |
| L3 | 0.18529 | 0.17222 | **−7.1 %** |

**Per-step cost falls, so a settled-rate extrapolation is conservative, not optimistic.**
The corroboration is L1, which is a **complete** run: its cost-per-millisecond over deciles
3–10 is 0.112, 0.097, 0.117, 0.119, 0.111, 0.126, 0.102, 0.119 core-min/ms — **flat, no
trend, all the way to `endTime`.** L3's deciles 3–10 are likewise flat (4.64 to 6.54, last
6.03, oscillating with the shock hunt and not trending).

**What DOES rise, by ~5×, is the cost per unit of PHYSICAL TIME, and it rises inside the
first two deciles only** — that is the `deltaT` collapse of §2 and it is entirely finished
by decile 3. **This is the single fact that broke R3 and it is stated here as a number, not
as a caution.**

---

## 3. THE MEASURED BASIS AND THE FILING — **AND THE ARITHMETIC SELF-CHECK OF `§26.3` IS DONE HERE, IN THE FROZEN BYTES**

**THE BASIS IS NOT A PROBE.** It is R3's three graded runs, at the graded mesh, the graded
numerics and the graded clock. The stated method is: *take the measured cost to the time
actually reached, and add the remaining physical time priced at the run's own settled rate,
measured over the last decile it reached.*

| level | measured | reached | settled rate | remaining | remainder | **full-run core-min** |
|---|---|---|---|---|---|---|
| L1 | 8.0452 | 100.0000 % | — | 0 ms | 0 | **8.0452** *(MEASURED, complete)* |
| L2 | 49.8660 | 91.4847 % | 0.80197 core-min/ms | 6.8122 ms | 5.4632 | **55.3292** |
| L3 | 419.8393 | 99.2144 % | 6.03031 core-min/ms | 0.6285 ms | 3.7898 | **423.6292** |
| **TOTAL** | | | | | | **487.0035** |

**The cross-check that could have failed and did not:** a plain linear extrapolation in
physical time gives 8.0452, 54.5075 and 423.1636 — **agreeing with the settled-rate figures
to 0.11 % at L3** and 1.5 % at L2. The settled-rate value is the larger at both levels and
is the one filed; the linear value is quoted so a reader can see the two methods rather than
one number.

**FILED: 536 core-min** — the basis 487.00 with a **disclosed +10 % contention allowance**
(487.00 × 1.10 = 535.70). The allowance is not decoration: `§27.4` records a case in this
lab where per-iteration cost differed by **1.36×** between a contended and an uncontended run
of the same mesh.

**`§26.3` SELF-CHECK, USING ONLY INPUTS AVAILABLE AT FILING.** The method above executed on
the three R3 logs — the only inputs it uses, all of which existed before this document —
yields **487.00**. The filed **536** is **1.101× above its own method**, and that factor is
the allowance named in the line above, not an unexplained gap. **`§26.3` also requires the
estimate to be re-priced against every configuration change this same document makes: this
document changes NO configuration** — eleven case inputs byte-identical to R3, same
`endTime`, same `writeInterval`, same level count, same refinement ratio — **so the
workload this estimate prices is exactly the workload that will run.** That is the failure
`§27.3` names (*"THE FREEZE PRICED A RUN AND THEN, IN THE SAME DOCUMENT, CHANGED THE
WORKLOAD IT HAD JUST PRICED"*) and it cannot occur here, because there is no change to make.

**THE CAPS, AT ~3× THE FILED FIGURE, `§26.2`:**

| level | basis | filed (×1.10) | **cap** | cap ÷ filed |
|---|---|---|---|---|
| L1 | 8.0452 | 8.85 | **27** | 3.05 |
| L2 | 55.3292 | 60.86 | **183** | 3.01 |
| L3 | 423.6292 | 465.99 | **1400** | 3.00 |
| **running total** | 487.0035 | **536** | **1610** | **3.00** |

> **THE ESTIMATE WAS MADE GOOD AND THE CAP WAS THEN SET ON IT. THE CAP WAS NOT LOOSENED
> AROUND A BAD NUMBER.** `§27` is not a licence to raise a cap, and this registration does
> not read it as one: every cap above is `~3×` a figure whose basis is a measured run of the
> same configuration at the same clock, not a projection.

**cost_basis:** core-min = wall_s × ranks ÷ 60, **MEASURED** from R3's `ExecutionTime`
lines. **Waste is MEASURED, not inferred:** `ExecutionTime/ClockTime` at the last logged
step is 0.99940 at L1, 0.99732 at L2 and 0.99962 at L3, i.e. **0.06 %, 0.27 % and 0.04 %** —
the R3 runs were effectively uncontended, and the contention allowance above is a margin
against a *future* box state, not a correction for a past one. Dollars **DERIVED** at
$0.0513/core-h (owner-stated; `COMPUTE_BUDGET_CHARTER` §5 — the box cannot read its own
billing): 536 core-min = 8.93 core-h → **$0.458, derived, not measured**; at the cap, 1610
core-min = 26.83 core-h → **$1.376, derived**. Under the $25 pre-authorisation.

**⚠ THE WALL-TIME CONSEQUENCE, DISCLOSED RATHER THAN BURIED.** Serial at `RANKS = 1`: the
**expected** wall time is **8.9 h** (L3 alone 7.1 h), and the **cap ceiling** is **26.8 h**
(L3 alone 23.3 h). That ceiling is a direct consequence of applying `~3×` to an honest
estimate, and it is the price of `§27.2`'s finding that a cap-hit forfeits everything spent.
**It is flagged for the supervisor as an occupancy question and is NOT resolved by
tightening the cap in this document.**

**A predicted-vs-actual row for `docs/COST_CALIBRATION.md` is owed at completion**
(`CLAUDE.md` rule 12), and **R3's own row is owed too** — its 162.08 filed against 477.75
consumed before the caps fired is this campaign's largest miss and belongs in the ledger
whether or not R4 runs.

---

## 4. THE CASE — **UNCHANGED, AND THE PARITY IS ENFORCED IN BOTH DIRECTIONS, TWICE**

Planar CD nozzle, half-modelled by symmetry about `y = 0`. Straight walls: inlet
`h = 0.2` → throat `h = 0.1` at `x = 0.5` → exit `h = 0.3` at `x = 2.0` (exit/throat area
ratio 3). Air as a perfect gas, `Cp = 1004.5`, `mu = 1.7894e-05`, `Pr = 0.72`, `laminar`.
Inlet `totalPressure p0 = 301 325 Pa` with `T = 500 K`; outlet `fixedValue p = 176 325 Pa`;
`noSlip` isothermal wall at 328 K; `symmetryPlane` centreline; `empty` front/back.

`r = 2` grid triple, **identical to R1, R2 and R3**: converging / diverging / transverse
counts 40 / 120 / 20 doubling twice, giving 3 200, 12 800 and 51 200 cells. Sampler
`nPoints = 2(NXA+NXB)+1` = **321/641/1281**, sampler/mesh ratio **0.499000 identically at
all three levels**.

**TWO MECHANICAL PARITY ASSERTS, EACH FIRING IN BOTH DIRECTIONS** (`run_vmfl046_r4.sh` §2a,
§2b, exit 7):

| assert | direction 1 — aborts if | direction 2 — aborts if |
|---|---|---|
| **R2-parity** *(carried forward from R3 verbatim)* | any of the 8 physics inputs **differs** from R2's | any of the 3 numerics inputs is **identical** to R2's — because that would mean branch (b)'s pre-committed numerics change was never made |
| **R3-parity** *(new, and its axis is R4's own delta)* | **any** of the 11 case inputs **differs** from R3's — R4 may not touch the physics or the numerics | the **cost envelope is identical** to R3's — a successor that re-files R3's caps changed nothing and would be killed in exactly the same place |

**THE SECOND ASSERT IS WHAT MAKES A NO-OP SUCCESSOR UNFREEZABLE IN R4's OWN TERMS.** R3's
assert was built around a numerics change and would be silent about a cost-only successor
that changed nothing at all; R4's is built around the cost envelope because that is what R4
changes. **And the R3 cap figures it compares against are read out of R3's own frozen
driver at launch, not typed into this one** — a hardcoded pair of numbers nobody checks is
a comparison against a memory, not against a file, and the driver aborts if they disagree.

**All six planted negatives fire and the unmutated control passes** (§12).

---

## 5. **W2 — THE PROBE-LENGTH FLOOR, AND IT IS REGISTERED AS A FROZEN CONSTANT, NOT AS ADVICE**

> **REGISTERED RULE.** A cost estimate in this registration must be built from a basis
> covering at least **`PROBE_FLOOR = 0.25`** — one quarter — **of the graded clock, at the
> level it prices. AN ESTIMATE DERIVED FROM A SHORTER BASIS IS NOT ADMISSIBLE.**
> The constant lives in `grade_vmfl046_r4.py`, the fraction each level's basis actually
> covers lives beside it in `COST_BASIS_FRACTION`, and **the module REFUSES AT IMPORT if any
> of them is below the floor** — so a registration filed on a short basis cannot grade
> anything through this comparator at all. `--selftest` exercises the refusal on **R3's own
> 0.10 basis, the one that killed both runs.**

**WHY 0.25 AND NOT THE MEASURED EDGE.** Worst |error| over the three levels of a
settled-tail extrapolation to `endTime`, as a function of the basis fraction:

| fraction | 0.100 | 0.125 | 0.150 | **0.175** | **0.200** | 0.250 |
|---|---|---|---|---|---|---|
| worst error | 74.8 % | 66.9 % | 51.5 % | **6.6 %** | **4.7 %** | 8.7 % |

The transition sits between 0.15 (every level 1.25–2.4× wrong in `deltaT` and 50–61 % wrong
in cost) and 0.175–0.20. **0.25 is registered rather than 0.175 or 0.20 because a floor set
AT its measured edge leaves a basis that just clears it with no margin** — and because 0.25
is this campaign's own positive control: R3's L1 probe covered it and landed at 0.845×.

**AND THE SECOND HALF OF THE RULE, WHICH IS THE PART THAT GENERALISES WITHOUT A CALIBRATED
NUMBER:**

> **A rate extrapolated from a partial run is admissible only if it is built from that
> run's SETTLED-TAIL rate, never from its run-average rate.** Measured here, a linear
> (run-average) extrapolation is **−15 % to −81 % wrong at every fraction up to 0.75**,
> while the settled-tail method is inside 7 % from 0.175 upward. The run-average method
> averages the cheap startup decile into the rate and therefore under-prices every
> adaptive-timestep transient, at every probe length.

### 5.1 ⚠ **WHAT COULD NOT BE DELIVERED — TWO SELF-CERTIFYING TESTS WERE BUILT AND BOTH FAILED, IN THE DANGEROUS DIRECTION**

A fixed fraction is calibrated on **this** case at **this** clock. The obviously better rule
would be a test the probe runs **on itself** to certify that its own `deltaT` has settled —
no calibration, no family dependence. **Two designs were built against R3's real logs and
both are ANTI-CORRELATED with the truth:**

| candidate limb | at fraction 0.10 (the probes that killed R3, 4.5× wrong) | at fraction 0.20 (accurate) |
|---|---|---|
| mean `deltaT` over the last fifth of the probe ÷ the fifth before it | **0.986, 0.970, 0.914 — reads "stationary"** | 0.62, 0.60, 0.56 — reads "not stationary" |
| mean `deltaT` over the last third ÷ the middle third | **worst deviation 14.7 %, inside a ±15 % band** | worst deviation 73.2 %, outside it |

**Both would have waved through exactly the probes that killed R3 and rejected the ones that
were right.** The cause is measured, not guessed: this case's `deltaT` keeps oscillating
with the shock hunt for the whole run, so a short-baseline stationarity test aliases against
that oscillation instead of detecting the startup collapse.

> **NEITHER IS REGISTERED. A TEST THAT WOULD HAVE PASSED THE FAILURE IT EXISTS TO CATCH IS
> WORSE THAN NO TEST, AND REPORTING THAT IS THE FINDING.** The floor is therefore a fixed
> fraction, **calibrated on this family and not claimed to generalise beyond it**, and this
> document says so rather than dressing 0.25 as a law.

---

## 6. **W3 — THE `writeInterval` GUARANTEE IS ARITHMETIC, AND IT IS CHECKED AT IMPORT**

Three identities, every term a frozen constant, all verified in `grade_vmfl046_r4.py` at
module import (`_check_frozen_arithmetic`, which **refuses** rather than warns):

| identity | value | what it protects |
|---|---|---|
| `endTime ÷ SAMPLE_DT` is a whole number | **160 samples** | the sampler can land on `endTime`; the completeness check can be exact |
| `W ÷ SAMPLE_DT` is a whole number of intervals, so a window holds `W/SAMPLE_DT + 1` **samples** | **16 intervals → 17 samples**, ≥ `MIN_WINDOW_SAMPLES` = 8 | a peak-to-peak over too few samples is not a peak-to-peak |
| `SAMPLE_DT ÷ maxDeltaT` ≥ 1 | **5.0** | `adjustableRunTime` always has a step in which to shorten and land on a write time |

**This holds at L1, L2 and L3 alike, and the reason is structural rather than lucky:** the
frozen `controlDict.template` carries **no per-level clock** — only `nPoints` is
level-dependent — so `endTime`, `writeInterval`, `maxCo` and `maxDeltaT` are literally the
same characters in all three generated dictionaries. The comparator's D1 limb additionally
verifies, per level, that the `controlDict` **that actually ran** carries exactly the graded
pair of `writeInterval` values, so the identity is tied to the run and not only to the
template.

**⚠ AND A COUNT IN R3's FROZEN REGISTRATION IS WRONG BY ONE, FOUND BY DOING THIS ARITHMETIC
RATHER THAN QUOTING IT.** R3 §6 and its `controlDict.template` both say the plateau window
*"holds 16 samples where R2's held 13"*. `W ÷ SAMPLE_DT` = 16 is the count of **intervals**;
a window closed at both ends holds **17 samples**, and the two adjacent windows share their
boundary sample, for **33 distinct samples** over the registered window. R2's *"13"* counted
samples correctly (12 intervals + 1), so **R3 compared a sample count against an interval
count.** The **direction** of R3's claim survives — 17 > 13, the limb is strictly stricter
than R2's — **and its number does not.** No gate, band, threshold or cap depends on the
figure; nothing graded moves. *Recorded here because a wrong number in a frozen document is
a finding whether or not it is load-bearing.*

---

## 7. **W1 — THE COMPARATOR WINDOW DEFECT, WHICH IS WHY R3 REFUSED**

R3's frozen comparator refused to grade with:

> `REFUSE: no downward Mach=1 crossing in sample …/centreline/0.0005/line_T_U.xy`

**The refusal was correct behaviour on that input.** At `t = 0.0005 s` — 0.6 % into the
transient — no shock has formed, the interpolating reader finds no downward `M = 1` crossing
and correctly declines to report a location. **The defect is that the reader was handed that
input at all.**

`grade()` called `shock_series()` on the **complete 160-sample history** and only then sliced
out the plateau windows. **The registered window of this gate is the last 20 % of the clock,
`t ∈ (0.064, 0.080]` — 33 samples. The other 127 could not change a single graded number,
and any one of them could refuse the whole grade. One did.**

> **A READER THAT CONSUMES DATA ITS OWN GATE NEVER ASKED FOR CAN BE REFUSED BY DATA ITS OWN
> GATE NEVER ASKED FOR.**

### 7.1 THE REPAIR, AND IT IS PROVED RATHER THAN ASSERTED

`registered_window()` selects the window **before any sample is opened**; `shock_series()`
consumes only it. **And the property is measured on the run that produces the verdict:**
`read_centreline_raw()` records every path it opens in a module-level audit, and
`audit_window_only()` **REFUSES the grade** if any recorded path lies outside the window.
The audit also **refuses if it is empty** — a control that cannot fail is not a control
(rule 3), and an audit over zero reads would make the window property vacuously true.

### 7.2 **NOTHING IS LOOSENED, AND NO GRADED NUMBER MOVES**

`windows()` already selected exactly `t ≥ endTime − 2W`. `P1`, `P2`, `P3`, `x_level` and
`x_final` are functions of those samples and of no others. **The `--selftest` BIT-IDENTITY
arm grades the same history both ways and compares the five statistics with `==`, not a
tolerance** — the claim is identity, not agreement, and it holds.

**THE REFUSAL FOR A GENUINELY MISSING CROSSING INSIDE THE WINDOW IS UNCHANGED AND IS A REAL
LIMB.** A window sample with no downward crossing means the shock is not resolvable in a
profile the gate depends on, and reporting a location from it would be a guess.
`--selftest` plants exactly that — a shockless profile substituted for the final sample,
deep inside window A — and requires the refusal.

**The structural completeness check is NOT weakened.** `centreline_history()` still demands
all 160 samples exist at their exact times and refuses if one is missing. **It enumerates
directory names and tests file existence; it opens nothing.** The distinction between *which
files must EXIST* and *which files may be READ* is the whole repair.

---

## 8. THE GATE — **UNCHANGED, AND THE COMPARATOR CANNOT PRINT A `PASS`**

| limb | value | provenance |
|---|---|---|
| primary reference | **`x_shock` = 1.250 m** | R1's frozen analytical normal-shock location, **UNCHANGED**; independently confirmed at 1.248513 m by R3 §3 |
| band | **5 %** (half-width 0.0625 m) | **UNCHANGED from R1, R2 and R3** |
| plateau | **`DELTA_X = 6.250e-04 m`** | **UNCHANGED from R2/R3**, which adopted it unchanged from charter `§31`. Not chosen by this document |
| plateau statistic | `ptp` over two adjacent windows `W = endTime/10`, plus their mean drift | **UNCHANGED** |
| reader | interpolating last downward `M = 1` crossing, **consuming only the registered window** | behaviour **UNCHANGED**; the window restriction is W1 and changes no value |
| ceiling | **`GATE REACHED`** | charter `§21.2` model-sameness **DIFFERENT** (viscous 2-D NS vs inviscid quasi-1D). **`PASS` is unreachable and `grade_vmfl046_r4.py` contains no code path that prints it** |
| secondaries | observed order in [0.5, 2.5], GCI ≤ 15 % | **DEMOTE-ONLY** (`§21.3`). They may turn a pass into a fail and may **never** license one; a secondary that does **not** fire is **not** evidence of quality, and the comparator prints that beside the verdict |

### 8.1 **THE PLATEAU CONJUNCTION IS NOW EXERCISED — R3's SELFTEST NEVER TOUCHED IT**

R3's comparator carried 30 `--selftest` arms and **not one of them called `plateau()`.**
Its verdict conjunction — `ok = (P1 ≤ ΔX) and (P2 ≤ ΔX) and (P3 ≤ ΔX)` — could have been
mutated to a constant `True` and **all 30 arms would still have passed.** *A verdict
conjunction no selftest touches is an untested verdict.* Seven arms now cover it:

- **steady** → plateau; **exactly at the threshold** (`P1` **exactly** `DELTA_X`) → plateau,
  which is the only construction that distinguishes `<=` from `<`, and a further arm asserts
  `P1 == DELTA_X` bit-exactly so that discrimination is real;
- **just over** (`P1 = ΔX(1+1e-9)`) → not plateaued;
- **`P1` alone over**, **`P2` alone over** → not plateaued;
- **`P3` decides** → `P1` and `P2` both sit **exactly at** the threshold and pass, and the
  mean drift `32/17 · ΔX` is what fails. **This arm proves `P3` is not redundant**, which is
  not obvious: because the two windows *share* a boundary sample, `P3 ≤ (16/17)(P1 + P2)`,
  so `P3` can never fire while `P1` and `P2` are small — it can only fire when both sit near
  the threshold, and this arm is that case.

**The mutation is verified, not claimed:** forcing `ok = True` makes `--selftest` fail 4 arms
and exit **1** under **both** `python3` and `python3 -O` (§12).

---

## 9. THE TWO PRE-REGISTERED BRANCHES — **BOTH FROZEN BEFORE COMPUTE, AND CARRIED FORWARD FROM R3 UNCHANGED IN SUBSTANCE**

> **BRANCH (a) — EVERY LEVEL PLATEAUS.** Roache triple on `x_shock`: if not `CONVERGING`,
> **`NOT A RESULT`** (rule 5 step 2), value and both triples printed beside it. If
> `CONVERGING`: **`GATE REACHED`** inside the 5 % band with no secondary fired,
> **`GATE FAIL`** outside it or with a secondary fired.
>
> **BRANCH (b) — ANY LEVEL FAILS THE PLATEAU AT `endTime = 0.080 s`.** Verdict
> **`NOT A RESULT`** (rule 5 step 1), with every level's P1/P2/P3 and its multiple of
> `DELTA_X` printed beside it. R4 has a **physical clock**, so a non-plateau here is a
> **measured unsteadiness with a frequency in Hz**, and it means the manual's *steady*
> reference is inapplicable to this configuration at this resolution. **That is a finding
> for Sanaa's desk under `§37.4`'s "the question is OPEN", not a reason to widen anything.**
>
> **BRANCH (c) — A LEVEL HITS ITS CAP AGAIN (`rc 124`).** **`NOT A RESULT`
> (budget/kill class)**, and the successor is a re-file whose estimate is corrected from
> **this** run's logs by the §3 method. **NO CAP IS RAISED MID-FLIGHT AND NO PARTIAL RESULT
> IS GRADED**: `check_completion` refuses `rc ≠ 0`, a missing `End`, and a last `Time` short
> of `endTime`, and `--selftest` exercises R3's L3 cap-kill trace explicitly.
>
> **NO LOOSENED THRESHOLD, NO LONGER `endTime`, NO LARGER `maxCo` AND NO SHORTER PLATEAU
> WINDOW IS AVAILABLE AS A REMEDY IN ANY BRANCH.**

---

## 10. THE GRADING PIN — **COMPLETE, NOT "TO BE PINNED", AND RE-DERIVED AFTER THE LAST EDIT**

The grading path is fixed at this pre-registration. `git hash-object` gives the blob before
the commit exists, so there is no window in which this reads "to be pinned by blob".

| artifact | blob sha |
|---|---|
| **`grade_vmfl046_r4.py`** (**THE GRADING PATH**) | **`e09bbf3cea03c633a7dbd6b04365bfc7fe2d9ca2`** |
| `run_vmfl046_r4.sh` (**THE DRIVER**) | **`032d241cc0aa1ae637255523081d6f73b9ff2d4c`** |
| `case/0/T` | `e3dbbd24fffbbcaba1fe5424502d802e3d98b5b3` |
| `case/0/U` | `1035057ac3c4703a1439049b01a274ce10374284` |
| `case/0/p` | `b2bdcfcf658a27eb289f9ce01c2cfbab14b8baec` |
| `case/constant/fvOptions` | `cc81891fd7445e2777a245e16baf0c9b829ec299` |
| `case/constant/momentumTransport` | `f7d93d54ebae9785586564ad6eb86faf764ebcc3` |
| `case/constant/thermophysicalProperties` | `051327833c9cf108289684de01e03618f26eab66` |
| `case/constant/turbulenceProperties` | `f7d93d54ebae9785586564ad6eb86faf764ebcc3` |
| `case/system/blockMeshDict.template` | `26acdba2b5a68fc0c220c162c0b0ac84e3080948` |
| `case/system/controlDict.template` | `bbbd4ac5874b62dac668d3b6a76ebb4c93af270e` |
| `case/system/fvSchemes` | `415eab1a859050b5a34cae9f6eba2493ad0cebf9` |
| `case/system/fvSolution` | `9be09f0642f3ec592be1485e39e4f9538b6265c9` |

**Every one of the eleven `case/` blobs above is IDENTICAL to the corresponding pin in R3's
frozen registration**, which is the arithmetic face of the R3-parity assert: the byte
identity is provable from the two documents alone, without running anything.

**⚠ THE CHECKER DOES NOT CHECK MOST OF THIS, AND THE GAP IS DECLARED.**
`check_freeze_ready.py`'s **C3 verifies the COMPARATOR pin only** — not the driver, not one
of the eleven case inputs. **All thirteen pins above were therefore re-derived mechanically
with `git hash-object` AFTER the last edit to every file**, because R3's lane caught a stale
driver pin only by doing exactly that and the checker was silent about it.

**The driver re-verifies every `case/` blob against `HEAD` at launch and ABORTS on any
mismatch** (exit 6). **⚠ Disclosed limitation, carried forward from R2 and R3 and not fixed
here: that check pins to `HEAD`, not to this registration's own freeze commit; rule 6 is the
backstop.**

---

## 11. THE DECLARED DEPARTURE (N2) AND THE PLANTED CONTROLS — **CARRIED FORWARD FROM R3 UNCHANGED**

**N2** replaces rule 4's `ExecutionTime`-count limb, which an adaptive-timestep transient can
never satisfy (`int(round(0.080)) = 0` against ~35 000 lines). The replacement is strictly
stronger and every term is computable from frozen constants: **N2a** every advanced step
printed its cost; **N2b** last `Time` is `endTime` within `maxDeltaT`; **N2c** at least
`endTime/maxDeltaT` = 800 steps; **N2d** the `Time` sequence is **strictly increasing**,
catching a restart splice a bare count never would. Every other rule-4 limb is unchanged,
including **the age guard** and the driver's refusal to start on a level that already holds a
numeric time dir. **A new `--selftest` arm feeds N2 R3's own L3 cap-kill trace and requires
the refusal**, so the limb that would have caught a forged `rc` is exercised against real
numbers rather than synthetic ones.

**The plants are unchanged in design and in tolerance** — **A** the gate reader (a
`+1.000e-02 m` profile shift recovered to 25 % of the plant); **B** the plateau reducer
(planted into the window's **maximum**, a proper subset, because an interior plant is
absorbed); **C1** the reduction's translation-invariance (an inert arm whose premise is an
identity of the reals, paired with a live arm on the argmax so the inertness is shown to come
from the covering and not from a dead reducer); **C2** per-sample field read-back with the
steadiness premise removed; **D** the `T`-field reader; **N4** the frozen `limitTemperature`
bounds must be **non-binding** at `endTime`, as a **refusal** and never a printed diagnostic.

**`--selftest`: 59 arms, ALL PASS**, under `python3` **and** `python3 -O`. **There is no bare
`assert` in the comparator** — a bare `assert` vanishes under `-O` and takes its check with
it — and the count is zero by measurement, not by intention.

---

## 12. `§39.5` — **THE INTERFACE EVIDENCE, AND EVERY CONTROL SHOWN ABLE TO FAIL**

**THE CLAUSE-B SMOKE RAN UNDER A DELIBERATELY BARE ENVIRONMENT** —
`env -u WM_PROJECT_DIR -u FOAM_APPBIN PATH=/usr/bin:/bin` — which is **the exact condition
that made every one of VMFL072-R2's five queue rows refuse at rc = 2**. The driver sourced
`/usr/lib/openfoam/openfoam2606/etc/bashrc` itself, asserted `blockMesh` and `rhoPimpleFoam`
on PATH **after** sourcing, and ran: **rc 0, 0.05 core-min, L1 only, `endTime` 4.0e-04 s.**
Both parity asserts printed OK inside that bare shell.

`grade_vmfl046_r4.py --paths` against that real run root reports **all 10 L1 paths OK**
(`RUN_RC`, `log.rhoPimpleFoam`, `system/controlDict`, `system/blockMeshDict`, `0/T`, the
three fields at the written time, and two centreline samples). The two `MISSING` it reports
are the **absent L2 and L3 directories of a single-level smoke**, which is the enumerator
being honest about a partial root rather than a defect. **`grade()` REFUSES the same root**
(exit 2, *"endTime 0.0004 is not the GRADED 0.08"*), so the enumerator's leniency is not
reachable from any verdict.

**EVERY CONTROL IN THIS REGISTRATION IS SHOWN ABLE TO FAIL, ON A PLANTED NEGATIVE:**

| planted defect | result |
|---|---|
| a physics input altered | **ABORT exit 7** (R2-parity, direction 1) |
| `fvSchemes` reverted to R2's | **ABORT exit 7** (R2-parity, direction 2) |
| a numerics input altered away from R3's | **ABORT exit 7** (R3-parity, direction 1) |
| the cost envelope re-filed identical to R3's | **ABORT exit 7** (R3-parity, direction 2 — the no-op successor) |
| `CAP_LEVEL_R3` invented rather than read from R3's driver | **ABORT exit 7** |
| a case file removed | **ABORT exit 2** (the §0 path loop) |
| **the verdict conjunction forced to a constant `PASS`** | **`--selftest` fails 4 arms, exit 1, under `python3` AND `python3 -O`** |
| the unmutated control | **rc 0, both asserts OK** |

**⚠ AND THE CHECKER IS NOT `§39.5` COMPLIANCE.** `check_freeze_ready.py`'s C2 defers every
runtime-composed path as **UNDETERMINED**. **The driver's own explicit existence loop (§0,
exit 2) is what discharges `§39.5` on the driver side, and this section is what discharges it
on the comparator side.** The checker's declared gaps stand: it cannot catch a wrong field
name, it cannot catch a missing runtime environment — which is why the smoke above ran under
a bare PATH — and **its C3 checks only the comparator's pin**, which is why §10's pins were
re-derived by hand.

---

## 13. WHAT THIS REGISTRATION KNOWS, AND WHAT IT DOES NOT PRETEND

### 13.1 ⚠ **THE FREEZE CLAIM — AND THE ONE EXPOSURE A READER WOULD FIND ANYWAY**

> **R3's L1 RUN COMPLETED, ITS 160 CENTRELINE SAMPLES ARE ON DISK, AND R4's L1 WILL RUN A
> BYTE-IDENTICAL CONFIGURATION. THE L1 GATE QUANTITY IS THEREFORE COMPUTABLE TODAY, BEFORE
> THIS DOCUMENT IS FROZEN, BY ANYONE WHO POINTS A READER AT IT.**

Stated first and plainly, because a reader who found it later would be right to distrust
everything above it. What can honestly be said:

1. **This lane did not read it.** The only bytes read from R3's run root were the
   `Time = ` and `ExecutionTime = ` lines of the three solver logs. **No field, no centreline
   sample, no `x_shock`, no plateau statistic, no observed order and no GCI was computed at
   any level**, and §14 declares the complete list of what the pre-freeze work did reveal.
2. **There is nothing for a known value to be fitted to.** The gate, the band, the plateau
   threshold, `endTime`, `SAMPLE_DT`, `maxCo`, `maxDeltaT` and all eleven case inputs are
   carried forward **byte-identical or unchanged**, and each was fixed in R1, R2, R3 or
   charter `§31` — **not one of them is this document's to set.** The only numbers this
   document chooses are **cost** figures and the **`PROBE_FLOOR`**, and none of them is a
   gate quantity or can move one.
3. **The two comparator repairs cannot move a graded value either.** W1's bit-identity is
   proved with `==` (§7.2); W3 is arithmetic on frozen constants; the new plateau arms only
   add coverage.
4. **But the exposure is real and is not argued away.** A registration frozen after a
   predecessor's completed run existed carries **less** evidentiary weight than one frozen
   before, and this document does not claim otherwise. **The supervisor may prefer that R4
   re-run all three levels from scratch rather than reuse anything** — which is what this
   registration specifies — and that choice is recorded here rather than left implicit.

### 13.2 WHAT THIS DOCUMENT CANNOT VERIFY, STATED PLAINLY

- **The settling time is still an estimate.** `endTime = 0.080 s` is ≈ 20 acoustic traverses
  by R3's a-priori argument. **If it is short, R4 grades `NOT A RESULT` on branch (b) and
  that is the answer** — a longer clock is not available as a remedy.
- **The cost basis is R3's runs, not R4's.** L1's figure is a **complete measured run**;
  L2's and L3's carry an extrapolation over the last 8.5 % and 0.8 % of the clock. Both were
  cross-checked by two methods agreeing to 1.5 % and 0.11 %, and **per-step cost falls**, so
  the direction of any residual error is conservative — **but they are extrapolations and
  are labelled as such, not as measurements.**
- **The `PROBE_FLOOR` of 0.25 is calibrated on this case and this family.** §5.1 says why no
  self-certifying alternative could be registered, and that failure is a finding rather than
  an omission.
- **The 26.8 h cap ceiling is a real occupancy cost** and is flagged for the supervisor
  rather than resolved by tightening the cap.
- **Serial, `RANKS = 1`.** Parallel decomposition would cut wall time without cutting
  core-minutes, at the price of `decomposePar`/`reconstructPar` machinery that would
  invalidate the §12 path evidence. **Not taken; flagged.**
- **The `HEAD`-not-freeze-commit pin limitation of §10 is carried forward and is not fixed
  here.**

---

## 14. `§20.3` DECLARATION — **EVERY QUANTITY THE PRE-FREEZE WORK REVEALED**

**WHAT RAN BEFORE THIS FILE WAS FROZEN:** (i) `awk` over R3's three solver logs, extracting
the `Time = ` and `ExecutionTime = ` pairs and nothing else; (ii) arithmetic on those pairs
in the scratchpad; (iii) `--selftest` of this comparator, on synthetic data only;
(iv) **one CLAUSE-B smoke**, L1 only, `endTime` 4.0e-04 s, 0.05 core-min, in the scratchpad,
under a bare environment (§12); (v) the eight planted negatives of §12, in a scratchpad
fixture, none of which ran a solver except the unmutated control's 3-second smoke.

**EVERY QUANTITY THEY REVEALED, EXHAUSTIVELY:**

- the three `RUN_RC` values, `End`-line counts, step counts, last `Time` values and last
  `ExecutionTime` values of R3's runs — all of which are already on the public record in
  register row **#60**;
- the per-decile cost rates, per-step costs and mean `deltaT` values of §2 and §2.1;
- the `ExecutionTime/ClockTime` ratios of §3;
- the probe-fraction sweeps of §5 and the two failed self-certifying limbs of §5.1;
- that R3's plateau-window sample count is 17 and not 16 (§6);
- that R3's frozen comparator refuses on a `t = 0.0005 s` sample (§7) — **already the
  recorded reason for row #60's `NOT A RESULT`**;
- that R3's `--selftest` never exercised `plateau()` (§8.1);
- from the smoke: that the sampler writes 321 rows in the five-column layout into
  exact-decimal directories, and that both parity asserts run under a bare PATH.

**WHAT NONE OF IT IS:** ⚠ **not one of these is a VMFL046 GATE QUANTITY.** No `x_shock`, no
plateau statistic, no `ptp`, no mean drift, no observed order and no GCI was computed at any
level, from any run, at any point in the preparation of this document. **The CLAUSE-B smoke
ran to `endTime` 4.0e-04 s against a graded 0.080 s and its output was consumed only by the
path enumerator, which prints existence and never a value.** **No threshold, band, cap,
window or label in this document was set from any of it** — the caps come from the §3
arithmetic, the floor from the §5 sweep, and everything else is carried forward.

---

## 15. FILES

| what | path |
|---|---|
| this registration | `cases/ansys_verification/VMFL046-R4/PREREGISTRATION.md` |
| **the grading path** | `cases/ansys_verification/VMFL046-R4/grade_vmfl046_r4.py` |
| the driver | `cases/ansys_verification/VMFL046-R4/run_vmfl046_r4.sh` |
| case inputs (11 files, byte-identical to R3's) | `cases/ansys_verification/VMFL046-R4/case/` |
| run root (**must not exist or be empty at launch**) | `verification/runs/ansys_verification/VMFL046-R4/` |
| predecessor, **READ-ONLY** | `cases/ansys_verification/VMFL046-R3/` · `verification/runs/ansys_verification/VMFL046-R3/` |
| the cost basis, **READ-ONLY** | `verification/runs/ansys_verification/VMFL046-R3/{L1,L2,L3}/log.rhoPimpleFoam` |
| the inviscid control arm, **READ-ONLY** | `verification/runs/ansys_verification/VMFL046_INVISCID/` |
