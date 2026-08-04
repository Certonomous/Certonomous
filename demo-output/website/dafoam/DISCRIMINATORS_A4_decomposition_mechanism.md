# The three discriminators, run: A4's decomposition-dependent adjoint is a wrong parallel operator, converged exactly

**2026-08-04, well W4. Docket item `w4-three-discriminators-for-the-decomposition-dependent-adjoint`.**
Executes the three discriminating experiments of
`LIAISON_RESEARCH_adjoint_conditioning.md` Target 2, cheapest first, on the case that
proved the phenomenon (`PROOF.md` §25.5, verified by
`VERIFICATION_A4_decomposition_supervisor_sweep.md`). All runs patched IDWarp (the
configuration of the verified np=4 cells), stock DAFoam v5 container
`dafoam/opt-packages:latest`, A4 coarse case (2,777 cells, kOmegaSST, one shape DV),
`IDWARP_IMPORTED_FROM` stamped in every log. Run artifacts:
`/home/ubuntu/certonomous-runs/W4-a4-discriminators/` (per-arm dirs, logs, `ledger.txt`,
`runScript_w4.py`, `build_maps.py`, `analyze_mats.py`).

**Verdict up front — the mechanism is NAMED, at subsystem level.** The defect is in
DAFoam v5's **parallel reverse-mode AD transposed-Jacobian-vector product** — the
operator of the matrix-free adjoint itself (`dRdWTMatVecMultFunction` via the global
CoDiPack tape, and equally the `calcJacTVecProduct` API path). Under the `scotch`
decomposition at np=4 that operator is **not the transpose Jacobian of the discrete
residual it claims to differentiate**: applied to the converged scotch adjoint vector,
the true (serially-evaluated) system residual is **329x ||b||**, concentrated to
**U-momentum rows of partition-interface cells** (largest single entry 42.2). GMRES
meanwhile converges the *wrong operator's* system cleanly (true-residual norm of its
own operator, rtol 1e-6, `PetscConvergedReason: 2`) — which is exactly why tolerance
tightening never moved the answer: **the solve is exact; the operator is wrong.**
Every other candidate in the memo is closed below: the primal (M3a), the RHS
`dCD/dW`, the mesh-derivative chain (M3b), the linear tolerance and the
state-reconvergence confound are exonerated by measurement; the
coloring/preconditioner (M2) is exonerated by architecture plus M1, its named
coloring-off run recorded as unrunnable in v5 with two measured failure modes.

**The proposal's pre-registered prediction — "the cross residual will be large" —
HELD.** Measured 3.288e+02 as a ratio to ||b||, against the serial operator's own
floor of 1.14e-04.

---

## M3(a) — bitwise primal compare: exonerated, from existing logs, zero cost

From the verified sweep's own logs (`W4-a4-stepsweep/`), full printed precision:

| arm | baseline CD |
|---|---|
| np=1 (`a4_np1_patched.log`, identical in `a4_np1_stock.log`) | 0.15297237 |
| np=4 scotch (`a4_np4_patched.log`) | 0.15297182 |
| np=4 simple 4x1x1 (`a4_np4_simple4x1x1.log`) | 0.15296979 |

np=1 vs np=4 scotch differ by 5.5e-07 absolute = **3.6e-06 relative** — separately
reconverged SIMPLE solves at `primalMinResTol 1e-4`, so this is reconvergence noise,
not bitwise equality (bitwise is unattainable across decompositions by summation-order
alone). It is **four orders of magnitude below the 8.95% analytic-gradient shift**, and
the simple arm (correct gradient) actually differs *more* from np=1 than scotch does.
The primal-side integration is not the carrier. Confirmed again by this session's own
arms: baseline CD 0.1529738/0.1529749/0.1529732 (np1/scotch/simple), and mapped
primal *state vectors* agree across decompositions at 2.0e-03/2.8e-03 relative — with
the **duplicated processor-face phi copies agreeing to 2.7e-15** (machine precision),
which also validates the state maps used below.

## M3(b) — dObj/dXv across decompositions: differs, so the defect is upstream of the warp chain

The `a4_dcddxv` capture hook (real reverse seed on `DAFoamWarper`) was run at all
three decompositions, with the warp-FD directional derivative `dXv/dshape` computed
identically in each arm (`w4_dump` task):

| arm | AN = <dCD/dXv, dXv/dshape> | framework `compute_totals` | AN vs framework |
|---|---|---|---|
| np=1 | 2.414994844096177e-01 | 2.414994857859927e-01 | 5.7e-09 |
| np=4 scotch | 2.208588587555006e-01 | 2.208588593817390e-01 | 2.8e-09 |
| np=4 simple 4x1x1 | 2.422030559126777e-01 | 2.422030573188107e-01 | 5.8e-09 |

