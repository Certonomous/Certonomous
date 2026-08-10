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

---

# §B. THE DIAGNOSIS (measured 2026-08-10, before any remedy was chosen)

Two runs: rung-3 diagnostic (`A3-diag-rung3`, 400 iterations, rc=0, 388 s = **25.9 core-min**)
and rung-2 PC-matrix dump (`A3-diag-rung2`, 93 s = **6.2 core-min**). Both carried
`transonicPCOption 1;` and no sub-LU banner. PC matrices: 983 MB (rung 3, 724,609 unknowns,
81,718,327 nonzeros, 112.8/row) and 517 MB (rung 2, 384,518 unknowns, 42,988,956 nonzeros,
111.8/row).

**A1 — recursive vs TRUE residual: they TRACK.** Throughout the stall, e.g. iteration 212:
`resid norm 1.618871461180e-02  true resid norm 1.618871461180e-02` (12 digits), and at
iteration 400 `1.615428631404e-02` vs `1.615428564220e-02` (7 digits). **No loss of
orthogonality. The Krylov recurrence is faithful and the method is not numerically broken — the
operator genuinely offers no progress.** `||r||/||b||` sits at 7.6e-01: the solve has removed
under a quarter of the initial residual in 400 iterations.

**A6 — preconditioned condition estimate: `sMax/sMin = 1.55588e+10 / 0.162545 = 9.57e+10`.**
This is the wall as one number: *after* ASM+ILU(0) preconditioning, the operator GMRES actually
sees has a condition number near 10^11.

**A2 — diagonal spread: 14.47 decades** (|diag| from 8.777e-04 to 2.579e+11); median 4.94e+04.

**A3 — field blocks do NOT separate.** With `adjStateOrdering: cell` the first 477,360 rows are
6 states per cell (79,560 cells; the remaining 247,249 are `phi` on internal + processor faces).
Per-slot medians are all within a factor of 1.7 (2.03e5–3.40e5) — `normalizeStates` is doing its
job — and **every slot individually spans 13.1–14.5 decades**. Of the 2,000 largest diagonals,
the slot histogram is flat (301/357/331/324/351/336). **There is no field to split off.**

**A4 — the extremes are NOT geometrically localized.** The 500 cells with the largest diagonals
span x[−8.29, 1.22], y[−8.68, 10.07], with spatial std (1.32, 1.77, 0.60) against the whole
mesh's (1.62, 1.59, 1.19); their median distance from the wing tip TE corner is 0.775 versus
0.881 for all cells, and they are *less* near-wing than average (21.8% vs 46.6% at |y|<0.05).
**The tip-TE pathology of this mesh family is not the driver.**

**Volume, tested and exonerated.** Cell volumes span 9.97 decades (1.246e-10 to 1.157e0), so the
obvious mechanism — mesh volume spread imprinted on the diagonal — was tested and REFUTED:
correlation of log|diag| against log(volume) is **r = −0.135**, fitted slope **−0.100** (−1.0
would mean diag ∝ 1/V), and the median |diag| is flat to within one decade across ten decades of
volume (4.79e9 → 8.92e8). The mesh is not doing this.

**A5 — THE DECISIVE COMPARISON: the spread did NOT grow, but convergence died.**

| | rung 2 (42,120 cells) | rung 3 (79,560 cells) |
|---|---|---|
| unknowns | 384,518 | 724,609 |
| nonzeros/row | 111.8 | 112.8 |
| **diagonal spread** | **14.40 decades** | **14.47 decades** |
| adjoint outcome | **converges, CD 987 iterations** | **stagnates** |

**0.07 decades apart — and one converges while the other cannot.** This refutes the hypothesis
the capability strategy's own phrasing gestures at: **the diagonal spread is NOT what conditions
this problem.** A 14.4-decade spread is survivable at 42,120 cells; the same spread is fatal at
79,560. Whatever changed is not the operator's diagonal scaling. Recording that plainly, because
it was the hypothesis I most expected to confirm and the one a motivated reading would have
confirmed.

