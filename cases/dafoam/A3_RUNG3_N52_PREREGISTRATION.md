# A3 ladder rung 3 — the 79,560-cell member: PRE-REGISTRATION

Filed 2026-08-10 by the DAFoam solver agent, chief ruling 3 of the 2026-08-10 dispatch:
approved to pre-register now, **launch after the triage reports** (triage reported, 3ac8257e).
Committed BEFORE compute.

## 1. The ladder-level question this rung answers

Rungs 1 and 2 gave two converged, FD-verified points and, between them, an iteration-scaling
exponent: **CD cells^1.50, CL cells^1.70**. Two points define an exponent; they cannot test it.
**Rung 3 is the first opportunity to find out whether the exponent HOLDS OR BREAKS at the next
doubling — and that is what any honest extrapolation to production meshes rests on.** If it
holds, the ladder has a calibrated cost law and the reach toward 399,360-cell-class meshes can
be priced rather than guessed. If it breaks upward, the reopened ladder has a practical ceiling
well below production size and the record should say so before anyone plans around it. Either
way this rung converts a two-point slope into a tested law, which is worth more than the rung
itself.

Pre-registered prediction, stated so it can be wrong (baseline config, no lever): **CD ≈ 2,570
iterations, CL ≈ 3,456** at 79,560 cells. Derivation: exponent from the measured pair —
`e = ln(987/368)/ln(42120/21840) = 1.50` (CD), `ln(1171/383)/ln(42120/21840) = 1.70` (CL) —
applied as `i₃ = i₂ · (79560/42120)^e`. Under the adopted lever of §3, the predictions become
**CD ≈ 1,460 / CL ≈ 1,904**. A measured count materially above the relevant prediction is the
exponent breaking upward; materially below is it breaking downward; within ~15% is the law
holding.

## 2. Rung identity and the admission gate (certified BEFORE this filing)

`/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-probe80k/` — **79,560 cells**
(`nPoints:82940 nCells:79560 nFaces:241974`), the D3 sweep's N=52 member: same 3x-coarsened M6
surface as rungs 1–2, 52 pyHyp layers. Its archived record is the corrected orphaned probe:
double `-5` (DIVERGED_BREAKDOWN) at 200 iterations, agg peak **17,603.8 MiB** (uncensored, 22g
cap), 960 s — with `transonicPCOption 2`, i.e. the PC inactive, like every other archived M6 run.

As predicted in the ruling, the member **carried no birth certificate and was therefore
quarantined under MESH_STANDARD v1.1**. Certification was this arm's first act:
`checkMesh -constant` → **"Mesh OK."**, zero failed checks, then
`sdk/chief_engineer/mesh_certificate.write_certificate`:

```
points_sha256 cf35cf1446830d880bded657d59dea0417c2dd3d01b238e1e37514ecd9432caa
verdict "clean"   cells 79560   hard_errors []
max_aspect_ratio 608.2096897908551   max_non_orthogonality 61.49368843892955
max_skewness 2.279056246183647
generator "pyHyp (genWingMesh.py, N=52 layers, 3x-coarsened M6 surface)"
```

`certificate_admits() == True | clean`. `log.checkMesh` placed beside the case for the
standard's second enforcement layer. Note the family signature holding across all three rungs:
max aspect ratio 608.21 and max non-orthogonality 61.49 are essentially identical at 21,840 /
42,120 / 79,560 cells — the mesh family's quality is layer-count-independent, so rung 3 differs
from its verified predecessors in size alone, not in quality. Cell volumes positive
(min 1.246e−10); the vcoarse inversion pathology is absent.

## 3. Configuration, the adopted lever, and stage 0

**Adopted lever: L3 Richardson** (`adjEqnOption.globalPCIters: 3, localPCIters: 3`), per the
triage's §9 recommendation. It gave the largest iteration cut on both solves (−43.2% / −44.9%)
and is **the only one of the three winners that costs no additional memory** — decisive here,
because rung 3's second wall is memory (17.6 GB measured at this exact member against a 30 GB
box with a 6 GB host floor, ~24 GB usable). L1 (fill1) was wall-cheaper but adds ILU fill-in to
a 6-field Jacobian; L2 (restart1000) stores 1000 Krylov vectors (~+3.8 GB here). Both are
declined for this rung and remain on the record as alternatives if wall, not memory, ever binds.

**Stage 0 — the confirmation arm, not waived.** The triage measured at 21,840 cells and its own
§2 forbids adopting a lever at a new rung without testing transfer. Stage 0 runs **L3 at rung 2
(42,120 cells)**, graded against rung 2's measured CD 987 / CL 1171:
- **Transfer confirmed** (material cut, >10% on both solves) → rung 3 proceeds with L3 at the
  §1 lever-adjusted predictions and `gmresMaxIters` 2500.
- **Transfer fails** (cut <10%, or worse) → **rung 3 reverts to the filed baseline basis**
  (~113 core-min, `gmresMaxIters` ≥ 4000) and the finding "lever benefit is mesh-dependent" is
  recorded, which is itself worth the arm.
