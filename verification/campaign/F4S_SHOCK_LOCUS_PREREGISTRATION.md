# F4-S — shock-locus successor to the F4 conversion: PRE-REGISTRATION

**FROZEN BY THIS COMMIT.** Nothing below may be altered after the first solver of
this campaign starts; changes land only as dated addenda that cannot alter a
gate, threshold, cap or label, and originals are struck, never rewritten
(standing rule 2).

**Written 2026-08-26, before any solver in this campaign has started.**
**Frame:** repo `/home/ubuntu/Certonomous`. **Team:** cfd. **Lane:** lab-lane
under cfd-supervisor. **Compute spent at freeze: ZERO.**

**Rule-2 condition, checked by `test -e` in the freeze commit's own shell
invocation and not recalled:** the run root
`verification/runs/F4_runs/successor_2026-08-26/runs/` **does not exist** — no
case directory, no `0/`, no time directory, no `log.rhoCentralFoam`. Checked
2026-08-26T03:57:30Z: **ABSENT** — and re-checked by the launcher itself, in its own
invocation, which refuses (rc 3) if the root exists.

---

## 0. THE PREDECESSOR IS CLOSED AND THIS DOCUMENT DOES NOT REOPEN IT

`F4_CONVERSION_PREREGISTRATION.md` (frozen `3e82e989`) fired and graded at
`d4308dde`: **8 `NOT A RESULT`, 1 `CONVERGING`, 0 `PASS`, 0 `GATE FAIL`**,
calibration row **C-91**, ratio **1.389**. Rule 2 closed its gates when its first
case ran. **This document does not amend it, regrade it, or raise its cap.** It
is a new registration with its own cap, bands, ladder, detector and grading path,
and it exists to close two questions the cfd supervisor registered as open and
assigned to a successor (`F4_CAP_CROSSING_RULING_2026-08-25.md`, `6d996408`).

**F4's one surviving graded row — `G-F4-3-M8.0`, `CONVERGING` at observed order
3.1905, GCI 0.0831 % — stands on its own frozen registration. This document
neither re-litigates it nor claims it.**

---

## 1. WHAT THIS DOCUMENT DECIDES

**F4C-Q1 — WHICH QUANTITY THE CAP GOVERNS. Decided here, in terms.**
F4's launcher measured wall **24.1108** core-min (cap crossed) while its frozen
grader measured `ExecutionTime` **22.3098** (not crossed), and the frozen document
never said which quantity the cap governed. **Neither instrument was defective;
the pre-registration was.**

> **THE CAP IN §9 GOVERNS `wall seconds × ranks ÷ 60` AND NOTHING ELSE**
> (`CLAUDE.md` rule 12). **`ExecutionTime` is not wall time** — it excludes
> process startup, mesh generation and sampling — and is recorded here as a
> **SECONDARY DIAGNOSTIC that is never compared to any cap.**

**Where a per-run wall figure is read from an OpenFOAM log, it is `ClockTime`,
never `ExecutionTime`.** The two print on the same line and are different
quantities; on F6d the `ExecutionTime` sum gave ratio 0.998 and the `ClockTime`
sum gave 1.0034, so the correction moves a ratio across 1.0. **`ClockTime` has
integer-second resolution**, so the log-side wall figure carries a quantisation
bound of **±0.5 s per case = ±4.5 s = ±0.075 core-min over nine cases** (worst
case ±9 s = ±0.15 core-min). **That bound is stated, not rounded away.** The
registered cap quantity is the launcher's own `time.time()` measurement, at
sub-millisecond resolution; `ClockTime` is the log-side cross-check.

**F4C-Q2 — A CAP EVALUABLE ONLY AT THE END IS NOT A GUARD.** F4's launcher
totalled wall **after the last case returned**, so the cap was evaluable exactly
once, when every core-minute had already been spent. **It could not have stopped
a runaway of any size.** See §9.4 for what replaces it. F4's mesh and sampling
clocks were never captured, so **24.1108 was a lower bound on gross spend**;
this campaign captures every clock (§9.1).

