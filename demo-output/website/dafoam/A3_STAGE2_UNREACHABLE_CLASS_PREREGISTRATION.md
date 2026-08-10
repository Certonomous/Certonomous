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