The hand composition equals the framework total to 6e-09 in **every** arm — the
warp/DVGeo leg composes exactly at np=4 too. The warp direction itself is
decomposition-invariant: `dXv/dshape` mapped point-by-point (`pointProcAddressing`)
matches np=1 to **0.0e+00** in both np=4 arms. What differs is the captured
**dCD/dXv seed itself**: mapped to np=1 point ordering (copies summed), scotch differs
from np=1 by **38.4%** in norm, simple by 3.1%. Per the memo: *"dObj/dXv already
differing puts it back inside DAFoam's adjoint/partials."* The IDWarp/DVGeo leg is
exonerated; dCD/dXv is wrong because the psi it contracts is wrong.

## M1 — the cross-residual: LARGE, as predicted, and it convicts the operator

Setup: each arm's converged adjoint psi was dumped, mapped to np=1 global state
ordering by an **exact integer map** built from `cellProcAddressing` /
`faceProcAddressing` (sign carried for flipped faces) plus DAFoam's own
`AdjointIndexing` dumps (`writeJacobians: ["adjointIndexing"]`) — no coordinate
matching. Map validated on the primal states (duplicated-phi copies 2.7e-15). Then
the **true residual ||A^T psi + b|| was evaluated under the np=1 (serial) AD
operator** via `calcJacTVecProduct`, the sign convention (OpenMDAO seeds -dF/dW)
fixed by the np=1 control. `d_crossres.log`:

| psi from | ||A^T psi + b|| under np=1 operator | ratio to ||b||=0.1826 | ||psi|| |
|---|---|---|---|
| np=1 (control) | 2.083e-05 | **1.14e-04** | 3.277e-02 |
| np=4 **scotch** | 6.004e+01 | **3.288e+02** | 5.411e-01 |
| np=4 simple 4x1x1 | 1.711e-02 | 9.37e-02 | 1.814e-02 |

Three decisive facts:

1. **The scotch psi does not remotely satisfy the serial system** — 329x ||b||,
   3.3 million times the np=1 floor — while it satisfies its own scotch-evaluated
   operator (same instrument, same API, np=4) at 1.2e-03 relative, and the KSP that
   produced it reports final true-residual 1.7e-07 (719 iterations, reason 2,
   `d_np4scotch.log`). Same vector, two operators, answers five orders apart:
   **the operators differ.**
2. **The RHS is not the carrier**: b = dCD/dW mapped across decompositions is
   invariant to **4.8e-06** (scotch) and 6.9e-06 (simple) relative.
3. **||psi|| itself is inflated 16.5x under scotch** (0.541 vs 0.033 np=1 /
   0.018 simple) at identical ||b|| — the extra content lives in the pressure
   (0.52 vs 0.031) and z-momentum (0.117 vs 0.005) adjoint blocks.

**Confounds closed.** (a) Linearization state: the cross-residual was re-evaluated
with the np=1 operator linearized **at the scotch arm's own mapped state**
(`w4_crossres2` task): scotch reads **6.004094e+01 — unchanged to six digits** —
while the np=1 control degrades only to 1.0e-03. The 2e-03 state reconvergence
difference contributes at the 1e-03 level, five orders below the signal; simple's
state differs *more* than scotch's (2.8e-03 vs 2.0e-03) and its residual is 3,500x
smaller. (b) Duplicated-phi averaging in the psi map: replacing the average by either
copy moves the residual by at most **9.1e-03** — four orders below the signal.

**Localization.** By state group, 59.78 of the 60.04 norm sits in **U0 (x-momentum)
rows**; by cell, entries with |r| > 0.5 number 15, of which **13 sit on scotch
partition-interface cells and 2 at distance one** (0 farther); all 15 are
`cellLevel` 0 cells, away from the refinement interfaces — consistent with the
already-refuted hanging-node hypothesis. The worst cells (|r| = 42.2) each touch
exactly **one** foreign rank through exactly **one** processor face, and cells
touching 2-4 foreign faces carry *smaller* residuals — so neither rank-corners nor
cut jaggedness per se is the trigger; what distinguishes the bad cuts is orientation
and shape, consistent with the verified table's own hierarchy (y-normal `simple`
1x4x1 cuts: 0.47%; x-normal 4x1x1 cuts: 0.00054%; scotch's mixed jagged cuts:
8.95%) — the worst offenders here sit at y = +/-0.195, i.e. y-normal processor
faces. The same instrument applied to simple 4x1x1 maxes out at **0.0084** on its
own interface cells — 5,000x smaller than scotch's worst.

