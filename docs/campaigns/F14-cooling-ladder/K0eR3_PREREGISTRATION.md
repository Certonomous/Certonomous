# K0eR3. Forced-convection flat plate, Bahrami (2005): PRE-REGISTRATION

**Registered 2026-09-04T01:1xZ, BEFORE ANY K0eR3 COMPUTE.** Zero core-minutes
have ever been spent against K0eR3.

**The absence was CHECKED, not asserted, and under a planted control** (standing
rule 3). One reader, four targets, in one invocation:

| target | directory | `STATUS.*` count |
| --- | --- | ---: |
| `verification/runs/F14-cooling-ladder/K0eR3_runs` | **ABSENT** | — |
| `.../K0eR2_runs` | PRESENT | **2** |
| `.../K0f_runs` | PRESENT | **20** |
| `.../K0e_runs` | PRESENT | **1** |

The reader that returned ABSENT on `K0eR3_runs` returned PRESENT on three
siblings and counted 2, 20 and 1 `STATUS.*` files there, so **it is demonstrably
able to see a non-zero**, and the zero it returned on K0eR3 is a statement about
the disk. No queue entry naming `K0eR3` exists in
`verification/queue/heat-transfer/` or anywhere under `verification/queue/`.

**This document SUPERSEDES `K0eR2_PREREGISTRATION.md`**, which is graded and
closed and is **not edited** (standing rule 6). K0eR2 is the predecessor; **the
physics problem is identical, the case is identical, the mesh is identical, and
the CONTROL DESIGN is not.**

---

## 0. WHAT VERDICTS THIS RUNG CAN REACH — stated first

| | |
| --- | --- |
| **`PASS`** | `M4b` at **0 ULP** AND `Z1` at **0 ULP against 0.0** on all 208 plate faces, with both arms `DONE` under the strict completion rule and every refusal cleared |
| **`GATE FAIL`** | `M4b` **non-zero** with both arms `DONE` and every control clear — a MEASURED failure of the `beta`/`g` neutralisation. **§5.2 is a deliberate departure from the predecessor's label and it is argued there, not slipped in.** |
| **`NOT A RESULT`** | any arm not `DONE`; or `Z1` non-zero (the reader manufactures flux, so no measurement exists); or `D0` non-zero (the 0-ULP design is void on this box) |
| **`BLOCKED`** | only with a capability gap NAMED and placed on Sanaa's desk |
| **`PENDING`** | queued, not yet taken by the daemon |
| **Not reachable, by construction** | a `PASS` **on the Stanton comparison** — REPORTED, never graded (§3) |

**A `PASS` here means `beta` and `g` were demonstrated neutral against a 20 K
thermal perturbation, so a Stanton error on this rung is attributable to the
thermal closure alone. It does not mean the thermal closure was validated** —
§2.1.3's circularity caution is why.

