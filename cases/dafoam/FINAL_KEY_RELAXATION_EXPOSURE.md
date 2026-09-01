# L-426 in the dafoam territory — the `Final` relaxation key IS dropped on the unsteady line, CONFIRMED from source, and the dictionary is UPSTREAM's

**Status: internal lab findings record.** This is **not** an upstream defect report. No upstream
report exists, none is drafted, and nothing here is filed, sent, posted or registered anywhere
outside this box. Any send is Sanaa's decision alone (CLAUDE.md rule 7).

**THE EXPOSURE IS INHERITED FROM UPSTREAM AND WAS NOT AUTHORED HERE.** Every one of the 165
affected dictionaries in this lab's D12-family run trees is **byte-identical** to the DAFoam
`Cylinder` tutorial's own `system/fvSolution`, md5 `95ab16a9141b0928bd352a9b9d8d93b9`. The lab
copied a tutorial verbatim and said so in advance: `curriculum_D12R2/d12y_run_script.py`'s header
records that the `daOptions` block is the upstream tutorial's *"VERBATIM"*. This record documents
an inherited property of that tutorial, not a lab authoring slip.

Written by a dafoam lane, 2026-09-01, as an ASSESSMENT. **No case file was edited, nothing was
repaired, and no solve was run.**

---

## 1. THE QUESTION, AND WHY THE FIRST ANSWER WAS AMBIGUOUS

L-426 established that OpenFOAM appends `Final` to the field name on the last PIMPLE outer sweep,
so a `relaxationFactors` key written as a bare alternation applies **no relaxation on exactly the
sweep that sets the answer**. The lesson closes by recording that no sweep of other cases had been
run: *"Nothing here establishes how widespread the defect is elsewhere in this lab."*

The dafoam steady line is immune — it has no PIMPLE control. The unsteady line carries L-426's
exact fingerprint, including the signature detail that **the same file gets the convention right
one dictionary higher up**: `solvers` in the affected file contains both `"(p|p_rgh|G)Final"` and
`"(U|T|e|h|nuTilda|k|omega|epsilon)Final"`, while `relaxationFactors.equations` carries only the
bare alternation.

**The first check was inconclusive and was correctly reported as such.** A grep of a D12R2W3 log
for `PIMPLE: iteration` and `PIMPLE: converged in` returned nothing. That is ambiguous three ways:
no pimpleControl, suppressed `Info`, or the wrong log. The honest state was recorded as **AT RISK,
NOT CONFIRMED HIT**, and this record exists to settle it.

## 2. WHY THE NEGATIVE GREP WAS NOT EVIDENCE — DAFOAM FORKS `pimpleControl`

**DAFoam does not use OpenFOAM's `pimpleControl`. It uses its own fork, `pimpleControlDF`.** The
tell is in every affected log: the line **`Create pimpleControlDF.`**

The fork wraps **every `Info` in `loop()` in `if (debug)`** and leaves the `setFinalIteration`
calls **unguarded**. Its constructor banner has no `verbose` parameter at all and is always
printed. So a live control prints its banner and nothing else, and:

> **"Banner present, iteration lines absent" is the signature of a LIVE `pimpleControlDF` with
> `debug` off. It is not the signature of an absent one.**

Corroborated by count: `PIMPLE: max iterations = 10` appears in **22 of 24** logs in the D12 run
tree and **31 of 33** in D12R; `PIMPLE: iteration` appears in **zero**. The run `controlDict`
declares only `SolverPerformance 0` under `DebugSwitches`, so `debug = 0`.

**This is the part that makes the defect hard to see, and it is a genuine extension of L-426.**
L-426 listed three hiding mechanisms. This is a fourth: *a vendor fork that silences the diagnostic
which would have told you the mechanism was running, while preserving the mechanism.*

## 3. THE SOURCE CHAIN, LINK BY LINK

Read inside the image these runs actually used — `dafoam/opt-packages:latest`, id
`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`, the `IMG_SHIPPED`
registered at `cases/dafoam/curriculum_D12R2/d12y_stage_and_run.sh:89-91`. **The OpenFOAM read is
the CONTAINER's own `OpenFOAM-v2506`, not this host's `v2606`** — the host tree is not the tree
that ran, and checking the host would have been an inference.

