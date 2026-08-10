# Restoring PETSc's escape hatch — stage 1: PRE-REGISTRATION

Filed 2026-08-10, chief-approved (~15 core-min), proposal
`dafoam-restore-ksp-options-escape-hatch` (178027ce). Committed BEFORE any compute.
Implements fix (a) of the defect candidate `DEFECT_CANDIDATE_ksp_options_override.md`
(f29378d9): honour `KSPSetFromOptions` instead of overriding it.

## 1. The patch, stated exactly

`src/adjoint/DALinearEqn/DALinearEqn.C`, function `createMLRKSP` (lines 28–358). The call
moves from the top of the setup block to the end of it — one call relocated, nothing else
touched:

```
@@ line 137-138: REMOVE
-    // First, KSPSetFromOptions MUST be called
-    KSPSetFromOptions(ksp);

@@ after line 343 (KSPSetTolerances(ksp, rtol, atol, PETSC_DEFAULT, maxIts);): INSERT
+    // PATCHED 2026-08-10 (Certonomous): KSPSetFromOptions moved from the TOP of this
+    // function to the END. Called first, every explicit setter below silently overrode
+    // it, so -ksp_type / -pc_type / -sub_pc_type were accepted and discarded. Called
+    // last, daOptions act as DEFAULTS and PETSc runtime options act as OVERRIDES, which
+    // is what both APIs promise. With no options set the behaviour is unchanged.
+    KSPSetFromOptions(ksp);
```

**Why the end of the function and not merely later:** `KSPSetFromOptions` also calls
`PCSetFromOptions` on the KSP's PC, so placing it last is what makes `-pc_type` reachable as
well as `-ksp_type`. It is placed **before** the `printInfo` block deliberately, so the
diagnostic echo is the last thing that runs.

**A wart in the fix, disclosed now and carried to the upstream report:** the `printInfo` block
echoes the *daOptions* values (`Solver Type: <kspObjectType>`, `GMRES Restart: …`), not the
*effective* ones, so after this patch a user who overrides `-ksp_type` would still see
`Solver Type: gmres` in the log. That is precisely the L-40 hazard this lab has spent two days
closing — a switch that ran differing from the switch the log claims. The minimal fix does not
address it; the upstream recommendation should therefore be **fix (a) plus an effective-value
echo** (`KSPGetType`/`PCGetType` after the options call). Recorded here so the report carries it.

## 2. Image discipline (the chief's note, and it is the right one)

- Base: **`dafoam-subpclu:v1`** — the image the A3 evidence chain actually ran on — so the
  regression comparison is against the exact baseline, not a different lineage.
- New tag: **`dafoam-kspopts:v1`**. Distinct, local-only, nothing pushed.
- **`dafoam-subpclu:v1` and `dafoam/opt-packages:latest` are left untouched and reachable.**
- Every arm from here on records its image tag in its own `lever_echo.txt` and in the result
  record. An unlabelled rebuild is exactly the "which switch actually ran" class this campaign
  has been closing.
- Build recipe per the lab's own measured precedent (`W4_ADJOINT_PC_UNBLOCK.md` §4), including
  its documented pitfall: **source the OpenFOAM environment BEFORE any `set -e`**. Three AD
  targets (original, ADR, ADF) rebuilt, as that record specifies.

## 3. GATE A — REGRESSION. The load-bearing gate, and it is load-bearing for the upstream report

A maintainer's first objection to fix (a) is *"does honouring the option channel change
behaviour by default?"*. This answers it by measurement.

**Test:** rung 1's converged arm (`A3-onera-m6-sweep-n15_21840` config, `transonicPCOption 1`,
stock ILU), on `dafoam-kspopts:v1`, with **no `PETSC_OPTIONS` set and `DAFOAM_SUBPC_TYPE`
unset**, cold-started.

**Pass:** **CD 368 iterations and CL 383 iterations, both `PetscConvergedReason: 2`** — the
exact counts measured on `dafoam-subpclu:v1` (11b90d25) and reproduced twice since. Iteration
counts are the sharpest available equality test: any change in the assembled solver stack moves
them.

**Fail → the more valuable finding, and it is reported with equal prominence:** a failure means
the override is **load-bearing** — that something in the explicit-setter ordering matters
beyond configuration — which would mean **the defect report's own recommended fix (a) is wrong
and must be re-graded before anyone upstream acts on it.** In that case fix (c) (options
prefix) becomes the recommended remedy instead, stage 2 is abandoned, and the defect record is
amended the same session.

## 4. GATE B — RESTORATION

**Test:** the same case on the same patched image with
`PETSC_OPTIONS="-ksp_type fgmres -ksp_view"`.

**Pass:** `-ksp_view` reports **`type: fgmres`** where the shipped build reports `type: gmres`
(the shipped behaviour is already on record: §3 of the defect candidate).

**Fail:** the patch does not restore the channel; the defect report gains a measured caveat that
its recommended fix is insufficient as written, and stage 2 does not proceed.

Both gates must pass for stage 2 to be requested. Either failing ends stage 1 with a reported
result, not a retry.

## 5. Price and mechanics

Measured basis (`W4_ADJOINT_PC_UNBLOCK.md` §4, the prior patch of this same file): ~40 s compile
per target, ~2 min container CPU across three wmake targets → **~5 core-min build**; Gate A is
rung 1's own measured arm at **7.33 core-min**; Gate B is a seconds-long `-ksp_view` run on the
same case with a 1-iteration cap. **Total ~15 core-min**, as approved.

Staged case copies (guidelines §8), cold start proven in-log, setsid + `.t0/.rc/.t1` ledger,
polled inline, explicit handoff if a run outlives the turn. Memory guard unchanged (rung 1 peaks
under 6 GB; 16g cap). **R11 discipline: the shipped-toolchain verdicts stand unchanged; every
patched-image result is recorded beside them, never in place of them.** The patch is committed
to the repo beside `subpclu_patch/DALinearEqn_subpclu.patch`.
