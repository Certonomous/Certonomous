# PRE-REGISTRATION — VMFL069-R2: Two Phase Poiseuille Flow

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, March 2026 — printed
page 205 (Test Case, Materials/Geometry/Boundary Conditions table and Analysis
Assumptions), printed page 206 (Figure .69.2, the only Results Comparison this case
carries).** The printed page maps to **PDF page 219** (offset 14), verified here by
`pdftotext -f 219 -l 219`, whose first line is *"VMFL069: Two Phase Poiseulle Flow"*
— the manual's own spelling, reproduced.

Sidecar title-page verified against the PDF beside it under `CLAUDE.md` rule 15 on
2026-08-30 by the drafting lane: the PDF's page 1 reads *"Ansys Fluid Dynamics
Verification Manual / ANSYS, Inc. / Southpointe / 2600 Ansys Drive / Canonsburg, PA
15317 / Release 2026 R1 / March 2026"*. **Not by filename, file type or hash.**

Drafted by `ansys-lane-opus48` (Opus 4.8), **2026-08-30**, for the supervisor to
freeze. This file is a frozen file under `CLAUDE.md` rule 6 from the moment its commit
lands: departures are dated addenda at the foot, never edits above.

**R2 SUCCESSOR TO THE CLOSED REGISTRATION `cases/ansys_verification/VMFL069/`.** VMFL069
R1 was frozen 2026-08-30, launched 22:51:45Z and **DIED**: interFoam took SIGFPE (rc
136) at t=69 of a registered endTime 2000, after 3 wall seconds. R1's verdict is
`NOT A RESULT` (R1's registered outcome 8), and R1's frozen files are **CLOSED** —
this registration does not touch them. R2 is a **NEW registration**, frozen before any
compute, on the ansys-verification supervisor's ruling of 2026-08-30 `[lab-attributed]`
that VMFL069-R2 is authorised. **R2 is not a retry and it does NOT supersede R1:** R1's
`NOT A RESULT` row stands, and R2 will earn a new row of its own. It is the successor
whose single physics change fixes the root cause of R1's death (sec.7, sec.8).

---

## 0. THE RULE-2 CONDITION, AND HOW IT WAS CHECKED

**NOT YET RUN. NO VMFL069-R2 SOLVER HAS EVER STARTED, ANYWHERE ON THIS BOX.** The gate,
the bands, the ceilings, the mesh family, the cap, the Courant control and the named
outcomes below are therefore **predictions**, which is the entire evidentiary content
of this document.

Checked at **2026-08-30T23:18:00Z** (repository HEAD `1a7121ca286404fa00a271fae88a6aaf9503278d`),
stated so a reader can re-run each check rather than take it on trust:

| condition | how it was checked | result |
|---|---|---|
| the run root does not exist | `test -e verification/runs/ansys_verification/VMFL069-R2` | **false** |
| no VMFL069-R2 artefact exists anywhere under the repository | `find . -iname '*VMFL069-R2*'` outside the new case directory | **zero hits** |
| the register carries no VMFL069-R2 row | `grep -c VMFL069-R2 verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` | **0** |
| this case directory holds no `0/` and no numeric time directory | it contains only `case/`, `artefacts/`, this file, the comparator and the launcher | **no answer on disk** |

**There is no VMFL069-R2 number on this box for any band, ceiling or window in this
document to have been fitted to.** And there is no VMFL069 R1 gate number either — R1's
gate was **never reached** (it died at t=69 of 2000, before any level completed or was
graded), so **no R1 gate quantity exists to have fitted R2's bands to** (sec.5, sec.7).

**Amendments before first compute are legal and must restate this condition and how it
was checked, naming the run directory that does not exist
(`verification/runs/ansys_verification/VMFL069-R2/`). After first compute the gates
close: dated addenda only, and no addendum may alter a gate, threshold, band, cap,
level, ceiling or the Courant control.**

**ONE FILE IS WRITTEN AFTER THIS FREEZE AND IT CHANGES NOTHING GATED.**
`PREFLIGHT_SMOKE_RECORD.txt`, if minted, records a post-freeze **toolchain** smoke: the
launcher's own `VMFL_SMOKE` mode, which refuses any run root outside a scratch area,
runs **L1 for 3 time steps** in a scratch copy and computes **no gate quantity**. It is
a **record, not an amendment**, and the graded run root still does not exist when it is
written.

---

## 1. THE TEN-LINE FORM

```
1.  CASE       : VMFL069-R2 -- Two Phase Poiseuille Flow, manual p.205.
                 Solver = interFoam (OpenFOAM v2606), laminar, two incompressible
                 phases of EQUAL density with a FLAT, NON-DEFORMING interface at
                 mid-height; 2-D; streamwise CYCLIC pair driven by a constant
                 -dp/dx = 0.5 Pa/m applied as an fvOptions body force. IDENTICAL
                 physics and mesh to R1; the ONLY change is the time-stepping.
2.  REFERENCE  : THE EXACT SOLUTION OF THE SAME CONTINUUM MODEL, INHERITED
                 BYTE-UNCHANGED FROM R1 and re-derived independently inside the
                 comparator:
                   lower-layer volume-mean u_x = 10           m/s   (EXACT)
                   upper-layer volume-mean u_x = 50/3         m/s   (EXACT)
                   whole-channel  volume-mean = 40/3          m/s   (EXACT)
                 The manual prints FIGURE .69.2 ONLY -- no Target table, no Ansys
                 number is used anywhere.
3.  CEILINGS   : limb A (lower-layer mean)  -> PASS   } INHERITED BYTE-UNCHANGED
                 limb B (upper-layer mean)  -> PASS   } FROM R1. CONTINUUM-EXACT
                 limb C (L2 profile error)  -> PASS   } on a Roache triple. Ground
                 in sec.3; the PASS ceiling is SETTLED for this team by charter
                 §11.1 -- there is NO deferred gate question here (charter §11.2).
4.  GATE       : |lab - exact| / |exact| <= 0.01 at the FINEST level L3 for limbs
                 A and B; normalised L2 profile error <= 0.01 at L3 for limb C;
                 AND a CONVERGING Roache triple on EACH limb (CLAUDE.md rule 5).
                 BYTE-UNCHANGED FROM R1 (TOL = 0.01, FS = 1.25, r = 2, P_MIN 0.05).
5.  CONTROLS   : planted zero in TWO stages on TWO independent channels
                 (velocity, alpha), each with a BLIND-WRITER negative arm; the
                 completion clauses; the interface-stationarity, streamwise-
                 invariance, mesh-structure and plateau clauses; the fvOptions
                 marker clause. ALL INHERITED BYTE-UNCHANGED FROM R1 (sec.8, sec.10).
6.  FAMILY     : three levels, r = 2 in BOTH directions, cells 256 / 1 024 /
                 4 096 (8x32, 16x64, 32x128). Uniform; NY even so the interface
                 lies on a cell FACE. INHERITED BYTE-UNCHANGED FROM R1.
7.  TIMESTEP   : *** THE ONLY THING R2 CHANGES. *** adjustTimeStep YES with a
                 registered maxCo = 1.0 and maxAlphaCo = 1.0. R1 ran
                 adjustTimeStep NO at deltaT 1 s, its maxCo limited NOTHING,
                 Courant reached 2.87e9 and it took SIGFPE. This BREAKS rule 4's
                 "ExecutionTime count == endTime" clause, which is ADAPTED (NOT
                 waived) BEFORE compute in sec.6, per VMFL063 sec.6 clause 4.
8.  COMPLETION : CLAUDE.md rule 4 in full, with ONE declared clause-5 adaptation
                 for the variable step count (sec.6). Every other clause -- rc 0,
                 an End line, LAST TIME == endTime, fields present, the age guard,
                 the plateau -- is UNCHANGED and each still gates. The comparator
                 REFUSES (exit 2) rather than grade a partial run.
9.  COST       : ESTIMATE ~2160 core-min, RANKS = 1 (L3 dominates, ~1900 core-min
                 ~32 wall-h). CAP 5000 core-min RUNNING TOTAL. An overrun STOPS
                 the run (rule 12); endTime is never reduced to fit a cap.
                 cost_basis $0.0513/core-h, REPORTED-BY-OWNER, not measured.
                 Estimate transferred WITHIN this case from R1's L1 per-step
                 timing -- disclosed as unreliable (sec.9, C-199).
10. PREDICTION : (a) if R1's blow-up was a NUMERICAL CFL instability, maxCo = 1
                 removes it and the run reaches the discretisation-error-only
                 steady state the case is built to measure -- predicted observed
                 order near ONE (arithmetic face viscosity at the interface,
                 inherited from R1 sec.9). (b) if it was a PHYSICAL 2-D
                 instability of the two-layer profile, maxCo does NOT prevent it,
                 the interface moves or x-invariance breaks, and the comparator
                 REFUSES -> NOT A RESULT (sec.11 outcome 4). Both are named.
```

---

## 2. THE CASE — INHERITED FROM R1, BYTE-UNCHANGED EXCEPT THE CONTROLDICT

The physics, geometry, materials, forcing, boundary conditions and mesh family are
**IDENTICAL** to R1 and are not re-derived here. The case files under
`cases/ansys_verification/VMFL069-R2/case/` are **byte-identical copies** of R1's
`case/` **except one file**: `system/controlDict.template`, which carries the
time-stepping change of sec.7. Manual p.205, quoted for the load-bearing sentences:

> *"This test case considers the horizontal stratified Poiseulle flow of two fluids
> between parallel walls. The interface between the two phases is located at half of
> the height of the channel."*
>
> *"The flow is steady. Deformation of the interface is not modeled."*

| quantity | in the frozen case files (unchanged from R1) |
|---|---|
| domain | `Lx = 2 m` (streamwise, **cyclic**), `H = 4 m` |
| interface | `y = 2 m`, on a cell **face** at every level |
| kinematic viscosity | `nu 0.1` lower layer, `nu 0.02` upper layer |
| density | `rho 1` kg/m³ for both (equal, per the manual; value declared by this lab) |
| forcing | cyclic x-pair + `vectorSemiImplicitSource` of `(0.5 0 0)` N/m³ |
| surface tension / gravity | `sigma 0`; `g (0 0 0)` |
| flow regime | `simulationType laminar` |

The three underspecifications R1 disclosed (which of "2m X 4m" is the height; the
density value; which layer is which) are resolved **exactly as R1 resolved them**, and
the reference is derived at those declared values. **Because the reference is the exact
solution of the case as defined here, the gate measures discretisation error and
nothing else** — R2 inherits that argument from R1 sec.2.1 without change.
`VMFL069_WB.wbpz` is **not opened**; neither VM2026R1 archive copy is touched.

---

## 3. THE REFERENCE TIER, AND THE GROUND FOR A `PASS` CEILING — SETTLED, NOT FLAGGED

**Reference kind: THE EXACT SOLUTION OF THE SAME CONTINUUM MODEL THE SOLVER
DISCRETISES.** Not an experiment, not a correlation, not another code's curve. With a
flat non-moving interface, equal densities and zero surface tension the manual's
declared model **is** the steady incompressible Navier–Stokes system with a
piecewise-constant viscosity, whose closed-form solution R1 derives and the comparator
re-derives independently. The convective term vanishes identically
(`U·grad U = u du/dx = 0`), so the Stokes solution is the Navier–Stokes solution at any
Reynolds number. **Model-form error is ZERO BY CONSTRUCTION and the residual is
discretisation error** — the whole ground for the ceiling.

### 3.1 The `PASS` ceiling is SETTLED LAW for this team — there is no interpretive call here

R1's original §3.3 flagged, for the supervisor, whether `VERIFICATION_CHARTER` §2f.3's
CONTINUUM cap (*"`GATE REACHED` maximum. `PASS` is unavailable"*) reaches a
triple-declaring registration. **That question is now settled and this registration
does NOT re-open it.** The ansys-verification supervisor ruled on it personally
(`cases/ansys_verification/VMFL069/SUPERVISOR_RULING_SEC3.3.txt`, freeze commit
`b1b7cfc1`, `[lab-attributed]`), and the ruling is now standing team law as
`ANSYS_VERIFICATION_CHARTER` **§11.1**: *"§2f.3's CONTINUUM cap … is the NO-TRIPLE
ceiling … a registration that declares a Roache triple is graded under `CLAUDE.md`
rule 5 step 3."* VMFL069-R2 declares a triple, so **§2f.3 does not reach it and the
ceiling is `CLAUDE.md` rule 5 step 3: `CONVERGING` → `PASS` inside the band else
`GATE FAIL`.** All three ceilings are therefore `PASS`, exactly as in R1.

Two register precedents, both this team's own, both exact-solution references graded
`PASS` on `CONVERGING` triples: **row #2 VMFL001-R2** (Taylor–Couette, order 2.0102)
and **row #3 VMFL005** (Hagen–Poiseuille, order 1.9341, inside a 2 % band). The
contrast that shows the rule is not stretched: **VMFL063's limb A is capped at
`GATE REACHED` even with a converging triple**, because its reference is *experimental*.
VMFL069-R2 is on the other side of that line because its reference is the exact solution
of the model being solved.

### 3.2 NO §3.3, AND WHY. `ANSYS_VERIFICATION_CHARTER` §11.2 (Amendment 1.5) forbids a
registration reaching its freeze commit with any gate question deferred to a later
decision: *"a deferred gate question is a gate not yet frozen."* R1 carried a §3.3;
**this registration carries none, deliberately.** The one interpretive call R1 flagged
is answered by §11.1 above and is not re-litigated. The drafting lane found **no** new
gate question to flag; had it found one, that would be a **blocker** raised to the
supervisor with the registration left unfrozen, never a clause written into this file.

---

## 4. THE MESH FAMILY AND THE ROACHE TRIPLE — INHERITED BYTE-UNCHANGED FROM R1

Single Cartesian block built by `blockMesh` from the **byte-identical** R1
`blockMeshDict.template`: `x ∈ [0, 2]` (cyclic pair), `y ∈ [0, 4]` (walls), one cell in
`z` (`empty`). Uniform grading `(1 1 1)` everywhere.

| level | NX | NY | **cells** | Δx (m) | Δy (m) |
|---|---|---|---|---|---|
| **L1** | 8 | 32 | **256** | 0.250 | 0.125 |
| **L2** | 16 | 64 | **1 024** | 0.125 | 0.0625 |
| **L3** | 32 | 128 | **4 096** | 0.0625 | 0.03125 |

Both counts double at every level, so `r = 2` is the true local ratio in both directions
and the cell count is exactly ×4 per level. NY is even, so the interface at `y = 2` lies
on a cell **FACE**. A triple is formed on **each** limb independently (rule 5, one-way);
GCI at `Fs = 1.25`; observed-order floor `P_MIN = 0.05`. **All of sec.4 is R1's,
unchanged.**

---

## 5. THE GATE — BANDS INHERITED BYTE-UNCHANGED FROM R1

**The bands, the reference, the ceilings and the Roache parameters are BYTE-IDENTICAL to
R1's frozen comparator and are NOT re-derived here.** This is load-bearing: R1's gate was
never reached (sec.7), so no gate quantity exists that a band could have been fitted to,
and R2's bands are **inherited, not chosen after an outcome**. If any band were thought
to need changing, that would be a **blocker raised to the supervisor**, never a change
made in this document.

### 5.1 The exact solution (R1's, re-derived in the comparator)

```
u_lower(y) = -2.5  y^2 + (40/3)  y                          0 <= y <= 2
u_upper(y) = -12.5 y^2 + (200/3) y - 200/3                  2 <= y <= 4
```

| quantity | exact value | role |
|---|---|---|
| volume mean of `u_x` over `0 <= y < 2` | **10** m/s exactly | **limb A reference** |
| volume mean of `u_x` over `2 < y <= 4` | **50/3 = 16.666666666666668** m/s | **limb B reference** |
| volume mean over the whole channel | **40/3 = 13.333333333333334** m/s | limb C normaliser |
| peak `u_x`, at `y = 8/3` (upper layer) | **200/9 = 22.222222…** m/s | **stability scale, sec.8** |
| `|tau_bottom| + |tau_top|` | **2 = G·H** | global force balance, checked in `--selftest` |

### 5.2 The three limbs — QUOTED FROM R1, IDENTICAL

| limb | quantity | reference | band | ceiling |
|---|---|---|---|---|
| **A** | volume-mean `u_x`, **lower** layer (`nu = 0.1`), at L3 | 10 m/s | `\|lab − 10\|/10 ≤ 0.01` | `PASS` |
| **B** | volume-mean `u_x`, **upper** layer (`nu = 0.02`), at L3 | 50/3 m/s | `\|lab − 50/3\|/(50/3) ≤ 0.01` | `PASS` |
| **C** | normalised L2 error of the whole profile vs the exact solution, at L3 | 0 | `sqrt(mean((u_i − u_exact)²))/(40/3) ≤ 0.01` | `PASS` |

**THE BAND IS ONE NUMBER, 1.0 % (`TOL = 0.01`), FOR ALL THREE LIMBS**, exactly as R1
froze it. In the comparator, the frozen constants `REF_LOWER = 10.0`,
`REF_UPPER = 50.0/3.0`, `REF_WHOLE = 40.0/3.0`, `TOL = 0.01`, `FS = 1.25`, `RATIO = 2.0`,
`P_MIN = 0.05` and `TIER_CEILING = {"A": "PASS", "B": "PASS", "C": "PASS"}` are
**byte-for-byte identical to R1's** — proven at drafting by extracting the gate constants
and every gate/reader/control function from both comparators and diffing them:
**445 lines captured, zero lines differ** (see the diff report to the supervisor).

---

## 6. STRICT COMPLETION (`CLAUDE.md` rule 4) — WITH ONE DECLARED CLAUSE-5 ADAPTATION

R1 satisfied rule 4's clause *"ExecutionTime count == endTime"* **literally** only
because it fixed `deltaT = 1 s` under `adjustTimeStep no`, so the number of time steps
equalled the numeric endTime. **That bookkeeping choice is exactly what killed R1**
(sec.7): with `adjustTimeStep no` the maxCo values limited nothing and the Courant
number ran to 2.87e9. R2 turns `adjustTimeStep yes` on with a registered maxCo (sec.8),
under which **deltaT is chosen every step to hold the Courant number at or below maxCo,
so the step count is VARIABLE and no longer equals the numeric endTime.** That makes
R1's clause 5 unsatisfiable for R2, and it is **ADAPTED — declared here, before compute,
not improvised in the comparator.**

### 6.1 THE RULE-4 CLAUSE-5 ADAPTATION, STATED IN FULL

> **R1's clause 5 required `ExecutionTime count == endTime` (2000). Under
> `adjustTimeStep yes` the step count is variable and does NOT equal the numeric
> endTime, so this numeric identity is unsatisfiable. It is ADAPTED, NOT WAIVED, to:
> the count of `ExecutionTime` lines in the log EQUALS the count of `Time =` lines in
> the log** — the solver's own internal-consistency condition that **every advanced step
> was timed and none was lost or truncated.** Combined with the **unchanged** clause
> *"last Time == endTime"* (the run reached the registered physical end), this pair is
> **strictly stronger** than the `#steps == endTime` artefact it replaces, which was
> never a physics condition — only a side effect of `deltaT = 1`. **What is dropped is
> the numeric identity `#steps == endTime`, and nothing else.**

**An adaptation is not a waiver.** Every OTHER completion clause is **UNCHANGED** and
each still gates (the comparator REFUSES, exit 2, on any failure):

| # | clause | changed for R2? |
|---|---|---|
| 1 | `rc = 0` from `RUN_RC.<level>` (INFRASTRUCTURE, L-342) | **UNCHANGED** |
| 2 | an `End` line in `log.interFoam` | **UNCHANGED** |
| 3 | the fvOptions markers are in the log (the source WAS read) | **UNCHANGED** |
| — | **NEW:** controlDict carries `adjustTimeStep yes` + the registered `maxCo`/`maxAlphaCo` | **ADDED** (R2 REQUIRES the control R1 lacked) |
| 4 | last `Time` **==** `endTime` | **UNCHANGED** (literal rule 4) |
| 5 | `ExecutionTime` count **==** the **`Time`-line count** | **ADAPTED** (was `== endTime`; sec.6.1) |
| 6 | fields `U`, `p_rgh`, `alpha.fluid1`, `Cx`, `Cy` present at `endTime`; `U` at the plateau time | **UNCHANGED** |
| 7 | numerically-latest time directory (`key=float`) == the log's last `Time` | **UNCHANGED** |
| 8 | **AGE GUARD**: every field at `endTime` strictly newer than `0/U` | **UNCHANGED** |
| 9 | **PLATEAU**: layer means at `t = 500` and `t = 1000` agree to `1e-6` relative | **UNCHANGED tolerance** (times moved with endTime) |
| 10 | **INTERFACE STATIONARITY**: `max\|alpha − alpha_0\| ≤ 1e-9` | **UNCHANGED** |
| 11 | **STREAMWISE INVARIANCE**: widest `u_x` spread in any y-row `≤ 1e-6` of the reference mean | **UNCHANGED** |
| 12 | **MESH STRUCTURE**: NX×NY, interface on a face, halves the cell count | **UNCHANGED** |

The clause-6 deltaT pin (R1 required `deltaT == 1`) is **dropped**, because under
`adjustTimeStep yes` the controlDict's `deltaT` is only the *initial* step; it is read
into the record for information and **not gated**. The Courant control replaces it as the
gated quantity.

**Precedent, and it survived a rule-4 challenge.** Declaring a rule-4 adaptation in the
pre-registration before compute, rather than improvising it in the comparator, is this
team's proven form: **VMFL063 PREREGISTRATION §6 clause 4** adapted rule 4's *"last time
== endTime"* clause for a `residualControl`-terminated steady solve (*"last Time <
endTime"* means it converged before the ceiling), was frozen 2026-08-28, and stood
against a supervisor's rule-4 challenge two days later. R2 follows that form exactly,
and its adaptation is **narrower** than VMFL063's: R2 keeps *"last Time == endTime"*
intact and adapts only the step-count clause.

### 6.2 The clauses that are physics claims about THIS case, not tidiness

Clauses 10 and 11 (interface stationarity, streamwise invariance) are R1's, and they are
what makes R1's outcome-5 risk **checkable rather than merely asserted**: with equal
densities, zero surface tension and a flat interface parallel to `U`, the alpha field is
an exact steady state of the VOF system and the wall-normal flux is identically zero, so
**a run whose interface moved, or whose solution developed x-variation, did not solve the
registered case** and the comparator refuses rather than grade it. **This is precisely
the clause that will catch a returning instability** (sec.11 outcome 4).

---

## 7. R1'S FAILURE, DISCLOSED IN FULL — AND WHY NO R1 GATE QUANTITY EXISTS

R1 (`cases/ansys_verification/VMFL069/`, frozen prereg blob
`f3d9f37336f0fbfadb60d86c3024af92ba7cfd1a`) launched 2026-08-30T22:51:45Z and **died on
L1**, the coarsest level, before any level completed:

- **rc 136 — SIGFPE, core dumped.** `verification/runs/ansys_verification/VMFL069/RUN_RC.L1`
  records `rc = 136`, `wall_s = 3`, `last_time_in_log = 69`, `End_lines = 0`. The log
  ends in `Foam::sigFpe::sigHandler` (`.../L1/log.interFoam`).
- **Courant 1802 → 2.87e9.** The convective Courant `max` was 71.85 at t=60 (developed,
  stable), then jumped to **1802.77 at t=65**, 8.5e3 at t=66, 8.5e6 at t=67, and
  **2.869e9 at t=68** — a runaway, not a gradual CFL drift.
- **The interface moved and alpha blew up.** Interface Courant was **exactly 0 through
  t=64**, then jumped to 141.7 at t=65 — a wall-normal velocity appeared where the exact
  solution has none. `Min(alpha.fluid1)` reached **−2.37e23 at t=68** and −1.55e107 by
  the SIGFPE step.
- **The root cause is the time-stepping.** R1's `system/controlDict.template` set
  `deltaT 1` with `adjustTimeStep no`, chosen (its own lines 13–15) so the step count
  equalled the numeric endTime to satisfy rule 4's clause 5 **literally**. Its lines
  48–51 acknowledge that under `adjustTimeStep no` the maxCo/maxAlphaCo/maxDeltaT values
  **limit nothing**. **A bookkeeping clause of the completion rule dictated a
  discretisation choice that destroyed the physics.** R2 fixes exactly this (sec.8).

**NO R1 GATE QUANTITY EXISTS.** R1 died at t=69 of 2000 on L1, so **no level completed,
no volume mean was computed, no L2 profile error was computed, no Roache triple was
formed, and no verdict was graded.** R1's gate was never reached. Therefore **R2's bands
cannot have been fitted to any R1 result** — there is no R1 number in existence to fit
to. R2's bands are the same bands R1 froze *before its own compute*, inherited
byte-unchanged (sec.5). This is why "inherited unchanged" is the honest description and
"re-derived" would be false: a band re-derived by a lane that has seen a failure is a
band chosen after an outcome, and the drafting lane declined to re-derive.

---

## 8. THE STABILITY ARGUMENT, WITH NUMBERS

Instability is what killed R1, so R2's central design choice is the Courant control, and
it is registered with its arithmetic.

**Registered control: `adjustTimeStep yes`, `maxCo = 1.0`, `maxAlphaCo = 1.0`,
`maxDeltaT = 1.0`.** maxCo = 1.0 is the textbook-conservative interFoam value; it removes
numerical CFL instability as a variable entirely, which is the point — R1 blew up because
its Courant number was uncontrolled (reaching 2.87e9), and R2 will not gamble on a higher
ceiling. maxAlphaCo = 1.0 does not bind while the interface is stationary (interface
Courant ≈ 0), but if the interface begins to move it limits the step and slows the run
toward the refusal the stationarity clause will issue — a safety, not a speed setting.

**Expected deltaT, from the mesh and the exact peak velocity.** The peak `u_x` of the
exact solution is `u_max = 200/9 = 22.2222 m/s` (upper layer, `y = 8/3`; computed, not
recalled). With `deltaT = Δx / u_max × maxCo`:

| level | Δx (m) | expected deltaT (s) | steps to endTime = 1000 s |
|---|---|---|---|
| **L1** | 0.2500 | 0.011250 | **≈ 88 900** |
| **L2** | 0.1250 | 0.005625 | **≈ 177 800** |
| **L3** | 0.0625 | 0.002813 | **≈ 355 600** |

(This is a mild over-estimate of the step count: R1's **measured** developed max Courant
at L1, deltaT 1 s, was ~72 against the formula's `u_max/Δx = 88.9`, so the real deltaT
will be ~20 % larger and the step counts ~20 % lower. The formula figure is registered as
the conservative bound.)

**Why endTime = 1000 s.** The slowest mode of the discrete two-layer diffusion operator
has `tau ≈ 33.6 s` (R1 sec.9.3). The relative deviation of a layer mean from steady state
decays as `exp(-t/tau)`. The plateau clause compares `t = 500` with `t = 1000`; at
`t = 500`, `exp(-500/33.6) = 3.5e-7`, comfortably below the frozen `1e-6` plateau
tolerance with 2.9× margin. `endTime = 1000 s ≈ 30 tau`. The `writeControl` is
`adjustableRunTime`, `writeInterval 500`, so the solver writes exactly at `t = 500` and
`t = 1000` — the two times the comparator reads by name.

**Expected cost (RANKS = 1), and it is dominated by L3.** Per-step wall time is
transferred *within this case* from R1's L1 (68 steps in 3 wall s including startup and
the blow-up steps → ~0.02 s/step at 256 cells) and scaled linearly with cell count. This
transfer is unreliable (sec.9):

