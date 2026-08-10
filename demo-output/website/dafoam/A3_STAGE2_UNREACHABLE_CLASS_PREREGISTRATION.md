# Stage 2 — first honest test of the previously-unreachable remedy class: PRE-REGISTRATION

Filed 2026-08-10, chief-approved (e59fcef6). Committed BEFORE compute. Runs on
**`dafoam-kspopts:v1`** (`d9d2aed02e36`), the patched image whose regression gate returned
bit-identical iteration counts (`A3_KSPOPTS_PATCH_PREREGISTRATION.md` §6).

## 0. BINDING 1 — this is a test of the class, not a rescue attempt

**A failure here is the eleventh elimination. A success is one reachable remedy working — not
vindication of anything.** The A3 ceiling verdict (`834574a6`) stands either way: it was measured
against the shipped toolchain, and nothing run on a locally patched image revises it. If an arm
converges, the correct sentence is *"a remedy that the shipped build cannot reach converges this
rung"* — which is a statement about the defect's cost, not about the ceiling being wrong. This is
binding on how the result is written, and it is written here before any number exists.

## 1. Which arms, and why only two

**Two arms. ~52 core-min total** at the measured 25.9 core-min per 400-iteration rung-3 arm.
Running the whole class would be ~104+ core-min for a question whose most likely answer is a
null; a partial test honestly bounded is the better buy, so the two most-indicated run and the
rest are declined **with reasons on the record**:

| candidate | run? | why |
|---|---|---|
| **`-ksp_type lgmres`** | **YES — arm 1** | The single most reproduced observation of this whole campaign is that **progress dies at the restart boundary** — three independent strikes: Richardson collapsing at exactly iteration 200 (stage 0), the baseline stalling across 20 restarts (stage 1), and the 5x-window arm flattening at exactly iteration 1000 (restart challenge). LGMRES (Baker/Jessup/Manteuffel 2005) augments each cycle with approximations to the error from previous cycles, i.e. it is built precisely to recover what restarting discards. It is the arm the evidence points at hardest. |
| **`-pc_type gamg`** | **YES — arm 2** | The coarse-space remedy. The Schwarz *overlap* arm refuted "wider overlap fixes it", but that is exactly what classical theory predicts: overlap buys a bounded factor, and **only a coarse space supplies the global information transfer a one-level method structurally lacks**. Overlap failing does not indict a coarse grid — it is the standard reason to reach for one. |
| `-ksp_type dgmres` | no | Same family and same mechanism as arm 1. If LGMRES does nothing, deflated restarting is unlikely to differ enough to justify another 25.9 core-min; if LGMRES helps, this becomes the natural follow-up. Declined now, named for later. |
| `-pc_type fieldsplit` | **no — contra-indicated by my own diagnosis** | The diagnosis measured that the field blocks **do not separate**: the 2,000 largest diagonals are flat across all six field slots (301/357/331/324/351/336) and every slot spans 13+ decades. Running field-split would be trying a knob against a precondition I already refuted. |
| `-sub_pc_type lu` | no | Not new — reachable already through the lab's own `DAFOAM_SUBPC_TYPE=lu` patch, and tested at rung 2 where it proved memory-infeasible. |

## 2. BINDING 2 — the Gate B restart lesson travels with every arm

Gate B established that **`-ksp_type` rebuilds the KSP's internal state, so DAFoam's
`KSPGMRESSetRestart(200)` — applied earlier to the previous type — is lost and PETSc's default
restart of 30 takes over.** In Gate B that alone turned a 368-iteration convergence into a
1000-iteration `-3`. Uncorrected here, an arm would inherit restart 30 and **I would be reading
the restart's failure as the method's.**

Therefore, explicitly per arm:

- **Arm 1 (lgmres)** changes the Krylov type, so it carries its own settings:
  `-ksp_type lgmres -ksp_gmres_restart 200 -ksp_max_it 400 -ksp_rtol 1.0e-4 -ksp_view`.
  Restart 200 and max-it 400 make it commensurable with the control **by construction**.
- **Arm 2 (gamg)** does **not** change the Krylov type, so restart 200 and the tolerances survive
  untouched; it carries `-pc_type gamg -pc_gamg_sym_graph true -ksp_view`. `sym_graph` is
  included because GAMG's defaults target symmetric systems and this operator is nonsymmetric —
  omitting it would be testing GAMG outside its documented envelope and calling the result a
  verdict.