| # | link | file:line (inside the image) |
|---|---|---|
| 1 | the solver drives its outer loop with `while (pimple.loop())`, `pimple` being `pimpleControlDF` | `repos/dafoam/src/adjoint/DASolver/DAPimpleFoam/DAPimpleFoam.C:174` |
| 2 | `loop()` calls `mesh_.data().setFinalIteration(true)`, **unguarded**, on the converged branch and on the `finalIter()` branch | `repos/dafoam/src/adjoint/DAMisc/pimpleControlDF/pimpleControlDF.C:238`, `:246` |
| 3a | `UEqn.relax()` inside that loop | `DASolver/DAPimpleFoam/UEqnPimple.H:18` |
| 3b | `nuTildaEqn.ref().relax()` — the primal branch, the one followed by `solveTurbState_` / `solve(nuTildaEqn)` | `DAModel/DATurbulenceModel/DASpalartAllmaras.C:460` |
| 3c | `TEqn.relax()` | `DASolver/DAPimpleFoam/TEqnPimple.H:17` |
| 3d | `p.relax()` | `DASolver/DAPimpleFoam/pEqnPimple.H:75` |
| 4 | `fvMatrix::relax()` resolves its key via `psi_.select(mesh.data().isFinalIteration())` | `OpenFOAM-v2506/src/finiteVolume/fvMatrices/fvMatrix/fvMatrix.C:1249-1258` |
| 5 | `GeometricField::select(bool final)` returns `this->name() + "Final"` | `OpenFOAM-v2506/.../GeometricField.C:1141` |
| 6 | **`GeometricField::relax()` appends `Final` too**, independently of `fvMatrix` | `OpenFOAM-v2506/.../GeometricField.C:1122` |
| 7 | `keyType::match` → `regExpCxx::match` → **`std::regex_match`** — FULL match | `OpenFOAM-v2506/.../keyType.C:66`; `.../regex/regExpCxxI.H:297` |
| 8 | `solution::relaxEquation()` falls through `found(name)` and `found("default")` and returns false — **silently** | `OpenFOAM-v2506/src/OpenFOAM/matrices/solution/solution.C:379-410` |

**Verdict on the mechanism: CONFIRMED.** This is a factual determination about solver behaviour.
It is not a gate verdict and no gate was registered for it.

## 4. THE EXPOSURE IS WIDER THAN L-426'S CASE — FOUR QUANTITIES, NOT THREE

Link 6 above is the extension. `GeometricField::relax()` appends `Final` on its own, so
`p.relax()` looks up **`pFinal`** against `relaxationFactors.fields { "(p|p_rgh|G)" 0.3; }` and
misses.

**In L-426's `chtMultiRegionFoam` case `p_rgh` ESCAPED**, because `solveFluid.H:39` had already
cleared the flag before `p_rgh.relax()` ran — L-426 records that only `U` and `h` were exposed
there. **Here `p.relax()` sits INSIDE the loop, so it does not escape.** So on the final outer
sweep of every timestep, in these runs:

> **`U`, `nuTilda`, `T`/`e`/`h` and `p` are all assembled with no relaxation contribution.**

One further correction to the reading that opened this investigation: **`setFinalIteration` is not
confined to a PIMPLE-class control even in stock OpenFOAM.** `chtMultiRegionFoam` sets it directly
at `applications/solvers/heatTransfer/chtMultiRegionFoam/fluid/solveFluid.H:5` and
`solid/solveSolid.H:24`. "Only a PIMPLE control can do this" is too strong and is struck here.

## 5. THE TERRITORY COUNT

Measured by `scan_final_key.py`, a read-only classifier that replicates the full-match semantics of
link 7. **It carries a two-sided planted control** — a synthetic bare dictionary it must classify
`AT_RISK` and the same file plus the `Final` keys it must classify `COVERED` — and **refuses to
report at all if either control fails**. Both passed on every run reported here. (L-426's own
closing warning is that a one-sided control is how the W3 fatal-token defect survived; a classifier
shown only to fire is not shown to be a classifier.)

A file is counted AT RISK when it carries a `PIMPLE` dict, has a non-empty
`relaxationFactors.equations` or `.fields`, and **no key in that sub-dict full-matches any `*Final`
name the solver will look up, and no `default` entry exists.**