**A `GATE FAIL` WILL BE REPORTED AS A `GATE FAIL`**, with the worst ULP
distance, its cell index, its component, its processor and its `|diff|` in m/s
printed beside the verdict. It will not be relabelled, softened, hedged, or
converted into `NOT A RESULT` to avoid naming a failure. The threshold is 0 ULP
and it is frozen here; **it will not be widened to fit whatever the run returns**
(Sanaa's standing ruling, and `CLAUDE.md` rule 2).

---

## 0.1 ⚠ THE STATE OF THIS REGISTRATION — READ BEFORE ANY LAUNCH

**THE GRADING PATH IS NOT CUT. THIS REGISTRATION IS NOT ARMED FOR COMPUTE AND
NOTHING MAY BE LAUNCHED AGAINST IT AS IT STANDS.** §9 specifies the three
scripts exhaustively — every row, every threshold, every refusal — and pins
none, because none has been written. **A dated pre-compute addendum cutting the
three git-blob pins is OWED before the first queue entry is dropped**, and rule 2
permits that amendment precisely because no K0eR3 compute exists (the condition
is checked at the head of this document, under a planted control).

**Everything that a gate could be laundered through is frozen HERE and now**: the
thresholds (0 ULP; 0.0 flux; the six eq.-(1) values at both wall temperatures),
the labels, the cost POINT and CAP, the predictions and their falsifiers. The
addendum may cut pins and may not touch any of them.

---

## 1. WHY THIS RUNG

Unchanged from the predecessor and restated because it is the reason the control
had to be redesigned rather than dropped.

**It breaks the confound `THERMAL_CAPABILITY_STATE.md` §5 names as binding.**
Every graded thermal result this lab owns is a buoyant cavity in which momentum
and thermal fields are **both wrong and coupled through buoyancy**, so no error
is attributable. **`K0cR` is the proof**: fixing the stress closure moved
velocity **19 points TOWARD** experiment and wall heat flux **30 points AWAY**,
in the same solves.

With `beta = 0` and `g = (0 0 0)` there is no buoyancy coupling, so any
Stanton-number error is attributable to the thermal closure **alone**.
**Attribution — not validation — is what this rung buys**, and `M4b` is the row
that demonstrates the neutralisation actually holds in the binary. Without
`M4b` the attribution is an assertion about a dictionary, not a measurement.

---

## 2. THE REFERENCE, ITS TIER, AND ITS TITLE-PAGE VERIFICATION

**Bahrami, P. A. (2005). *Heat Transfer on a Flat Plate with Uniform and Step
Temperature Distributions.* NASA/TM–2005-212841. May 2005.** Tier **READ IN
FULL** (D430).

| check | result |
| --- | --- |
| Path | `docs/papers/forced_convection_heat_transfer/bahrami_2005_nasa_tm_212841.pdf` |
| sha256 of record | `0cd29adb20c0f6c21c07f37f101f0f8d3f3a7f85a81a95abc023da25a66f8be6` |
| **Title page, standing rule 15** | **page 1 of the PDF was rendered and READ** at the K0eR2 freeze, not inferred from filename or hash: `NASA/TM–2005-212841`; "Heat Transfer on a Flat Plate with Uniform and Step Temperature Distributions"; "Parviz A. Bahrami"; "May 2005". **VERIFIED** — and this document records that verification as the predecessor's, carried forward by citation, **not as a fresh read performed by this lane.** |

**Equation (1), as printed** (`.txt` sidecar line 353):

    St = 0.0296 Re^-0.2 (Pr Tw / T_inf)^-0.4

with `St = q / (Cp_inf rho_inf U_inf dT)` (line 441).

### 2.1 Three limits carried into the design, unchanged

1. **The primary is NOT OBTAINED.** Moretti & Kays (1965) exists here only as
   figures inside this secondary. **No row grades against their data.**
2. **Equation (1) is a correlation, not a measurement.**
3. **Circularity, the load-bearing caution.** Eq. (1) is Colburn-type and sits in
   the family of the Reynolds and Von Karman analogies. **The Reynolds analogy is
   close to what a constant-`Prt` gradient-diffusion closure asserts**, so
   agreement between a `Prt = 0.85` RANS solve and eq. (1) is **partly structural
   rather than evidential**. `Pr^-0.4` against `Pr^-2/3` is the only genuinely
   testing part, **and at `Pr = 0.71` that gap is small.**

---

## 3. NO BAND IS ARMED ON THE CORRELATION — UNCHANGED, AND NO NEW SOURCE IS HELD

**This rung REPORTS the Stanton number against equation (1). It does NOT gate on
it. No band is armed, because none can be honestly derived from the source in
hand, and nothing has been acquired since the predecessor's freeze that would
change that.**

Bahrami states uncertainties for Moretti & Kays — temperature 3 %, heat flux
2 %, velocity 1 % — **but those belong to their experiment, not to equation (1)**,
and the document states no uncertainty for the correlation itself.
`LITERATURE_CHARTER.md` §2 forbids a fourth tier for *"widely reported"*, **so
the correlation's conventional accuracy may not be invoked to arm a band.**

**And the tempting alternative is the one the discipline exists to prevent.**
Bahrami reports two-equation models at *"deviations of approximately 10
percent"*. **Setting the band to ~10 % would be setting the gate to what we
expect to achieve.** Standing rule 2 is the assertion that the gate could not
have been chosen to fit the answer; **a band chosen from the published
expectation is a band chosen to be met.** Not armed, and this paragraph is why.

**What would arm one later:** a source stating eq. (1)'s own uncertainty, or the
Moretti & Kays primary. Neither is held.

---

## 4. THE CONFLICT THIS RUNG EXISTS TO RESOLVE — STATED AT SOURCE

K0eR2 was graded **`NOT A RESULT`** at commit `1b6b710c`. Its transferable
finding is a **design conflict**, and this section states it exactly, because
the redesign in §5 is unreadable without it.

### 4.1 WHAT THE ZERO-`dT` ARM WAS FOR — two jobs on one artifact

`K0eR2_PREREGISTRATION.md` §4.3 defines `FP_T00` (plate at 300 K, `dT = 0 K`
exactly) as, verbatim, *"the zero-`dT` control **and the second operand of the
gated row**"*. **Those are two different jobs and the conflation is the defect.**

**Job A — the second operand of `M4b`, the only gated row.** `M4b` is the
ULP distance between `FP_T10`'s and `FP_T00`'s momentum field `U` at `endTime`,
threshold **0 ULP** (`K0eR2_PREREGISTRATION.md` §5, §5.1). Its evidentiary
content is the registered premise at `:238-240`: *"one binary, one operator set,
two wall temperatures. With `beta = 0` the thermal field cannot enter the
momentum equation at all, so a moved momentum field means one thing only."*
**Job A requires the two arms be IDENTICAL in every operator and every setting
except the wall temperature.**

**Job B — the physical zero-heat-flux control.** `M6`, *"zero-`dT` wall heat
flux | identically zero | REPORTED"* (`K0eR2_PREREGISTRATION.md` §5), and the
predecessor gate spec is explicit about the reader it protects
(`K0e_FORCED_CONVECTION_FLAT_PLATE_GATE.md` §4.2 control 2): *"With
`T_wall = T_inf` the heat flux must be identically zero and the Stanton number
undefined rather than small. **This catches a spurious flux from the
discretisation or the boundary conditions.**"* **The reader whose zero it
protects is the WALL-HEAT-FLUX READER — the instrument that produces `q`, and
therefore `St`, for every reported row on this rung.** Under standing rule 3 a
zero from that reader is not evidence unless the reader is shown able to see a
non-zero; `M6` was the arm that was supposed to establish it. **Job B requires
`dT` be identically zero.**

### 4.2 THE MECHANISM OF THE DEGENERACY, EXACTLY

`FP_T00`'s `0/T` sets `internalField uniform 300`, inlet `fixedValue 300` and
plate `fixedValue 300`, with `zeroGradient` at outlet and top and `symmetry` at
the bottom (verified on disk; `FP_T10/0/T` and `FP_T00/0/T` differ at **line 39**
only, `value uniform 310` against `uniform 300`, and `diff -rq` over `constant/`
and `system/` returns **nothing at all**).

**`T ≡ 300` is therefore simultaneously the initial condition and the exact
steady solution.** A uniform field has zero gradient everywhere, so convective
and diffusive fluxes vanish identically and both `zeroGradient` and `symmetry`
are satisfied by construction. The temperature equation is satisfied to machine
precision **before the first sweep**; OpenFOAM's residual normalisation factor
degenerates to round-off; and the **normalised** residual the solver tests
against `tolerance 1e-10` / `relTol 0.01` is **a ratio of two round-off
quantities** — an O(1) number that cannot fall.

**MEASURED, from `K0eR2_RESULTS.md` §3.2 and the arms' own `log.solve`:**

| | `FP_T10` | `FP_T00` |
| --- | ---: | ---: |
| T solves reporting `No Iterations 1000` (the smoothSolver default cap; no `maxIter` registered) | **0 of 9000** | **349 of 349** |
| first solve, initial residual | — | **0.5053587649** |
| first solve, final residual | — | **0.6092429219** — **LARGER THAN THE INITIAL**, which a converging solve on a well-posed system cannot do |
| final initial residual | 8.18e-08 | — |
| s / outer iteration | **0.3126** | **8.99** — factor **28.8**, flat (successive deltas 8.85, 8.91, 9.08) |

**HONEST LIMIT, KEPT RATHER THAN QUIETLY DROPPED: `normFactor` was NOT
instrumented.** The mechanism above is the reading those observations support;
it is not a measurement of the normaliser, and no claim is made that it was
measured. **This document repeats that limit rather than laundering the
predecessor's caveat into a fact.**

**Consequence, extrapolated at the measured flat rate:** `FP_T00` needed
**~80,900 wall s ≈ 2,696 core-min** to reach `endTime 9000` — **25.7× its own
registered 105.00 core-min cap and 12.8× the whole rung's 210.30 core-min
ceiling.** It was killed by its cap at iteration **350 of 9000**
(`STATUS.FP_T00`: `rc=124`, `wall=3151`, `timeout_s=3150`), and with
`writeInterval 9000` the loss was total: the case holds `0/` only, no field, no
restart point.

### 4.3 THE TWO HORNS — each with its mechanism

**HORN 1 — a fix that makes the control arm RUNNABLE breaks the premise `M4b`
depends on.** The fixes available at the dictionary are a `maxIter` on the T
solver, a looser `tolerance`/`relTol`, or freezing/disabling the T equation.
Applied **to the control arm only**, every one of them makes the arms differ in
more than the wall temperature: `diff -r` over `0/`, `constant/` and `system/`
would return two differences instead of the one it returns today, and the
registered premise *"one binary, one operator set, two wall temperatures"* is
false as written. `M4b`'s claim to isolate a `beta`/`g` leak rests on that
premise and on nothing else, so the comparison stops isolating what it says it
isolates.

**HORN 1 IS OVER-BROAD AS THE PREDECESSOR STATES IT, AND THIS DOCUMENT SAYS SO
RATHER THAN INHERITING IT UNEXAMINED.** `K0eR2_RESULTS.md` §4 asserts that *any*
solver-setting fix breaks the premise. **For a SYMMETRIC fix — the same
`maxIter` in both arms — the one-line-identity premise survives**, and the
predecessor's horn does not reach it. That variant nonetheless fails, for three
separate reasons which are §5.3's R3 and are argued there rather than smuggled
in here.

**HORN 2 — a fix that PRESERVES the premise leaves the degeneracy exactly where
it was.** The degeneracy is not a property of the solver settings. It is a
property of **the physical specification of the control**: `T_wall = T_inf` is
what makes the initial condition the exact solution. Any arm that is genuinely
`dT = 0` and genuinely identical to the thermal arm in every operator **is** the
arm that was killed by its cap, whatever else is done to it. Measured
consequence: no version finishes under any ceiling this rung could carry
(2,696 core-min required against a 105.00 per-arm cap), and under rule 2 the cap
could not have been widened in any case, first compute having closed it.

**THE CONFLICT IN ONE SENTENCE.** The condition that gives the arm its
discriminating power as a control (`dT ≡ 0`, so the true wall heat flux is
*exactly* zero and any non-zero reading is manufactured) is precisely the
condition that makes the arm's solve degenerate; and the arm cannot be repaired
in either direction because it is simultaneously the operand of a bit-exactness
comparison. **The fault is the CONFLATION of Job A and Job B onto one artifact,
not either job.**

### 4.4 THE PREDECESSOR'S FIGURES, RE-MEASURED AGAINST ITS ARTIFACTS

Re-derived by this lane from `K0eR2_runs/STATUS.FP_T10` and
`STATUS.FP_T00` rather than accepted from the results prose:

| figure | re-measured | source | agrees with the record? |
| --- | ---: | --- | --- |
| `FP_T10` wall | 2843 s | `STATUS.FP_T10` `wall=2843` | yes |
| `FP_T10` core-min = 2843 × 2 ÷ 60 | **94.7667** | rule 12's unit | yes — the record's **94.77** is this, rounded |
| ratio against the registered POINT 35.00 | **2.7076** | | yes — the record's **2.708** |
| timeout margin, 3150 − 2843 | **307 s** | `timeout_s=3150` | yes — **9.75 % of the registered wall cap** |
| cap margin in core-min, 105.00 − 94.7667 | **10.2333 core-min** | | not previously stated in these terms; **the arm cleared its cap by 9.75 %, on luck rather than on margin** |
| `FP_T00` core-min = 3151 × 2 ÷ 60 | **105.0333**, ratio **3.0010** | `STATUS.FP_T00` `wall=3151` | yes |
| rung actual | **199.80 core-min**, ratio **2.8502** against POINT 70.10 | | yes |
| dollars actual, DERIVED | **$0.17083** at $0.0513/core-h | | yes |

**No figure in the brief or in `K0eR2_RESULTS.md` §10 was found wrong against its
artifact.** The one thing added is the cap margin stated in core-minutes: 307 s
of wall headroom is **9.75 %**, and §7 of this document treats that as the
calibration lesson rather than as a success.

---

## 5. THE CONTROL REDESIGN — THE SUBSTANCE OF THIS REGISTRATION

**The resolution is structural: SPLIT JOB A FROM JOB B, and give each the
instrument that fits it.** Neither the gate nor the control is relaxed; the gate
threshold stays 0 ULP and the control's expectation stays an exact zero.

### 5.1 THE THREE COMPONENTS

**C1 — `M4b`'s second operand becomes `FP_T290`, the plate at 290 K
(`dT = −10 K`), a NON-DEGENERATE solve.**

- **One line differs from `FP_T10`.** `0/T` line 39, `value uniform 290` against
  `uniform 310`. Verified as the correct line on disk against the existing arms,
  where `diff -rq` over `constant/` and `system/` returns nothing and `0/`
  differs in `T` alone. The premise `M4b` rests on is preserved **literally**,
  and §5.4's `P7` makes it a blocking refusal rather than an expectation.
- **The degeneracy is removed, not truncated.** With `T_wall = 290` and
  `T_inf = 300` the temperature field has a real gradient, the normaliser is
  well conditioned, and the T solve is the same well-posed problem `FP_T10`
  solved with **zero** of its 9000 T solves hitting the 1000-sweep cap. The sign
  of `dT` is irrelevant to well-posedness; a cooled plate is as well-posed as a
  heated one.
- **SENSITIVITY IS DOUBLED, NOT MERELY RESTORED.** In
  `buoyantBoussinesqSimpleFoam` the only route from `T` to `U` is
  `rhok = 1 − beta·(T − TRef)` entering `UEqn.H`'s
  `fvc::reconstruct((−ghf·fvc::snGrad(rhok) − fvc::snGrad(p_rgh))·mesh.magSf())`.
  That coupling is **linear in `(T − TRef)`, hence ODD**. The registered pair
  `(0, +10)` drives any leak with amplitude ∝ `beta·10`. The pair `(−10, +10)`
  drives it with amplitude ∝ `beta·20`, **and with opposite sign between the
  arms**. A leak the predecessor's design would have shown at amplitude `L`
  shows at `2L` here.

**C2 — Job B, the zero-heat-flux control, is re-homed onto `Z1`: a PLANTED,
ON-DISK control at ZERO solver compute.**

The predecessor spent a projected 2,696 core-min to produce a field whose exact
value is known a priori. **Construct it instead.** In scratch, copy
`FP_T10/<endTime>/T` and overwrite it, **by line index**, with a *nonuniform*
internal field every one of whose 52,224 values is exactly `300.0`, and with
every `plate` patch face value exactly `300.0`. Run the **production
wall-heat-flux reader** — the same function the graded path calls — on that
field.

- **Registered requirement: identically zero wall heat flux on every one of the
  208 plate faces, expressed as `0` ULP against `0.0`. There is no epsilon and
  there must never be one.** A non-zero is flux manufactured by the reader, the
  flux formula or the mesh — exactly what Job B exists to catch — and it is
  printed per face with its magnitude and its face index.
- **`Z2`, the POSITIVE plant, without which `Z1` is not evidence** (standing
  rule 3, on the working model of `T3_runs/analyse_t3.py`'s `plant_into_T` /
  `planted_zero_control` and its refusal at `:801`, and `T10a_runs/
  analyse_t10a.py:846`). Into a copy of the `Z1` field, plant
  `PLANT_T = 1.234e-03` K by line index into the **owner cell of a NAMED plate
  face** (the plate face of smallest `x`; its index and the line index are
  printed), read it back through the **same wall-flux reader**, and **REFUSE
  (exit 2) if the flux reader does not move.** A zero from a reader not shown
  able to see a non-zero is not evidence.
- **`Z3`, the NEGATIVE plant, which tests that the reader reads the RIGHT
  cells.** Plant the same `1.234e-03` K into a NAMED interior cell adjacent to no
  plate face, and **REFUSE (exit 2) if the plate wall-flux reader fires.** A
  reader that fires here is summing over cells it has no business reading, and
  `Z1`'s zero would then be meaningless in the other direction.

**C3 — the structural clause, registered so this cannot recur.** **No arm or
artifact in this rung is simultaneously the operand of a bit-exactness
comparison and the carrier of a physical null.** `M4b` reads two solves; `Z1`
reads one constructed field; they share no operand. That is the rule K0eR2 paid
105.03 core-min of total-loss waste to learn, and it is written here as a
constraint rather than as a lesson.

### 5.2 A DELIBERATE DEPARTURE FROM THE PREDECESSOR'S LABEL — `M4b` NON-ZERO IS `GATE FAIL`

`K0eR2_PREREGISTRATION.md` §0 registers a non-zero `M4b` as **`NOT A RESULT`**.
**K0eR3 registers it as `GATE FAIL`, and the change is argued rather than
slipped in.**

`NOT A RESULT` is for a row that **could not be measured** — an arm that did not
complete, a control that refused, a Roache triple that is not `CONVERGING`. A
non-zero ULP distance between two complete arms **is a measurement**: the
neutralisation was tested against a 20 K perturbation and was found to leak. It
fails a threshold frozen before compute. That is the definition of `GATE FAIL`
(standing rule 1; `VERIFICATION_CHARTER.md` §2). Labelling it `NOT A RESULT`
conflates *"we measured it and it failed"* with *"we could not measure it"*, and
the vocabulary exists precisely to keep those apart.

**The threshold is UNCHANGED at 0 ULP. This departure is strictly in the honest
direction: it makes a failure NAMEABLE as a failure instead of dissolving it
into an absence, and it makes `GATE FAIL` genuinely reachable on this rung for
the first time.** It widens nothing.

Standing rule 5's ordering is not disturbed: no grid triple exists on this rung
(§8.3), so rule 5 does not engage, and no gate here converts a `NOT A RESULT`
into a `PASS` or a `GATE FAIL` in the forbidden direction.

### 5.3 THE ALTERNATIVES, AND WHY EACH WAS REJECTED

**R1 — REJECT: a plant-only design, dropping the second solve entirely.**
A plant into a field on disk demonstrates that **the reader** can see a
non-zero. It does not re-run the momentum equation, so it **cannot test whether
`T` reaches `U`**. Substituting a plant for `M4b`'s second operand would replace
a physics test with an instrument test and then report the instrument's health
as though it were the physics — **`FAIL_OPEN` face (d) exactly: the absence of an
error read as the presence of a check.** The plant is therefore used for the job
it fits (`Z1`/`Z2`/`Z3`, Job B) and refused for the job it does not (Job A).
*The grader's existing `P1`/`P2`/`P3` plants already do the reader-discriminability
job for the ULP reader and are carried forward unchanged in role (§8.1); they
were never a substitute for a second solve either.*

**R2 — REJECT: fix `FP_T00` by dictionary, ASYMMETRICALLY** (a `maxIter` or a
looser tolerance on the control arm only). This is Horn 1 in its exact form:
`diff -r` returns two differences, the registered premise is false as written,
and the comparison no longer isolates a `beta`/`g` leak.

**R3 — REJECT: fix `FP_T00` by dictionary, SYMMETRICALLY** (the same `maxIter`
in both arms). **This variant survives Horn 1 as the predecessor states it, and
§4.3 says so.** It is rejected on three other grounds:

1. **It truncates the degeneracy rather than removing it.** The control arm's T
   solve would stop at `maxIter` having provably not converged — measured: its
   first solve's final residual *exceeds* its initial. A strict-completion rule
   satisfied by a solve that is measured not to converge is bookkeeping, not
   evidence, and the lab's own rule-5 ordering treats "not iteratively
   converged" as `NOT A RESULT` wherever a triple is graded.
2. **It forces a re-run of `FP_T10`.** The arms must be identical, so a
   symmetric `fvSolution` change invalidates the existing complete, rule-4-clean
   `FP_T10` (94.77 core-min already spent) and costs ~95 core-min to reproduce
   — the "cheap" fix is not cheap, and it discards the rung's only usable
   artifact.
3. **It does nothing for sensitivity.** The pair remains `(0, +10)`, half the
   leak drive of `(−10, +10)`.

**R4 — REJECT: freeze or disable the T equation in the control arm.** Applied
asymmetrically it is R2. Applied symmetrically it destroys `FP_T10` — no `T`
field, no `alphat`, no Stanton number, no thermal arm, no rung.

**R5 — REJECT: a small-but-nonzero `dT` with the expectation stated as a LIMIT
rather than an identity** (e.g. `dT = 0.1 K`, *"flux → 0 as `dT` → 0"*). This is
**worse than both** on this rung, for two reasons:
1. It **approaches** the degeneracy rather than removing it. The normaliser's
   conditioning degrades continuously as `dT → 0`, and **no `dT` is known at
   which it is safe** — establishing one would need a measurement this lab does
   not hold. `dT = −10 K` is at the opposite extreme of that continuum, at the
   same magnitude the thermal arm already ran cleanly at, so its conditioning is
   evidenced by a completed 9000-iteration solve rather than by hope.
2. It **replaces an exact identity with a band nobody can derive.** `flux ≡ 0`
   is gradeable at 0 ULP with no tolerance constant; *"flux is small"* requires a
   threshold, and there is no source from which to derive one. **This is the same
   ground on which §3 refuses to arm a Stanton band**, and it is refused here for
   the same reason.

**R6 — REJECT: widen the cap, or widen the gate.** Gates are never widened to
fit (Sanaa's standing ruling; `CLAUDE.md` rule 2). And K0eR2's caps were closed
by first compute in any case. The arm needed **25.7×** its cap; no widening was
ever the answer.

### 5.4 WHAT THE CHOSEN DESIGN CANNOT DETECT — THE NAMED BLIND SPOTS

**A control whose blind spot is unstated is `FAIL_OPEN` face (d). These are
stated before the run, not after it.**

**B1 — `M4b` on the pair `(−10, +10)` is BLIND to a leak that is EVEN in
`(T − TRef)`.** Any coupling whose effect on `U` is an even function of
`(T − TRef)` — a term in `(T − TRef)²`, in `|T − TRef|`, or a transport property
symmetric about `TRef` — produces *identical* `U` perturbations in both arms and
**cancels exactly** in the ULP difference. **The predecessor's `(0, +10)` pair
was NOT blind to this class.** The blindness is bought deliberately, in exchange
for removing the degeneracy and doubling the odd-mode drive, and it is named
here rather than discovered later. *Mitigation registered as an argument, NOT as
a measurement:* the only `T → U` term in the installed v2606 source is
`rhok = 1 − beta·(T − TRef)`, which is linear and therefore odd, so the leak this
rung exists to detect is in the covered class — **but the whole point of a gate
is to catch a route nobody anticipated, and the even class is genuinely
uncovered.**

**B2 — `M4b` is a DIFFERENCE test and is blind to a leak common to both arms.**
Any contamination of `U` that is identical in both arms — a constant spurious
body force, a `T`-independent defect — cancels. `M4b` tests differential
sensitivity to `T`, not the correctness of `U`. **This rung carries no GATED
check on absolute momentum correctness and does not claim one**; `M4` is the row
that would have, and it is REPORTED for the operator-confound reason
(`K0eR2_PREREGISTRATION.md` §5.1, carried forward at §5.5 below).

**B3 — `Z1` cannot detect a spurious flux that requires a NON-UNIFORM near-wall
`T` field to appear.** A wrong `alphat` wall value, a wrong face-to-cell
distance, a wrong sign on one patch: none of these fires on an exactly uniform
field. **`Z1` tests the reader's NULL case, and that is all it tests.**

**B4 — `Z1`'s zero is a statement about the reader, the mesh and the flux
formula, not about the solver.** The `dT = 0` **solve is not performed at all**,
so nothing in this rung demonstrates that the solver, run at `dT = 0`, would hold
`T` at 300. K0eR2 measured evidence *consistent* with `T ≡ 300` being the
discrete solution (residuals behaving as round-off from the first sweep) but
**`normFactor` was not instrumented and no such claim is made here.**

**B5 — `0` ULP is on the WRITTEN artifact at `writePrecision 10`.** Carried
forward verbatim in substance from `K0eR2_PREREGISTRATION.md` §5.1: 0 ULP means
the two fields agreed to at least the written precision and rounded identically;
**it does not prove agreement in the unwritten low-order bits. The gate is a
NECESSARY condition, not a sufficient one.**

**B6 — NO GRID TRIPLE, so NO DISCRETISATION BOUND AT ALL.** §8.3. Every K0eR3
number is a single-mesh number.

**B7 — `D0` establishes determinism WITHIN this epoch and at 200 iterations.**
It cannot detect a nondeterminism that manifests only after long runs, or only
under a load pattern absent while `D0` ran. It is a cheap decisive test for the
*presence* of nondeterminism, not a proof of its absence at scale.

### 5.5 THE ROWS

| # | quantity | against | status |
| --- | --- | --- | --- |
| **`D0`** | determinism twin: two 200-iteration invocations of the same case, processor-local `U` ULP distance | **0 ULP** | **REFUSAL GATE, ARMED BEFORE THE MAIN ARMS.** Non-zero → the main arms are **NOT LAUNCHED**, rung `NOT A RESULT`, mechanism named |
| **`P7`** | `diff -r` over `0/`, `constant/`, `system/` between the two arms | **exactly one** difference, at `0/T` line 39 | **REFUSAL (exit 2)** on any other count, or on a difference at any other line or file |
| **`M4b`** | same-solver ULP distance, `FP_T10` vs `FP_T290`, `U` at `endTime`, processor-local, every component of every cell | **0 ULP** | **GATED. Non-zero → `GATE FAIL`** (§5.2) |
| **`Z1`** | wall heat flux from the production reader on the constructed uniform-300 field, all 208 plate faces | **identically 0**, at **0 ULP against `0.0`** | **GATED. Non-zero → `NOT A RESULT`** |
| **`Z2`** | positive plant `1.234e-03` K at the owner cell of a named plate face | must **FIRE** | **REFUSAL (exit 2)** if unseen |
| **`Z3`** | plant `1.234e-03` K at a named interior cell adjacent to no plate face | must **NOT** fire on the plate reader | **REFUSAL (exit 2)** if it fires |
| **`P1`/`P2`/`P3`** | the three registered ULP-reader plants, carried forward unchanged | `K0eR2_PREREGISTRATION.md` §8.1 | **REFUSAL** |
| **`M1`** | `St(Re_x)` at six stations, **BOTH ARMS** | eq. (1) at `Tw = 310` and at `Tw = 290` | **REPORTED, NO BAND** (§3) |
| **`M1b`** | `\|St(FP_T290) − St(FP_T10)\| / St(FP_T10)` at the six stations | — | **REPORTED** — the new row the redesign buys (§6, Pred-10) |
| **`M2`** | `Cf(Re_x)` | the reference's own field, same reader | **REPORTED** (control) |
| **`M3`** | `Prt_eff = nut/alphat`, over cells with `alphat > 0` only, excluded count PRINTED | — | **REPORTED**, a CONVERGENCE diagnostic and not physics (`K0eR2_PREREGISTRATION.md` §6.5) |
| **`M4`** | cross-solver ULP distance, `FP_T10` vs the recorded `simpleFoam` field | — | **REPORTED, NOT GATED** — the discrete pressure-gradient operators differ independently of `beta`/`g`, so it cannot answer its own gating question (`K0eR2_PREREGISTRATION.md` §5.1) |
| **`M5`** | thermal BL thickness, near-wall `alphat`, both arms | — | **REPORTED** |
| **`D2`** | cross-epoch ULP distance, this rung's `FP_T10` vs `K0eR2_runs/FP_T10` at `9000` | — | **REPORTED, NOT GATED** — a non-zero cannot separate solver nondeterminism from a change in the box between 2026-09-03 and now, and a row that cannot answer its own question is not gated |

**Reported stations, fixed before any compute:**
`Re_x = 1.0e6, 2.0e6, 3.0e6, 5.0e6, 7.0e6, 1.0e7` — nearest plate face to each
target, with the actual `Re_x` printed beside the value.

**Eq. (1) at those stations (`Pr = 0.71`), COMPUTED AND COMMITTED BEFORE ANY
K0eR3 CASE DIRECTORY EXISTS, for BOTH wall temperatures:**

| `Re_x` | `St`, `Tw = 310 K` (`Tw/T_inf = 1.03333333`) | `St`, `Tw = 290 K` (`Tw/T_inf = 0.96666667`) |
| ---: | ---: | ---: |
| 1.0e6 | **2.113938e-03** | **2.171089e-03** |
| 2.0e6 | **1.840290e-03** | **1.890043e-03** |
| 3.0e6 | **1.696946e-03** | **1.742824e-03** |
| 5.0e6 | **1.532139e-03** | **1.573561e-03** |
| 7.0e6 | **1.432427e-03** | **1.471154e-03** |
| 1.0e7 | **1.333805e-03** | **1.369865e-03** |

The `Tw = 310` column is byte-identical to `K0eR2_PREREGISTRATION.md` §5's
table. The ratio of the two columns is the constant
**`(0.71·290/300)^-0.4 / (0.71·310/300)^-0.4 = 1.027036`**, and Pred-10 turns
that constant into a falsifiable statement about the model.

### 5.6 THE D-J1 DENOMINATOR AUDIT — EVERY DIVISION IN THIS RUNG, AND WHAT IT DOES AT ZERO

The D-J1 class of defect is `rel = dmax / rng if rng > 0 else 0.0` — a
divide-by-zero guard that substitutes **the value which grades best**. Every
denominator in this rung is enumerated here with its zero behaviour registered.

| row | denominator | can it be zero? | registered behaviour at zero |
| --- | --- | --- | --- |
| `D0`, `M4b`, `D2` | **none** — an integer ULP distance between bit-keys | — | not applicable |
| `Z1`, `Z2`, `Z3` | **none** — an absolute comparison of flux against `0.0` at 0 ULP | — | not applicable |
| `M1` | `St_eq1` (the table above) | **no** — all twelve values exceed `1.3e-03` and are frozen here | — |
| `M1`, inner | `dT` inside `St = q/(Cp·rho·U·dT)` | yes in principle | **`\|dT\| = 10 K` on both registered arms. If any arm's `\|dT\|` is zero the Stanton row is `NOT A RESULT`, never `0.0` and never silently skipped** — the predecessor gate spec already required *"the Stanton number undefined rather than small"* |
| `M1b` | `St(FP_T10)` at a station | yes in principle | **`NOT A RESULT` for that station, printed as such, never `0.0`** |
| `M3` | `alphat` | **yes — `alphat_wall = 0` by construction** on a wall-resolved plate | **cells with `alphat == 0` are EXCLUDED and their COUNT is PRINTED. If every cell is excluded, `M3` is `NOT A RESULT`, never `0.0`** |

**BLANKET CLAUSE, BINDING ON THE GRADER: no comparator in this rung may
substitute a value on a zero denominator. Every zero-denominator branch returns
`NOT A RESULT` or REFUSES (exit 2); none returns `0.0`, none returns a pass, and
none is silently skipped.** `Z1` is expressed **absolutely rather than
relatively for exactly this reason**: a relative form `|q|/q_ref` has a
denominator that is *identically zero on the null case*, which is the D-J1 trap
in its purest form.

---

## 6. PREDICTIONS AND FALSIFIERS, REGISTERED BEFORE COMPUTE

**Nothing here is a quantity this lane has already computed.** In particular
`FP_T10/9000/`'s `T`, `alphat`, `nut` and `wallShearStress` fields **were
deliberately NOT read before this freeze**, so Pred-6, Pred-7 and Pred-10 are not
reverse-engineered from an answer already in hand. That abstention is stated so
a reader can hold it against the record.

| # | prediction, with number and direction | falsifier | consequence |
| --- | --- | --- | --- |
| **Pred-1** | `FP_T290` completes all six rule-4 clauses, and **zero of its 9000 T solves report `No Iterations 1000`** (`FP_T10`: 0 of 9000; `FP_T00`: 349 of 349) | **any** T solve reporting `No Iterations 1000` | recorded; the arm's completion is judged on rule 4 regardless |
| **Pred-2** | `FP_T290`'s cost lands in **[71.1, 118.5] core-min**, i.e. within ±25 % of `FP_T10`'s **measured 94.7667** | outside that interval | recorded as a calibration miss with its direction; the CAP (§7) is the guard, not this interval |
| **Pred-3** | **`M4b` = 0 ULP** — with `beta 0` and `g (0 0 0)` there is no source-level route from `T` to `U` in v2606 | any component of any cell at non-zero ULP | **`GATE FAIL`**, with the worst ULP, its cell, component, processor and `\|diff\|` in m/s printed beside it |
| **Pred-4** | **`Z1` = 0 flux at 0 ULP on all 208 plate faces** | any face non-zero | **`NOT A RESULT`**, with the manufactured flux printed per face |
| **Pred-5** | **`D0` = 0 ULP** — the solver is bit-reproducible across invocations at a fixed decomposition | non-zero | **the main arms are NOT LAUNCHED**; rung `NOT A RESULT`; the 0-ULP design is recorded as void on this box |
| **Pred-6** | on `FP_T290` at `endTime`, **`max \|nut/alphat − 0.85\|` over cells with `alphat > 0` is below `1e-3`**, against **0.697** measured on K0eR2's 5-iteration preflight (min 0.4391, max 1.5470) | at or above `1e-3` | recorded; `M3` is REPORTED and gates nothing |
| **Pred-7** | `\|St − St_eq1\|/St_eq1` **of order 10 % or less** at all six stations on **both** arms, from Bahrami's own statement about two-equation models | a deviation far outside that order | recorded. **THIS IS A PREDICTION AND NOT A BAND, NOT A THRESHOLD, NOT A GATE.** It cannot produce `PASS` and cannot produce `GATE FAIL`. §3 is unaffected |
| **Pred-8** | **`M4` will be non-zero** — `fvc::grad` and `fvc::reconstruct(snGrad(·)·magSf)` are different discrete operators and differ independently of `beta` and `g` | zero | REPORTED either way; `M4` gates nothing |
| **Pred-9** | **`D2` = 0 ULP** — this rung's fresh `FP_T10` reproduces K0eR2's `FP_T10` bit-for-bit across the epoch | non-zero | REPORTED. A non-zero is recorded as *"reusing the predecessor's arm would have been unsound"* and does not touch this rung's verdict, because **both arms are run fresh** (§7.4) |
| **Pred-10** | **The two arms' Stanton numbers will be EQUAL at matched `Re_x` to within `1e-5` relative** (`M1b`), because the constant-property Boussinesq energy equation is **exactly linear in `(T − TRef)`** and, at `beta = 0`, the momentum field is independent of `T`: `q` scales linearly with `dT`, so `St = q/(Cp·rho·U·dT)` is **independent of `dT` and of its sign**. **Equation (1), by contrast, predicts the cooled arm's `St` to be `1.027036 ×` the heated arm's.** The rung will therefore **MEASURE a ~2.70 % structural discrepancy between the constant-property model and the correlation's temperature-ratio factor** — a variable-property effect the model has no mechanism to represent | `M1b` at or above `1e-5` at any station | REPORTED, not gated. **This row is impossible under the predecessor's design, whose control arm had no Stanton number at all**, and it doubles as an independent cross-check on `M4b`'s premise: an `M1b` far above round-off means either the momentum field moved or the energy equation is not linear, both of which `M4b` should also see |

**The `1e-5` in Pred-10 is derived, not chosen:** `FP_T10`'s final linear-solve
initial residual is `8.18e-08` and fields are written at `writePrecision 10`, so
agreement much tighter than `1e-5` cannot honestly be claimed from the artifact.

---

## 7. COST — POINT AND CAP, BUILT ON THE MEASUREMENT AND NOT ON THE PREDECESSOR'S OPTIMISM

### 7.1 THE CALIBRATION THAT SETS THIS ESTIMATE

**K0eR2's `FP_T10` ran at ×2.7076 its registered POINT, and this registration
does not repeat that point.** The predecessor derived 35.00 core-min as
**28.00** (the measured `simpleFoam` reference on this exact mesh) × **1.25**, a
solver factor its own §7.1 flagged as *"an ESTIMATE, not a measurement"*. The
**measured** multiplier is **3.38×** (94.7667 ÷ 28.00): the added `T` equation
cost **2.7 times what the registration allowed for it**.

**THE K0eR3 BASIS IS THE MEASUREMENT ITSELF, NOT A FACTOR APPLIED TO A PROXY:**
`FP_T10`, 52,224 cells, `endTime 9000`, 2 ranks, **94.7667 core-min MEASURED**
(`K0eR2_runs/STATUS.FP_T10`, `wall=2843`, `ranks=2`).

**The contention confound is named and NOT netted out.** The same binary on the
same mesh has been measured at **1.440 s/it under load and 0.112 s/it free — a
factor of 12.9** — and `FP_T10`'s own run-average of **0.3126 s/it** sits between
those bounds. **The POINT is therefore set from a MODERATELY-LOADED measurement,
which is the box's normal state, rather than from a free-box rate that would be
optimistic for the same reason 35.00 was.**

### 7.2 THE REGISTERED FIGURES

| item | POINT (core-min) | CAP (core-min) | enforced as |
| --- | ---: | ---: | --- |
| `D0`, invocation 1 (200 it) | **3.50** | **10.50** | `--timeout 315` s at 2 ranks |
| `D0`, invocation 2 (200 it) | **3.50** | **10.50** | `--timeout 315` s at 2 ranks |
| `FP_T10` (9000 it) | **95.00** | **475.00** | `--timeout 14250` s at 2 ranks |
| `FP_T290` (9000 it) | **95.00** | **475.00** | `--timeout 14250` s at 2 ranks |
| grader, one invocation | **0.30** | **0.90** | — |
| **RUNG** | **197.30** | **CEILING 971.90** | |

**Derived dollars at $0.0513/core-h: POINT `$0.16869`, ceiling `$0.83098`.**
**DERIVED, NOT MEASURED.** `cost_basis`: **reported-by-owner** — this box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Well inside the
pre-authorised envelope, **and costed anyway**, because rule 12 requires it and a
blanket is not a per-item read (rule 9).

**`D0`'s POINT** = 200 × 0.3126 s/it × 2 ÷ 60 = **2.084** core-min of solve, plus
build and solver startup, which K0eR2 measured as dominant on short runs (its
5-iteration preflight ran at `2.30e-05` core-s/cell-it against the reference's
`3.57e-06`, **six times** the steady rate). Rounded to **3.50**.

**THE CAP CARRIES REAL MARGIN, AND THIS IS THE ONE LESSON THE PREDECESSOR'S
`FP_T10` DID NOT LEARN.** That arm cleared its 3150 s timeout by **307 s —
9.75 %** — and its 105.00 core-min cap by **10.23 core-min**. **That was luck,
not margin.** The K0eR3 per-arm CAP is **5× the POINT**, and the multiple is
derived rather than chosen:

- The worst measured contention factor against `FP_T10`'s own rate is
  **1.440 / 0.3126 = 4.606**, i.e. a worst case of **436.5 core-min**. The
  475.00 cap covers it with **8.8 % headroom**, so a merely-slow run finishes
  instead of being killed and re-spent.
- The K0eR2 degeneracy failure mode demanded **~2,696 core-min**. The cap sits
  **5.7× below** it, so it still **separates "slow" from "degenerate"** and still
  stops a runaway.
- Predicted wall at the POINT is **2843 s** against a **14,250 s** timeout —
  **11,407 s of headroom**, against the predecessor's 307 s.

**The two columns are different instruments and are not collapsed** (L-463): the
POINT is the prediction rule 12's ratio divides by; the CAP is the guard.
**An overrun STOPS the run; it does not get a new budget.**

**The momentum reference `simpleFoam` solve is NOT re-run.**

### 7.3 SPEND AGAINST THE PREDECESSORS, NAMED SEPARATELY AND NOT ABSORBED

Per `COMPUTE_BUDGET_CHARTER.md` §6, waste is reported, never folded into a ratio.

| item | core-min | class |
| --- | ---: | --- |
| K0e attempt 1 (`FP_T10`, rc=1, `wall=0`) | **0.00** solver time | **WASTE** — it bought nothing |
| K0eR2 preflight (5 it, 2 ranks) | **0.10** | **PREFLIGHT, not waste** |
| **K0eR2 `FP_T00`** (capped at iteration 350 of 9000, no field written, no restart point) | **105.0333** | **WASTE — a total loss, 52.6 % of the K0eR2 rung spend** |
| K0eR2 `FP_T10` | **94.7667** | **PRODUCTIVE** under K0eR2, and **it is NOT credited against K0eR3's POINT** (§7.4) |

**None of these figures enters the §7.2 POINT and none may be absorbed into
K0eR3's actual/predicted ratio.** All are carried into K0eR3's
`docs/COST_CALIBRATION.md` row when this rung completes. **K0eR2's own row is
already landed** as `C-20260903T221017.737046Z-a995ad3a` and is not duplicated.

### 7.4 RE-RUN VERSUS REUSE — THE DECISION, AND WHY IT COSTS 95 CORE-MIN ON PURPOSE

K0eR2's `FP_T10` is complete, rule-4 clean and on disk at
`verification/runs/F14-cooling-ladder/K0eR2_runs/FP_T10/9000/`. Reusing it would
save ~95 core-min. **It is NOT reused, and the reason is recorded so the spend
is not read as carelessness.**

A 0-ULP comparison across two run epochs and two registrations is sound only if
the box's arithmetic is unchanged between them, and **that cannot be established
by any cheap test** — `D0` proves invocation-to-invocation determinism *now*, but
cannot see a CPU, microcode or OpenFOAM change between 2026-09-03 and the K0eR3
launch. A non-zero `M4b` arising from an epoch difference would be reported as a
**`GATE FAIL` on a leak that does not exist** — a false failure, which is worse
than a wasted 95 core-min.

**Both arms are therefore run fresh, inside one run root, under one
registration, in one box epoch**, and the cross-epoch comparison is kept as
`D2`, REPORTED, where a non-zero teaches the lab something instead of
manufacturing a verdict.

---

## 8. THE CONTROLS, ARMED HERE

### 8.1 Planted controls (standing rule 3) — SIX, and each is separate on purpose

| plant | what | into | must |
| --- | --- | --- | --- |
| **P1** | `1.234e-03` K | a **copy** of the graded arm's `endTime` `T`, **BY LINE INDEX** | be **SEEN** by the production scalar reader, else REFUSE |
| **P2** | `1.234e-03` m/s into the **X-COMPONENT** | a **copy** of the graded arm's `endTime` `U`, by line index | be **SEEN** by the production **VECTOR** reader, else REFUSE |
| **P3** | exactly `0.0` | a copy of the same `T` | **NOT fire**, else REFUSE |
| **Z1** | the constructed exact uniform-`300.0` `T` field (nonuniform internal field, all 52,224 values `300.0`; every `plate` face value `300.0`) | scratch, by line index | read **identically zero** wall heat flux on all **208** plate faces, at 0 ULP against `0.0`. Non-zero → **`NOT A RESULT`**, printed per face |
| **Z2** | `1.234e-03` K at the owner cell of a **NAMED** plate face (smallest `x`; index printed) | a copy of the `Z1` field, by line index | make the **wall-flux reader** move, else REFUSE |
| **Z3** | `1.234e-03` K at a **NAMED interior cell adjacent to no plate face** | a copy of the `Z1` field, by line index | leave the **plate** wall-flux reader at 0 ULP, else REFUSE — a reader that fires here is reading cells it has no business reading |

**P2 is separate because a scalar plant does not exercise a vector reader**, and
**`M4b` reads vectors.** **Z2 is separate from P1 because the scalar-field reader
and the WALL-FLUX reader are different instruments**, and it is the wall-flux
reader whose zero `Z1` asserts. **Z3 is separate from Z1 because a reader can be
wrong in two directions** — blind, or over-inclusive — and only Z3 tests the
second. Each plant goes into the **field file the graded path reads** — never a
dict, a spec or a constants table — and is read back through the **same function
the graded path calls**. All are matched at **0 ULP**, not at a tolerance.

**K0eR2 EXERCISED NONE OF ITS PLANTS**: they sit after the both-arms early
return, so on a `NOT DONE` arm they are structurally unreachable
(`K0eR2_RESULTS.md` §7.1). **No planted-control evidence is inherited by this
rung, and none is claimed. All six must be exercised here.**

### 8.2 Strict completion rule (standing rule 4) — ALL-OR-NOTHING, WRITTEN OUT, BOTH ARMS

**Both `FP_T10` and `FP_T290` must satisfy EVERY clause. A failure of any one
clause on either arm is `NOT A RESULT` for the rung.**

1. **`rc = 0`**, read from `K0eR3_runs/STATUS.<arm>`.
2. **An `End` line** in the arm's `log.solve` — exactly one.
3. **Last time == `endTime`**, i.e. the last `Time = ` in the log equals the
   `endTime 9000` of that arm's own `system/controlDict`.
4. **Fields present at `endTime`**: `T U p_rgh alphat nut k omega`, the thermal
   family's set, all seven in `<arm>/9000/`.
5. **`ExecutionTime` line count == `endTime`**, i.e. 9000.
6. **THE AGE GUARD: every field at `endTime` NEWER than the case's own `0/T`.**
   `0/T` is touched **last** at launch, immediately before the solver, and so
   dates the run that was allowed to produce the answer. K0eR3 is
   **single-region** — one mesh, one case, no regions — so `0/T` is the correct
   dating file; the launcher must **touch it last** and must **refuse outright
   if `0/T` is absent after the build**, so the guard can never run without a
   datum.

**THE GUARD REFUSES A CASE WHERE `0/` OR ANY NUMERIC TIME DIRECTORY ALREADY
EXISTS**, on the reconstructed side **and** on the decomposed (`processorN/`)
side. A build into a directory that already holds state cannot be dated, and a
run that cannot be dated is not a run.

**CLAUSE 6 IS NOT AN INDEPENDENT CHECK AND THIS REGISTRATION SAYS SO**, because
K0eR2 found it the hard way (`K0eR2_RESULTS.md` §2.3): with **no** `endTime`
directory, the guard's `older` list is built by filtering the required fields on
a path that returns `None` for every one of them, so the list is **empty** and
the clause reports `PASS` **over an empty set** — a vacuous pass. Clause 4 fails
on exactly the same missing fields, so the guard is never load-bearing alone.
**Registered requirement for the K0eR3 grader: clause 6 must PRINT the number of
fields it actually compared, and a comparison over ZERO fields is reported as
`VACUOUS`, never as `PASS`.**

**The grader REFUSES (exit 2) rather than degrading**, on every refusal row of
§5.5.

### 8.3 Roache triple gating (standing rule 5) — NO TRIPLE IS FORMED

**Two arms on ONE mesh (52,224 cells). No grid triple exists, standing rule 5
does not engage, no GCI is computed and none is printed. GCI at `Fs = 1.25` is
the lab's convention where a triple exists; none exists here.** Quoting a GCI
where no triple exists would be inventing a convergence claim, and the
comparator must not.

**Registered for completeness, so a successor that DOES build a triple inherits
the rule correctly:** a triple that is not `CONVERGING` — `DIVERGENT`,
`STAGNANT`, `OSCILLATORY` or `EXACT` — is **`NOT A RESULT` whatever the value
says**, with the value, both triples and both orders printed beside it; any
level not iteratively converged or not plateaued is `NOT A RESULT` before that;
and **no GCI is ever quoted when the three values are not monotone.**

**THIS IS A REGISTERED LIMITATION OF K0eR3: every number this rung produces
carries NO discretisation bound at all** (B6).

### 8.4 The mesh, and the orthogonality assertion — carried forward as corrected

The case is the lab's existing TMR flat plate,
`/home/ubuntu/certonomous-runs/tmr-flatplate-finer`.

| item | value | source |
| --- | --- | --- |
| Cells | **52 224** | `log.checkMesh`; `constant/birth_certificate.json` |
| **Max non-orthogonality** | **0** | same — **asserted by the grader before any wall gradient is read** |
| Max skewness | 4.376137948e-14 | same |
| Max aspect ratio | **65 467.84834**, birth-certificate verdict **`flagged`** | same — a **prediction, not a blocker**, and predicted benign: a wall-resolved zero-pressure-gradient boundary-layer mesh is *supposed* to be extreme in aspect ratio, and this same mesh produced the momentum solution the lab records |
| `nu` | 2e-07 m2/s | `constant/transportProperties` |
| `U_inf` | 1.0 m/s | `0/U` |
| Plate | `x = 0` to `2.0 m`, **208 wall faces** | `constant/polyMesh/boundary` |
| **Plate cell spacing** | **min 4.493756e-04 m**, max 4.394886e-02 m | measured on the K0eR2 preflight |
| `Re_x` range | 0 to 1.0e7 | `U_inf x / nu` |
| `y+` on the plate | min 0.0592, max 0.2088 | wall-resolved |
| Momentum reference | `log.simpleFoam`, 9000 iterations, 2 ranks, ClockTime 840 s = **28.00 core-min** | the same case |

**The orthogonality evidence is `checkMesh`'s MEASUREMENT, not a per-face
epsilon.** The grader reads `constant/birth_certificate.json` from the case —
the builder copies it with the mesh so the case is self-describing — and
**REFUSES if `max_non_orthogonality` is absent or non-zero** (an exact comparison
against zero; any non-zero refuses). The per-face consistency bound is
`2e-9 × max(1, |x|)`, **DERIVED from `writePrecision 10`** — one unit in the 10th
significant digit, doubled because the two coordinates round independently and
can round in opposite directions. K0e's original `1e-12` assertion was
**measuring ASCII round-off and calling it non-orthogonality**, and it refused on
the preflight for that reason. **Its discriminating power was MEASURED**: over
all 208 plate faces the worst `|x_cell − x_face|` is `1.000000e-09` (pure
round-off) while the smallest plate cell spacing is `4.493756e-04 m` — **five
orders of magnitude above the bound**, so the bound sits in the gap and near
neither edge.

### 8.5 The case, unchanged in physics from the predecessor

| item | value | reason |
| --- | --- | --- |
| Solver | `buoyantBoussinesqSimpleFoam` (OpenFOAM **v2606**) | the solver the whole thermal ladder uses |
| `beta` | **0** | removes buoyancy exactly |
| `g` | **(0 0 0)** | removes it again, independently |
| `TRef`, `T_inf` | 300 K | |
| `Pr` | 0.71 | air |
| `Prt` | 0.85 | the ladder's value; comparable to K0cS and K0cX |
| **`div(phi,T)`** | **`bounded Gauss limitedLinear 1`** | the LADDER'S OWN scheme — what K0f and K0cS register — and the defect whose absence killed the original K0e as a launch-time fatal under `default none;` |
| `alphat` on the plate | `calculated`, value 0 | wall-resolved: `nutLowReWallFunction` with `y+ ≤ 0.209` gives `nut_wall = 0`, hence `alphat_wall = 0`. **An `alphatJayatillekeWallFunction` would impose a high-Re thermal law on a resolved wall** and is deliberately not used |
| `endTime` | **9000**, `startFrom 0` | identical to the momentum reference |
| Decomposition | **2 ranks, COPIED from the reference**, not re-derived | `scotch` re-derives; a cell-for-cell comparison across two derivations is meaningless. The builder copies `processorN/constant/polyMesh` including `cellProcAddressing` and runs `decomposePar -fields` |

**The arms**

| arm | `T_wall` | `dT` | `Tw/T_inf` | purpose |
| --- | --- | --- | --- | --- |
| **`FP_T10`** | 310 K | **+10 K** | 1.03333333 | the heated thermal arm |
| **`FP_T290`** | 290 K | **−10 K** | 0.96666667 | the cooled arm: `M4b`'s second operand, non-degenerate, and a Stanton measurement in its own right |

**`|dT| = 10 K` is small on purpose**: large enough that Stanton is well
conditioned, small enough that constant properties hold and a Boussinesq solver
with `beta = 0` is not asked to represent variable-density physics. **The
magnitude is unchanged from the predecessor's thermal arm; only the sign of the
control arm's `dT` has moved, from `0` to `−10`.**

---

## 9. THE GRADING PATH — SPECIFIED HERE, PINNED IN A PRE-COMPUTE ADDENDUM

**NOT ONE PIN IS CUT AND NOTHING MAY BE LAUNCHED UNTIL THEY ARE** (§0.1).

| file | role | what it MUST do |
| --- | --- | --- |
| `scripts/build_k0e.py` | case builder | **INSERT** an `FP_T290: ("300", "290")` entry into its `ARMS` table **with an assert, never by replacing an entry** (standing rule 14) — the assert must check that `FP_T10` and `FP_T00` are still present and unchanged. **REFUSE (exit 2)** on a case already holding `0/` or any numeric time directory, reconstructed **and** decomposed. Keep the three existing refusals around the `div(phi,T)` edit: refuse if the reference already has it; refuse if the edit did not take; refuse if the `div(phi,U)` entry count moved |
| `scripts/launch_k0e.sh` | launcher | **`touch <case>/0/T` LAST, immediately before the solver**; refuse outright if `0/T` is absent after the build; convert the registered per-arm CAP to a `timeout` by `cap_core_min × 60 ÷ ranks`; write `STATUS.<arm>` with `rc`, `wall`, `timeout_s`, `ranks`, `started_utc`, `ended_utc` |
| the K0eR3 grader | the gate | every row and every refusal of §5.5; the §5.6 denominator behaviour; the §8.2 completion rule including the **`VACUOUS` reporting of clause 6**; the six plants of §8.1; the §8.4 orthogonality refusal; and **`--expect-sha` support, with the grade valid ONLY when it is armed** |

**THE HASH FUNCTION IS NAMED SO A PIN CANNOT BE CHECKED AGAINST THE WRONG
DIGEST.** The pins to be cut are **git blob SHA-1**:

    sha1( b"blob " + str(len(content)).encode() + b"\0" + content )

**NOT sha256, and NOT a plain sha1 of the file's bytes.** `git hash-object <path>`
reproduces them; `sha1sum` and `sha256sum` do not.

**THE GRADER MUST NOT INHERIT THE PREDECESSOR'S TWO TRAPS**, both of which
K0eR2's results record:

1. **`rc = 0` on a `NOT A RESULT`.** K0eR2's grader exited `rc = 0` while
   printing `NOT A RESULT`, so a reader scripting against `$?` reads success
   (`K0eR2_RESULTS.md` §1). **The K0eR3 grader must exit NON-ZERO on any verdict
   that is not `PASS`, and the verdict of record is still taken from stdout and
   the landed artifact, never from the exit code.**
2. **A hard-coded banner naming the WRONG registration.** K0eR2's grader printed
   `prereg: .../K0e_PREREGISTRATION.md` while running under
   `K0eR2_PREREGISTRATION.md` (`K0eR2_RESULTS.md` §11.1). **The K0eR3 grader must
   take the registration path as an argument and print what it was given.**

---

## 10. WHAT THIS RUNG CANNOT DO

- **It cannot validate a thermal closure** (§2.1.3).
- **It cannot fail a model on the Stanton comparison** — no band is armed (§3).
- **It cannot bound its own discretisation error** — no triple (§8.3, B6).
- **`M4` cannot gate** (§5.5), and a non-zero `M4` is not a defect of this rung.
- **It is blind to an even-in-`(T − TRef)` leak** (B1) and to a leak common to
  both arms (B2).
- **`Z1` tests the reader's null case only** (B3) and says nothing about the
  solver at `dT = 0` (B4).
- **It is not the mixed-convection rung.** K0d is `BLOCKED`; K0f supersedes it.
- **It says nothing about buoyant flows.**
- **Nothing here is sent, filed, uploaded, registered or posted. PARKED**
  (standing rule 7).

---

## 11. WHAT CHANGED FROM `K0eR2_PREREGISTRATION.md`

| # | change | reason |
| --- | --- | --- |
| 1 | **The control arm becomes `FP_T290` (`dT = −10 K`); `FP_T00` (`dT = 0`) is retired** | the zero-`dT` arm is degenerate by design and uncompletable under any registered ceiling (§4) |
| 2 | **Job B — the zero-heat-flux control — is re-homed onto `Z1`/`Z2`/`Z3`, a planted on-disk control at ZERO solver compute** | the two jobs conflict on one artifact; splitting them is the resolution (§5.1 C2, C3) |
| 3 | **A non-zero `M4b` is `GATE FAIL`, not `NOT A RESULT`** | a measured threshold failure is a failure, not an absence (§5.2). **The threshold is unchanged at 0 ULP** |
| 4 | **`D0`, a 200-iteration determinism twin, is armed as a REFUSAL GATE before the main arms** | a non-zero `M4b` from solver nondeterminism would be a false `GATE FAIL`; this finds it for ~7 core-min instead of ~190 (§5.5, §7.4) |
| 5 | **`M1b` and `D2` are new REPORTED rows** | the cooled arm has a Stanton number the zero-`dT` arm never had (Pred-10), and the cross-epoch comparison teaches rather than grades |
| 6 | **The D-J1 denominator audit is registered as a section, with a blanket clause** | §5.6 |
| 7 | **Clause 6 of the completion rule must print its comparison count and report `VACUOUS` over an empty set** | K0eR2 §2.3 found it passing vacuously |
| 8 | **The cost POINT is the MEASURED 94.7667, not a factor on a proxy; the CAP is 5× with a derived multiple** | the ×2.7076 miss, and 307 s of headroom that was luck (§7.1, §7.2) |
| 9 | **The grader must exit non-zero on a non-`PASS` verdict and must print the registration path it was given** | two traps recorded in K0eR2's results (§9) |
| 10 | **All pins are UNCUT and launch is BARRED until a pre-compute addendum cuts them** | §0.1 |

**Unchanged and carried forward in substance:** the reference and its
title-page verification; **no band, and §3's reasoning**; the mesh, the case, the
solver, `beta = 0`, `g = (0 0 0)`, `Pr`, `Prt`, `div(phi,T)`, the `alphat` wall
treatment, `endTime 9000` and the copied 2-rank decomposition; the 0-ULP
threshold with **no tolerance constant anywhere in the comparator**; the three
`P1`/`P2`/`P3` plants including the vector plant; the strict completion rule and
its age guard; no Roache triple and no GCI; the `writePrecision 10` secondary
limit; and the cost POINT-plus-CAP shape.

---

## 12. QUEUE AND LAUNCH

Launches are **daemon-only**. Entries are dropped in
`verification/queue/heat-transfer/` and picked up by `scripts/queue_runner.py` on
its one-minute tick. Run root: `verification/runs/F14-cooling-ladder/K0eR3_runs/`.

**Launch order is registered and is not optional:** `D0` invocation 1, `D0`
invocation 2, **then and only then** `FP_T10` and `FP_T290`. A non-zero `D0`
stops the rung there.

**If the box is over the runner's busy ceiling the entry QUEUES.** That is a
resource gate queueing and is **not a block, not a refusal and not a `BLOCKED`
verdict.** The rung's state until the daemon takes it is **`PENDING`**.

**NOTHING MAY BE QUEUED UNTIL §0.1's ADDENDUM CUTS THE THREE PINS.**

---

*Registered by a heat-transfer lane, 2026-09-04. This lane assigns the rung no
verdict and launches nothing; the launch decision is the supervisor's own check
(`SUPERVISION_CHARTER.md` §3 check 4). Nothing was sent, filed, uploaded,
registered or posted — submissions are PARKED.*
