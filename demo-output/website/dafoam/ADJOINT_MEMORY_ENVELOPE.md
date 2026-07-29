# DAFoam adjoint memory envelope (D3)

Date: 2026-07-29 (UTC). Directive D3: exhaust the DAFoam adjoint memory envelope,
measured, before anyone spends money on bigger hardware. This is a live document,
updated as measurements land — see the STATUS line per section for what is done
vs still running.

**This session was interrupted multiple times** (harness resume, not a host
reboot — `uptime -s` was unchanged across the interruptions). Every number below
was re-verified against the actual log/registry files on disk before being
written here, per the resume instruction; nothing is carried over from memory
alone.

## The measured wall going in (established before this session, restated for context)

Adjoint runs succeed at 4,032 and 63,920 cells; fail at 156,089 (dies mid
Jacobian-coloring), and at 99,840 / 399,360 (OOM at both 12 GB and 18 GB
container caps). Eight mitigations already ruled out on the 399,360-cell case:
12g/18g caps, 4-rank/2-rank decomposition, gmresRestart 1000→200, pcFillLevel
1→0. Structural cause (established, not re-derived here): OpenMDAO's
reverse-mode sweep for any requested total derivative builds a mesh-sized
`d[residuals]/d[vol_coords]` Jacobian block regardless of the requested `wrt=`.

**New factor folded into the analysis below**: DAFoam rejects OpenFOAM `empty`
patches outright — `"Mesh geometric directions is less than 3 and not
supported"`, `DACheckGeometry.C:278` (reproduced directly in this project,
`ladder-b/B3_work/fixA_kbounds/stage2_serial_run3.log:471`). Every nominally-2D
DAFoam case is therefore a true 3D solve, and **both** Jacobian blocks (dR/dW
and dR/dXv) are sized for the 3D mesh regardless of the physics being 2D. This
means the bytes-per-cell constant below is a *3D* constant even for cases whose
geometry looks 2D (single-cell-thick extrusion) — there is no cheaper 2D
adjoint path in this installation.

---

## Option 1 — matrix-free / Jacobian-free adjoint (`adjUseColoring=False`)