| scope | `fvSolution` files | AT RISK |
|---|---|---|
| `cases/dafoam/` (the repository territory) | 165 | **0** — every one is SIMPLE-only, no PIMPLE dict |
| D12-family run trees, 8 roots under `/home/ubuntu/certonomous-runs/` | 246 | **165** |

Per run root: `CURRICULUM-D12` 23 · `D12R` 32 · `D12R2` 32 · `D12R2W2` 2 · `D12R2W2R` 32 ·
`D12R2W3` 12 · `D12R2W3_prior_fires` 1 · `CURRICULUM-PROBES-D10-D11-D12` 31. **Total 165.**

**All 165 are ONE md5: `95ab16a9141b0928bd352a9b9d8d93b9`**, byte-identical to
`/home/ubuntu/dafoam-tutorials/Cylinder/system/fvSolution`. For context beyond this territory:
**42 of 114** `fvSolution` files across the two local DAFoam tutorial mirrors carry the same
fingerprint.

**The repository is clean. The exposure lives entirely in staged run trees, and it arrived from
upstream.**

## 6. BLAST RADIUS — A PHYSICS EXPOSURE THAT DOES NOT MOVE A LANDED VERDICT

This is a **physics** change, not a bookkeeping one: momentum, turbulence and pressure running
unrelaxed on the final outer sweep of every timestep changes the discrete iteration. Bookkeeping
never voids physics and physics never gets waved through. It is assessed on measurement, not on the
comfort of the conclusion.

The binding number is `h_min = δ_eff / (0.01·|g|)` with `δ_eff = max(δ_repeat, δ_window, δ_pert)`.
From the landed `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady/step_plan.json`:

| term | value | note |
|---|---|---|
| `δ_window` | `1.7958478225974517e-03` | **dominant** |
| `δ_pert` | `2.279666841643725e-06` | 788× smaller |
| `δ_repeat` | `0.0` | measured |
| `|g|` (`g_component_0`) | `1.0304158599180422` | |
| `h_min` | `0.1742837908900481` | vs `h_max = 0.05`, `admissible: false` |

Three measured facts bound the exposure:

1. **`δ_repeat = 0.0`** — the solver is bit-deterministic at np=1, so the unrelaxed sweep injects
   **zero** run-to-run jitter.
2. **`δ_window` dominates by three orders**, and it is `block_max − block_min` of the CD series — a
   shedding-amplitude-and-window-mismatch quantity, not an outer-loop-path quantity. Re-derived
   here from the artefact through the frozen instrument's own `read_series` / `g3_delta_window`
   (`d12y_grade_w3.py`): 2,400 samples from `S2b_20260826T033053Z_3069758.log`, CD mean
   `0.6563231414421499`, p2p `0.1316244994972485`, `δ_window(300) = 0.0017958478225974517` —
   **reproducing the landed value exactly**.
3. **The direction is monotone.** Extra numerical noise raises `δ_eff`, which raises `h_min`, which
   pushes toward `NOT A RESULT`. This is the registration's own argument at
   `W3_PREREGISTRATION.md:76`: *"Adding a term to a maximum can only RAISE h_min: it can cause a
   NOT A RESULT and it cannot manufacture a PASS."*

**The landed verdicts in this family are all `NOT A RESULT`** — D12R2 `G12R-4` (`RESULTS.md:12-13`),
D12R phase 1 (closed), W3 (refused at `G12R-0b`). **None is falsely favourable, and no `PASS`
anywhere in this family rests on the defect.**

**What IS genuinely exposed**, stated as exposure and not as damage: the primal CD/CL values and
the gradient `|g|` were produced with four fields unrelaxed on the last sweep. The printed
per-timestep residuals **are** that sweep's — DAFoam sets `pimplePrintToScreen` only when
`pimple.finalIter() && printToScreen_` — and read `U0 initRes ≈ 1.15e-06`, not machine zero, so the
state does depend on the iteration path. `|g|` sits in `h_min`'s **denominator** and its direction
under repair is **not established**. The margin to flip `G12R-4` is 3.49×, which is large; large is
not measured.

## 7. THE FINDING THAT MATTERS MOST IS NOT A THREAT TO A VERDICT — IT RUNS THE OTHER WAY

This family's headline is *"no admissible FD step exists"*, and that has been written into
`docs/capability/dafoam_GRID.md` as a property of unsteady DAFoam gradients.