| level | steps | per-step (s) | wall (s) | core-min | wall-hours |
|---|---|---|---|---|---|
| L1 | 88 900 | 0.02 | 1 780 | ~30 | 0.5 |
| L2 | 177 800 | 0.08 | 14 200 | ~237 | 4.0 |
| L3 | 355 600 | 0.32 | 113 800 | **~1 896** | **~31.6** |
| **total** | | | | **≈ 2 160 core-min ≈ 36 core-h** | |

Derived dollars at the estimate: `2160/60 × $0.0513 = $1.85` (derived, not measured).
**L3's ~32 wall-hour solve is the practical weak point of this design** and is flagged to
the supervisor in the accompanying report; it is a Courant-limited transient-to-steady
solve and is inherently expensive at the fine mesh (fast advection, slow diffusion). The
cost scales as `1/maxCo`, which is a run-control lever the supervisor may weigh at the
freeze — but this document registers `maxCo = 1.0`.

**What happens if it still will not run.** Three named failure paths, all honest:
1. **The instability was PHYSICAL** (a two-layer / interfacial mode; the upper-layer Re is
   ~4400, below plane-Poiseuille's linear critical ~5772 but not trivially so). maxCo = 1
   does not prevent a continuous-problem instability; a wall-normal velocity grows, the
   interface moves and/or x-invariance breaks, and the comparator **REFUSES → NOT A
   RESULT** (sec.11 outcome 4). This is a genuine finding, not a defect.
2. **It diverges numerically anyway** (SIGFPE / non-zero rc): `NOT A RESULT`, spend
   reported (outcome 6), exactly as R1.
3. **The cost cap fires** before L3 completes (rc 124): the run stops, no CONVERGING
   triple, **NOT A RESULT** (outcome 7). endTime is never reduced to fit the cap.

In any of these, the honest verdict is `NOT A RESULT` and R2 stops. A successor (R3, if
ever authorised) would change the *physics/numerics approach* — a lower maxAlphaCo, an
interface-damping scheme, or parallel decomposition to make L3's wall-time tractable —
registered in advance so it cannot be a silent reaction to an unwelcome result.

---

## 9. COST (`CLAUDE.md` rule 12)

| | |
|---|---|
| **unit** | core-minutes = wall_s × RANKS / 60 |
| **RANKS** | **1** (serial; matches R1 and the VMFL063 family convention) |
| **ESTIMATE** | **~2 160 core-min** total (sec.8 table), L3 ~1 896 of it |
| **CAP** | **5 000 core-min, RUNNING TOTAL across all three solves.** Each level's `timeout_s` is `(CAP − spent) × 60 / RANKS`. ~2.3× the estimate, to absorb the per-step misprediction below. |
| **overrun** | **STOPS the run (rc 124).** No new budget; `endTime` is NEVER reduced to fit a cap. |
| **cost_basis** | `$0.0513/core-h`, c7a.4xlarge, **REPORTED-BY-OWNER, NOT MEASURED**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars are **derived**. |
| **$ at estimate** | 2 160 core-min = 36 core-h × $0.0513 = **$1.85** — derived |
| **$ at cap** | 5 000 core-min = 83.3 core-h × $0.0513 = **$4.27** — derived |
| **GPU** | none. CPU case. Under-$25 CPU runs are pre-authorised (rule 12); the run is still costed. |

**THE COST MODEL IS TRANSFERRED, AND THAT IS DISCLOSED AS UNRELIABLE (C-199).** This
team's C-199 lesson is that a cost model transferred **across** a case is unreliable;
R2's per-step estimate is transferred **within** this case, from R1's single L1
measurement (68 steps in 3 wall s), which is the least-bad basis available but is still
weak: R1's 3 s included blockMesh/checkMesh/setFields/startup **and** the expensive
blow-up steps (1000 alpha iterations each), so the clean per-step cost could be 0.5–3×
the 0.02 s/step assumed. That uncertainty is the reason the cap is 2.3× the estimate, not
1.2×. **Estimate-versus-actual calibration is owed at completion** (rule 12, Sanaa's
directive of 2026-08-23): actual core-minutes from `RUN_RC.*`/`COST.txt` against the
~2 160 above, the ratio, attribution (contention / waste / misprediction, waste named
separately), and one row in `docs/COST_CALIBRATION.md`.

---

## 10. THE PLANTED-ZERO CONTROL (`CLAUDE.md` rule 3) — INHERITED BYTE-UNCHANGED FROM R1

The two-stage, two-channel planted-zero control (velocity and alpha, each with a
blind-writer negative arm and a refusal-text-difference check), the cardinality guard
(`one_match`, no `sorted(glob)[-1]`), the numeric-vs-lexicographic time-dir hazard
demonstration, and the AST guard (`ast.Assert` count must be 0, run on the grading path
too) are **byte-identical to R1's comparator** — proven by the 445-line gate/control
extraction diff (sec.5.2, and the diff report). The lexicographic hazard remains **live
in this very case**: R2 writes time directories `500` and `1000`, whose lexicographic
maximum is `500` (since `"1000" < "500"`) and whose numeric maximum is `1000`; the
comparator sorts `key=float`, cross-checks against the log's last `Time`, and records
that the lexicographic reading would have been wrong.

---

## 11. NAMED LIVE OUTCOMES — every one can happen, and each is written down now

The fixed vocabulary and nothing else (`CLAUDE.md` rule 1).

| # | outcome | condition |
|---|---|---|
| 1 | **ROW `PASS`** *(the target)* | every triple `CONVERGING`, every limb inside 1 % at L3, interface stationary, x-invariant, plateaued. The case IS PASS-capable (sec.3); this is the only currently-reachable `PASS` in this team's queue. |
| 2 | **ROW `GATE FAIL`** | triple `CONVERGING`, L3 **outside** the 1 % band on some limb. A finding, recorded with its numbers. |
| 3 | **`NOT A RESULT` — a triple is not `CONVERGING`** | `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT`, or `p < P_MIN`. Whatever the value; no GCI printed. Most likely on limb B (R1's predicted `p ≈ 0.89`). |
| 4 | **`NOT A RESULT` — the instability RETURNS ("diverges again")** | the interface moves (`check_alpha_stationary` refuses) or streamwise invariance breaks (`check_x_invariance` refuses). This is the R1 failure re-manifesting despite the Courant control, i.e. a **PHYSICAL** two-layer instability rather than a numerical CFL one. The comparator **REFUSES**; the finding is that the registered case does not have a stable laminar steady state at these parameters. |
| 5 | **`NOT A RESULT` — SIGFPE / non-zero rc** | the solver dies (as R1 did) or `rc != 0` recorded. The launcher stops at the first non-zero rc; the comparator refuses. Spend reported. |
| 6 | **`NOT A RESULT` — the cost cap fires (rc 124)** | L3 (or an earlier level) exceeds the 5 000 core-min running total. The run stops; endTime is not shrunk to fit. |
| 7 | **`NOT A RESULT` — not plateaued / completion clause failed** | the plateau, fvOptions, age-guard, mesh-structure, field-presence, time-dir or last-Time/ExecutionTime clauses fail. The comparator **REFUSES**. |
| 8 | **`NOT A RESULT` — a control did not fire** | a plant unseen on either channel, the cardinality guard ≠ 1 match, or the AST guard finding an `assert`. |
| 9 | **`BLOCKED`** | the toolchain is absent (no `interFoam`/`blockMesh`) or `blockMesh`/`checkMesh` fails. A crash is a **FINDING, not a retry**. |
| 10 | **`PENDING`** | registered and not yet run — the state this document is in as it is committed. |

**THE PREDICTION (falsifiable content):** if R1's blow-up was a numerical CFL instability,
maxCo = 1 removes it and the run reaches the discretisation-error-only steady state,
landing outcome 1 or 2 with an observed order **near ONE** (the arithmetic face-viscosity
mechanism of R1 sec.9, inherited). If it was a physical two-layer instability, maxCo = 1
does not prevent it and outcome 4 lands. **This document does not predict which**, and
that is honest: the gate is not constructed so that only one answer is possible.

---

## 12. THE GRADING PATH, FROZEN

| artefact | path |
|---|---|
| pre-registration | `cases/ansys_verification/VMFL069-R2/PREREGISTRATION.md` (this file) |
| comparator | `cases/ansys_verification/VMFL069-R2/grade_vmfl069_r2.py` |
| launcher | `cases/ansys_verification/VMFL069-R2/run_vmfl069_r2.sh` |
| case inputs | `cases/ansys_verification/VMFL069-R2/case/` — **12 files**, each hashed against its own HEAD blob at launch |
| run root | `verification/runs/ansys_verification/VMFL069-R2/` — **does not exist** |
| grading record | `verification/runs/ansys_verification/VMFL069-R2/GRADING_VMFL069_R2.json` |

**The grading path is fixed at this commit.** The launcher hashes this file and the
comparator against their HEAD blobs before it does anything else and **aborts** if either
differs; `grade_vmfl069_r2.py --verify-frozen` does the same on demand, deriving the
repository root from `git rev-parse --show-toplevel`. The comparator's `--selftest` is
green (**70 checks, 70 PASS, 0 FAIL, rc 0 under both `python3` and `python3 -O`**), it
carries all named control markers, and the launcher requires PASS/FAIL/rc agreement and
the AST-guard marker under both interpreters plus every named marker DRIVEN — including
the three new markers that drive R2's clause-5 adaptation guard, the adjustTimeStep-required
guard and the maxCo guard to refusals.

**Launch:** `bash cases/ansys_verification/VMFL069-R2/run_vmfl069_r2.sh verification/runs/ansys_verification/VMFL069-R2`
**Grade:** `python3 cases/ansys_verification/VMFL069-R2/grade_vmfl069_r2.py --run-root verification/runs/ansys_verification/VMFL069-R2 --out verification/runs/ansys_verification/VMFL069-R2/GRADING_VMFL069_R2.json`

**QUEUE NOTE (filing requirement).** The queue entry for this case must set **`cwd` to
the run root** `verification/runs/ansys_verification/VMFL069-R2`, never to the case
directory — runtime artefacts beside frozen files is what `FILING_CHARTER` R6 forbids,
and it would put unhashed files next to the twelve this launcher hashes.

---

## 13. WHAT THIS REGISTRATION DOES NOT CLAIM

- **It does not claim to reproduce Ansys's result.** The manual prints Figure .69.2 and
  no numeric Target; no curve is digitised and no Ansys number appears anywhere in this
  document, the comparator or the case files.
- **It does not claim to reproduce Marchandise & Remacle (2006).** That paper is not on
  this box and was not read; it is named for provenance only.
- **It does not claim R1 was wrong to try `adjustTimeStep no`.** R1 registered a
  falsifiable premise (large Courant is harmless because the scheme is implicit and the
  interface is stationary), it was tested, and it **failed** — which is what a
  pre-registered premise is for. R2 records the falsification and fixes it.
- **It does not claim the case has a stable laminar steady state.** Whether the two-layer
  profile is stable at these parameters is exactly what outcome 4 leaves open, and R2
  will report `NOT A RESULT` if it is not.
- **It does not claim mesh-independence, or a validated physical model.** It claims what
  three levels measure against an exact solution, and nothing about meshes not run or
  about whether the model describes a real stratified flow.
- **It supersedes nothing.** R1's `NOT A RESULT` row stands; R2 earns its own row.

---

## AMENDMENT 1 — 2026-08-30 — **THE COST BASIS IS REPLACED WITH A MEASURED ONE; `endTime` STAYS AT 1000 s AND THE REASON IS RECORDED SO IT CANNOT BE "OPTIMISED" AWAY; AND OUTCOME 4's DETECTOR IS PROVEN ABLE TO REFUSE BEFORE THE FREEZE**

**Version 1.1.** Appended at the foot. **Nothing above this line is rewritten, reworded,
struck or renumbered** — not sec.0's rule-2 condition, not the ten-line form, not the
reference, not the ceilings, not the gate, not the bands, not the mesh family, not the
completion clauses, not the controls, not the named outcomes. The original carries no
version line, so the bump is declared **here** rather than by editing the header — the
form `ANSYS_VERIFICATION_CHARTER` Amendment 1.3 established, and for the same reason:
editing above would renumber every line beneath it and falsify this amendment's own
prefix assertion.

**THIS AMENDMENT IS LEGAL BECAUSE NO COMPUTE HAS HAPPENED.** `CLAUDE.md` rule 2: *"Before
first compute, amendments are legal and must state the condition and how it was checked
(name the run directory that does not exist)."* That statement is §A1.0. **Nothing here
alters a gate, threshold, band, cap, level, ceiling, label or control.** The estimate
changes; the **cap does not**. Written by `ansys-lane-opus` (Opus 5) on the
ansys-verification supervisor's ruling of 2026-08-30 that VMFL069-R2 is cleared to freeze
and enqueue.

---

### §A1.0 THE RULE-2 CONDITION, RE-VERIFIED BY THIS LANE — not inherited from sec.0 and not taken from the supervisor's check

**Re-run and re-measured at `2026-08-30T23:35:23Z`, repository HEAD
`03dbcc1454380574b84cb6275373e6f8b46acd4f`**, by the lane writing this amendment. The
supervisor's own check of `23:33:18Z` is **not cited as this lane's evidence**; these are
this lane's own commands and this lane's own timestamp.

| condition | how it was checked, here | result |
|---|---|---|
| **the run directory `verification/runs/ansys_verification/VMFL069-R2/` DOES NOT EXIST** | `test -e verification/runs/ansys_verification/VMFL069-R2` | **false — it does not exist** |
| no VMFL069-R2 artefact anywhere on the box | `find / -xdev -iname '*VMFL069-R2*'` (single filesystem; `/tmp`, `/var/tmp`, `/home/ubuntu` swept separately) | **one hit, and it is the case directory itself**; zero artefacts |
| the register carries no VMFL069-R2 row | `grep -c 'VMFL069-R2' verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` | **0** |
| the case directory holds no solver log, no `RUN_RC.*`, no grading record and no numeric time directory | `find` over the case directory for `log.*`, `RUN_RC.*`, `GRADING_*` and numeric-named directories | **none of any kind** |
| no VMFL069-R2 queue entry exists, launched or pending | `find verification/queue -iname '*VMFL069*'` | one hit, and it is **R1's** `launched/VMFL069.json` |

**THREE HONEST QUALIFICATIONS, STATED RATHER THAN GLOSSED**, because a clean check whose
edge cases are hidden is worth less than a check whose edge cases are named:

1. **`cases/ansys_verification/VMFL069-R2/case/0/` EXISTS AND IS NOT AN ANSWER.** It holds
   `U`, `alpha.fluid1` and `p_rgh` — three of the **twelve frozen case INPUTS**, the
   initial condition the launcher copies. It is not a written time directory, it contains
   no solved field, and `case/` holds no numeric-named directory whatever. The rule-4 age
   guard is armed against the **run root's** `0/U`, which does not exist.
2. **A SCRATCH SCOPING PROBE DIRECTORY EXISTS AND COMPUTED NO GATE QUANTITY**, at
   `.../scratchpad/vmfl069_probe/L1` (scratch, outside the repository, cited here only to
   disclose it — no repository document depends on that path, per L-186). **Verified by
   this lane rather than assumed:** its `log.interFoam` carries 2005 `Time =` lines but
   its only time directory is `0/`, so **no velocity field at any `t > 0` exists anywhere
   on this box** and no layer mean, no L2 profile error and no Roache triple could have
   been formed from it. It also lies outside `verification/runs/`, as
   `ANSYS_VERIFICATION_CHARTER` Amendment 1.4 clause B requires.
3. **THERE IS STILL NO VMFL069-R2 NUMBER FOR ANY BAND TO HAVE BEEN FITTED TO**, and there
   is no R1 gate number either (sec.7). Every band, ceiling, tolerance and window in this
   document remains a **prediction**, which is the whole of its evidentiary content.

---

### §A1.1 THE COST BASIS IS REPLACED — the drafted estimate rested on a contaminated 3-second measurement; it has now been measured

**What sec.9 registered, and why it was weak.** Sec.8/sec.9 projected **~2 160 core-min**
from R1's only timing datum: **68 steps in 3 wall seconds**, a figure that included
`blockMesh`, `checkMesh`, `setFields`, solver startup **and** the blow-up steps (1 000
alpha iterations each). Sec.9 disclosed that basis as unreliable and put the possible
error at 0.5–3×. **It was pessimistic by 2.5×**, and this amendment replaces it.

**THE MEASUREMENT.** A bounded scoping probe ran **L1 only, 2 005 time steps, in a scratch
directory**, stopped by its own step ceiling (`rc 143`, `STEP_CEILING 2005`), reaching
`t = 49.6445 s` of the registered 1 000 s. It computed **no gate quantity** and wrote **no
time directory but `0/`**. Re-derived from its log by this lane, startup excluded, over
four independent windows:

| window (steps) | CPU (`ExecutionTime`) ms/step | wall (`ClockTime`) ms/step |
|---|---|---|
| 100 – 2003 | 7.3148 | 7.8823 |
| 500 – 2003 | 7.3054 | 7.9840 |
| 1000 – 2003 | 7.2881 | 7.9761 |
| 1500 – 2003 | 7.2763 | 7.9523 |

**REGISTERED MEASURED FIGURES: 7.97 ms/step wall and 7.28 ms/step CPU at 256 cells** —
stable to better than 0.5 % across all four windows, so the number is not a window
artefact. That is **31.13 µs per cell per step** at L1. The drafted 20 ms/step was
**2.5× pessimistic**.

**CONTENTION IS DISCLOSED, NOT ABSORBED** (`COMPUTE_BUDGET_CHARTER` §6). The probe started
at `loadavg 36.88` on `nproc 16` with 6 other OpenFOAM processes live. The wall/CPU ratio
is **1.0948**, so contention inflated the wall figure by **9.5 %**. The lab's unit is
`wall_s × ranks / 60`, so **the projections below use the contended 7.97 ms wall figure
and are conservative by that 9.5 %.**

**THE CORRECTED PROJECTION, AND ITS HONEST BRACKET.** Steps double per level (`deltaT`
halves with `Δx` at fixed `maxCo`); cells quadruple. Anchored on the probe-based L1
projection of **84 817 steps**:

| level | cells | steps | core-min, per-step ∝ cells | wall-hours |
|---|---|---|---|---|
| L1 | 256 | 84 817 | **11.3** | 0.2 |
| L2 | 1 024 | 169 634 | **90.1** | 1.5 |
| L3 | 4 096 | 339 268 | **721.1** | **12.0** |
| **total** | | | **822 core-min = 13.7 core-h** | |

**Derived dollars: $0.70** at `$0.0513/core-h` — **DERIVED, NOT MEASURED**, the rate being
owner-stated and the box unable to read its own billing (`COMPUTE_BUDGET_CHARTER` §5).
**L3 is a 12.0 wall-hour solve, not the ~32 wall-hours sec.8 projected** — the practical
weak point sec.8 flagged is substantially smaller than it registered.

**822 IS NOT QUOTED AS CERTAIN, AND HERE IS THE BRACKET.** Two independent assumptions sit
under it, and **neither was measured**:

1. **The L2 and L3 per-step costs were NOT measured.** The probe was L1-only by
   instruction. Cost scaling **linear in cell count** is an *assumption*. At 31.13 µs per
   cell per step on a 256-cell case, an appreciable share of the L1 step is **fixed
   per-step overhead** (matrix assembly setup, MULES sub-cycle bookkeeping, PISO
   orchestration, log I/O), which does not grow with cells — so **linear extrapolation
   OVER-estimates L3.** The opposite extreme, per-step cost entirely fixed, gives a floor
   of **76 core-min** total.
2. **The step count is an EXTRAPOLATION, not a measurement** (§A1.4). Two defensible fits
   to the measured `deltaT` series bracket the L1 step count at **82 182 – 91 825**.

**REGISTERED: the true total is bracketed 76 – 890 core-min, and 890 is the conservative
end.** 822 core-min is the point estimate at the probe-based step count under
linear-in-cells scaling; sec.8's own formula step count gives 862. **This bracket is wider
than a per-step-cost bracket alone would be, because this lane's step-count extrapolation
is wider than the drafting figure** — that is disclosed rather than narrowed.

**THE 5 000 core-min CAP IS UNCHANGED, AND THE REASON IS RECORDED.** The supervisor's
reasoning, adopted here: **a cap is protection, not a target**, and the L2/L3 scaling is
an *assumption* rather than a measurement — the one direction in which a cheap-looking
estimate could be wrong is the direction the cap exists to catch. **822 against 5 000 is
6.1× margin; the conservative 890 is 5.6×.** An overrun still **STOPS the run** (rule 12);
`endTime` is **never** reduced to fit a cap (§A1.2). Derived dollars at the cap remain
**$4.27**.

---

### §A1.2 `endTime` STAYS AT 1000 s — **AND THIS IS THE MOST IMPORTANT PARAGRAPH IN THIS AMENDMENT**

**Shortening `endTime` looks like the obvious cost lever on a 12-wall-hour L3. IT IS A
TRAP, AND ACTING ON IT WOULD HAVE DESTROYED THE RUN.** The supervisor proposed it as a
lever; the probe caught the error; it is written down here so that a future reader — who
will see a long L3 and reach for exactly this — cannot repeat it.

**THE MECHANISM.** The plateau clause is the check that steady state was reached. It does
not sample a fixed absolute time: it compares the layer means at the **earlier written
time** against those at `endTime`, and the earlier written time is `endTime/2` under the
registered `writeInterval` (`controlDict.template` `writeInterval 500`, comparator
`PLATEAU_TIME = 500`, `ENDTIME = 1000`). **Shorten `endTime` and the first sample moves
DOWN with it, into the part of the transient the clause exists to exclude.**

The layer mean approaches steady state as `exp(-t/tau)`, so the relative change the clause
measures between the two samples is `≈ exp(-t1/tau)` with `t1` the **earlier** sample.

**`tau` DERIVED INDEPENDENTLY BY THIS LANE**, not inherited: the slowest mode of the
two-layer diffusion operator solves
`sqrt(nu1)·cot(2·k1) + sqrt(nu2)·cot(2·k2) = 0` with `k_i = sqrt(lambda/nu_i)`, whose
smallest positive root is `lambda_1 = 0.0296317686041 s^-1`, giving

> **`tau = 33.7475637502 s`** (residual `F(lambda) = -8.3e-17`).

This **corrects sec.8's `tau ≈ 33.6 s`** — a 0.44 % correction, in the *unfavourable*
direction, and it is recorded rather than quietly used.

| `endTime` | first plateau sample | `exp(-t1/tau)` | against the frozen `1e-6` |
|---|---|---|---|
| **1000** | **500** | **3.6774e-07** | **INSIDE — 2.72× below tolerance** |
| 932.5 | 466.2 | 9.9970e-07 | inside, by 0.03 % |
| 928 | 464.0 | 1.0686e-06 | **FAILS** (1.07×) |
| 900 | 450.0 | 1.6180e-06 | **FAILS** (1.6×) |
| 800 | 400.0 | 7.1193e-06 | **FAILS** (7.1×) |
| **600** | **300.0** | **1.3782e-04** | **FAILS BY 138×** |
| 400 | 200.0 | 2.6682e-03 | FAILS by 2 668× |

> **MINIMUM `endTime` UNDER THE REGISTERED `writeInterval = endTime/2` STRUCTURE:
> `2·tau·ln(1e6) = 932.4796 s`. The registered 1000 s clears it by 67.52 s — 7.24 %.
> `endTime = 1000` IS ALREADY NEAR-MINIMAL AND IS NOT PADDING.**

Stated as the general constraint, so it survives any restructuring of `writeInterval`:
**the EARLIER plateau sample must sit at or beyond `tau·ln(1e6) = 466.24 s`.**

**WHAT SHORTENING TO 600 s WOULD ACTUALLY HAVE COST.** The plateau sample would land 138×
outside the frozen tolerance, `completion()` would raise `NOT PLATEAUED` and **REFUSE
(exit 2)**, and the item would be **`NOT A RESULT`** — after the full L3 spend. The saving
would have been ~40 % of the compute; the price would have been **the entire verdict**,
and on this team's only currently PASS-capable item.

**THE GENERAL LESSON, AND IT IS THE HALF WORTH KEEPING.** `endTime` is not a free
bookkeeping parameter here: **a completion clause is coupled to it, and the coupling runs
through a sample time that moves.** This is the same shape as the failure that killed R1 —
there, rule 4's `#steps == endTime` clause dictated `deltaT = 1` and destroyed the physics
(sec.7). **Twice now on this case, a bookkeeping quantity has reached into the
discretisation.** R1 paid for it; R2 caught it before compute only because the arithmetic
was re-derived rather than recalled. **`endTime = 1000 s` is registered, is unchanged by
this amendment, and is not to be reduced as a cost measure** — rule 12's own words, and
sec.9's: *`endTime` is NEVER reduced to fit a cap.*

---

### §A1.3 A NEW REQUIREMENT, IMPOSED BY THE SUPERVISOR AND **DISCHARGED BEFORE THE FREEZE** — outcome 4's detector is proven able to refuse

**WHY IT WAS IMPOSED.** The probe found that with an x-invariant initial condition and
x-invariant forcing, the discrete problem preserves x-invariance **BIT-EXACTLY**. Verified
by this lane over all 2 005 probe steps: **interface Courant `max = 0` and `min = 0`, zero
steps non-zero**; and across all 8 020 alpha reports, **`Min(alpha) = 0` exactly and
`Max(alpha) = 1` exactly, with zero steps departing from either.** Excellent for
stability — **and it raises the question the supervisor asked: is outcome 4's detector
(`check_alpha_stationary` / `check_x_invariance`) STRUCTURALLY CAPABLE OF FIRING AT ALL?**
**A guard seen only to pass is unproven** — this lab's standing principle and rule 3's:
*a zero from a reader not shown able to see a non-zero is not evidence.*

**REQUIREMENT, NOW SATISFIED: the detector was DRIVEN TO A REFUSAL against R1's real
diverged data, before the freeze commit.** Artefacts committed with the freeze:
`cases/ansys_verification/VMFL069-R2/artefacts/drive_outcome4.py` and
`.../artefacts/OUTCOME4_DETECTOR_DRIVE.txt`.

**HOW.** The functions driven are **imported from this frozen comparator itself**, not
reimplemented. R1's real field bytes are **copied, never touched**. Every perturbation is
planted **on disk** and read back through the **production readers** (`read_internal_scalar`,
`read_internal_vector_x`), per rule 3.

- **Alpha channel — R1's REAL bytes.**
  `verification/runs/ansys_verification/VMFL069/L1/0/alpha.fluid1`, sha256
  `50fa5ccfba92363d9dfa17906e32942767c5af14f2eecacac2988720e719a5a8`, the genuine
  256-value `setFields` output. R1 wrote **no** field directory beyond `0/`
  (`writeInterval` was 500 **timesteps** and it died at step 69), which is confirmed here,
  so this is the only real alpha field R1 produced. Planting used the comparator's own
  `_plant_internal_scalar`.
- **Velocity channel — CONSTRUCTED, and that is disclosed.** R1's real `0/U` is
  `internalField uniform (0 0 0)` and carries no `nonuniform` list, so the production
  vector reader cannot consume it. The x-invariance input was therefore **constructed from
  R1's LOGGED values** — the second route the requirement allows: the exact solution on
  the registered L1 mesh, written to disk in the production format, then perturbed in one
  x-column at the magnitude R1's log actually recorded. **R1's logged convective Courant
  max 2 869 282 454.01 at `deltaT = 1 s`, `Δx = 0.25 m`, gives `|u_x| = 7.173e+08 m/s`.**

**TEN ARMS, ALL AS REGISTERED, `rc 0`:**

| arm | input | expected | observed |
|---|---|---|---|
| A0 | R1's real bytes, unperturbed | no refusal | **no refusal**, `worst = 0.0` exactly |
| A1 | +9.0e-10 (below the frozen `1e-9`) | no refusal | **no refusal**, `9.0000007e-10` |
| A2 | +1.1e-9 (above the frozen `1e-9`) | **REFUSE** | **REFUSED** |
| A3 | R1's logged `Min(alpha) = -2.36630181882e+23` | **REFUSE** | **REFUSED** |
| A4 | **BLIND** — writer writes nothing | no refusal | **no refusal**, `worst = 0.0` |
| X0 | exact solution, unperturbed | no refusal | **no refusal**, spread `0.0`, 32 rows |
| X1 | column offset 0.9 × threshold | no refusal | **no refusal**, `9.0e-07` |
| X2 | column offset 1.1 × threshold | **REFUSE** | **REFUSED** |
| X3 | column offset `7.173e+08 m/s` (R1's logged magnitude) | **REFUSE** | **REFUSED** |
| X4 | **BLIND** — nothing written | no refusal | **no refusal**, spread `0.0` |

**THE EXACT REFUSAL MESSAGES, VERBATIM FROM THE R1-MAGNITUDE ARMS:**

```
REFUSING (exit 2): INTERFACE MOVED: max |alpha - alpha_0| = 2.36630181882e+23 at y = 0.0625,
above the frozen 1e-09. The registered case has a NON-DEFORMING interface (manual p.205);
a run whose interface moved did not solve it.

REFUSING (exit 2): STREAMWISE INVARIANCE BROKEN: the widest spread of u_x within a single
y-row is 53799046.0127 of the reference mean (at y = 0.0625), above the frozen 1e-06.
The registered solution is x-invariant.
```

**FOUR THINGS THIS PROVES, AND ONE IT DOES NOT:**

1. **The detector fires on R1's actual divergence magnitude** — outcome 4 is detectable,
   so the registration does not need rethinking.
2. **It is CALIBRATED AT ITS FROZEN THRESHOLD, not merely able to see `1e23`.** The
   near-miss pair (A1/A2 straddling `1e-9`; X1/X2 straddling `1e-6`) is the arm that
   matters: a detector that only catches astronomical values would pass A3 and still miss
   a real, small interfacial drift.
3. **The refusal came from the DISK BYTES.** The blind arms A4 and X4 — where the writer
   writes nothing and the same read-back and same call are made — **do not fire**. Without
   them, a refusal could have come from the call rather than from what was on disk.
4. **The two channels carry DISTINCT refusal headings** (`INTERFACE MOVED` vs `STREAMWISE
   INVARIANCE BROKEN`), so one generic message is not standing in for two independent
   checks.
5. **WHAT IT DOES NOT PROVE, stated plainly:** it does not prove the case is stable, and it
   does not prove the detector would catch a *physical* instability whose signature is
   smaller than the frozen tolerances. It proves the guard is not structurally dead. **A0
   also proves, incidentally, that R1's real `setFields` cell ordering agrees exactly with
   the registered geometry** — `worst = 0.0`, not merely small.

---

### §A1.4 TWO REGISTERED PREDICTIONS, TESTED — **and one of them is NOT confirmed, which is recorded rather than smoothed**

**PREDICTION 1 — the asymptotic `deltaT`. NOT CONFIRMED. NOT REFUTED. NOT MEASURED.**
Sec.8 registers `deltaT_∞ = Δx·maxCo/u_max = 0.25/(200/9) = 0.011250 s`. **The probe did
not measure it.** It stopped at `t = 49.6445 s` — **1.47 `tau`, 5 % of `endTime` — with
`deltaT = 0.0150175099 s` and still falling.** Any asymptote is an **extrapolation**, and
this lane's two defensible extrapolations disagree materially:

| extrapolation of `1/deltaT = A(1 − exp(−t/tau))` | `deltaT_∞` | vs the registered 0.011250 |
|---|---|---|
| `tau` **pinned** at the derived 33.7476 s | 0.0117565 s | **+4.50 %** |
| `tau` **free** (best fit 41.30 s) | 0.0104425 s | **−7.18 %** |

**REGISTERED HONESTLY: `deltaT_∞` is bracketed 0.01044 – 0.01176 s, and the formula's
0.011250 sits inside that bracket.** What the probe *does* confirm is the **direction**:
the measured `deltaT` is above the formula asymptote and decreasing, which is exactly what
a still-developing `u_max` requires. **The formula is CONSISTENT WITH the probe; it is not
CONFIRMED BY it,** and the free-`tau` fit returning 41.30 s against the derived 33.7476 s
shows the single-exponential model is not well constrained over 1.47 time constants.

**PREDICTION 2 — the L1 step count. BRACKETED, NOT CONFIRMED.** Sec.8 registers
**≈ 88 900** steps to `endTime`, calling it a conservative over-estimate. Integrating the
two extrapolations above from the probe's last measured step gives **82 182** (pinned
`tau`) and **91 825** (free `tau`). **The registered 88 900 lies INSIDE that bracket**, so
it is neither confirmed conservative nor shown optimistic — it is simply within the
extrapolation spread. The 84 817 used to anchor §A1.1's projection is likewise inside it.

**THIS SECTION EXISTS BECAUSE THE ALTERNATIVE WAS TO WRITE "CONFIRMED" TWICE.** Both
figures were put to this lane as confirmed measurements. Neither is a measurement: **the
probe covered 5 % of the run's physical time, and an asymptote is not observable from
inside a transient.** Recording them as confirmed would have put a false measurement into
a frozen file, in the one document whose entire value is that its contents were fixed
before the answer existed.

---

### §A1.5 TWO DISCLOSURES CARRIED WITH THIS AMENDMENT — neither is converted into a gate here

1. **THE MEASURED CONVECTIVE COURANT OVERSHOOTS THE REGISTERED CEILING, AND NOTHING GATES
   ON IT.** Over the probe's 2 005 steps the convective Courant reached **1.17487** against
   the registered `maxCo = 1.0` — a **+17.5 % overshoot**. This is expected OpenFOAM
   behaviour (`deltaT` for the next step is set from the *previous* step's Courant, so the
   realised value overshoots while the field accelerates) and it is **nowhere near R1's
   1802 → 2.87e9**, so the control is working as designed. **What is disclosed is that the
   comparator gates on the controlDict's DECLARED `maxCo` (`completion()`, requiring
   `maxCo == 1.0`) and reads NO Courant number from the log at all.** The realised Courant
   is therefore **unmeasured by the frozen grading path**. This is the same shape as
   `ANSYS_VERIFICATION_CHARTER` Amendment 1.4's disclosure 3 against VMFL045-R2.
   **It is NOT converted into a gate here.** Adding a clause is a change to the
   registration's control set, and this amendment's mandate is the cost basis, `endTime`
   and the outcome-4 detector. **Referred to the supervisor** for a future registration.
2. **`tau` IS CORRECTED FROM 33.6 s TO 33.7475637502 s** (§A1.2), derived here rather than
   inherited. Sec.8's consequential figures move with it: `exp(-500/tau)` is **3.6774e-07**,
   not `3.5e-7`, and the plateau margin is **2.72×**, not `2.9×`. **Both still clear the
   frozen `1e-6` tolerance, so no clause changes** — the correction is recorded because a
   figure quoted to two significant digits and used as the ground for a design decision
   should be the figure that was actually solved for.

---

**Lines whose number changed above this section: 0** — **verified, not asserted**: the
sha256 of the pre-amendment file was taken and its byte length recorded, and after the
append the first N bytes of the resulting file were re-hashed and required to equal it
**byte-for-byte, in the same shell invocation as the write**, with the write reverted on
any difference. The verification output is
`cases/ansys_verification/VMFL069-R2/artefacts/AMENDMENT1_PREFIX_ASSERTION.txt`.