**F4C-Q3 (this document's own question) — IS THE NON-CONVERGENCE IN THE FLOW OR
IN THE DETECTOR?** F4 confirmed *"a resolution-dependent systematic bias in the
peak-density-gradient detector itself"* and could not separate the two. §5
separates them by registering a second detector and grading both. **That is what
this campaign buys.**

---

## 2. FULL DISCLOSURE — everything this lane already knows

Naivety is impossible and is not claimed. Before writing a band this lane read
`F4_CONVERSION_PREREGISTRATION.md`, its `RESULTS.md` and the cap ruling in full.

**Standoff δ/R by the argmax detector, all nine, graded at `d4308dde`:**
M=6 `0.438012 → 0.436842 → 0.448538`; M=7 `0.428070 → 0.438596 → 0.434503`;
M=8 `0.442690 → 0.408187 → 0.418129`. All three triples `OSCILLATORY`.
**Fine-level deviations vs Billig: +2.0644 %, +2.3327 %, +0.7007 %.**
**Cp RMS:** M=6 `4.479217 → 4.207655 → 3.909620` (`DIVERGENT`, p = −0.1342);
M=7 `4.693088 → 3.850089 → 3.908692` (`OSCILLATORY`); M=8
`4.080258 → 3.889367 → 3.868458` (`CONVERGING`, p = 3.1905, GCI 0.0831 %).

**What this lane has NOT done, and it is checkable.** The registered primary gate
quantity of §5 — the Rankine–Hugoniot mid-density crossing locus — **has never
been evaluated on any F4 output, by this lane or any other, at any Mach number or
any refinement level.** No such number exists in this repository at this commit.
The only F4 sample-file values this lane read are the **two endpoints** of one
non-graded file, quoted in §7 for the intermediate-value argument.

**How the bands are protected from the knowledge above.** Every band in §6 comes
from **one formula applied uniformly to every Mach number and every level**,
whose only inputs are (i) the Billig reference and (ii) the radial cell height
read out of the **written** `blockMeshDict`. **No CFD value is an input to any
band, and §6 states the principle so a reader can check that.** The formula is
`band_abs()` in the frozen grader and all nine outputs are value-checked in
`--selftest`, so the supervisor can recompute every number without a solver.

---

## 3. THE GATES, FIXED NOW

Nine cases: M ∈ {6.0, 7.0, 8.0} × level ∈ {coarse, medium, fine}.

| gate | quantity | detector | band | label vocabulary |
|---|---|---|---|---|
| **G-F4S-1**-M | Roache triple on δ_x/R, the mean over the sustained window | **RH mid-density crossing, linear-interpolated, sub-cell (§5)** | rule 5 clause order | `CONVERGING` → the §6 band binds; else **`NOT A RESULT`** |
| **G-F4S-1B**-M | Roache triple on δ_a/R, same window | **argmax \|dρ/ds\|, the predecessor's detector, semantics unchanged** | rule 5 clause order | `CONVERGING` / **`NOT A RESULT`** |
| **G-F4S-2**-M | δ_x/R at the fine level vs Billig | as G-F4S-1 | δ_Billig ± one local radial cell (§6) | **`PASS`** inside / **`GATE FAIL`** outside / **`NOT A RESULT`** if G-F4S-1-M is not `CONVERGING` |

**G-F4S-2 is not a separate call.** It is the `band_verdict` channel of the same
`grade_ladder` call that issues G-F4S-1, computed **first and unconditionally**,
printed on every row whatever the triple did, and sealed by the instrument's own
structural check that the final verdict is **either that band verdict or
`NOT A RESULT`**. **That is rule 5's one-way door made checkable rather than
asserted in prose.** `G-F4S-1B` is graded against the same band by the same
mechanism, so the two detectors are compared like for like.

**G-F4S-1B is a full gate with a registered verdict, not a diagnostic.** A
printed discrepancy labelled "diagnostic only" is worse than one never computed.

**Gate 0 (admissibility, per case, all nine) — every clause REFUSES, and a
refusal is not a `GATE FAIL`:** strict completion (§8), the endpoint-censoring
guard and the single-valued-locus guard (§7), the free-stream guard (§7), Class C
(§10), and ladder similarity measured from the written dicts (§11).

**The Cp / modified-Newtonian limb is `PENDING`, and the reason is the point.**
`grade_ladder` refuses to grade without a pre-registered band and **will not
invent one**; no citable uncertainty for modified Newtonian pressure away from
the stagnation point is available on this box (`F4_CONVERSION_PREREGISTRATION.md`
§5.2, §13). **`PENDING: a citable reference-class uncertainty for modified
Newtonian pressure.`** The runs write the surface samples regardless, so a later
registration that finds one can grade them without new compute.

**The SWBLI limb stays `BLOCKED`** on Sanaa's unmade event-1/event-2 ruling. No
agent at any level makes that ruling.

---

## 4. REFERENCE VALUES AND THE DETECTOR THRESHOLD — theory only, full precision

**Billig cylinder standoff**, δ/R = 0.386·exp(4.67/M²) — Anderson, *Hypersonic
and High-Temperature Gas Dynamics* 2nd ed. §5.4 eq. 5.36, after Billig,
*J. Spacecraft and Rockets* **4**(6) 1967 pp. 822–823. The printed primary
coefficient **4.67** was taken from the textbook page (a web search had returned
a wrong 4.76).

| M | δ_Billig/R |
|---|---|
| 6.0 | `0.43946566521114816` |
| 7.0 | `0.4245982772504153` |
| 8.0 | `0.41521901145222184` |

**The detector threshold, ρ\*(M) = ρ∞·(1 + ρ₂/ρ₁)/2**, the mid-density of the
Rankine–Hugoniot jump, with ρ₂/ρ₁ = (γ+1)M²/((γ−1)M²+2), γ = 1.4, and
**ρ∞ = γ·p∞/T∞ = 1.4** from the registered initial conditions (`0/p` and `0/T`
are both `internalField uniform 1`; the gas is `Cp 2.5`, γ = 1.4, a = 1 at
T = 1).

| M | ρ₂/ρ₁ | ρ₂ | **ρ\*** |
|---|---|---|---|
| 6.0 | `5.268292682926828` | `7.375609756097559` | **`4.3878048780487795`** |
| 7.0 | `5.444444444444445` | `7.622222222222222` | **`4.511111111111111`** |
| 8.0 | `5.565217391304348` | `7.791304347826086` | **`4.595652173913043`** |

**Every input is theory. No value from any solve enters ρ\*.** All are
value-checked to 1e-15 in `--selftest`, together with the assertion-free check
that ρ∞ < ρ\* < ρ₂ at every M — the threshold lies strictly inside the jump, so
it cannot be crossed in the subsonic shock layer or in the free stream.

---

## 5. THE DETECTOR DECISION, AND THE PRE-COMPUTE PROOF THAT IT MATTERS

### 5.1 What is registered, and why

**The predecessor located the shock by `argmax |dρ/ds|` over a fixed 400-point
sample line. argmax over a fixed point set is a DISCRETE-VALUED functional of the
data: its output is always a member of the 400-point set, so it can only move in
whole sample intervals and cannot vary continuously with the mesh.** A Roache
triple built on it grades the detector's jumps, not the flow. F4's own census
made the scale explicit: **five of six level-to-level differences on the graded
rows were smaller than one local fine cell (7.75–7.95 quanta)** — precisely the
scale at which a discrete detector steps.

**Registered primary detector: the linear-interpolated crossing of ρ\*.** Walking
outward from the wall, the unique index *i* with ρ_i > ρ\* ≥ ρ_{i+1} is located,
and the locus is
`δ_x = dist[i] + w·(dist[i+1] − dist[i])`, `w = (ρ_i − ρ\*)/(ρ_i − ρ_{i+1})`.
**Continuous in the data, sub-cell, single-valued, and it uses a threshold fixed
from theory rather than from the profile.**

**Three alternatives were considered and are named so nobody assumes they were
missed.**
1. **More sample points.** REJECTED, with the arithmetic: the sample spacing is
   already `0.0017543859649122805` and the fine-level radial cell at the shock is
   **7.75–7.95 spacings wide** (`--selftest` checks `Δr/Δs > 7` at all three M).
   **The sample line is not the binding constraint and refining it buys nothing.**
2. **A parabolic sub-cell fit to the three points around the argmax.** REJECTED:
   it still takes its bracket from a discrete argmax over a smeared front, so it
   inherits the argmax's cell-scale jumps between brackets.
3. **A gradient-weighted centroid over a window.** REJECTED: continuous, but its
   value depends on a window whose width has no principled derivation here, and
   an arbitrary window is a fitted parameter in a gate.

### 5.2 THE PREMISE IS DEMONSTRATED BEFORE COMPUTE, AND IT IS FALSIFIABLE

`detector_resolution_demo()` in the frozen grader sweeps a **known** shock
location across **one sample interval in 20 sub-steps**, writing each profile to
disk in the solver's own `setFormat raw` format and reading it back through the
production parser. **Measured at freeze, at M = 7:**

| | result |
|---|---|
| distinct loci reported by the **registered crossing** detector | **20 of 20** |
| its worst absolute error against the known location | **4.170e-06 = 0.0024 sample spacings** |
| distinct loci reported by the **predecessor's argmax** detector | **2 of 20** |

**If the argmax locus had tracked the sweep, this document's premise would have
been wrong and the check would have said so.** It is registered as a `--selftest`
check that must pass, not as a claim.

**One honest caveat, stated first.** The demonstration uses a *synthetic*
tanh-smeared Rankine–Hugoniot profile: the numbers are synthetic, the file
format, parser, detectors and plants are the production ones. **It proves the
detectors' resolution, not that the captured shock in a real solve is
tanh-shaped.** Whether the registered locus actually converges on real output is
exactly what G-F4S-1 asks, and §15 records this lane's prediction before the run.

---

## 6. THE BANDS — derived from a stated principle, and NOT the predecessor's

**Band(M, level) = δ_Billig(M) ± Δr(M, level)**, one local radial cell height at
the shock.

**THE PRINCIPLE, AND IT IS NOT REUSED FROM F4.** F4 banded an *argmax* locus at
±1 cell on a **quantisation** argument — two shock positions inside one cell
produce the same detected index. **That argument does not carry over to a
continuous sub-cell locus and is not recycled here.** The principle registered
here is **numerical smearing**: a shock-capturing scheme spreads a normal shock
over O(1) cells, and when that captured profile is asymmetric the mid-density
crossing is displaced from the true discontinuity by up to about the local cell
height. One local cell is therefore a **conservative upper bound on the
instrument's systematic displacement**, and it is the dominant term.

**Δr is computed in closed form from the WRITTEN `blockMeshDict`, not a requested
value** (`MESH_STANDARD.md` §9.2). Radial span L = 0.7, `simpleGrading` expansion
E = 8.0 over nR cells, k = E^(1/(nR−1)), h₁ = L(k−1)/(k^nR − 1), cell *i* height
h₁k^i; Δr is the height of the cell containing δ_Billig. Implemented as
`cell_at_distance()`.

| M | coarse (nR=20) | medium (nR=40) | **fine (nR=80)** |
|---|---|---|---|
| 6.0 | ±13.3916 % | ±6.4598 % | **±3.1747 %** |
| 7.0 | ±13.8605 % | ±6.6860 % | **±3.2005 %** |
| 8.0 | ±12.7042 % | ±6.4820 % | **±3.2728 %** |

**The operative fine-level bands, in absolute δ/R** (the units `grade_ladder`
grades in):

| M | band |
|---|---|
| 6.0 | `[0.42551403932551807, 0.45341729109677825]` |
| 7.0 | `[0.4110090956234202, 0.43818745887741045]` |
| 8.0 | `[0.4016298298252267, 0.42880819307921697]` |

**The band tightens by ~2× per refinement level** — the correct signature of an
instrument-resolution band — and that property is a `--selftest` check (measured
ratios 2.073/2.035, 2.073/2.089, 1.960/1.981), so a reader can verify the
formula's behaviour across the ladder without a solver.

**The smaller floor that is NOT the band, recorded so a reader knows it was
considered.** Linear interpolation between sample points has its own floor at the
sample spacing: **±0.39921 %, ±0.41319 %, ±0.42252 %**. It is **8× smaller than
the cell height and never binds.** Registering the *smallest* available floor
while ignoring the dominant smearing term would manufacture `GATE FAIL`s that are
instrument artefacts, which is the same defect as manufacturing `PASS`es.

**WHAT THIS BAND DISCRIMINATES, STATED BEFORE THE RUN.** This lane knows F4's
three fine-level argmax deviations (+2.0644 %, +2.3327 %, +0.7007 %) and **all
three lie inside these bands.** If the crossing locus lands near the argmax locus
and the triples converge, **G-F4S-2 would return three `PASS`es and this band
would not have discriminated among them.** That is said plainly rather than
discovered afterwards. **The gate that bites in this campaign is G-F4S-1, not the
band** — see §15.

---

## 7. EVERY GATE QUANTITY CAN PASS AND CAN FAIL — proved on this solver's actual
   on-disk output, with the write path named

This class has bitten four campaigns — VMFL059, F12's `P4`, F11's `C4`, and F5c's
M4, where the gate was bound exclusively to a Re_θ that is never computed. It is
proved here, not asserted.

**THE WRITE PATH, END TO END.** `rhoCentralFoam` **(vanilla — not
`rhoCentralFoamBounded`, which is the binary that clamps)** writes
`<time>/{T,U,p,rho}` in ASCII at `writePrecision 8`; **no bounding or limiting is
applied to ρ on this path.** `postProcess -func sampleDict` then writes
`postProcessing/sampleDict/<time>/r0_T_p_rho.xy`, `setFormat raw`,
`interpolationScheme cellPoint`, four columns, `nPoints 400`. The reader
**refuses** any file whose basename does not end `_T_p_rho.xy` — the column order
comes from the name the writer chose, which closes the positional-read trap by
construction.

**CAN PASS — from real on-disk output, using only the two endpoints of the line.**
On `verification/runs/F4_runs/cyl/M7.0/medium/postProcessing/sampleDict/5.2500466487/r0_T_p_rho.xy`
(a **non-graded** case in the 2026-07-28 tree; read-only, nothing was modified):
ρ at the wall is **8.1134373** and ρ at the far end is **1.400005**. The
registered threshold ρ\*(7.0) = **4.5111111** lies strictly between them, so **a
crossing exists on this solver's real output by the intermediate value theorem** —
established without evaluating the crossing. The far-end value also confirms
ρ∞ = 1.4 to **3.6e-6 relative**, independently of the theory derivation. The M=7
fine band window is `[0.41101, 0.43819]`, which is representable on a line
spanning `[0, 0.7]`.

**CAN FAIL.** The locus is representable anywhere in (0, 0.7); a shock at 0.30 R
gives a crossing at 0.30, far outside the band. **And it is not hypothetical:**
F4's record documents the detector family returning **0.70** — the far end of its
range — at θ ≈ 60° at every resolution, and F4's census found station r5 pinned
at index 399 in **27 of 27** reads.

**THE CENSORING THAT IS PRESENT, AND THE THREE REFUSALS THAT ANSWER IT.**
1. **Endpoint censoring.** Both detectors return an index in [0, 399] whatever
   the flow does; a locus at either end is the instrument's **range limit**, not a
   measurement. Refused, at **both** detectors. Control **P1b** plants a
   dominating gradient at index 399 and requires the argmax reader to return it,
   so the guard is shown to guard a **reachable** state.
2. **No crossing at all** (a bow shock outside the sampled span) is a
   **REFUSAL**, never a value.
3. **More than one crossing** — a locus that is not single-valued — is a
   **REFUSAL**.
Plus a **free-stream guard**: if the far end of the line has moved more than 1 %
from ρ∞ the domain is disturbed at its outer edge and the case is refused, because
a standoff measured against a moving reference is not a standoff.

---

## 8. THE COMPLETION RULE (standing rule 4), and its ONE declared adaptation

Per case, all nine, every clause refusing: **`rc = 0` read back from `RC.txt`**
and never inferred (`set -e` does not gate at tool top level nor inside
`( set -e; … )`); an **`End`** line; **`Time =` count == `ExecutionTime` count**;
last logged time == latest written time directory to 1e-6; **fields `T U p rho`
present** at that time (the compressible inviscid family's set, named explicitly
rather than inherited from rule 4's thermal list); **every one NEWER than the
case's own `0/T`** — the age guard, and the launcher touches `0/T` last before
the solver starts, so it dates the run allowed to produce the answer; the
per-case wall guard `ClockTime ≤ 1200 s`; and the launch-side guard refusing any
case directory in which `0/` or a numeric time directory already exists.

**THE ONE DECLARED ADAPTATION — THE REACH TEST.** `adjustTimeStep yes` with
`maxCo 0.3` and nothing clipping the last step onto `endTime`, so landings
straddle it: F4 measured **5.9998543386, 5.9999993531, 5.99979092006,
5.999927519** below 6.0 and five above. **The registered clause is
`t_last + dt_final > ENDTIME`** — *the solver could not have taken another step
without passing `endTime`* — with `dt_final` read from **the run's own log** (the
difference of its last two `Time =` lines). **It never looks at whether the run
passed**, which is what makes it a derivation rather than a threshold fitted to
the answer.

> **A two-sided tolerance `|t_last − endTime| ≤ ε` is REFUSED as the expression
> of this clause and is named here so it cannot be reintroduced.** Choosing ε
> after seeing which runs it admits is the fit rule 2 exists to prevent, and it
> would be no better for coming from a supervisor.

**Rule 4 loses no refusing power.** A run that died at the previous write sits at
5.625 with a Δt of order 1e-4 and is still refused. **The clause is self-scaling**
and registers no constant a later mesh or a different `maxCo` could invalidate.
`t_last ≤ endTime·1.001` is retained as the runaway guard.

**Why this clause is written in a successor and not inherited quietly.** F4's
grader was first drafted as `t_last ≥ endTime`, which **would have refused four
of nine genuinely complete runs**, scattered with no pattern in Mach number or
refinement, and reported as `NOT A RESULT` inside a campaign that returned eight
`NOT A RESULT`s for real reasons. **The two would have been indistinguishable in
the record.** A gate that fails totally announces itself; a gate that fails
partially, at random, disguises itself as a finding.

---

## 9. COST (standing rule 12), AND A CAP THAT IS ACTUALLY A GUARD

### 9.1 The basis — measured, and every clock captured this time

| limb | value | basis |
|---|---|---|
| nine solver runs, **wall × ranks ÷ 60** | **24.1108 core-min** | **MEASURED** — `conversion_2026-08-25/RESULTS.md` §1.3, calibration row **C-91**, np = 1, at a launcher-measured load of **11.14 rising to 15.05** of 16 |
| `blockMesh` + `checkMesh`, nine cases | **4.4930 s = 0.07488 core-min** | **MEASURED** — `t_mesh_s` + `t_check_s` in the nine `verification/runs/F4_runs/cyl/*/*/result.json` |
| sampling, nine cases, scaled 3 → 8 snapshots | **14.7326 s = 0.24554 core-min** | **MEASURED basis** (`t_sample_s`, 5.5247 s at 3 snapshots), **linearly scaled — an ESTIMATE in the scaling** |

**F4's 24.1108 was a lower bound because the last two rows were never captured.
Here the launcher clocks `blockMesh`, `checkMesh`, the solver and both sampling
passes separately, so the reported gross is a measurement.**

### 9.2 The prediction, arithmetic shown

- Solver wall basis: **24.1108** (measured).
- `nWrites` 8 → 16 (§10 needs the sample count): **+5 % = +1.2055**. **ESTIMATE.**
- Mesh + checkMesh, `0.07488 × 1.5` contention = **0.1123**. **ESTIMATE in the factor.**
- Sampling at 8 snapshots, `0.24554 × 1.5` = **0.3683**. **ESTIMATE in the factor.**
- Grading: pure Python, no solver, **≤ 0.5**. **ESTIMATE.**
- **PREDICTED TOTAL: 26.30 core-minutes**, ranks = 1, nine cases.
- Dollars: 26.30 core-min = 0.43833 core-h × $0.0513/core-h = **$0.02249 —
  DERIVED, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5: the box cannot read
  its own billing; the rate is owner-stated).