## M2 — coloring and preconditioner: exonerated, plus one upstream usability finding

**The permuted matrix diff cannot convict anything, and the record shows why.** Both
`dRdWTPC` and the full assembled `dRdWT` (both built by the coloring-FD partials
machinery, `calcdRdWT`) were dumped in all three arms and permuted to np=1 ordering
on the 1-1 subspace (`analyze_mats.py`). The diffs do **not** correlate with the
defect: full-dRdWT Frobenius diff 4.8e-02 (scotch) vs **5.4e-02 (simple — the
FD-exact arm!)**, PC diff 3.7e-04 (scotch) vs 3.7e-03 (simple). The assembled
matrices differ across decompositions mainly through the reconverged linearization
state and their own FD assembly error — at np=1 the assembled dRdWT applied to psi
already disagrees with the AD product by 230x ||b|| (the assembled matrix is a crude
FD object; only the PC is built from it, which is why the KSP operator is
matrix-free). A matrix diff at each arm's own state is the wrong instrument here; the
AD-product cross-residual above is the right one, and the memo's gate condition
("counts only after both dumps are permuted to the same global cell ordering") was
met before drawing this negative.

**Coloring-off run (the memo's last, most expensive discriminator).** First finding,
recorded because upstream users will hit it: **`adjUseColoring: False` crashes the v5
Krylov path by construction** — `mphys_dafoam.solve_linear` skips `runColoring()`
when the option is False, but `calcdRdWT` unconditionally calls
`readJacConColoring()`, which reads a file that was never written and dies in
`DAColoring::validateColoring` (`DAColoring.C:1021`; log
`d_np4scotch_nocolor.log`, first attempt). The identity-coloring branch (one color
per global column) is reachable only through `runColoring()`, so the arm was rerun
with an explicit `runColoring()` call before `compute_totals`
(`w4_totals_forcecolor` task): identity coloring accepted, `nJacConColors: 26149`,
PC partials computed by pure per-column FD with no color compression. **Second
finding: the forced path is memory-unbounded and could not be brought to
completion on this 2,777-cell case.** The first forced attempt thrashed at the
case's predicted 8 GiB envelope (all ranks in D state at ~10% CPU while the
colored path peaks under 2 GiB) and was killed at 701 s; a second attempt at a
20 GiB cap completed all 26,149 column evaluations (258 s, memory growing
roughly linearly through assembly) and then blew through 20 GiB in the
post-assembly stage — consistent with the per-column FD columns being nearly
dense (the FD response of the elliptically-coupled residual is global, so
without the coloring's connectivity restriction the "PC" densifies) — and was
killed thrashing at 591 s. **Recorded outcome of the coloring-off discriminator:
unrunnable in v5** — it crashes by construction as shipped, and when forced it
exhausts 2.5x the case's memory envelope before producing a gradient. The
pre-registered prediction for this arm ("the gradient will not move, because
coloring builds only the PC") is therefore **NOT SCORED** — the discriminator
could not deliver its number. The coloring exoneration does not rest on it: the
coloring machinery touches only the preconditioner in the Jacobian-free path, a
preconditioner cannot move a right-preconditioned GMRES solution converged in
the **unpreconditioned** norm (`DALinearEqn.C:170,313`), the scotch KSP did so
converge (true-residual 1.7e-07, reason 2), and M1 convicts the matrix-free
operator that coloring never enters.

## What the mechanism is, and what it is not

**Named:** under decomposition, DAFoam v5's reverse-mode AD product
`(dR/dW)^T v` — the global-tape shell operator the adjoint KSP iterates
(`initializeGlobalADTape4dRdWT` / `dRdWTMatVecMultFunction`, `DASolver.C:1364ff`)
and the `calcJacTVecProduct` API that reverses the same recorded computation —
differs from the true transposed Jacobian of the discrete residual at
partition-interface cells, by amounts that depend on the cut's shape and
orientation: negligible for x-normal planar slabs, 0.47%-of-gradient scale for
y-normal slabs, catastrophic (8.95%) for scotch's jagged mixed-orientation
boundary on this mesh. The two parallel AD paths sit *together* on the wrong side:
they agree with each other to 1.2e-03 of ||b|| (KSP final residual 1.7e-07 on its
shell operator; the `calcJacTVecProduct` instrument reads the same psi at 1.2e-03
relative) while both sit 3.3e+02 of ||b|| from the serially evaluated truth — the
defect is common to the recorded reverse computation, not to one call site. The GMRES then
solves the wrong system exactly, the adjoint inherits O(1) error along directions
the wrong operator mislabels (psi norm 16.5x), and the gradient contraction
`psi^T dR/dXv` delivers the 8.95%. Every published symptom follows: converged wrong
answer (true residual of the wrong operator IS small), tolerance-invariance,
decomposition-dependence, primal/FD/RHS invariance, and A1/A2/A5's near-invariance
(conformal meshes, different cut geometry, smaller boundary coupling error).

**Not claimed:** the defective source line. The candidate surface is the reverse-AD
handling of inter-processor halo exchange inside the recorded residual evaluation
(CoDiPack tape over OpenFOAM processor-boundary updates); pinning the line needs an
instrumented rebuild of `libDASolver.so`, which is a docket proposal, not a casual
edit. What IS pinned: the subsystem, the spatial signature (interface-cell
U-momentum rows), the orientation dependence, and the discriminating instrument
(the cross-residual protocol) that any candidate fix must satisfy.

## Scored predictions

- Proposal, pre-registered: *"the cross residual will be large."* **HELD** (3.3e+02
  vs a 1.1e-04 floor).
- This session, pre-registered before the coloring-off run: *"coloring-off will not
  change the gradient, because coloring builds only the PC."* **NOT SCORED** — the
  discriminator proved unrunnable (crash by construction; then memory-unbounded when
  forced), so the prediction never met its measurement.

## Cost ledger (all runs, `--cpus` cap x wall, per `ledger.txt`)

| run | task | wall | core-min |
|---|---|---|---|
| d_np1 | w4_dump (primal+adjoint+dumps) | 95 s | 3.17 |
| d_np4scotch | w4_dump | 141 s | 4.70 |
| d_np4simple | w4_dump | 133 s | 4.43 |
| d_crossres | w4_crossres (np=1) | 10 s | 0.33 |
| d_crossres2 | w4_crossres2 (state-controlled) | 10 s | 0.17 |
| d_np4scotch_nocolor (crash by construction, finding recorded) | w4_totals | 27 s | 0.90 |
| d_np4scotch_nocolor (forced, killed thrashing at 8 GiB cap) | w4_totals_forcecolor | 701 s | 23.37 |
| d_np4scotch_nocolor (forced, killed thrashing at 20 GiB cap) | w4_totals_forcecolor | 591 s | 19.70 |
| **total** | | | **56.77 of 45 budgeted** |

**The overrun is 11.77 core-min, 26%, and it is confined entirely to the
coloring-off discriminator** the docket names as the last arm: 43.97 of the 56.77
went into three attempts at it, all three ending in a measured failure mode rather
than a number (and the wall-times-cap ledger convention overstates their true CPU,
which sat at 10-60% while thrashing). In hindsight the second forced attempt
should not have been launched after the first showed unbounded memory growth
rather than a slow finish; it is ledgered, not hidden. The five arms that decided
the item cost 12.63 core-min.

M3(a), the maps, the cross-residual analysis, the matrix diffs and the localization
were arithmetic on logs and dumped operators at zero solver cost, as the cost basis
predicted; what the cost basis mispriced was the coloring-off arm, whose v5
implementation turned out not to run at all.

## Gate check (docket item gate, clause by clause)

- *"one mechanism is named, with the discriminator that convicted it and its logs
  cited"* — named above; convicted by M1 (`d_crossres.log`, `d_crossres2.log`,
  `d_np1.log`, `d_np4scotch.log`, `d_np4simple.log`); M2 and M3 outcomes recorded
  with logs besides.
- *"a matrix diff counts only after both dumps are permuted to the same global cell
  ordering"* — done (`build_maps.py`, validated at 2.7e-15; `analyze_mats.py`), and
  its outcome is the recorded negative above.
- *"a cross residual is judged against the serial operator's own scale"* — judged
  against ||b|| = 0.1826 and the serial arm's own floor 1.14e-04.
- *"nothing is claimed about any gradient without the finite difference column
  beside it"* — no new gradient value is claimed here; every gradient number quoted
  (8.95%, 0.00054%, 1.10%, 0.34%, 0.47%) carries its FD column in the verified
  table this record builds on (`VERIFICATION_A4_decomposition_supervisor_sweep.md`).

Follow-ups filed: upstream report drafted, NOT filed
(`UPSTREAM_BUG_REPORT_decomposition_adjoint.md` — filing is Katie's call);
LESSONS **L-35**.
