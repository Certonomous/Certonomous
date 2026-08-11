# W3 — Ahmed body 25°: pre-registration of the band-containment test

**Written 2026-07-30, before any solver was launched for this study.** No number
below is edited after the fact. If the result falsifies a prediction, the
prediction stays exactly as written and the result file says so in those words —
the way F6a's channel-1 prediction was scored FALSE rather than quietly rewritten.

This repeats the D9 pattern (`campaign/D9_TALKING_POINTS.md`,
`dafoam/f6a_epistemic_band/PREDICTION.md`) on a second, independent case. D9's
whole claim was "our uncertainty machinery predicted a known model error, in
writing, before the run." A claim like that is worth exactly one case unless it
is made again on a case chosen after the machinery was already built. This is
that second case.

---

## 1. Which Ahmed numbers are alive — settled before predicting anything

The A4 record was amended today and one number came off the board. Predicting
against a withdrawn number would make the whole exercise worthless, so the census
comes first.

| Cd (frontal basis) | Cells | Solver / algorithm | Closure | Status | Primary evidence |
| --- | --- | --- | --- | --- | --- |
| **0.3622** | 20,621 | `simpleFoam`, SIMPLEC | kOmegaSST | **ALIVE** — coarse rung of the act's own ladder | `models/curriculum/uq-studies/ahmed_25.json` (`cd` 0.10099115988888889, planform); `mission-output/ahmed-body/transcript.txt` |
| **0.3220** | 45,753 | `simpleFoam`, SIMPLEC | kOmegaSST | **ALIVE** — the validated baseline, = A4's "0.3219" | `mission-output/geometry-study/study-ahmed_25/report.md` and `coefficient.dat` (`8.97763675e-02`); `models/curriculum/results/ahmed_25.json` (`"tier": "VALIDATED"`) |
| **0.3041** | 79,439 | `simpleFoam`, SIMPLEC | kOmegaSST | **ALIVE** — the filmed act's production result, the finest mesh the lab has run | `mission-output/ahmed-body/act7-ahmed_25/log.simpleFoam` (`Cd: 0.084801705`, `SIMPLE solution converged in 154 iterations`), `.../coefficient.dat`, `.../log.checkMesh` (79,439 cells) |
| ~~0.2510~~ | 45,760 | DAFoam `DASimpleFoam`, plain SIMPLE | kOmegaSST | **WITHDRAWN 2026-07-30 — must not be cited** | `ACTIVE_RESEARCH.md` A4 row; `dafoam/ladder-a/A4_ahmed_body.md` scope note; `NOT_PASSING_REGISTER.md`. Its omega field diverged while its normalised residual read as converged, and the drag was computed from that state |
| 10.04% | 2,777 | DAFoam adjoint vs FD | — | **Not a drag number at all**, and graded CONDITIONAL | `dafoam/DAFOAM_CASE_STATUS.md`, `NOT_PASSING_REGISTER.md` |

**Experimental reference, single source of truth:**
`models/curriculum/ahmed_25/reference.yaml` — **Cd = 0.285**, frontal area basis
(0.389 × 0.288 = 0.112 m²), Re ≈ 2.8×10⁶ on model length 1.044 m, from
**Ahmed, Ramm & Faltin 1984, SAE 840300**. The file carries two different widths
and this study uses them for two different things: `cd_range: [0.27, 0.30]` is the
experiment's own spread and `tolerance: 0.15` is the lab's acceptance band
(→ [0.24225, 0.32775]). **The containment test below is against the point value
0.285**, not against either band; the bands are reported alongside for context.

All planform→frontal rebasing in this study uses the ratio the whole record
already uses: **0.401696 / 0.112 = 3.5865714**. It is applied identically to
every number so it cancels out of every comparison.

**The documented model bias this study is answering to:** our converged
kOmegaSST solve on the finest mesh the lab owns gives **0.3041 against a measured
0.285 — an over-prediction of +6.73%.** That is the analogue of the hump's
+13.95%, and it is the miss the band either contains or does not.

**Why 0.3041 and not 0.3220** as the centre: 0.3041 is the finest rung, it is
what is on camera, and centring on a coarser rung would be choosing the number
that flatters containment. Both are reported.

---

## 2. The binary test

> Does a defensible uncertainty band on Ahmed 25° drag coefficient **contain**
> the measured experimental value 0.285, given a baseline that over-predicts it
> by +6.73%?

---

## 3. The channels, and one that is deliberately absent

**Channel N — numerical (discretisation).** Already measured, not re-run here.
The act's own three-rung refinement ladder, machine record
`models/curriculum/uq-studies/ahmed_25.json` (`"updated_utc": "2026-07-30T17:28:52Z"`):

| rung | cells | Cd planform | Cd frontal |
| --- | --- | --- | --- |
| coarse | 20,621 | 0.10099116 | 0.36221 |
| medium | 45,753 | 0.08978750 | 0.32203 |
| production | 79,439 | 0.08481225 | 0.30419 |