**The 1.5 contention factor is applied only to the mesh and sampling limbs**,
because the 24.1108 solver basis was *itself measured on a near-saturated box*
and already carries its contention. **The load at launch is measured by the
launcher in its own invocation** and written to `LAUNCH_LOAD.json` — never a
figure relayed from a brief. C-91's 1.389 miss came from a supervisor's stale
3.70 while the box was at 11.14, and that error is on the board.

### 9.3 THE HARD CAP

> **HARD CAP: 36.0 core-minutes**, on **wall × ranks ÷ 60**, summed over the
> solver, `blockMesh`, `checkMesh` and both sampling passes of all nine cases.
> **Per-case runaway guard: 1200 wall s.**

36.0 is **1.369× the §9.2 prediction** and **1.493× the measured solver-wall
basis**. The known F4 runaway mode does **not** announce itself as a CFL blow-up
(an exploratory run reached t ≈ 9.3 with Courant numbers bounded throughout), so
a loose cap would not catch it. At 1.369×, a single fine case running ~1.6× its
basis trips the batch. **1200 s is 2.73× the slowest measured case (439.3 s
wall)** and well under `COMPUTE_BUDGET_CHARTER.md`'s 3600 s stall definition.

**If the cap is crossed the batch STOPS and it is REPORTED to the cfd supervisor,
who decides. This lane does not extend a cap** and does not stop work to save
money — cost is not what is being guarded.

