# A3 rung 3 — conditioning the transonic adjoint DELIBERATELY: PRE-REGISTRATION

Filed 2026-08-10, chief-approved (docket
`a3-transonic-adjoint-conditioned-deliberately-not-by-knob-luck`, ~35 core-min), scoped to
rung 3. Katie's capability strategy §2 states the clause this arm must satisfy: *"A3's transonic
adjoint conditioned DELIBERATELY (diagonal-spread diagnosis → chosen preconditioner →
converged), not by knob-luck."*

**Committed BEFORE any diagnosis compute.** §A (below) fixes what will be measured and — the
part that makes this a method proof rather than a search — **the decision rule mapping each
possible diagnosis to the preconditioner it implies, written before the diagnosis exists.** §B
will record the diagnosis, §C the choice as a prediction, §D the outcome.

**Binding honesty clause (the chief's ground rule, restated as mine):** if something converges by
trial rather than by diagnosis, it is reported as a knob and explicitly NOT dressed as the proof.
A knob that works is a useful engineering result and a failed proof at the same time, and it will
be written that way.

## 0. What is reachable — the constraint that bounds this proof, established before choosing

Read from the run image's own source (`DALinearEqn.C:125–200`) before the diagnosis, because a
diagnosis that implies an unreachable remedy must be declared as such rather than quietly
redirected to a reachable one:

```
138:    KSPSetFromOptions(ksp);          // runtime options applied here...
144:    KSPSetType(ksp, kspObjectType);  // ...then OVERRIDDEN: kspObjectType = KSPGMRES, hardcoded
158:    KSPGMRESSetRestart(ksp, restartGMRES);
170:    KSPSetPCSide(ksp, PC_RIGHT);
```

Because every explicit setter runs AFTER `KSPSetFromOptions`, **the Krylov method itself is not
reachable at runtime**: `-ksp_type lgmres` (augmented restarting, Baker–Jessup–Manteuffel 2005),
`-ksp_type dgmres` (deflated restarting), and `PCFIELDSPLIT` are all unreachable without
recompiling `libDASolver.so`. The global PC is hardcoded `PCASM`; sub-PC is `PCILU` (or complete
`PCLU` through the lab's own env patch).

**Reachable choice space:** `pcFillLevel`, `asmOverlap`, `globalPCIters`/`localPCIters`,
`gmresRestart`, `useMGSO` (modified vs classical Gram–Schmidt), `jacMatReOrdering`,
`DAFOAM_SUBPC_TYPE=lu`, `useNonZeroInitGuess`. **Reachable diagnostics** (viewers/monitors are
not overridden): `-ksp_monitor_true_residual`, `-ksp_view_pmat binary:` (proven in this lab,
`PROOF.md` §25.2), plus `adjEqnOption.KSPCalcSingularVal` which calls
`KSPComputeExtremeSingularValues` (`DALinearEqn.C:428`).

## A. The diagnosis — what will be measured

**A1. Recursive vs TRUE residual at stagnation** (`-ksp_monitor_true_residual`). This is the
crux and it is nearly free. Restarted GMRES prints a *recursively updated* residual; if the
Krylov basis loses orthogonality, the recursion drifts from the actual `||b − Ax||`. So:
- recursive stagnates AND true tracks it → the operator genuinely offers no progress (a real
  conditioning wall);
- recursive stagnates BUT true differs materially → the *method* has broken down numerically,
  not the operator, and the ceiling would be an artifact of the arithmetic rather than of A.

**A2. Diagonal spread of the assembled PC matrix** (`-ksp_view_pmat binary:`, analysed offline
with scipy — the lab's own established route). Reported as decades between max and min
|diagonal|, over the ~713k unknowns; R5's comparable figure for this family (PC dead) was 14.17
decades against CBFS's 8.67.

**A3. Field-block structure.** Which field block (U, p, T, nuTilda, phi) owns the extreme
entries, and whether the blocks separate by orders of magnitude. `adjStateOrdering: cell` means
the state vector interleaves fields per cell, so block membership is recoverable by index
modulo the per-cell state count, verified against the printed state layout rather than assumed.

**A4. Geometric location of the extremes** — mapped back to cell centroids, specifically testing
whether they concentrate at the wing tip trailing-edge corner, which has form in this family
(the vcoarse mesh's 23 inverted cells clumped in exactly that corner).

**A5. Growth from rung 2**, the same measurements on the 42,120-cell PC matrix, to test whether
the spread grew across the doubling in a way that tracks the iteration exponent (cells^1.50/1.70)
or the ceiling.

**A6. Condition estimate**: sMax/sMin via `KSPCalcSingularVal`.

## B. THE DECISION RULE — written before the diagnosis exists

Each branch names the remedy, the Saad-terms reason, and the falsifier. Whichever branch fires,
§C records it and the arm runs exactly that remedy — no substitution, no second pick.

| # | if the diagnosis shows | then choose | why, in Saad's terms | falsifier |
|---|---|---|---|---|
| **R1** | **A1: true residual departs from recursive** at stagnation | **`useMGSO: 1`** (modified Gram–Schmidt; the build defaults to classical GS with `CGS_REFINE_IFNEEDED`) | Loss of orthogonality in the Krylov basis is classical GS's known failure on ill-conditioned bases (Saad §6.3); MGS restores orthogonality, and a longer cycle is worthless while the later basis vectors are contaminated — which would also explain why a 5x window bought only 1.65x | if MGSO does not restore descent, the drift was a symptom, not the cause |
| **R2** | **A1 tracks** (both stagnate) **and A2 shows extreme spread concentrated in one field block (A3)** | **`DAFOAM_SUBPC_TYPE=lu`** (complete LU on ASM sub-blocks), memory permitting; else `pcFillLevel: 1` | ILU(0) drops exactly the fill that carries the coupling it cannot represent; when the sub-block is badly scaled the dropped entries are not small (Saad §10.3). Complete LU removes dropping entirely — the PETSc developers' own sanctioned escalation, and the lab's proven unblock on CBFS | if complete sub-block LU still stagnates, the trouble is not local to the sub-blocks |
| **R3** | **A1 tracks** and the extremes are **geometrically localized (A4)** rather than field-separated | **`asmOverlap: 1 → 2`** | Additive Schwarz converges poorly when the difficult region straddles subdomain interfaces; wider overlap couples the pathological cells into neighbouring solves (Saad §14.3) | if wider overlap does nothing, the pathology is not interface-mediated |
| **R4** | **A3 shows clean field separation** (e.g. the p block orders apart from U/T) | **field-split is implied — and is UNREACHABLE in this build (§0)** | the diagnosis would be sound and the remedy blocked by `PCASM` being hardcoded | **the proof clause CANNOT be met without a source change, and I will report exactly that** rather than substituting a reachable knob |
| **R5** | diagnosis is **inconclusive** (no signature separates) | **nothing is run** | a diagnosis that does not discriminate cannot license a choice | reported as a failed diagnosis, ~0 further core-min |

Precedence if several fire: R1 first (a broken method invalidates every other reading of the
same run), then R2, then R3. Stated now so precedence is not chosen later.

**What counts as the proof clause being MET:** the chosen remedy — chosen by this rule, from the
diagnosis, in writing, before running — converges the rung-3 adjoint (`PetscConvergedReason: 2`
on the CD solve, the solve that stagnated). Anything else fails it, and §D says so plainly.

## C. Price, honestly, against the ~35 core-min approved

Measured basis: rung-3 primal + PC assembly ≈ 150 s; CD iterations ≈ 0.316 s at restart 200.

| step | design | estimate |
|---|---|---|
| D1 rung-3 diagnostic run | `gmresMaxIters 400` (enough to cross the first restart and enter the stall), `KSPCalcSingularVal 1`, `-ksp_monitor_true_residual`, `-ksp_view_pmat binary:` | ~280 s ≈ **19 core-min** |
| D2 rung-2 dump | `gmresMaxIters 1` — matrix only, for the A5 growth comparison | ~90 s ≈ **6 core-min** |
| offline analysis | scipy, no solver | **0** |
| the chosen arm | one remedy, cap 1200 (the restart-challenge bound; it cannot repeat the 4,000 burn) | **~20 core-min** |
| | **total** | **~45 core-min** |

**That is ~10 core-min over the ~35 approved, and I am flagging it before spending rather than
after.** The overrun is the diagnosis half; the arm half is the approved shape. If the chief
prefers the approved envelope exactly, D2 (6 core-min) is the droppable piece — it strengthens
the A5 growth story but no branch of §B depends on it.

## D. Mechanics

Staged copies (guidelines §8), cold start proven in-log, both standing proofs (`transonicPCOption
1;`, no sub-LU banner unless R2 fires and then its banner is required), setsid + `.t0/.rc/.t1`
ledger, polled inline, explicit handoff naming container/ledger/log if a run outlives the turn.
Memory guard unchanged (22g cap, 6 GB host floor, a memory death is NOT EVALUABLE). The matrix
dumps are written inside the staged case dirs and their sizes reported.
