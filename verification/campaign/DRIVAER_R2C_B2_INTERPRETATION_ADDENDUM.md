# DRIVAER R2c — B2 INTERPRETATION, REGISTERED BEFORE THE MEASUREMENT

**Dated addendum. 2026-09-12T06:13:54Z, cfd lane.** Rung `R2c`, gate B2.

## 0. WHAT THIS DOCUMENT IS, AND WHAT IT IS NOT

This is a **dated addendum under rule 2**. It **alters no gate, no threshold, no cap and
no label.** B1, B2 and B3 stand exactly as frozen in
`DRIVAER_R2C_BLENDED_WALL_TREATMENT_PREREGISTRATION.md`, frozen commit `76e2030c1`,
sha256 `6dc537a116bf62ba10774cb1498d22a330ad3a6e139946e50d340c85bd9f416f`.

**THE FROZEN FILE IS NOT EDITED BY THIS DOCUMENT.** Its sha256 above was re-computed at
the moment this addendum was written and matched worktree, HEAD and the frozen commit.
This addendum is a separate file precisely so that hash cannot move — the lab's existing
pattern for exactly this (`T1b_L4_AMENDMENT.md` is a separate file from its
registration).

**WHY IT EXISTS.** An interpretation of what a B2 reading of "INACTIVE" would *mean* was
reached while both arms were still running. Written afterwards it would be an excuse.
Written now it is a prediction. That is the whole evidentiary content of this file, and
it is why the state of the runs at the moment of writing is recorded in §1.

## 1. THE STATE OF THE EVIDENCE AT THE MOMENT OF WRITING

Recorded so that no reader has to take on trust that this predates the measurement.

| run | iteration at writing | of | Cd at writing |
|---|---|---|---|
| `r2_coarse` (B2 control, non-blended) | 1139 | 2000 | 0.359559 |
| `r2c_coarse_blended` | 122 | 2000 | 0.349097 |
| `r2c_medium_blended` | 47 | 2000 | 0.310406 |

**B2 is `PENDING`. B1 is `PENDING`.** Neither gate has been evaluated by any instrument.
The frozen grader has not been run on either blended arm. B2's threshold is
2 × the control's trailing-200 plateau excursion **measured at `endTime` 2000**, and the
control is at 1139.

## 2. THE CLAIM, AND I REPRODUCED IT RATHER THAN ACCEPTING IT

The claim relayed to this lane: `nutUSpaldingWallFunction` and `nutkWallFunction` are
numerically the same function at the y⁺ values in this case, because Spalding's law
asymptotes to the log law at high y⁺.

**I did not take the numbers on relay.** Both OpenFOAM forms reduce to the same
expression, `nut/ν = y⁺/u⁺ − 1`, differing only in how `u⁺` is obtained —
`nutUSpaldingWallFunction` solves Spalding's implicit law, `nutkWallFunction` uses
`u⁺ = ln(E y⁺)/κ`. I solved Spalding's relation by bisection at κ = 0.41, E = 9.8 and
computed both:

| y⁺ | nut/ν Spalding | nut/ν log-law | difference |
|---|---|---|---|
| 5 | 0.0223 | −0.4733 | 104.7 % |
| 15 | 0.4371 | 0.2324 | 88.1 % |
| 30 | 1.2957 | 1.1641 | 11.3 % |
| 100 | 5.0265 | 4.9528 | 1.489 % |
| 159.5 (C1 layered) | 7.9515 | 7.8919 | 0.755 % |
| 232.0 (medium layered) | 11.3564 | 11.3067 | **0.440 %** |
| 300 (band limit) | 14.4452 | 14.4016 | 0.303 % |
| 481.6 (coarse layered) | 22.3745 | 22.3413 | **0.148 %** |
| 556.6 (unlayered) | 25.5527 | 25.5225 | **0.118 %** |
| 1941 | 79.7727 | 79.7655 | **0.009 %** |