**Dollars at the cap: 36.0 core-min = 0.6 core-h × $0.0513 = $0.03078 — DERIVED,
NOT MEASURED.** Under the $25 pre-authorisation, and **still costed here**,
because a blanket is not a per-item read (rule 9).

### 9.4 THE CAP IS CHECKED INCREMENTALLY AND THE LAUNCHER HALTS — F4C-Q2 closed

**Nothing in this document is totalled only at the end.** `launch_f4s.py`:

1. **Dispatches SERIALLY, concurrency 1.** Concurrency would put cases in flight
   that a halt cannot stop, and an unstoppable in-flight overrun is exactly the
   defect this rewrite removes. **Elapsed time (~30 min) is spent to buy a real
   guard.**
2. **Converts the remaining budget into the next case's solver timeout:**
   `timeout = min(1200 s, (CAP − running_total) × 60 / ranks)`. **No single case
   can carry the batch past the cap** — the solver is killed at the remaining
   budget. The residual overrun is then bounded by that case's mesh and sampling
   clocks (seconds), and it is measured and reported, never absorbed.
3. **Refuses to start a case at all** when the remaining budget is under 60 s,
   writing `CAP_HALT.json` with kind `PROJECTED`.
4. **Re-checks the running total after every case** and halts with kind
   `CROSSED`, launching nothing further.
