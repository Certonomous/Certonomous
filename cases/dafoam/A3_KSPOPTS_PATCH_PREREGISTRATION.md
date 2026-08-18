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

---

# §6. RESULTS — **both gates PASS. Fix (a) works and is behaviour-neutral by default.**

Image built and tagged **`dafoam-kspopts:v1`** (`d9d2aed02e36`, 10 GB). **`dafoam-subpclu:v1`
(`ba2d16ab9d57`) and `dafoam/opt-packages:latest` (`9d45679d55fd`) are untouched and reachable** —
verified by `docker images` after the commit. Build: all three AD targets rebuilt rc=0 in **29 s
wall at `-j 8`** (original 9 s, ADR+ADF 20 s); `WM_AD_MODE` restored to its original `ADF`;
`libDASolver{,ADR,ADF}.so` all relinked. Patch archived at
`kspopts_patch/DALinearEqn_kspopts.patch` (3f631c4d) beside the subpclu one — 28 lines, one call
relocated. Every arm below records its image tag in its own `lever_echo.txt`.

## GATE A — REGRESSION: **PASS, bit-identical**

Rung 1's converged arm on `dafoam-kspopts:v1`, `PETSC_OPTIONS` unset, `DAFOAM_SUBPC_TYPE` unset,
cold-started (`lever_echo.txt` records `IMAGE=dafoam-kspopts:v1`, `PETSC_OPTIONS=[]`):

```
**Completed**! Total iterations: 368. PetscConvergedReason: 2.   (CD)
**Completed**! Total iterations: 383. PetscConvergedReason: 2.   (CL)
Time step continuity errors : sum local = 0.5969274433533561
```

**368 / 383, reason 2 on both — exactly the counts measured on the shipped-lineage image
(11b90d25) and reproduced twice since**, with the cold signature matching to all 16 digits.
rc=0, 130 s = 8.67 core-min.

**This is the answer to the maintainer's first objection, by measurement: honouring
`KSPSetFromOptions` changes nothing when no options are set.** Iteration counts are the sharpest
equality test available — any change in the assembled solver stack would move them, and they did
not move at all. The override is **not** load-bearing, so fix (a) stands as the recommended
remedy and does not need re-grading.

## GATE B — RESTORATION: **PASS**

Same case, same image, `PETSC_OPTIONS="-ksp_type fgmres -ksp_view"`:

```
KSP Object: 4 MPI processes
  type: fgmres
    restart=30, using Classical (unmodified) Gram-Schmidt Orthogonalization ...
```

**`type: fgmres`, where the shipped build reports `type: gmres`.** The escape hatch is open:
`-ksp_type` now takes effect. 126 s = 8.4 core-min.

### Two findings from Gate B that belong in the upstream report

1. **Overriding the type resets PETSc-level settings that DAFoam applied to the old object.** The
   view reports `restart=30` — PETSc's default — not the `gmresRestart: 200` from `daOptions`,
   because `KSPSetType` rebuilds the KSP's internal state and DAFoam's `KSPGMRESSetRestart(200)`
   ran earlier against the previous type. Consequence, and it is correct "user override wins"
   semantics rather than a bug: **a user who overrides `-ksp_type` must also pass
   `-ksp_gmres_restart` (and any other GMRES-family setting) if they want DAFoam's values.**
   Gate B's run then hit `-3` at 1000 iterations, which is exactly what restart 30 buys against
   restart 200's 368 — the non-convergence is the small restart, not the patch.
2. **The `printInfo` echo remains stale**, as disclosed in §1: with `-ksp_type fgmres` in force,
   the log still prints `Solver Type: gmres` and `GMRES Restart: 200` from `daOptions`. This is
   the L-40 hazard in its purest form — the log names a switch that did not run. **The upstream
   recommendation is therefore fix (a) PLUS an effective-value echo** (`KSPGetType`/`PCGetType`
   after the options call), and the defect record now says so with this run as its evidence.

## §6.1 Spend

| step | core-min |
|---|---|
| patch + rebuild (3 AD targets, 29 s at `-j 8`) | 3.87 |
| image commit (31 s) | 0.52 |
| Gate A regression | 8.67 |
| Gate B restoration | 8.40 |
| **total** | **21.5 against ~15 approved (1.4x)** |

The overrun is Gate B: I priced it as a seconds-long 1-iteration `-ksp_view` check and ran the
full solve instead. That was worth it — the full run is what produced the `restart=30` finding
and the stale-echo evidence, both of which go upstream — but it was more than I said, and it is
recorded as an overrun rather than folded into the estimate.

**Stage 2 is now unblocked and is NOT started**: the previously-unreachable remedy class
(`lgmres`/`dgmres`, `gamg`, `fieldsplit`, `sub_pc_type lu`) is reachable on this image, and per
its own framing must be run as a first honest test of that class, not as a rescue attempt — and
with the Gate B lesson applied: any `-ksp_type` override must carry its own restart setting.