`observed_order: 1.95`, `band_abs: 0.020223634` on planform Cd, **`conclusive:
false`**, method string *"Richardson-extrapolated value falls outside the measured
range; ladder not in the asymptotic range, conservative band, largest spread
times 1.25"*. Rebased: **± 0.072534 on frontal Cd, i.e. ±23.85% relative.**
This channel is wide *because it is honest about not being in the asymptotic
range*, and that width is declared here, in advance, as the thing most likely to
decide the verdict.

**Channel M — model form (inter-closure spread).** The new compute. Four
additional RANS closures at the **production mesh, 79,439 cells**, everything
else held byte-identical to the filmed act's case: same STL, same
`blockMeshDict`/`snappyHexMeshDict` (castellated refinement 3), same
`fvSchemes`, same SIMPLEC coupling, same `forceCoeffs` block
(`magUInf 40; lRef 1.044; Aref 0.401696; rhoInf 1.225`), same inlet conditions.
The only knob moved is `constant/turbulenceProperties`:

| member | closure |
| --- | --- |
| M0 | kOmegaSST — the act's baseline, 0.3041, not re-run |
| M1 | kEpsilon |
| M2 | kOmega |
| M3 | realizableKE |
| M4 | SpalartAllmaras |

Same four closures as F6a channel 1, chosen so the two studies are comparable
rather than because they are convenient here.

**Channel 3 — eigenvalue perturbation — is NOT used, and its absence is
declared now.** The lab's eigenvalue-perturbation machinery applied its source
term with the wrong sign: `eqn += fvc::div(deltaR)` puts the perturbation on the
right-hand side, producing `2·b_Bouss − b_pert` instead of `b_pert`, which is
non-realizable in **95.93%** of cells (`campaign/F6d_random_matrix_uq.md`,
**LESSONS L-26**). Every channel-3 corner is withdrawn. **On the hump, channel 3
is what carried containment.** Removing it here is not a simplification — it
removes the strongest channel D9 had, and this study has to succeed or fail
without it. Saying that in advance is the point.

**Combined band = channel M ∪ channel N**, specifically
`[min(members) − band_abs_frontal, max(members) + band_abs_frontal]`, i.e. the
closure spread widened by the numerical band on each side. Both the union and
channel M alone are reported, because which one carries containment is the
interesting quantity, not the verdict.

---

## 4. Gates, declared now

**Admission gate.** A member is admitted to the primary band only if:

- **(a)** `simpleFoam` prints its own `SIMPLE solution converged in N iterations`
  statement (LESSONS L-14, L-15: a small-looking residual is not a substitute);
- **(b)** every field's **Initial** residual at the final iteration is under the
  case's `residualControl` (1e-4 on p, U and the turbulence fields) — Initial,
  not Final, which is the error F6a's kOmega made;
- **(c) NEW — the turbulence-field gate.** This is the gate A4 did not have and
  the reason 0.2510 is withdrawn. A converged normalised residual is not accepted
  on its own. In addition: no `bounding k` / `bounding omega` / `bounding
  epsilon` / `bounding nuTilda` message may appear in the **final 10% of
  iterations**, and the printed `min:`/`max:` of any bounded turbulence field
  must not grow by more than one order of magnitude across the run. A normalised
  residual that collapses because its own normalisation factor blew up reads as
  convergence and is not;
- **(d)** the drag coefficient is flat: the spread of `Cd` over the final 50
  iterations of `coefficient.dat` is within **0.5%** of its mean.

Gates (a)–(d) are the admission criteria. They are declared before any member has
run and will not be moved to change the answer.

**Gating-disclosure policy — mandatory, from today's own finding.** F6d
established that *gating out hard-to-converge ensemble members biases the band
away from the truth*, and that at larger dispersion the gate **destroys
containment that the ungated ensemble had**
(`campaign/F6d_random_matrix_uq.md` §7.2). Therefore:

1. **Every member that runs is reported with its Cd, gate-by-gate, whether or not
   it is admitted.** No member disappears.
2. **The band is reported twice** — gated (primary) and ungated (all members that
   produced a number at all) — and the difference between them is stated as a
   measured quantity, not a footnote.
3. **If gating changes the containment verdict, that fact is the headline**, not
   the verdict.
4. A member that fails to produce any Cd (crash, no time directory) is reported
   as such with its failure mode.