## §B.1 What the diagnosis leaves standing

Refuted by measurement: method breakdown (A1), field separation (A3), geometric localization
(A4), volume scaling, and diagonal-spread growth (A5). What differs between the rung that
converges and the rung that does not is **not** the assembled operator's scale structure —
it is **size**: 384,518 → 724,609 unknowns at a FIXED 4-subdomain decomposition, i.e. subdomain
size 10,530 → 19,890 cells per rank, with the preconditioned condition number reaching 9.57e+10.

**In Saad's terms this is the textbook signature of one-level additive Schwarz:** ASM without a
coarse-space correction has no mechanism for global information transfer, so its condition number
degrades as subdomains grow relative to the problem — `κ ~ C(1 + 1/(Hδ))` in the classical
estimate (Saad §14.3), with `H` the subdomain size and `δ` the overlap. It also explains the two
observations this campaign already has and could not previously account for: a 5x Krylov window
buying only 1.65x (the subspace is not the deficiency — the preconditioner is), and Richardson
*collapsing* rather than helping (applying a deficient preconditioner three times amplifies its
error modes instead of damping them).

# §C. THE CHOICE, as a prediction — and an honest statement of its weakened evidential status

**Declared before running: my pre-registered decision rule was INCOMPLETE.** R1 (MGSO) is refuted
by A1; R2's precondition (spread concentrated in one field block) is refuted by A3; R3's
precondition (geometric localization) is refuted by A4; R4's (field separation) by A3. The
diagnosis is *not* inconclusive — R5 does not fire either — it returned a **fifth, coherent
signature my rule did not anticipate**: uniform non-localized spread, faithful arithmetic, and a
preconditioned κ ≈ 10^11 that tracks subdomain size rather than operator scale.

**Therefore this choice is written after seeing the diagnosis, though before seeing the outcome,
and it is one notch weaker than the pre-registered ideal. I am stating that rather than
presenting a post-hoc branch as if it had been pre-committed.** The proof, if it succeeds, is
"diagnosis-derived and outcome-pre-registered", not "rule-pre-registered end to end."

**The choice: `asmOverlap: 1 → 2`** — the one parameter of the hardcoded `PCASM` that the theory
above says controls κ, and the only reachable lever that acts on the diagnosed deficiency.
Everything else identical to the rung-3 diagnostic run, so the pair is a controlled comparison.

**The prediction, falsifiable both ways:**
- If one-level Schwarz deficiency is what walls rung 3, **`sMax/sMin` must fall materially below
  9.57e+10** and the residual must descend further than the overlap-1 control at iteration 400
  (which reached 1.615428631404e-02, `||r||/||b||` = 7.615e-01).
- If κ and the residual are essentially unchanged, **the ill-conditioning is not Schwarz-mediated**,
  the diagnosis above is wrong in that stated way, and the ceiling is intrinsic to ILU-class
  preconditioning of this operator.

**Pre-stated, because it is the likeliest outcome and the one most open to motivated reading:**
classical ASM theory predicts overlap buys a *factor*, not decades. If κ moves materially but the
solve still does not converge, that **confirms the diagnosis and simultaneously fails the proof
clause** — because the remedy the diagnosis actually implies is a **two-level method with a coarse
space** (or PCFIELDSPLIT/PCGAMG), and §0 established those are **UNREACHABLE** in this build:
`PCASM` is hardcoded and `KSPSetType` overrides `KSPSetFromOptions`. That is the R4-shaped outcome
my rule did pre-register: *the diagnosis is sound and the remedy is blocked, and I report exactly
that rather than substituting a reachable knob and calling it the proof.*

**Price update, flagged again:** diagnosis actually cost 32.1 core-min against the 25 estimated;
with this arm (~26) the total reaches **~58 core-min against the ~35 approved**. The overrun is
disclosed here before the arm runs, not after.