5. Writes the running total to `RUN_LEDGER.json` with `fsync` after every case,
   so a halt is legible even if the launcher itself dies.

### 9.5 The calibration row owed at completion

Rule 12's estimate-versus-actual comparison is owed at completion and lands as a
row in `docs/COST_CALIBRATION.md`: actual core-minutes wall from
`RUN_LEDGER.json`, the ratio against **26.30**, the gap attributed (contention /
waste / misprediction) with **waste named separately and never absorbed into the
ratio**, and dollars **derived, not measured**. **The row id is re-derived
tolerantly and by hand from the HEAD blob inside the committing shell
invocation** — matching both plain and bold id forms. Rule 11's id race bit three
times in one lane on 2026-08-25 (C-87 → C-90 → the row landed C-91).

---

## 10. CLASS C — temporal convergence of the locus, all four elements

Graded over the **sustained window: the last 8 of 16 write times**,
t ∈ [3.375, 6.0]. The floor is `Δr(M, level)`, the same mesh-derived local cell
height as §6; **no measured deviation enters it.**

| element | registered clause | reports |
|---|---|---|
| 1 **sustained window floor** | peak-to-peak spread over the **whole 8-snapshot window** ≤ Δr — evaluated over a window, never at one instant | feeds `iterative_states` |
| 2 **trend fit** | \|OLS slope\| × window duration ≤ Δr **AND** the absolute increments must not be strictly growing — **a growing series is rejected even when its net slope is small** | feeds `iterative_states` |
| 3 **stationarity** | \|mean(second half) − mean(first half)\| ≤ Δr/2, and it **CAN report NOT stationary** | feeds `plateau_states` |
| 4 **minimum sample count** | **fewer than 8 snapshots in the window is a REFUSAL (exit 2)**, never a grade | refuses before either |