> **If the unrelaxed final sweep contributes materially to `δ_eff`, the honest claim is narrower —
> no admissible step WITH THE UPSTREAM TUTORIAL'S RELAXATION DICTIONARY — and the capability cell
> is UNDERSTATING the lab.**

On the measured evidence that is unlikely: the dominant term is the physical one. But it has never
been tested. **A `NOT A RESULT` that is an artefact of a missing dictionary key is a different
object from one that is a property of the method**, and the difference is worth one cheap run.

**`docs/capability/dafoam_GRID.md` is NOT touched by this record.** A capability claim corrected on
an inference is the same error that started this thread. The cell moves when the paired run
measures it, registered at `cases/dafoam/D12RLX_RELAXATION_PAIRED_PREREGISTRATION.md`, and not
before.

## 8. THE REPAIR'S DEBT, WHICH L-426 REQUIRES BE STATED — AND HERE IT IS MEASURABLY NIL AT THE GATE

L-426 records that the fix does not come free: in T25R the unrelaxed final sweep was *what made the
last-sweep initial residual a meaningful convergence measure*, so repairing it owed a replacement
measure.

**Checked here rather than assumed: no D12 gate reads a primal residual.** `d12y_grade_w3.py`
contains zero references to `initRes`, `finalRes` or `primalMaxRes` in any gate; the thirteen gates
`G12R-0`…`G12R-11` grade completion, stage binding, limit cycle, the three noise terms, step
sizing, plateau, adjoint-vs-FD, the trivial baseline, the checkpoint envelope, the planted zero, the
two rows and the optimisation. **So the T25R debt does not bite this family at the gate level.**

It is not zero everywhere, and that is stated rather than dropped: DAFoam's own internal
`daGlobalVarPtr_->primalMaxRes`, fed by `DAUtility::primalResidualControl`, **is** a final-sweep
quantity and its meaning does change under the repair. Nothing registered reads it. Anyone who
later registers a gate on it inherits the debt.

## 9. HONEST LIMITS

- **The chain is READ, not DRIVEN.** L-426's own closing rule is *"exercise each key, do not read
  it."* No key was exercised through the solver here. The chain is source-complete and the log
  signature corroborates it, but this is airtight-by-construction, **not** airtight-by-measurement,
  and the two are not blurred. Converting it is the paired run's second job.
- **The magnitude of the effect on CD and `|g|` is NOT established.** That needs the paired run.
- **Which of the two `setFinalIteration(true)` branches fires per timestep is not established** —
  only that one must, since `finalIter()` is reached unconditionally at `nOuterCorrectors = 10`.
- **`dafoam-idwarp-rot:v1` (the registered PATCHED row) was not opened.** Every source read was
  against `dafoam/opt-packages:latest`. The W3 patched row has never been queued.
- **Cost of this record: reading only.** Six short read-only container invocations plus filesystem
  scans, ≲2 core-minutes single-rank. That is a **wall-clock estimate, explicitly not ledgered**.
  No process completed, so no `COST_CALIBRATION.md` row is owed and none is manufactured.

## 10. ONE BOARD CORRECTION FOUND IN PASSING, AND IT IS THE REASSURING DIRECTION

`docs/LAB_STATE.md` records `d12y_grade_w3.py` md5 **`3b0a75079c932b41ec19477388498842`** as the
live value pinned by `d12y_w3_chain_driver.sh`, verified "on disk and identical from the HEAD blob".
**That value is now stale.** Measured 2026-09-01: the grader reads
**`3950d30fd09c9b56213a02f5e9864e20`** on disk **and** at HEAD, and the driver's pin at
`d12y_w3_chain_driver.sh:47` reads **`3950d30f…`** on disk **and** at HEAD.

**The pin and the comparator MATCH, so W3 remains launchable and the guard will not fire.**
`3b0a7507…` was the Amendment-2 blob (`af44d244`), superseded by Amendment 3 (`764bb0c8`), whose
commit subject records that the pin was bumped *"in the SAME commit as the comparator it pins"*.
**The board is stale, not wrong-at-the-time, and nothing is broken.** Recorded because a stale md5
on the board is exactly the shape that produces a false alarm on somebody's next check — this lane
began writing one before completing the comparison.

---

**Disposition.** Filed as a dafoam findings record. `docs/capability/dafoam_GRID.md` untouched. No
frozen file edited, no `fvSolution` deleted, moved or rewritten, no solve run, nothing sent.
