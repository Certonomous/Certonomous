# A3 ladder rung 2 — the 42,120-cell member under transonicPCOption:1: PRE-REGISTRATION

Filed 2026-08-10 by the DAFoam solver agent, chief ruling 1 of the post-epilogue dispatch
(Katie's standing instruction: continue with the ladder). Resume protocol executed first: the
8th fleet kill (2026-08-08 ~23:5x) landed before this arm was pre-registered — git log verified
no rung pre-registration exists, tree clean at 62354dd8, zero containers/solvers, nothing of
mine ran in the gap; nothing to reuse, so this is a fresh filing. Committed BEFORE compute.

## 1. Rung identity and the admission gate

`/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n28_42120/` — **42,120 cells** (polyMesh note
`nPoints:44660 nCells:42120 nFaces:128838`), the D3 envelope sweep's N=28 member: same
3x-coarsened M6 surface as rung 1, 28 pyHyp extrusion layers instead of 15. It is the archived
member directly above the verified rung, so no substitute selection was needed.

**Admission gate asserted BEFORE this filing** (the standing rule: run it first so a gate
rejection cannot fire twice, and per the birth-certificate rule that a mesh must be certified
to launch). Standalone `checkMesh -constant`, stock utility in the run image, this session:
**"Mesh OK." — zero failed checks.** Max aspect ratio 608.214865637278 (identical to rung 1 —
same surface mesh and first-layer spacing), max non-orthogonality 61.49354913677975 (average
14.37), **min volume 1.413939465425704e−10, positive** (no inversion — the vcoarse pathology
absent), max skewness 1.9169, face pyramids OK, boundary openness ~1e−18.

**Birth certificate ISSUED before this filing (MESH_STANDARD v1.1 §6).** The archived member
carried NO `birth_certificate.json` — under v1.1 it is quarantined from new work and a launch
against it is refused, so certification was the arm's first act, not an afterthought. The
checkMesh run above was captured to a log and passed to
`sdk/chief_engineer/mesh_certificate.write_certificate`, which wrote the certificate beside the
`polyMesh` it certifies (both the archived member and the staged copy of §7 — identical
`points_sha256`, so one reading binds both):

```
points_sha256 7eb9866ec3a810f4557c1ced08977d4b7553a6c04e5f06a3f364722b8d342d24
verdict "clean"   cells 42120   hard_errors []
max_aspect_ratio 608.214865637278   max_non_orthogonality 61.49354913677975
max_skewness 1.916854554279592
generator "pyHyp (genWingMesh.py, N=28 layers, 3x-coarsened M6 surface)"
```

`certificate_admits()` returns **True | clean** on both roots — the launch gate is satisfied by
the standard's own checker, not by my assertion. The certificate is a record of a check that
ran (the log is retained beside it as `checkMesh_rung2.log` / `checkMesh_n28.log`).

Case state at filing: serial `0/` byte-identical to `0.orig` (verified), NO `processor*` dirs
present, coloring cache `dRdWColoring_4.bin` on record from the D3 run (1315 colors, 4 ranks,
matching `decomposeParDict` numberOfSubdomains 4 / scotch). The archived `runScript.py` is
**line-identical to rung 1's record script** (diff empty) — the two rungs differ only in mesh.

## 2. The baseline this rung re-probes

The record `-5` on THIS member (`run_opt5_onera_n28_42120.log`, 2026-07-30): both adjoint
solves `PetscConvergedReason: -5` at 200 iterations — solve 1 stalling at the 2.12e−02 scale
(2.121211553380e−02 → 2.104215761028e−02) into a denormal (1.482196937524e−322), solve 2 at
the 1.8392e−01 scale (1.839192419993e−01 → 1.839033948692e−01) into 4.047385770731e−320. That
run had `transonicPCOption 2` — dead code for `DARhoSimpleCFoam`
(`DAResidualRhoSimpleCFoam.C:173`), i.e. the transonic PC was never active here either.

Cold-start signature for this mesh (from the record run's own first line, which was this dir's
first run): `Time step continuity errors : sum local = 0.6833296303785072` — this rung's
expected cold value, distinct from rung 1's 0.5969274433533561 as different meshes should be.

## 3. Arms, levers, and the L-40 activity proofs

**Arm A (convergence):** `transonicPCOption: 1`, everything else the archived record config
(stock ILU(0), `natural`, `gmresRestart 200`, `gmresRelTol 1e-4`, `DAFOAM_SUBPC_TYPE` UNSET),
task `compute_totals`, 4 ranks. Script `runScript_tpc1.py` = archived `runScript.py` with the
single token changed (diff asserted to be one line before launch).

**Arm B (FD verification, charter §7):** the protocol validated at rung 1 — `primalMinResTol`
1e−8 with `primalMinResTolDiff` 1e4 (S1 tight-primal discipline; the honest plateau-not-crash
gate), central differences at h and 2h, three components one per DV group, repeat-baseline
noise floor, the standing bands of §5.

**Activity proofs required in-log (L-40), pre-declared:** the DAOption dump must read
`transonicPCOption 1;` (the record log reads `2;`), and NO sub-LU banner may appear (env
unset). Both arms additionally must print this rung's cold signature 0.6833296303785072 as
their first continuity error (guidelines §8 item 2). If any proof is missing the arm is void
and stops. Launcher-side lever echo per §7.

## 4. Component selection — the mis-parse hazard closed mechanically

At rung 1 the pre-registered `shape[5]` reference was a mis-parse of a line-wrapped numpy row
(disclosed in b9f42631); the true max-|g| component was `shape[115]`. This arm removes the
hazard rather than repeating the caution: **the FD script selects components at RUNTIME as
`argmax|g|` within each DV group, from this rung's own converged totals array**, and logs for
each the group, index, array length, and value. No component index is transcribed by hand from
any printed output, so no parse of a wrapped print can enter the selection. (Cell-naming
permutations do not arise: these are patchV/twist/FFD-shape DVs, not field cells; the totals
columns are read from the same `om.Problem` vectors that are perturbed — mapping closed by
construction, as at rung 1.)

## 5. Acceptance criteria (unchanged from the validated rung-1 protocol)

- **Converged adjoint** = positive `PetscConvergedReason` (2 = KSP_CONVERGED_RTOL) on BOTH the
  CD and CL solves, read from the raw log, never the wrapper's "Residual tolerance satisfied"
  line; any negative reason on either solve = DIVERGED; the denormal-residual false-success
  pattern counts as DIVERGED; crash/OOM before a reason prints = NOT EVALUABLE (a memory death
  is not a conditioning verdict — the standing precedent).
- **FD, per component:** evaluable only if |CD(+h) − CD(−h)| > 10x the measured baseline drift
  AND step-consistency |FD(h) − FD(2h)|/|FD(h)| < 1%. Verdict on evaluable components:
  **PASS < 5%**, CONDITIONAL 5–15%, FAIL > 15% or sign flip.
- **FD arm verdict:** PASS = all evaluable components PASS with >= 2 evaluable; CONDITIONAL =
  an evaluable component at 5–15% with none failing; FAIL = any FAIL; NOT EVALUABLE = < 2
  evaluable (reported with the noise numbers). Step-inconsistent small signals are reported
  with their numbers and carry NO verdict — the honest unverdicted branch, as at rung 1.
- Steps: h = 1e−2, 2h = 2e−2 (the sizes that cleared the floor at rung 1); if the measured
  floor at this rung leaves components unevaluable, the not-evaluable branch fires and any
  re-step is a NEW pre-registered addendum, never a silent retry.

## 6. Outcome mapping (the chief's wording, binding)

- **Arm A converges AND arm B passes** → **the ladder has two verified rungs and the
  mesh-size question opens honestly**: the transonic-PC fix is not a one-rung accident, and
  how far up it carries becomes a live, answerable question rather than a hope.
- **Arm A diverges (negative reason, PC proven active)** → **the wall is real ABOVE this rung
  with the PC active** — a clean scoping statement: the fix reopens the ladder at 21,840 cells
  and does not carry to 42,120, which bounds the reopened ladder precisely rather than
  overselling it.
- Arm A converges but arm B fails/not-evaluable → the rung's convergence stands as an
  existence proof only, with the gradient explicitly unusable at this rung (the rung-1
  precedent), and the mesh-size question stays half-open pending an FD re-file.
- Arm A dies on memory/crash → NOT EVALUABLE at this rung, reported as such, with the memory
  numbers; no conditioning claim in either direction.

## 7. Mechanics, guards, and price

- **Staged-copy pattern (guidelines §8 item 3):** both arms run in a fresh staged copy
  `/home/ubuntu/certonomous-runs/A3-rung2-n28-tpc1/`, leaving the archived D3 member
  untouched as the record it is. The copy carries the pristine `0/`, `constant/`, `system/`,
  `FFD/`, the scripts and the coloring cache; `decomposePar` runs inside the copy, so every
  arm starts from the same certified mesh and provably cold fields.
- **Certificate:** issued and verified before this filing per §1 — `verdict: clean`,
  `certificate_admits() == True` on both the staged copy and the archived member.
- **Launcher-side lever echo (L-40):** `run_arm_a.sh` writes `lever_echo.txt` at launch
  declaring what the arm claims to set (`transonicPCOption=1`, `DAFOAM_SUBPC_TYPE=<unset>`,
  the expected cold signature, image/ranks/cap). The declaration is checked against the
  solver's OWN DAOption dump and banner absence after the run, so the claim and the artifact
  are compared rather than the claim being trusted.
- Image `dafoam-subpclu:v1`, env unset, 4 ranks, `--cpus=4`, **`--memory=16g`**: the record
  aggregate peak at this exact member is 9,991.9 MiB (D3 Option 5, uncensored), so 16g leaves
  headroom without inviting the swap-thrash failure the sub-LU arm hit; the pre-declared
  memory guard is that this arm must never approach the cap or drive host MemAvailable below
  6 GB — if it does, STOP and report (that would itself be a finding).
- setsid-detached launchers with the `.t0/.rc/.t1` self-ledger, logs `tpc1_computetotals.log`
  and `fd3_run.log` inside the staged dir; polled inline; **explicit handoff if the turn ends
  mid-run** (naming container, ledger path, and log path). Host load checked before each
  launch (idle at filing: load 0.08, 28 GB free, zero containers).
- **Price, from the measured 7.33 core-min basis with the mesh-size scaling note:** rung 1's
  convergence arm measured 110 s wall x 4 ranks = 7.33 core-min at 21,840 cells with a warm
  coloring cache. This rung is 1.93x the cells; adjoint work per Krylov iteration scales
  ~linearly in cells and the record shows a comparable iteration count, so Arm A is priced at
  **~15 core-min** (7.33 x 1.93, cache warm — the 1315-color pass is already on disk and is
  NOT re-paid). Arm B ran 16 primal evaluations + 1 adjoint in 16.4 core-min at rung 1; at
  1.93x per primal that is **~32 core-min**. **Total ~47 core-min**, reported measured against
  this estimate. Rung 1's own numbers are the anchor; both figures are estimates and the
  overrun rule applies (report, do not silently exceed).

## 8. Item 2 of the dispatch, sequenced as instructed

The D3 n15 variant-lever cold reruns (the warm-start audit's flagged rows) exceed the ~25
core-min bar as a pair with this rung, so per the chief's instruction they are NOT launched
here: this rung runs first and is reported before any D3 launch, and their pre-registration
follows separately.