**Element 4 is the one most likely to be quietly dropped, BECAUSE DROPPING IT
ALWAYS MAKES A RUN GRADEABLE.** It carries control **P5** and a **mutation** that
must fail. **One residual reading is not evidence of convergence**, and
`nWrites` is raised 8 → 16 for this gate alone — **not as a fix for the detector,
which §5 establishes is the binding constraint.**

`iterative_states` and `plateau_states` are handed to `grade_ladder`, which is
where rule 5 clause (a) lives.

---

## 11. THE LADDER AND THE PINNED INSTRUMENT

**Similarity is measured from the WRITTEN dicts** (`MESH_STANDARD.md` §9.2 — *the
requested value is the thing that lied*). `measure_similarity()` parses the `hex`
line out of each case's `system/blockMeshDict` and refuses unless cell counts are
exactly 1000 / 4000 / 16000, `(nθ, nR)` exactly (50,20) / (100,40) / (200,80),
written radial grading exactly 8.0, `|r21 − r32| ≤ 1e-9`, and near-wall
first-cell heights refining within 5 % of 2 (**a convention, not a derivation —
named in §17**). F4 measured r21 = r32 = **2.000000** and h₁ ratios **1.982046 /
1.991308**; `LADDER_RECIPE_CONSISTENCY_SWEEP_2026-08-10.md` classifies this
ladder **single-recipe (CLEAN)**, so a non-monotone triple here is a property of
the detector or the flow and cannot be dismissed as a recipe fork.

**The instrument:** `scripts/roache_triple.py`, `dim = 2`, `fs = 1.25`,
**`form = "equal"` and never `"auto"`** — `"equal"` REFUSES when
`|r21 − r32| > 1e-9`; `"auto"` silently falls through to the Celik unequal
formula, and a silent fallback is how a mis-built ladder gets a plausible order.
`--selftest` checks `FORM == "equal"` and `FS == roache_triple.FS`.

**FORBIDDEN INSTRUMENT:** no GCI, observed order or Richardson value here comes
from `sdk/workflows/tmr_verification.py` — three implementations in this
repository quote a negative GCI (−10.714 %) on a divergent triple and that is one
of them. `grade_f4s.py` does not import it and contains **no triple
implementation of its own**.

**Rule 5's clause order, as registered:** (1) any level not iteratively converged
or not plateaued (§10) → **`NOT A RESULT`**; (2) triple `DIVERGENT`, `STAGNANT`,
`OSCILLATORY`, `EXACT` or `NO_ORDER`, or not monotone → **`NOT A RESULT`**, with
values, states and orders printed beside it and **`GCI_pct` returned as `None`**;
(3) `CONVERGING` and monotone → GCI at Fs = 1.25 printed, and the §6 band binds.

---

## 12. PLANTED-ZERO CONTROLS (standing rule 3) — every one REFUSES (exit 2)

All run **before any gate is graded**. A zero — or any number — from a reader not
shown able to see a non-zero is not evidence.

| control | what is planted | what must happen | what it rules out |
|---|---|---|---|
| **P0** | `PLANT = 1.234e-03` added to ρ at the crossing's own bracketing index, in a copy written at full precision | read back through `read_xy` with delta = PLANT to 1e-12 | **this is the control `grade_ladder` itself consumes**; it refuses without it |
| **P1** | the ρ column shifted by **+7** and by **−11** whole sample intervals, in a copy whose distance column is bit-identical | the located crossing must move by **exactly** that many indices with a **bit-identical** interpolation weight | a reader that ignores the file or returns a constant. **Two shifts, opposite directions**, so luck cannot pass one. **Exact, not tolerance-bounded.** |
| **P1b** | a dominating gradient at index **399** | the frozen argmax reader must **return 399** | an endpoint guard guarding an unreachable state |
| **P2** | a plant into **`r3_T_p_rho.xy`** (θ ≈ 36°), a station the θ = 0 gate does not select | the gate value must be **bit-identical** before, during and after, and the file must restore **byte for byte** | **the negative control: the selector must be UNABLE to see a plant at a station it did not declare** |
| **P3** | the written medium `blockMeshDict` perturbed `(100 40 1)` → `(100 41 1)` | `measure_similarity()` must **stop** calling the ladder similar | a similarity check that always says yes, indistinguishable from no check |
| **P4** | synthetic flat / ramp / growing-increment series | flat → CONVERGED+PLATEAUED; ramp → **NOT** both; growing increments → **rejected by the trend fit** | a stationarity test that cannot report NOT stationary |
| **P5** | a 7-snapshot window | **REFUSAL** | Class C element 4 being quietly dropped |
| **C1** | two synthetic cases **built on disk**, landing under `endTime` by **0.4·Δt** and by **3·Δt** | accept the first, **refuse** the second | a completion checker that cannot tell a real `adjustTimeStep` landing from an early stop. **P0–P3 are about the READERS**; this is how the reach-test defect survived a 21-check selftest in the predecessor |