**Verification, not assumption:** each arm's `-ksp_view` output must be read back and quoted —
the effective `type:`, `restart=`, and PC type — before its number is graded. This is the stale
`printInfo` lesson applied to my own arms: the log's `Solver Type:` line will still print
`gmres` from `daOptions`, and it must not be mistaken for what ran.

## 3. BINDING 3 — grading, commensurable with the ten that preceded it

Base configuration is the diagnostic control's own script (`runScript_diag.py`: 400 iterations,
`transonicPCOption 1`, `pcFillLevel 0`, restart 200, `KSPCalcSingularVal 1`), so the only
difference is `PETSC_OPTIONS`.

**Standing control: residual `1.615428631404e-02` at iteration 400** (fill-0 diagnostic,
`sMax/sMin` 9.57e+10, `-3`).

- **CONVERGES** (`PetscConvergedReason: 2`): one reachable-only-after-patch remedy converges
  rung 3. Recorded per Binding 1.
- **MATERIAL** (residual at iteration 400 at least **10x** below the control, i.e.
  ≤ `1.615e-03`): partial; reported with its number; no extension without new approval.
- **STALL** (within 10x, or flat): joins the elimination table. Two stalls = the class is tested
  and the table gains its eleventh and twelfth entries.
- **SETUP FAILURE** (arm 2 specifically): DAFoam configures `PCASM` and retrieves its sub-KSPs
  *before* the relocated `KSPSetFromOptions` can change the PC type. If replacing the PC type
  crashes or errors in setup, that is **not** a verdict on GAMG — it is a **refinement for the
  upstream report**: fix (a) restores the option channel but the surrounding setup path assumes
  ASM, so a complete fix must apply the options *before* the ASM-specific configuration. Recorded
  as such, and the arm reports no conditioning verdict.

## 4. Memory arithmetic, before launch (fifth consecutive statement)

Rung-3 baseline peak: **11.65 GiB** against a 22 GiB cap, host ~29 GB free.

- **Arm 1 (lgmres):** stores the restart-200 basis exactly as GMRES does (200 x 5.8 MB ≈ 1.16 GB,
  already in the baseline) plus LGMRES's augmentation vectors — default 2 extra directions,
  ~12 MB. Predicted peak **≈11.7 GiB**. Essentially free.
- **Arm 2 (gamg):** replaces ASM/ILU with a multigrid hierarchy — coarse-level operators plus
  interpolation. Typical GAMG overhead is ~1–3x the fine operator; the assembled fine matrix is
  ~1.0 GB (81.7M nonzeros), so **+1–3 GB**, predicted peak **≈13–15 GiB**, with the ILU storage
  it replaces recovered. Under the 22 GiB cap with headroom.
- Standing guard: stop and report if a container approaches the cap or host MemAvailable falls
  below 6 GB. **A memory death is NOT EVALUABLE, never a conditioning verdict.**

## 5. Mechanics

Staged copies per arm (guidelines §8), cold start proven in-log against rung 3's signature,
`DAFOAM_SUBPC_TYPE` unset, `lever_echo.txt` recording **image tag and the exact PETSC_OPTIONS
string** for every arm, setsid + `.t0/.rc/.t1` ledger, polled inline, explicit handoff if a run
outlives the turn. Arms run **sequentially** (the memory guard forces ordering; the graded metric
is per-arm and contention-insensitive). Results appended here as §6; docket updated inline, own
entry only. R11: shipped-toolchain verdicts stand unchanged beside every patched-image result.

---

# §6. RESULTS — **both arms fail. Eleventh and twelfth eliminations.**

Both ran on `dafoam-kspopts:v1`, `DAFOAM_SUBPC_TYPE` unset, cold-started, with the identical
base script as the control — so the only difference is `PETSC_OPTIONS`. **Both arms report the
same iteration-0 residual as the control, `2.121343646203e-02`, which establishes
commensurability directly rather than by assumption.**

## Arm 1 — `-ksp_type lgmres`: FAILS

**Verification readback (Binding 2), quoted before grading:**
```
KSP Object: 4 MPI processes
  type: lgmres
    restart=200, ... aug. dimension=2
  maximum iterations=400, tolerances: relative=0.0001
  right preconditioning
  using UNPRECONDITIONED norm type for convergence test
```
The type took effect; **restart=200 was preserved because the arm carried it explicitly** — the
Gate B lesson doing exactly the job it was included for — and the norm type matches the control,
so the residuals are directly comparable.