> **Premise correction, 2026-08-11 — the four rules stand and the gates above
> them are exemplary; only the cited rationale is withdrawn.**
> `campaign/F6D_ENSEMBLE_CONVERGENCE_AUDIT.md` re-measured the F6d ensemble and
> found that **no member of it ever settled**: all 84 ran to a fixed cap under
> an unreachable `residualControl` target, and the one integrated output the
> tree retains still swings by 86% of its own level over the final 500
> iterations at the median. Reattachment there tracks settledness monotonically
> (most-settled quartile 7.21, least-settled 5.25), and the 12 members that
> fail F6d's residual gate are 83% unsettled against 14% for the 28 that pass.
> **So F6d's gate was largely separating converged from unconverged members,
> not calm samples from hard ones, and the sentence "gating biases the band away
> from the truth" asserts a reading whose confound was never excluded.** The
> audit states this as correlational and names the competing physics reading it
> cannot rule out on existing data; the 152 core-min continuation
> pre-registered in `campaign/F6D_OPTION_A_PREREGISTRATION.md` discriminates
> them.
>
> **Why this pre-registration is nonetheless in good shape, and is the model
> the audit recommends elsewhere.** Gate (a) requires the solver's own
> `SIMPLE solution converged` statement — which would have excluded the entire
> F6d ensemble — and gate (d) is a *settledness gate on the reported quantity
> itself* (Cd flat to 0.5% over the final 50 iterations). That is precisely the
> discipline the audit concludes F6d lacked. Rule 2 already makes the **gated**
> band primary, which is the correct ordering and the opposite of the inverted
> rule the audit flags in `W2_DOW_STRUCTURAL_UQ_PROGRAM.md` §4.3.
>
> **The only operative change:** rule 3 should read *if gating changes the
> containment verdict, that fact is the headline **and the first question asked
> of it is whether the discarded members had converged*** — because on F6d's own
> data that difference was the answer. Rules 1, 2 and 4 are unaffected. **No
> gate has been moved**; this note adds a question, not a threshold.

---

## 5. Predictions, recorded before any of these numbers exist

**P1 — direction.** Every admitted closure will **over-predict** Cd relative to
0.285. Reason: at 25° the slant flow is attached-with-C-pillar-vortices, which is
the high-drag branch, and linear eddy-viscosity closures over-produce turbulent
shear stress in exactly that shear layer, holding the flow attached and keeping
drag high. The same one-sided bias is already on this lab's record — F6a's
+13.95% and F6b's +63% to +66%. Compounding it, the 79,439-cell mesh is not in
the asymptotic range and every coarser rung of our own ladder is *higher* still
(0.3220, 0.3622), so the mesh bias points the same way as the model bias.
**Falsified if any admitted member lands below 0.285.**

**P2 — channel M alone does NOT contain 0.285.** I predict the closure spread's
minimum stays **above 0.285**, and specifically that all four new members land in
**[0.29, 0.36]** frontal Cd.

I am aware this is the same shape as the prediction F6a made and got **wrong** —
there, channel 1 straddled the truth because kOmega crossed to the low side. I
am making it again, on this case, for a reason that is specific to this case and
not carried over: on the hump the graded quantity was a *bubble length*, where
closures genuinely disagree about the sign of the error, whereas here it is an
*integrated drag on a mesh two rungs short of asymptotic*, where a shared
coarse-mesh bias sits on top of the shared closure bias and pushes every member
the same way. If P2 is falsified the same way P1's hump ancestor was, that is a
real result and it says the closure spread is a better bracket than I think.

**P3 — the combined band DOES contain 0.285.** Arithmetic stated now, so nothing
is fitted later: the numerical band alone, ±0.072534 about the production value
0.30419, spans **[0.23165, 0.37672]**, which already contains 0.285 with
0.0534 to spare on the low side. Unless channel M's minimum moves the lower edge
*up*, which it cannot — the union only widens — **containment is arithmetically
guaranteed by channel N before channel M runs at all.**

**P4 — and therefore the honest finding is P4, not P3.** Containment will be
**carried by the numerical channel**, not by the model-form channel. This is the
same structural weakness D9 had, with a different channel doing the carrying: on
the hump the wide channel was the eigenvalue perturbation (−52% to +14%, a factor
of 2.4); here it will be the grid band (±23.85%). **A band that wide accepts
almost any answer.** The diagnostic I commit to computing and reporting is the
**margin ratio** — how much of the distance from the baseline to the experiment
is covered by each channel — and the **leave-one-channel-out test**: does
containment survive deleting channel N? I predict **no**.

If P3 and P4 both hold, the correct public sentence is *"our band contains the
experiment, and we can tell you exactly which channel is doing the work and how
little of it is model-form knowledge"* — not *"our machinery bounded another
published error."* The second sentence would be true and misleading, and D9's
own correction history is the reason to refuse it in advance.

**P5 — cost.** The act's kOmegaSST solve converged in 154 iterations at
`ExecutionTime = 36.02 s` on this host. I predict the four new members total
under **60 core-minutes** including meshing, and that at least one of the four
fails to converge at the first attempt — F6a needed per-model initialisation
fixes for kEpsilon and realizableKE and 22,211 iterations for kOmega.

---

## 6. What this study will not claim

- Not that the band is useful. Containment is necessary, not sufficient — D9's
  own talking points say this out loud and this study inherits the caveat.
- Not anything about the bistable wake. The 25° slant's real wake is bistable
  (`reference.yaml`: *"steady RANS scatters more here ... and may miss the
  coefficient even with a good mesh"*). A steady-RANS ensemble cannot resolve a
  bistability and no member's position will be attributed to one.
- Not a re-run of the withdrawn DAFoam primal. 0.2510 stays off the board; this
  study does not resurrect it and does not use it as an ensemble member.

---

*Nothing in this file may be revised once the first solver launches. The results
land in `campaign/W3_AHMED_BAND.md`, which references this file by commit hash.*