**Mutation-tested — three mutations that MUST fail:** a `class_c` stub that never
refuses must break **P5**; the same stub must break **P4**; a `check_completion`
that never refuses must break **C1**.

**P0, P1, P1b and P2 are exercised END TO END before compute** on a file written
in the production format and read by the production parser
(`controls_on_synthetic()`), and again on the real sample files at grade time —
**an unrun control is not a passed one.**

**A hazard this creates, and the guard.** P2 and P3 mutate files and restore
them; aimed at a graded tree they could break its age guard. `grade_all()`
therefore **refuses any root whose path does not contain `successor_`**, verified
to exit 2. **An instrument that could silently corrupt the artifact it measures
is a hazard, not an instrument.**

**`shutil.rmtree` appears exactly once in the grading path, inside
`rmtree_tmp_only()`, which REFUSES any path outside the system temp directory.
A dirty case directory is answered by a REFUSAL, never a delete.**

---

## 13. THE RUN MATRIX

Nine cases, run root
**`verification/runs/F4_runs/successor_2026-08-26/runs/cyl/M<M>/<level>/`**.

| | coarse 50×20 | medium 100×40 | fine 200×80 |
|---|---|---|---|
| **M = 6.0** | ✓ | ✓ | ✓ |
| **M = 7.0** | ✓ | ✓ | ✓ |
| **M = 8.0** | ✓ | ✓ | ✓ |

Solver **vanilla `rhoCentralFoam`**, inviscid (μ = 0), γ = 1.4, `endTime = 6.0`,
`adjustTimeStep yes`, `maxCo 0.3`, `maxDeltaT 1e-3`, **`nWrites = 16`**,
sustained window **last 8**. Case generation by `make_cylinder_case.py`, sample
dicts by `run_cylinder_case.write_sampledicts` (7 stations, `nPoints 400`,
`interpolationScheme cellPoint`, `setFormat raw`) — **both resolved against the
disk by the launcher in its own invocation** (`resolve()`), because the
`a1fbe127` reorg left ~140 tracked scripts citing a tree that no longer exists.

**Ranks: `np = 1`, all nine.**
**DECOMPOSITION SEED: `none` (identity; `decomposePar` is NOT invoked; np = 1).**
Recorded explicitly and written into every `RUN_LEDGER.json` row, never omitted.

**Execution constraints:** serial dispatch, one case at a time (§9.4);
**no process this lane did not start is touched, reniced or killed.**

**Log capture is an assertion, not a hope.** `.gitignore` hides
`verification/runs/*_runs/**/log.*` and `F4_runs` matches;
`git update-index --add` bypasses ignore rules so the logs **can** land, and the
standing requirement is the **assertion that they did** — every log path
confirmed in `git diff-tree --stat` before `commit-tree` and
`git cat-file -e HEAD:<logpath>` after, failing loudly on any miss. On the
predecessor `check-ignore` confirmed **all 45 logs** would otherwise have been
silently dropped.

---

## 14. THE GRADING PATH, FIXED AT THIS COMMIT

**`verification/runs/F4_runs/successor_2026-08-26/grade_f4s.py`**
— HEAD blob **`9585c90606aa7e60b985ed5d7c6e115e020667b4`**, sha256
**`c67cfe06b2ff324bd0ac53807d3b63b85672e00353abac6bddd1d69c13ca621d`**.
**`--selftest` passes 52 checks including 3 mutations that must fail.**

**`verification/runs/F4_runs/successor_2026-08-26/launch_f4s.py`**
— HEAD blob **`ea49d2c7709598f8b3892d25ea5310c75cc669a4`**, sha256
**`a2b19de73f3e662dcd4ebe44b46949790851f9895863b49efe2961692ebc7eca`**.

Before grading, the file that runs is hashed against the blob above; a mismatch
is a **refusal**, not a note.

**Four structural properties of this path, each verified rather than claimed:**

1. **`grade_ladder` is CALLED DIRECTLY, with `iterative_states` and
   `plateau_states` supplied.** F4's grader called `triple_from_cells` and never
   `grade_ladder`, so rule 5 clause (a) was **unreachable for all nine rows** —
   the `ABSENT` defect. There is **one production call site**, `grade_f4s.py`
   line 1012. **Grep with a planted control:** the same grep on a copy with the
   call renamed returns **0** hits, so it can distinguish. **Runtime control:**
   `--selftest` checks `grade_f4s.grade_ladder is roache_triple.grade_ladder`
   (True), and separately that omitting `iterative_states` **REFUSES** and that
   a level marked `NOT CONVERGED` reaches `NOT A RESULT` — **clause (a) is shown
   to be reachable, not assumed to be.** This file contains **no triple
   implementation of its own** (`triple_from_cells`, `gci_equal`, `richardson`:
   zero occurrences).
2. **A hard `-O` refusal at entry: `sys.exit(2)` if `__debug__` is False, before
   anything else runs.** `grade_ladder` reaches its gate through four `assert`
   statements in the **shared** `scripts/roache_triple.py` (`:195, :632, :634,
   :637`), three of which carry standing rules 1 and 5. **That instrument is
   referred to verification and is NOT this lane's or this team's to edit;** the
   entry refusal makes its exposure irrelevant at the boundary this document
   owns. **Driven for real as a registered control:** `python3 -O grade_f4s.py
   --selftest` **exits 2**. The launcher carries the same refusal (verified,
   rc = 2).