**Result: `-3` at 400 iterations, residual `8.236875832365e-02`.** That is **5.10x WORSE than the
control** (`1.615428631404e-02`) and **3.88x above its own iteration-0 value**. 291 s = 19.4
core-min.

*Anomaly disclosed rather than binned:* a residual rising above its own starting value is not
what a GMRES-family method should produce, so this is flagged rather than quietly filed as a
stall. Either the solve genuinely diverged, or LGMRES's augmented recurrence reports an
intermediate norm differently in this PETSc build. **This arm cannot separate those**, and it
does not need to for its verdict: under either reading the method did not converge and did not
descend. Graded a STALL per Binding 3.

## Arm 2 — `-pc_type gamg -pc_gamg_sym_graph true`: FAILS

**Verification readback:**
```
PC Object: 4 MPI processes
  type: gamg
    type is MULTIPLICATIVE, levels=4 cycles=v
```
The option took effect and GAMG built a **4-level hierarchy** — confirming the patch unlocks the
**preconditioner family**, not just the Krylov type.

**Result: `PetscConvergedReason: -5` at 200 iterations, residual `7.554080154832e+179`.** The
solve diverged catastrophically: barely moving at iteration 100 (`2.120914790716e-02`, from
`2.121343646203e-02`) and then exploding by 180 orders of magnitude.

**Memory was never a factor** — peak **7.0 GiB**, host never strained. *Disclosed launcher
discrepancy:* the shared runner hardcodes `--memory=16g` while §4 stated a 22 GiB cap against a
predicted 13–15 GiB peak. The tighter cap was **never approached** (7.0 of 16 GiB), so it had no
effect on the result — but the mismatch between what I pre-registered and what I ran is recorded
rather than passed over.

**Arm stopped after its graded solve.** CD — the graded solve throughout this campaign — had
returned `-5`; the CL solve was continuing on this family's known `-5` false-success path and
would have added ~30 core-min for no additional information. Ledger rc=137 at 1,575 s. **This
arm therefore billed 105.0 core-min against 25.9 estimated**, the overrun being GAMG's setup and
per-iteration cost, which I had no measured basis for and under-priced from the ILU baseline.

## §6.1 Verdict, bounded exactly as Binding 1 requires

**Neither previously-unreachable remedy converges rung 3.** The elimination table gains its
**eleventh (augmented-restart Krylov)** and **twelfth (algebraic multigrid)** entries. Per
Binding 1, this is *not* vindication of the ceiling: the shipped-toolchain verdict already stood
on its own and is untouched by anything run on a patched image.

**Scope, stated so nobody over-reads it in either direction:** this tested **two off-the-shelf
members of the class, at documented defaults**, on a nonsymmetric transonic adjoint. It did
**not** test the class in a tuned form — GAMG's defaults target elliptic/SPD-like operators even
with `sym_graph`, and a convection-dominated compressible adjoint is outside that envelope, so
arm 2 is evidence that **off-the-shelf AMG fails here**, not that a coarse-space method cannot
work. A physics-appropriate coarse space, or AMG with smoothers chosen for this operator, remains
untested and is not cheap.

**What the arms did prove beyond their own verdicts:** the patched escape hatch genuinely works
on both axes — a Krylov type (`lgmres`) and an entire preconditioner family (`gamg`, 4 levels)
were selected at runtime on a build where both were previously unreachable. **That is the defect
report's cost made concrete**: a user reaching for either of these on the shipped build gets
silence, and the two arms above are what they would have been unable to try.

**A third instance of the campaign's standing caveat:** the Krylov condition estimate again
failed to predict convergence. Arm 1 reported `sMax/sMin` 2.70e+05 and arm 2 7.71e+17, against
the control's 9.57e+10 — six orders of spread in the estimate across arms whose convergence
behaviour ranged only from *stalling* to *worse*. With fill-1's 10^7 improvement buying 1.9x,
that is now three independent arms saying the same thing: **this estimate is not the instrument
for this question.**

## §6.2 Spend

| arm | core-min | vs estimate |
|---|---|---|
| arm 1 lgmres | 19.4 | 25.9 — under |
| arm 2 gamg | 105.0 | 25.9 — **4.1x over** |
| **stage 2 total** | **124.4** | ~52 — **2.4x over** |

The overrun is arm 2 alone and its cause is nameable: I priced both arms off the ILU baseline's
per-iteration cost, and GAMG's hierarchy setup plus V-cycle cost has no relation to it. **The
correction for any future AMG arm: price the setup phase separately, and cap on wall rather than
on iterations when the per-iteration cost is unknown.**