**Predicted effect** (source-confirmed before running anything): `DAJacCon.C`
(`/home/dafoamuser/dafoam/repos/dafoam/src/adjoint/DAJacCon/DAJacCon.C`,
~line 1946) shows `adjUseColoring=False` replaces graph-coloring (which grouped
this A1 case's Jacobian into **375 colors**) with a brute-force fallback that
assigns **one unique color per matrix row** (`jacConColorsArray[relIdx] = i`).
Predicted: memory drops (no coloring-graph storage) but the number of residual
evaluations needed to build the Jacobian rises by roughly (state DOFs) /
(375 colors) — for this ~4,032-cell case, state DOFs ≈ 20,000, so **≈53x more
residual evaluations**, growing with mesh size since colors compress a graph
whose connectivity stays local while DOF count grows.

**Measured, on the smallest known-working case (A1 NACA0012, 4,032 cells, 2
ranks, `runScript_nocoloring.py` = baseline `runScript.py` +
`"adjUseColoring": False`)**:

| attempt | cache state | wall | peak RSS | outcome |
|---|---|---|---|---|
| v1 | stale `dRdWColoring_2.bin` from an earlier session present at launch | 302 s (300 s time-box) | 1,188.9 MiB | **inconclusive** — log shows `Reading Coloring dRdWColoring_2` / `dRdWColoring_2.bin exists.`, i.e. it read the cached 375-color file and never exercised the brute-force path. Discarded as contaminated. |
| v2 (cache deleted first) | no cache file | 15 s | 1,137.7 MiB | **crash**, `exit=1` |
| v3 (cache deleted first, re-verified absent, no time-box) | no cache file | 15 s | 1,130.5 MiB | **crash, reproduced identically**, `exit=1` |

v2 and v3 both crash at the identical point, inside the preconditioner-matrix
(`dRdWTPC`) coloring-validation step, **before the adjoint GMRES solve is ever
reached**:
```
Reading Coloring dRdWColoring_2
Validating Coloring...
--> FOAM FATAL ERROR: (openfoam-2506)
 row: 0 col1: 0 col2: 1 color: 0
 row: 18239 col1: 0 col2: 1 color: 0
    From Conflicting Colors Found!
    in file DAColoring/DAColoring.C at line 1021.
```
Full-file search of both crash logs found **no** `"Calculating dRdW Coloring"` /
`"Checking if Coloring file exists"` line preceding this — the `dRdWTPC`
(preconditioner) coloring path calls `daJacCon.readJacConColoring()`
unconditionally (`DASolver.C:1043`), not gated by `adjUseColoring` and not
preceded by an existence check the way the main `dRdW` coloring is
(`DASolver.C:718-737`). With no valid cached coloring file, it is either
reading nothing (uninitialized/zeroed data, matching "every row got color 0")
or reading a stale file this run's cleanup should have prevented; either way
the result is a crash, not a slow-but-correct answer, and it is 100%
reproducible (2/2 clean attempts).

**Verdict: RULED OUT — for a stronger reason than "too slow."**
`adjUseColoring=False` does not just trade memory for runtime as the brief
anticipated; on this installation it fails outright in preconditioner setup
whenever no pre-existing valid coloring cache is on disk. Since the OOM cases
(99,840 / 399,360 cells) never successfully complete a coloring pass in the
first place, they can never produce that cache — so this option cannot rescue
them even in principle. **Do not retry this option on a case that has never
had a successful coloring run.**

---

## Option 2 — reduced ILU fill / alternative preconditioner families

**Preconditioner family, source-checked (no run needed to answer this part):**
`DALinearEqn.C`
(`/home/dafoamuser/dafoam/repos/dafoam/src/adjoint/DALinearEqn/DALinearEqn.C`,
lines 185-267) hardcodes the PC stack: global PC = `PCASM`
(`PCASMSetOverlap`, tunable via `adjEqnOption.asmOverlap`), local/sub-domain PC
= `PCILU` (tunable via `adjEqnOption.pcFillLevel`, already ruled out 1→0 in the
prior session). **There is no user-facing switch to Jacobi or block-Jacobi** —
the PC type is compiled in, not exposed through `daOptions`. This closes that
half of Option 2 definitively: alternative PC families are not available
without patching and recompiling `libDASolver.so`, which is out of scope.

**New, previously-untried levers found in `pyDAFoam.py`** (distinct from
`pcFillLevel`, which was already ruled out): `maxResConLv4JacPCMat` (per-field
connectivity level for the *reduced* `dRdWTPC` preconditioner matrix, default
2) and `jacLowerBounds` (sparsification threshold below which a Jacobian entry
is dropped to exactly 0, default `1e-30` — i.e. effectively off). **Predicted
effect**: lowering connectivity to 1 and raising the threshold should shrink
the PC matrix's stored nonzero count directly, at the cost of a weaker
preconditioner (more GMRES iterations, possible convergence risk).

**Measured — A1 NACA0012, 4,032 cells (clean control, coloring cache intact,
no other change):**

| variant | peak RSS | wall | GMRES iters (CD, CL) | `PetscConvergedReason` | CD / CL |
|---|---|---|---|---|---|
| baseline (`pcFillLevel=1`, default connectivity) | 2,185.2 MiB | 31 s | 164, 165 | 2 (converged) | 0.0209105 / 0.4987653 |
| `maxResConLv4JacPCMat=1` + `jacLowerBounds` raised (1e-12/1e-10) | **1,538.0 MiB (−29.6%)** | 47 s (1.5x) | 422, 435 | 2 (converged) | 0.0209105 / 0.4987653 (bit-identical) |

**Result: a genuine, previously-untried, working memory reduction** — ~30%
peak-RSS cut, correctness preserved (identical CD/CL, GMRES still converges
cleanly), at a real but modest 1.5x runtime cost. This is the first option in
this whole study that reduces memory *without* breaking anything.

**Measured — A3 ONERA M6 coarse mesh, 99,840 cells (the case that already OOM'd
at 8 GB in the prior session), same sparsify levers stacked on the
already-tried `pcFillLevel=0`, generous 20 GB cap to find the true peak:**

| variant | cap | peak RSS | wall | `PetscConvergedReason` (CD, CL) | verdict |
|---|---|---|---|---|---|
| sparsify + `pcFillLevel=0` (prior session's setting) | 20g | 18,421.8 MiB | 524 s | **−5, −5 (DIVERGED_BREAKDOWN, both)** | completes without OOM, but the "answer" is garbage |
| sparsify + `pcFillLevel=1` (reverted to default) | 20g | ≥20,480.0 MiB (**censored at the cap**) | 403 s | **−5, −5 (DIVERGED_BREAKDOWN, both)** | still breaks down; also needs ≥ the full 20 GB |

Both runs print `Residual tolerance satisfied, solution finished!` and produce
a full derivative dictionary — **this is exactly the false-success pattern the
prior A3 session already caught once** (attempt #6, `pcFillLevel=0`): the
script's own success message does not mean the linear solve actually
converged. Neither of these derivative tables should be trusted.

**Verdict, precisely stated because it is easy to overstate:** the sparsify
levers *do* measurably shrink the memory footprint (99,840-cell peak came in
under a 20 GB cap where the prior session's 8 GB cap OOM'd — a real, disclosed
memory result) but they did **not** fix — and did not appear to cause —
`DIVERGED_BREAKDOWN`; that failure reproduces with fill=0 *and* fill=1, so it
is not the fill level. **Memory and convergence are two separate blockers on
this case; solving one does not solve the other.** No working (converged)
adjoint gradient has been obtained at 99,840 cells by any combination tried so
far, in this session or the prior one.

---

## Option 3 — more ranks (8, 16)

**STATUS: not yet run this session.** Predicted effect: per-rank peak RSS
should drop roughly in proportion to rank count for the domain-decomposed
state/Jacobian data, but fixed per-rank overhead (MPI, PETSc, OpenFOAM
runtime, Python/OpenMDAO) does not shrink and may even grow slightly with
inter-rank communication buffers — so there is a rank count past which adding
more ranks stops helping and may hurt. Queued next.

## Option 4 — coarse-adjoint-mesh boundary

**STATUS: not yet run this session.** Known so far from the existing
cross-rung table: adjoint **succeeds** at 63,920 cells (naca0015_sail_coarse,
FD-verified PASS) and **fails** at 99,840 (A3 coarse — OOM at 8g, and per
Option 2 above, breaks down even with more memory) and at 156,089
(naca0015_sail_medium — dies mid-coloring). **The working/failing boundary is
therefore narrower than the previously-stated "10³–10⁴ cells": it sits
somewhere between 63,920 and 99,840 cells**, not at 10⁴. Pinning it more
precisely (e.g. an ~80,000-cell probe) is queued next, along with rechecking
whether A4's fine mesh (45,760 cells, primal-only so far) can produce a
working adjoint directly, without coarsening to A4's already-proven 2,777.

## Option 5 — the scaling-law study (bytes per cell)

**STATUS: partial.** These are **real, individually-measured points**, but
they are **not yet a controlled single-geometry sweep** — each point below is
a different pre-existing case (different solver, field count, rank count,
number of design variables), so a single global bytes/cell constant fit across
all of them would overstate precision. They are reported as an honest
cross-case envelope; the controlled same-geometry sweep (4k/10k/25k/50k/64k on
one mesh family) is still queued.

| case | cells | solver | ranks | peak RSS (compute_totals) | note |
|---|---|---|---|---|---|
| A1 NACA0012 | 4,032 | DASimpleFoam (incompressible, SA) | 2 | 2,185.2 MiB | clean, uncensored |
| A5 U-Bend | 4,800 | DASimpleFoam (incompressible, SA) | 4 | 2,664.4 MiB | clean, uncensored |
| naca0015_sail_coarse | 63,920 | DASimpleFoam (incompressible, SA) | 3 | ≥10,240 MiB | **censored** at the 10g test cap; true peak is higher, not yet re-measured uncapped |
| A3 ONERA M6 coarse (sparsify levers) | 99,840 | DARhoSimpleCFoam (compressible, transonic, SA) | 4 | 18,422–≥20,480 MiB | different solver family (6 fields incl. T vs 4-5), not directly comparable to the incompressible points; also the GMRES diverged (see Option 2), so this is a memory-only data point |

Rough same-family (incompressible SA, `DASimpleFoam`) read: 4,032 cells →
2,185 MiB and 4,800 cells → 2,664 MiB are close in per-cell terms (~0.54–0.56
MiB/cell) but a 2-point line between them gives a *negative* intercept, which
is nonphysical — meaning these two alone are not a clean pair either (A5 has
double the ranks and a different DV count, both of which shift the constant
term). **A real bytes-per-cell constant needs the controlled sweep**, not
cross-case comparison. What the heterogeneous points already prove
unambiguously: peak RSS crosses from the 2-3 GiB range at ~4-5k cells to well
into the double-digit-GiB range by 99,840 cells (compressible) — consistent
with, not contradicting, the previously-established 12g/18g OOM wall for
399,360 cells.

**Queued next**: generate 3-4 more points on ONE mesh family (reuse the A1
NACA0012 geometry/pyHyp recipe at different extrusion/refinement settings, or
equivalent) spanning ~10k-64k cells, all at the same rank count and DV set, to
fit an honest linear (or better) model and a defensible predicted ceiling.

---

## Provisional hardware read (NOT a recommendation — options 1-5 are not yet
exhausted, this is a placeholder pending the full sweep)

The 99,840-cell transonic case alone needs ≥18.4-20.5 GB peak RSS even with
every memory-reduction lever tried so far, and the underlying gradient is
still not usable at that size (`DIVERGED_BREAKDOWN`). 399,360 cells has never
completed under 18 GB. **Nothing here is provisioned or proposed to the docket
yet** — that step only happens after ranks (Option 3) and the coarse-mesh
boundary (Option 4) are measured, per the directive's ordering.

## What is still open, explicitly

- Option 3 (8/16 ranks): not started this session.
- Option 4 (pin the exact working/failing mesh-size boundary between 63,920
  and 99,840; check A4's 45,760-cell mesh directly): not started this session.
- Option 5: needs a controlled same-geometry sweep, not just the cross-case
  envelope above.
- naca0015_sail_coarse's true (uncensored) peak RSS at 63,920 cells: the one
  clean run hit exactly its 10g test cap (10,240.0 MiB), which is itself
  suspicious as a coincidence and should be re-measured at a materially higher
  cap.
- Hardware recommendation: withheld until the above land, per the directive.

## Raw logs (this session)

All under `/tmp/claude-1000/-home-ubuntu-Certonomous/982d6244-5800-47f3-a450-80ce0b0a24b7/scratchpad/logs/`
(scratchpad, not committed — paths recorded here for traceability):
`A1_baseline_4032.log`, `A5_4800.log`, `sail_coarse_63920.log`,
`A1_nocoloring_4032{,_v2,_v3}.log`, `A1_sparsify_4032.log`,
`A3coarse_sparsify_99840.log`, `A3coarse_sparsify_fill1_99840.log`. Solve
registry completion records (survive session interruptions):
`demo-output/website/solve_registry/d3_*`.