3. **Zero `Assert` nodes, checked by AST parse and not by grep** — `grade_f4s.py`
   **0**, `launch_f4s.py` **0**, and the grader AST-checks *itself* at the top of
   `grade_all()` and refuses on any. **No `assert` carries a refusal, guard,
   control or gate anywhere in this path (L-332).**
4. **No unconditional success print.** The `SELFTEST PASSED` line sits **inside**
   the passing branch, so removing the checks removes the claim.

---

## 15. WHAT EACH OUTCOME MEANS, AND THIS LANE'S PREDICTION — RECORDED BEFORE THE RUN

**Registered so it can be scored wrong.** F4's own prediction scored **8 of 9**
and the one miss (reading monotonicity as convergence) is what made the other
eight worth anything.

- **G-F4S-1B (argmax): `OSCILLATORY` → `NOT A RESULT` at all three Mach
  numbers.** The solver is deterministic and reproduced 2026-07-28 to 4–5
  significant figures; the only changes are `nWrites` and the window, which §5
  establishes are not the binding constraint. **High confidence.**
- **G-F4S-1 (crossing): `CONVERGING` at at least TWO of the three Mach
  numbers.** The level-to-level differences that made the argmax triples
  non-monotone were **7.75–7.95 sample quanta ≈ one fine cell** — exactly the
  scale at which a discrete detector steps. If those steps are detector
  artefacts, a continuous sub-cell locus should settle.
- **G-F4S-2:** binding only where G-F4S-1 is `CONVERGING`; on the deviations this
  lane has seen, `PASS` is the likely value verdict there (§6 says so plainly).

| outcome | what it means |
|---|---|
| G-F4S-1 `CONVERGING` where G-F4S-1B is `NOT A RESULT` (**predicted**) | **F4's non-convergence was the DETECTOR, and it is now measured rather than diagnosed.** A defensible standoff verdict is recovered on the same solver, same mesh, same runs — and the two detectors graded side by side under one registration are the evidence. |
| **Both** `NOT A RESULT` at all three M | **The prediction is WRONG and the finding is bigger than the prediction was.** The non-convergence is in the captured-shock solution, not in the detector — a result F4 could not distinguish and this design can. It is reported as such, not softened. |
| G-F4S-1 `CONVERGING`, G-F4S-2 `GATE FAIL` | The ladder converges and the converged answer is more than one local cell from Billig. A real disagreement, resolved above the instrument. |
| G-F4S-1B `CONVERGING` too | This document's §5 premise is weaker than stated, and §5.2's demonstration is the thing to re-read first. |
| Any case fails §7, §8 or §10 | **Refusal**, and the gate is `NOT A RESULT`. **A crash or a timeout is `NOT A RESULT`, NEVER `GATE FAIL`** — the gate can only turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse. **A crash is a FINDING about the case, the method or the toolchain until triage says otherwise, and triage is the supervisor's and is not delegated.** |

---

## 16. WHAT THIS DOCUMENT DOES NOT CLAIM

- **No P-tier claim.** Billig is a **correlation**; `F_FAMILY_TRIPLE_CROWN_SURVEY.md`
  line 152 records that F4 cannot reach the P tier via its own references. This
  campaign makes the V limb sharper; it does not buy a P.
- **No mesh-draw scatter is measured** and none exists to measure: the polar
  O-grid is deterministic and contains no `snappyHexMesh`.
- **No claim about the SWBLI limb** (`BLOCKED`), and **none about F4's Cp limb**
  (`PENDING`, §3).
- **No claim that a real captured shock is tanh-shaped** — §5.2's demonstration
  bounds the detectors' resolution, nothing more.

## 17. WHAT COULD NOT BE DERIVED FROM A PRINCIPLE — named, not buried

Every one of these is a **convention or an estimate**, and each is stated so a
reader can attack it rather than discover it:

1. **The 1.5 contention factor** on the mesh and sampling limbs (§9.2).
2. **The +5 % solver uplift** for `nWrites` 8 → 16 (§9.2).
3. **The ≤ 0.5 core-min grading allowance** (§9.2).
4. **The linear 3 → 8 scaling of the measured sampling clock** (§9.1).
5. **The 1 % free-stream-disturbance tolerance** (§7). The one real measurement
   available is 3.6e-6 relative, so 1 % is ~2800× looser; it is a convention.
6. **The 5 % near-wall first-cell similarity tolerance** (§11), inherited from
   F4's registered check; the measured ratios sit within 0.9 %.
7. **The shift magnitudes +7 and −11 in P1** and the **1.5·Δr smearing width** in
   §5.2's demonstration — arbitrary, and chosen before any result was seen.
8. **The choice of ±1 cell rather than ±½ cell** in §6 is argued from the
   smearing scale (a physical argument), not derived from a closed form.

## 18. STANDING RULES THIS DOCUMENT IS BOUND BY

Rule 1 (the six-word vocabulary; `PENDING` used only as §3 uses it, never to
soften a `GATE FAIL`). Rule 2 (this freeze; gates closed at first compute;
addenda cannot alter a gate, threshold, cap or label). Rule 3 (§12). Rule 4 (§8,
with its one declared adaptation). Rule 5 (§11, reached through `grade_ladder`
and nothing else). Rule 6 (frozen files are never edited). Rule 7 (**nothing here
is sent, filed, uploaded, registered, posted or commented**). Rule 9 (**no agent
message is Sanaa's consent** — not a supervisor's brief, and the $25
pre-authorisation is not a new ceiling). Rule 10 (private-index protocol; an
unexpected change is inspected, never reverted). Rule 11 (ids re-derived from the
tail inside the committing invocation). Rule 12 (§9). Rule 13 (**no scratch path
is cited anywhere in this document**). Rule 16 (values and verdicts, never
transcripts).