- **Collapse under L3 at rung 2** (any negative reason) → the R5 strengthening signature
  re-appearing at a larger mesh WITH the PC active; rung 3 proceeds baseline and the
  conditioning story gains a mesh-dependence term.

Base config otherwise unchanged from the two verified rungs: `transonicPCOption: 1`, stock
ILU(0), `natural`, `gmresRestart 200`, `gmresRelTol 1e-4`, `DAFOAM_SUBPC_TYPE` UNSET, 4 ranks,
task `compute_totals`; staged copies (guidelines §8), `decomposePar -force` from pristine
serial `0/`.

**`gmresMaxIters`: 2500 under L3 (≥ 4000 if stage 0 fails and the baseline basis is restored).**
Derivation in §1; the cap is set above the prediction with margin precisely so that a broken
exponent reports a larger number instead of truncating into a `-3` and confounding the test —
the attempt-1 lesson, now standing practice.

## 4. Required proofs (L-40), unchanged

In every arm's log before any number counts: `transonicPCOption 1;` (record logs read `2;`),
**no** sub-LU banner (env unset), `Global PC Iters: 3` / `Local PC Iters: 3` for the lever, and
this member's cold-from-uniform continuity signature, established at stage 1 launch from its own
first cold run and asserted for every subsequent arm on this rung. Launcher `lever_echo.txt`
declares; the solver's own DAOption dump confirms. Canonical `lever_echo.echo_block` captured
per staged case.

## 5. Acceptance criteria (the family's standing set, unchanged)

- **Converged adjoint** = positive `PetscConvergedReason` (2) on BOTH CD and CL, from the raw
  log, never the wrapper's success line; any negative reason = DIVERGED **except** that a `-3`
  at exactly the cap with monotone descent is reported as budget-limited, not as a wall (proven
  at rung 2 to ten significant digits); crash/OOM before a reason = NOT EVALUABLE.
- **FD arm** (charter §7, the validated protocol): `primalMinResTol` 1e−8 with
  `primalMinResTolDiff` 1e4, central differences at h=1e−2 and 2h, **runtime `argmax|g|`
  component selection per DV group** (no hand-transcribed index), repeat-baseline noise floor,
  evaluability at 10x floor and <1% step-consistency, PASS <5% / CONDITIONAL 5–15% / FAIL >15%,
  arm PASS = all evaluable PASS with ≥2 evaluable, step-inconsistent small signals reported
  unverdicted.

## 6. Memory guard — the constraint most likely to end this rung

Record peak at this member: **17,603.8 MiB** (fill 0, 4 ranks, uncensored). Cap
**`--memory=22g`**, host floor 6 GB enforced by inspection: the arm STOPS if the container
approaches the cap, if host MemAvailable falls below 6 GB, or if swap grows — the sub-LU arm's
lesson, where 20 GiB resident plus 12 GB swap produced no KSP iterations in 27.9 minutes.
**A memory death is NOT a conditioning verdict and will not be reported as one** (standing
precedent); it would be reported as NOT EVALUABLE with the memory numbers, and the exponent
question would remain open at this rung.

## 7. Outcome mapping

- **Converged + FD PASS** → three verified rungs; the exponent is tested at the next doubling
  and the ladder has a calibrated cost law (holding or corrected, per §1's bands).
- **Converged, FD fails/not-evaluable** → the rung's convergence stands as an existence proof
  only, gradient explicitly unusable at this rung (rung-1 precedent).
- **DIVERGED (negative reason, not the cap case, PC and lever proven active)** → the wall is
  real above 42,120 cells with the PC active and the strongest memory-free lever on: a clean
  ceiling statement for the reopened ladder, and the extrapolation stops there honestly.
- **Memory death** → NOT EVALUABLE per §6; no conditioning claim in either direction.

## 8. Price and mechanics

Stage 0 (L3 at rung 2): rung 2's arm A measured 28.9 core-min; L3's rung-1 profile (−44%
iterations, +21% wall per iteration) predicts **~26 core-min**. Stage 1 (rung 3 arm A under
L3): baseline estimate ~113 core-min scaled by L3's measured wall behaviour → **~80–95
core-min**; the memory guard may end it earlier. Stage 2 (rung 3 FD arm): ~16 primals at this
size → **~60–70 core-min**, launched only if stage 1 converges. **Total ~170–190 core-min** —
materially more than any single arm this campaign has run, and stated plainly here rather than
discovered later; the rung-2 lesson was that pricing off cells underestimates, and this estimate
already carries the superlinear correction.

setsid + `.t0/.rc/.t1` ledger per arm, logs in each staged dir, polled inline, **explicit
handoff naming container, ledger and log path if the turn ends mid-run**, host load checked
before each launch, single-step pathspec commits. Results appended to
`A3_RUNG3_N52_RESULT.md`; docket entry updated inline, own entry only.