**The relayed figures are reproduced to three significant figures at every y⁺ checked.
The claim is correct.** (The y⁺ = 5 sign differs by convention only — the log-law form
goes negative there, so the sign of a relative difference depends on the denominator's
sign. The magnitude agrees. Note also that at y⁺ = 5 and 15 the real
`nutkWallFunction` clamps at `y⁺_lam ≈ 11.53` and returns zero, so those two rows
describe the unclamped formulae, not the shipped code's output.)

**The swap corrects the opposite direction of error from the one this case has.** The two
functions diverge only **below** y⁺ ≈ 30. DrivAer's problem is y⁺ too **high**.

## 3. PREDICTION 1 — THE EXPECTED B2 READING IS `INACTIVE`, AND THAT WOULD BE CORRECT PHYSICS

**Registered prediction: B2 reads INACTIVE** — the Cd change between blended and
non-blended on the identical coarse mesh does **not** exceed 2 × the control's own
trailing-200 plateau excursion.

**An INACTIVE reading is not a failed swap and is not a null result to be explained
away.** At layered y⁺ 481.6 and unlayered y⁺ 556.6 the two wall functions differ in
`nut/ν` by 0.148 % and 0.118 %. A wall treatment that is y⁺-insensitive **by
construction agrees with the log law wherever the log law is valid.** Finding no change
is the arithmetic above being confirmed, not the hypothesis failing.

For scale: the control's trailing-200 plateau excursion read **1.635 %** at iteration
1122 and **1.599 %** at iteration 1013, so B2's threshold will land near 3.3 %. The
wall-function difference is an order of magnitude below that before any Cd integration.

**What this costs the R2c arm, stated plainly and in advance:** if B2 reads INACTIVE,
then B1's agreement — should B1 agree — carries **no evidence of y⁺ insensitivity**,
exactly as §3 of the frozen registration already warned. Outcome 1 of §5 (the wall
treatment was the defect; the fine mesh becomes legitimate) **would not be reached.**

## 4. PREDICTION 2 — WHAT REFUTES THE CLAIM, STATED SO THE GATE CAN FALSIFY IT

**If B2 reads ACTIVE — a Cd change above the frozen threshold — the equivalence claim in
§2 is wrong about this case, and this addendum is wrong with it.** It is registered here
as falsifiable by a gate neither I nor its author may touch, and if the gate says ACTIVE
the gate wins.

## 5. THE ASSUMPTION §2 DOES NOT STATE — REGISTERED NOW SO IT CANNOT BE A RESCUE LATER

**The equivalence in §2 holds only under LOCAL EQUILIBRIUM, and I am registering that
before the measurement rather than producing it afterwards if B2 reads ACTIVE.**

The two functions take **different inputs**. `nutkWallFunction` forms y⁺ from the
turbulent kinetic energy, `y⁺ = C_μ^0.25 √k y/ν`; `nutUSpaldingWallFunction` solves for
`u_τ` from the velocity. They coincide only where production balances dissipation, so
that `C_μ^0.5 k = u_τ²`. **In a separated wake that balance fails**: at separation and
reattachment `u_τ → 0` while `k` stays finite, and the two forms decouple **regardless of
how high y⁺ is.** DrivAer's rear end is massively separated, and the frozen registration
itself names **19.65 % of wetted area on 16 unlayered patches**.

**So an ACTIVE reading has TWO possible causes and B2 alone cannot separate them:**

1. the high-y⁺ asymptotic arithmetic in §2 is wrong — **§4's refutation**; or
2. the arithmetic is right for the attached boundary layer and the change comes from
   **non-equilibrium regions where √k and u_τ decouple**.

**THE DISCRIMINATOR, REGISTERED IN ADVANCE AND NOT AVAILABLE YET:** cause 2 puts the Cd
difference **in the separated rear patches and leaves the attached forebody patches
unchanged**; cause 1 puts it **everywhere the wall function acts**. Distinguishing them
needs **per-patch** force data, which `forceCoeffs` does not write — it needs a `forces`
function object run over both stored solutions on the identical mesh. **That measurement
does not exist today and is not authorised here.** Naming it now is what stops cause 2
being reached for as an explanation after an ACTIVE reading.

## 6. PREDICTION 3 — THE DISTINCTION B2 CANNOT MAKE, AND THE EVIDENCE THAT CAN

**"The wall function did not change the answer" and "the wall function was not applied"
produce the IDENTICAL B2 reading.** B2 cannot separate them and must never be cited as
if it could.

**The separating evidence is a census of the decomposed field the solver actually reads,
and it is already measured:**

- `r2c_coarse_blended/processor0/0/nut` — **51 patches `nutUSpaldingWallFunction`, 1
  `nutkWallFunction`**, and that single holdout is **`floorNoSlip`**, exactly as §1 of the
  frozen registration declares it should be.
- `r2_coarse/processor0/0/nut` (control) — **52 `nutkWallFunction`**.
- `r2c_medium_blended/0/nut` — carries `nutUSpaldingWallFunction` with the one
  `nutkWallFunction` holdout.

**THE SWAP IS APPLIED. This census is load-bearing and is to be cited beside the B2
verdict permanently, whichever way B2 reads.**

**A test that was tried and is NOT evidence, recorded so nobody re-runs it believing in
it:** per-iteration cost was proposed as independent evidence the new wall function
executes. It does not work. The control's own cost moved **2.07×** under contention
(1.904 → 3.9340 CPU-s/iter/rank), so scoring against the registered figure would have
printed +87 % and charged contention to the wall function. Contention-matched over the
concurrent window the ratio is **0.931 (−6.9 %)** — the wrong sign for Spalding's Newton
iteration, and confounded by the control sitting ~1000 iterations deeper into
convergence. **Inconclusive, not a null.**

## 7. δ⁺ ON THE EXISTING COARSE SOLUTION — COSTED, NOT LAUNCHED, NOT AUTHORISED

Asked: if the band's upper limit is the real question rather than the wall function, what
would it take to measure δ⁺ and establish where the log layer actually ends here?

**A flat-plate ESTIMATE first — this is an estimate, NOT a measurement, and is labelled
as such wherever it is quoted.** With ν = 1.507e-5 m²/s and u_τ = 1.3657 m/s (C1's
measured `yplus_per_metre` = 90,623.25), using δ = 0.37x/Re_x^0.2:

| x | Re_x | δ | δ⁺ | y⁺ 481.6 sits at y/δ | y⁺ 556.6 at y/δ |
|---|---|---|---|---|---|
| 0.50 m | 1.29e6 | 0.0111 m | 1,005 | 0.479 | 0.554 |
| 1.00 m | 2.58e6 | 0.0193 m | 1,750 | 0.275 | 0.318 |
| 2.00 m | 5.16e6 | 0.0336 m | 3,047 | 0.158 | 0.183 |
| 2.79 m | 7.20e6 | 0.0439 m | 3,977 | 0.121 | 0.140 |

**The answer is position-dependent, and that is the finding.** The log layer
conventionally ends near y/δ ≈ 0.15–0.2. At the **rear** of the vehicle the first cell
centre sits at y/δ ≈ 0.12–0.14 — **inside** the log layer, so y⁺ 556 is arguably
defensible there. At **mid-body** it sits at 0.16–0.18, **at the edge**. At the **front**
it sits at 0.48–0.55 — **far outside the log layer**, and no wall function of any kind is
valid there. **A single-number y⁺ verdict for this vehicle is therefore the wrong
instrument**, and `[30, 300]` applied globally is a convention, not a local physical
statement.

**Cost of the real measurement, on the solution already on disk:**
- Only `processor0/1000` and `0` exist as written time directories on `r2_coarse`; t=1000
  is a complete, static, decomposed field set and needs **no new solve**.
- `reconstructPar -time 1000` (186,709 cells) ≈ 20–60 s; `postProcess -func
  wallShearStress -time 1000` → real per-face u_τ ≈ 10–30 s; wall-normal line sampling,
  ~200 rays ≈ 30–120 s. All serial, peak ≈ 0.5 GiB.
- **≈ 1–4 core-min uncontended; ≈ 8–35 core-min at tonight's ~8× contention. Derived cost
  under $0.01 — DERIVED, NOT MEASURED.** Compute is effectively free; the real cost is
  writing the sampling instrument and its planted control, which is lane time, not
  core-minutes.

**THE LIMITATION THAT MAY DEFEAT IT, STATED BEFORE ANYONE SPENDS THE TIME:** δ would be
extracted from a profile whose **first cell centre already sits at 12–55 % of δ**. The
layer stack spans roughly `t₁ × 8.21` ≈ 28.7 mm against an estimated δ ≈ 33.6 mm at
x = 2 m, so the boundary layer is covered by about **five cells**. A δ from five points is
crude — call it ±20–30 % — and **it is circular in the direction that matters**: the
mesh whose adequacy is in question is the mesh supplying the profile. It can establish
the *position dependence* above, which is already useful; it probably **cannot** settle
whether y⁺ 556 is admissible to a tolerance anyone should gate on.

**Not launched. Not authorised by this addendum. Costed only.**

## 8. WHAT THIS ADDENDUM DOES NOT DO

It does not alter B1, B2 or B3, their thresholds, their labels or their cost caps. It
does not stop, restart or touch any run. It does not authorise the per-patch `forces`
measurement of §5 or the δ⁺ measurement of §7. It records predictions and one named
assumption **before** the frozen instrument speaks, so that neither can be introduced
afterwards as an explanation.

---

## 9. DECISIONS TAKEN ON THIS ADDENDUM — 2026-09-12T06:17Z, STILL BEFORE B2

**Lines whose number changed above this section: 0.** §§0–8 are byte-identical to the
text committed at `99a49c026`; this section is appended, and nothing above it is edited.
**B2 and B1 are still `PENDING` at the moment of writing** — control 1142/2000, blended
coarse 124/2000, blended medium 49/2000, C2 `RUN_RC` still absent. **No gate, threshold,
cap or label is altered by this section either.**

Recorded because a successor lane reading §5 and §7 alone would otherwise stall on a
branch that may fire while no agent is awake.

### 9.1 The δ⁺ sampler of §7 is DECLINED, not deferred

Decided by the cfd-supervisor on the limitation stated in §7 **before** any lane time was
spent. The reason is on record and is not "too expensive": compute was ~1–4 core-min. It
is that **the mesh under question would be supplying the evidence for its own adequacy** —
δ from a profile whose first cell sits at 12–55 % of δ, ~5 cells across the boundary
layer, ±20–30 %. **Cheapness is not the test; usability of the answer is, and it fails
that test.** Nobody should re-propose it for this mesh without new information.

**The free flat-plate ESTIMATE in §7 stands and is the night's result from this line.** It
remains an ESTIMATE, flat-plate-based, **explicitly not a measurement**, and **no gate is
attached to it and none may be.** It does not move `[30, 300]` — §8 governs. What it
changes is the QUESTION: not "is y⁺ 556 too high" but **"too high WHERE"**, the first
cell sitting at y/δ ≈ 0.12–0.14 at the rear and 0.48–0.55 at the front.

### 9.2 The per-patch discriminator of §5 is DEFERRED and CONDITIONALLY PRE-AUTHORISED

**It is needed ONLY if B2 reads ACTIVE.** Measuring it now would spend on a branch that
is predicted not to be taken (§3).

**IF B2 READS `ACTIVE`, the per-patch `forces` measurement of §5 IS AUTHORISED** by the
cfd-supervisor, with one binding constraint stated in advance:

> **on the SAVED fields of both runs — NEVER by adding function objects to a running
> case.**

If B2 reads `INACTIVE`, it is not needed and is not to be run. **This authorisation
creates no gate**: it permits a measurement whose purpose is to separate the two causes
in §5, and any verdict drawn from it needs its own pre-registration.

### 9.3 Accepted into the record

Both §2 footnotes are adopted by the claim's author: the y⁺ = 5 sign is a denominator-sign
convention, and the shipped `nutkWallFunction` clamps at `y⁺_lam ≈ 11.53` and returns zero
below it, so the y⁺ 5 and 15 rows describe the unclamped formulae.

**§5's local-equilibrium limit is adopted by the claim's author as a CORRECTION to the
§2 claim, not a footnote to it:** the asymptotics were right, and incomplete about where
they apply. Recorded so that an INACTIVE reading cannot later credit a prediction that
came true for a reason its author had not identified.

The coverage-formula omission recovered in `grade_c2_exits.py` remains attributed to the
frozen C2 registration and its signatory. That the derivation recovered the intended
formula to four figures does not make the omission harmless.
