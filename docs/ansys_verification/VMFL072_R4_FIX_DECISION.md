# VMFL072-R4 — FIX PATH DECIDED — 2026-09-11 [lab-attributed]

**Status: DECISION RECORD, NOT a pre-registration. NOTHING HERE IS FROZEN AND NOTHING MAY BE LAUNCHED ON IT.**
The team is under Sanaa's 2026-09-10 ~18:55Z rest (*"ANSYS and closure team can rest for now"*), which no later word lifts. This file records **what the fix will be** so that freezing it is a mechanical step when the rest lifts; the pre-registration, its gate, its tolerance and its costed cap are written then, before any solver starts (rule 2).

## 1. Why this decision is the team's to make

Sanaa, 2026-09-11 ~16:00Z, her own words: *"no when i said openfoam issue i meant openfoam capabilties. The team can proceed to fix with what its supervisor decides the fix is."*
Her 2026-09-10 16:15Z *"the fixes continue UNLESS It's an openfoam issue"* therefore reaches only cases where **OpenFOAM lacks the capability** — no model, no solver, no physics. A **SIGFPE inside** `libregionFaModels.so` is a breakage, not a missing capability. **VMFL072-R3's SIGFPE leaves her desk.** It is not escalated again unless the fix would need a charter clause widened or a spend above a registered cap.

## 2. What is actually established, and what is not

**ESTABLISHED, from run artifacts:**
- `pimpleFoam`, serial, level **L3 (256 x 64 x 1, 16,384 film faces)**, died `rc = 136` (SIGFPE) at `Time = 1.10875` after 887 steps and `ExecutionTime = 142.51 s`.
- The faulting frame is **`Foam::DILUPreconditioner::calcReciprocalD`** in `libOpenFOAM.so` — the reciprocal of a matrix diagonal — reached through `PBiCGStab::solve` from **`kinematicThinFilm::evolveRegion()`** in `libregionFaModels.so`, itself called from `velocityFilmShellFvPatchVectorField::updateCoeffs()`. Evidence: `verification/runs/ansys_verification/VMFL072-R3/L3/log.pimpleFoam`, `[stack trace]` block; `.../L3/RC.txt`.
- **It is not a CFL blow-up.** The step before the fault reports `Courant Number mean: 7.92e-09 max: 1.07e-05`, and the four film solves at that step converged to ~1e-11.
- L1 and L2 (same `H_IN`, coarser) and both controls B2 and C1 completed `rc = 0`.
- **The 256 x 64 mesh is not intrinsically fatal:** B2 ran it to completion.

**NOT ESTABLISHED — and R4 exists because of this list:**
- **No single-variable control at fixed grid exists.** B2 differs from L3 in `H_IN`, `U_IN` **and** `DELTAT` simultaneously. Which of the three lets B2 survive is unknown.
- Whether the failure threshold **scales with cell size** is **UNTESTED**; it rests on one failing level.
- The mechanism is unproven. A zero diagonal in the film matrix is consistent with local dewetting (film height driven to zero in a face), but "consistent with" is not "shown", and no artifact records the minimum `hf_film` at the failing step.

**A remedy chosen before the mechanism is isolated is a guess wearing a gate.** R4 therefore leads with a diagnostic, not a cure.

## 3. The decided fix path — three rungs, in order, each gated on the last

**R4-A — THE MISSING CONTROL (diagnostic, runs first).**
A single-variable `h0` ladder **at fixed 256 x 64 grid** with `U_IN` and `DELTAT` pinned to L3's values, so exactly one knob moves. This is the control R3 should have had. It answers: does precursor thickness alone cure L3?
- Instrument the film region to write **min `hf_film` per timestep** to its own artifact, so the dewetting hypothesis is measured rather than asserted. This is an added **observer**, not a change to the solve: it must not clip, floor or otherwise alter any field, and the pre-registration will say so explicitly.

**R4-B — THE SCALING TEST (runs only if R4-A finds a surviving `h0`).**
Take the `h0` that survives 256 x 64 and run it at **512 x 128** — the actual next refinement, *not* the 960 x 416 that the mis-labelled triage projected. If it dies again, the threshold scales with cell size and a **constant** `h0` is dead for this case on its own evidence.

**R4-C — THE RULE, if and only if R4-B shows scaling.**
Make the precursor thickness a fixed fraction of the local cell size rather than a constant, so the grid family stays self-similar and the L1/L2 answers are not moved by whatever L3 needs. The functional form is chosen from R4-A/B data, not now — choosing it now would be fitting a remedy to an unmeasured mechanism.

## 4. The abandonment criterion, registered in advance

**If no `h0` within a factor of 10 of 1e-5 survives 256 x 64 without shifting the L1 and L2 film-thickness answers outside the case's tolerance band, the precursor-film approach is ABANDONED for VMFL072** and the successor moves to `kinematicSingleLayer` or a VOF re-formulation — the two alternatives already named in `docs/ansys_verification/FIX_SUCCESSOR_REGISTRY.md`. Writing the abandonment condition **before** the runs is what stops the ladder being extended indefinitely because each rung is individually cheap.

## 5. What this fix explicitly is NOT

- **Not a clip, floor or `max(h, eps)` on the film height.** That would suppress the SIGFPE by hiding the state that causes it and would make every subsequent film-thickness number unfalsifiable. The crash is the measurement.
- **Not a preconditioner swap** (DILU to diagonal) to route around `calcReciprocalD`. Same objection: it converts a hard failure into a silent wrong answer.
- **Not an upstream filing.** Rule 7 stands: **SUBMISSIONS ARE PARKED**, sending is Sanaa's alone, and no defect report leaves this box. No draft exists and none is being written.

## 6. Cost, to be carried into the pre-registration

R3's measured actuals are the estimate basis: L1 0.38, L2 2.90, L3 2.375 (partial, waste), B2 28.62, C1 2.63 core-min — **~37.5 core-min gross** against **92 filed** and a **184.5 cap** (`cases/ansys_verification/VMFL072-R3/PREREGISTRATION.md` §8). R4-A is three L3-length runs; a completed L3 has never been measured, so its cost is **predicted, not measured**, and the pre-registration must say so and carry a per-level cap. Dollars are derived at $0.0513/core-h and labelled derived — the box cannot read its own billing.

## 7. Owed before this can be frozen

1. **The VMFL072-R3 register row is OWED.** `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` carries `#58` for R2 and, at line 933, *"`VMFL072-R3` is owed."* The R3 verdict exists — `NOT A RESULT`, grader refused at the completion clause — and the charter records every case whatever its verdict. Append it with the row number re-derived at append.
2. Its estimate-versus-actual calibration row in `docs/COST_CALIBRATION.md` (rule 12).
3. Then the R4-A pre-registration, frozen by sha before any solver starts.
