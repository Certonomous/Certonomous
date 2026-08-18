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

## Headline finding (this session's Option 4/5 sweep): a WINDOW, not a ceiling — and it is per-family, not per-cell-count

Every finding below this line was produced, and independently re-verified
against raw solver logs (not summary artifacts), in this session. The
central claim of every earlier version of this document — "the adjoint works
below some cell count and fails above it" — **is wrong as stated**. It was an
artifact of never having tested a small mesh in the ONERA-M6/compressible
family. The corrected picture:

**Three distinct failure modes exist, and they are not the same kind of
thing:**

| edge | failure mode | example | binds because |
| --- | --- | --- | --- |
| too coarse | **primal never converges** — nothing to differentiate around | ONERA M6, 10,920 cells: 1000 SIMPLE iterations, residuals plateau at 1e-3–1e-5 vs 1e-6 tolerance | a **physics-resolution** limit — property of the case/Re, not of the adjoint machinery (see caveat below) |
| usable | primal converges, adjoint `PetscConvergedReason` is positive | sail-family, 4,032–63,920 cells | — |
| too fine (memory) | primal converges, adjoint runs, but exceeds available RAM | ONERA M6, 399,360 cells (established pre-session); extrapolated further above | a **solver/hardware** limit |
| too fine (conditioning) | primal converges, adjoint GMRES `PetscConvergedReason: -5` (`DIVERGED_BREAKDOWN`), regardless of memory headroom | **every ONERA-M6-family point tested this session: 21,840 / 42,120 / 79,560 / 99,840 cells** | a **solver/physics-regime** limit, and it binds before memory does |

**The ONERA-M6 (compressible, transonic, shock-containing, `DARhoSimpleCFoam`,
6 transported fields incl. T) family has never, at any tested size from
21,840 to 399,360 cells — a 18x range — produced a converged adjoint.** Every
attempt either OOMs or returns `PetscConvergedReason: -5`. The earlier "works
below ~80,000 cells" read was never tested at a small M6 mesh; the first time
it was (this session, 21,840 cells), it broke down identically to the
99,840-cell case that had been assumed to define the wall. **Coarsening this
case's mesh as an escape route is closed, not merely unpromising**: a mesh
4.6x smaller than the previously-assumed threshold still diverges.

**The sail/NACA (incompressible, `DASimpleFoam`, 4-5 fields) family behaves
differently and has a real, demonstrated window**: converges cleanly at
4,032 (A1), 63,920 (naca0015_sail_coarse) cells (independently re-verified,
see Option 4), and reportedly at 4,800 (A5) cells; fails by a **different**
mechanism — the Jacobian-coloring pass stalls and never completes, not a
GMRES breakdown — at 156,089 (naca0015_sail_medium) and 337,334
(naca4412_wing_coarse) cells. So this family's window is real and
demonstrated, roughly 4k–64k cells confirmed working, the far edge sitting
somewhere between 64k and 156k.

**Why this probably tracks the physics, not an accident of these two
geometries**: A6 CRM wingbody (579,072 cells, primal-only, never adjoint-
attempted) uses the **same solver**, `DARhoSimpleCFoam`, at the **same flow
regime** — Mach 0.85, transonic, shock-containing — as A3 ONERA M6. It was
never adjoint-tested, so this is an inference from shared solver family and
physics, not a measurement, and is stated as such: **A6 CRM should be
expected to hit the same conditioning wall as A3, not assumed to be
memory-limited only, before anyone launches its adjoint.**

**Connection to the docket.** Proposal `r4-coarse-adjoint-prolongation`
(docket, proposed 2026-07-29) asks whether a gradient computed on a
deliberately *coarsened* adjoint mesh, prolongated onto a fine primal mesh,
can sidestep the memory/breakdown walls the way A4 Ahmed already does
informally (2,777-cell adjoint driving a 45,760-cell primal comparison).
This session's coarse-end finding puts a **floor** under that strategy: for
the ONERA-M6 case specifically, a mesh coarsened to 10,920 cells cannot even
produce a converged primal to linearize about. The escape route is bounded
below as well as above — "coarsen the adjoint mesh" cannot be pushed
arbitrarily far down before the primal itself stops converging, and for THIS
case, the entire tested range above that floor (21,840 cells and up) already
fails via GMRES breakdown. **For the M6 family specifically, there is
currently no known cell count, coarsened or not, at which this case's
adjoint both has a converged primal to linearize about and converges. The
prolongation strategy's premise — that a coarse mesh has an affordable
*working* adjoint to prolongate from — is unmet for this case as tested; the
proposal's measurement should be read against that, not assumed to have a
viable coarse anchor available for a transonic/shock case without further
work on the conditioning problem itself.**

**One caveat stated plainly, because it changes how the window should be
read**: the coarse-end (primal-non-convergence) wall is a property of
**the case and its physics** — geometry, Reynolds number, how aggressively
the surface mesh was coarsened before extrusion — not of the adjoint
machinery. A different case, or the same geometry at a different Re, would
put that floor somewhere else; it is not a machine specification. The
fine-end walls (memory, GMRES breakdown) ARE about the solver and are more
likely to generalize across cases within the same solver family.

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

## Option 3 — more ranks (2, 4, 8, 16)

**STATUS: DONE — measured, and it closes the option.**

**This session resumed after a host interruption** (a prior attempt at this
same directive was lost when the harness process exited mid-task before
anything was written to disk or committed — confirmed via `uptime -s`
showing a genuinely fresh boot, not a false alarm). Nothing below is carried
over from memory; every number was measured fresh in this session.

**Methodology note, found and fixed before trusting any number:** the
straightforward way to measure "peak memory of an N-rank MPI job" — sum each
rank's own RSS from `ps` — **overcounts**, because OpenFOAM/PETSc/Python/MPI
shared libraries are mapped into every rank's address space and `ps` counts
those resident pages once per process that maps them, not once per physical
page. Verified directly: on a 2-rank A1 control, summed-`ps`-RSS read ~2,472
MiB while the container's own cgroup accounting (`memory.peak`, cgroup v2 —
the number that actually determines whether a memory cap trips) read
1,613–1,615 MiB, reproducible across three independent runs. **All aggregate
figures below use cgroup `memory.peak`**, polled once per second while the
container is confirmed still running (reading it after exit races docker's
own cgroup teardown and silently returns 0 — hit this once, fixed it by
sampling only while `docker inspect .State.Running` is true and trusting the
kernel's own monotonic peak counter). Per-rank figures below use `ps` RSS per
process and are reported for balance/shape only, explicitly flagged as an
overcount if summed.

**This session's own cgroup-based 2-rank number (1,613–1,615 MiB) does not
match the previously-documented 2,185.2 MiB baseline for the same case**
(Option 2's table, above). The prior session's exact measurement script no
longer exists to inspect (scratchpad from that session was not preserved),
so the cause of the ~26% gap cannot be pinned to a specific mechanism with
certainty — plausibly a different accounting method (e.g. summed RSS with
different dedup behavior, or a `docker stats`-derived figure). **This is
disclosed, not resolved**, and the fix is procedural: everything reported
below and in Options 4/5 uses one consistent method throughout this session
(cgroup `memory.peak`), so ranks/mesh-size comparisons *within* this
session's own numbers are apples-to-apples even though the absolute
magnitude may not be directly comparable, digit-for-digit, to numbers from a
different, unrecoverable methodology in an earlier session.

**Contention note (new standing instruction this session):** other compute
agents came online partway through this measurement (a hump-turbulence
sweep, an adjoint-NaN field scan, a closure-challenge study — CPU/light-
memory budgeted, not colocated on this case). Load climbed from 0.29 to as
high as 20.5 across these runs. **A direct sensitivity check was run**: the
2-rank case was re-measured at load 15.88 (vs. 3.40 clean) and read 1,566.3
MiB vs. 1,613.0 MiB clean — a 2.9% difference, well inside normal run-to-run
noise, while wall-clock time nearly tripled (64s vs 22s). This makes sense:
cgroup memory accounting is per-container and isolated from other host
processes' CPU/memory use as long as the *host* itself is not memory-
constrained (it was not — MemAvailable never dropped below 28.4 GB across
this whole option). **Conclusion: these peak-RSS numbers are trustworthy
despite the CPU contention; the wall-clock times are not** and should not be
compared across rows without checking the load column.

**Measured — A1 NACA0012, 4,032 cells, `runScript.py` (unmodified baseline,
default `pcFillLevel=1`), `compute_totals`, no memory cap that was ever
approached (8g cap, nowhere close to hit):**

| ranks | agg peak RSS (cgroup) | per-rank RSS (ps, min–max) | per-rank mean | wall | MemAvailable before | load (1-min) before |
|---|---|---|---|---|---|---|
| 2 | 1,613.0 MiB | 1,240.8–1,241.0 MiB | 1,240.9 MiB | 22 s | 29.0 GB | 3.40 |
| 2 (contention check) | 1,566.3 MiB | 1,247.5–1,247.8 MiB | 1,247.6 MiB | 64 s | 28.6 GB | 15.88 |
| 4 | 2,282.1 MiB | 1,027.6–1,028.5 MiB | 1,027.9 MiB | 19 s | 29.0 GB | 3.86 |
| 8 | 3,635.1 MiB | 938.4–945.2 MiB | 942.8 MiB | 16 s | 29.0 GB | 8.01 |
| 16 | 6,071.5 MiB | 873.0–876.0 MiB | 874.5 MiB | 385 s (heavily contended, see load) | 29.0 GB | 7.28→20.5 during run |

**Both halves of the predicted effect happened, and the second one is the
answer that matters:**
- Per-rank peak RSS *did* drop with more ranks — 1,240.9 → 1,027.9 → 942.8 →
  874.5 MiB as ranks went 2→4→8→16, a real 29.5% reduction — but **strongly
  sublinearly**: 8x more ranks bought only a 1.4x per-rank reduction. This is
  consistent with each rank paying a large, largely rank-count-independent
  fixed cost (loading PETSc/OpenFOAM/Python/MPI/numpy, DAFoam's own
  in-memory structures) that does not shrink just because its slice of the
  4,032-cell mesh does (at 16 ranks that slice is 252 cells — trivial — yet
  each rank still needs ~875 MiB just to exist).
- **Aggregate peak RSS grew, monotonically and substantially**: 1,613 →
  2,282 → 3,635 → 6,072 MiB, a **3.76x increase** from 2 to 16 ranks. The
  fixed per-rank cost, paid 16 times instead of 2, dominates any savings from
  smaller per-rank data.

**Verdict: RULED OUT, and closed permanently, exactly per the brief's second
predicted outcome.** For this case (and by the same fixed-cost-per-rank
mechanism, for any case where mesh-local data isn't already the dominant
memory cost — which describes the coloring/Jacobian-block structural wall
this whole document is about), adding MPI ranks does not reduce the total
memory needed to complete a compute_totals call; it increases it. Rank count
is not a lever for fitting a big adjoint into a fixed-RAM box. **This also
answers, in the negative, whether more ranks could rescue A3/A6/sail_medium/
naca4412_coarse**: the mechanism that would need to hold for ranks to help
(memory dominated by per-rank mesh data, not fixed overhead) is directly
contradicted by this measurement, on the same solver family, same host,
same session.

*Corroborating but incompletely-specified secondary data point, found already
on disk from a session interrupted before it was written up*: a rank=8 run on
A3 ONERA M6 coarse (99,840 cells, the actual blocked case) exists in the
solve registry (`d3_ranks8_A3coarse_20260729T035114Z`), reading
`peak_MiB=20480.0` (**censored at its 20g cap**) after 1,014 s. The exact
preconditioner/sparsify settings used for that run are not recoverable from
the surviving `.done`/`.log` records (no script name or option dict was
retained) so it is **not** compared numerically against the 4-rank sparsify
runs in Option 2 above (18,421.8 / ≥20,480.0 MiB) — both 4-rank and 8-rank
runs on this case hit or exceeded the same 20g cap, so this pairing cannot
show whether 8 ranks helped, hurt, or made no difference on the case that
actually matters; it can only confirm that 8 ranks did **not** rescue it
under a 20g cap. Re-running it cleanly, to a specified configuration, would
be needed to say more — not done here, given the A1 result above already
closes the option on structural grounds.

## Option 4 — coarse-adjoint-mesh boundary

**STATUS: DONE — measured, and it overturns the previous read rather than
refining it.**

**The orphaned 79,560-cell probe, verified rather than taken on trust.** An
earlier agent instance was killed after launching a 79,560-cell ONERA M6
probe (`d3_opt4_probe80k`, 4 ranks, 22g cap) and before writing it up. The
collector recorded `docker_exit=0 inner_exit=0`, `agg_peak_MiB=17603.8`
(comfortably under the 22g cap — genuinely uncensored) — on the surface,
a clean success. **It was not one.** Grepping the actual solver log
(`run_opt4_probe80k.log`, not the truncated summary) for `PetscConvergedReason`
finds:

```
Main iteration 200 KSP Residual norm 1.482196937524e-322 887.48 s
**Completed**! Total iterations: 200. PetscConvergedReason: -5. 887.48 s
Residual tolerance satisfied, solution finished!
```

`-5` is `KSP_DIVERGED_BREAKDOWN` — the residual underflows to denormal range
and PETSc reports it as "converged" with a negative reason code; the script's
own success message and full derivative dictionary print regardless. **Both**
the CD and CL adjoint solves hit this. This is the exact same false-success
pattern Option 2 already caught once on the 99,840-cell case — caught a
second time here because the instruction was to verify the exit, not adopt
the reading. The 17,603.8 MiB figure stands as a real, uncensored **memory**
point; the run itself did not succeed.

**A same-family sweep (in-plane surface mesh identical — 1,560 faces,
3x-coarsened from `m6_surfaceMesh_fine.cgns` — spanwise/extrusion layer
count `N` the only variable, via `pyHyp`) was then run to find out whether
79,560 cells was near a boundary or deep inside a failure region:**

| cells | `N` (pyHyp layers) | agg peak RSS (cgroup) | `PetscConvergedReason` | wall | verdict |
| --- | --- | --- | --- | --- | --- |
| 10,920 | 8 | 1,482.0 MiB (primal-setup only, not comparable) | n/a — **primal never converged** (1000 SIMPLE iters, residual 1.5e-3 vs 1e-6 tol) | 22 s | too coarse: nothing to differentiate around |
| 21,840 | 15 | 5,876.6 MiB | **-5, -5 (DIVERGED_BREAKDOWN)** | 420 s | diverged |
| 42,120 | 28 | 9,991.9 MiB | **-5, -5 (DIVERGED_BREAKDOWN)** | 667 s | diverged |
| 79,560 | 52 | 17,603.8 MiB | **-5, -5 (DIVERGED_BREAKDOWN)** | 960 s | diverged (the orphaned probe, above) |
| 99,840 | 65 | 18,422–≥20,480 MiB (Option 2, sparsify variants) | **-5, -5 (DIVERGED_BREAKDOWN)** | 403–524 s | diverged |

**Four for four, across a 4.6x cell-count range (21,840 to 99,840): every
ONERA-M6-family adjoint attempted diverges with the identical PETSc reason
code.** The mesh-size boundary this document previously reported ("works at
63,920, fails at 99,840, boundary somewhere in between") does not exist for
this family — 63,920 is a **different case** (naca0015_sail_coarse,
incompressible), not a smaller M6 mesh. No M6-family mesh, at any size
tested from just above the primal-convergence floor (10,920) to the
established OOM ceiling (399,360), has ever produced a converged adjoint.
**The working/failing boundary this section originally set out to pin does
not exist on the cell-count axis for this case — see the Headline finding
above for the corrected, per-family framing.**

Mesh-quality note, checked and ruled out as the cause: all three new sweep
meshes were `checkMesh`'d and flagged for the identical pattern already
present (unnoticed) on the known-good-through-coloring 79,560-cell mesh
itself — max non-orthogonality 61.5, ~20-28% of cells flagged for small
determinant, concentrated in one specific near-wall/tip region. Re-running
`checkMesh` on the original 79,560-cell mesh confirms this is a structural
property of the whole `pyHyp`-extruded, 3x-coarsened ONERA-M6 mesh family,
present identically regardless of `N` — not something introduced by this
sweep, and not obviously the cause of the divergence (the sail-family meshes
have their own, unrelated quality issues — see the 1,912 concave cells noted
on `naca0015_sail_coarse` — and still converge).

## Option 5 — the scaling-law study (bytes per cell)

**STATUS: DONE for the ONERA-M6 family — a real, controlled, well-fitted
same-family law. Sail/incompressible family: one clean point, not yet a
fit — see below.**

**The controlled same-family sweep** (identical in-plane surface mesh,
identical solver/options/ranks, only extrusion layer count varying — the
same three points used to close Option 4) gives three clean, uncensored
memory measurements on ONE mesh family:

| cells | agg peak RSS (cgroup, MiB) |
| --- | --- |
| 21,840 | 5,876.6 |
| 42,120 | 9,991.9 |
| 79,560 | 17,603.8 |

Least-squares log-log fit (computed independently with `numpy.polyfit`, not
taken on report):

**memory (MiB) = 1.2125 x cells^0.8485**, R² = 0.9992

| cells | measured | fit | residual |
| --- | --- | --- | --- |
| 21,840 | 5,876.6 | 5,825.6 | -0.87% |
| 42,120 | 9,991.9 | 10,170.6 | +1.79% |
| 79,560 | 17,603.8 | 17,446.0 | -0.90% |

**The exponent is 0.85 — SUBLINEAR.** Memory grows more slowly than cell
count in this family: doubling the mesh costs roughly 1.8x the memory, not
2x. (An earlier same-session estimate of a *super*linear ~1.35 exponent was
computed from only two points — 63,920 cells/sail-family at 13,089.7 MiB and
79,560 cells/M6-family at 17,603.8 MiB — **across two different solver
families**, and is withdrawn: it was comparing a converged incompressible
run to a diverged compressible one and had no business being fit as one
line. The 0.85 exponent above is the first one computed within a single
controlled family and is the one that should be used.)

**Extrapolated (label clearly as extrapolation, not measurement):**

| cells | extrapolated peak RSS |
| --- | --- |
| 99,840 (A3 coarse, already known to diverge) | 20.7 GB |
| 200,000 | 37.2 GB |
| 400,000 | 67.1 GB |
| 579,072 (A6 CRM wingbody's actual mesh, primal-only, never adjoint-run) | 91.8 GB |

**Sail/incompressible family, cross-check only, not a fit**: the M6-family
law predicts ~14.2-14.5 GB at 63,920 cells; naca0015_sail_coarse's actual,
independently re-measured, uncensored, converged peak at that exact cell
count is 13,089.7 MiB (12.8 GB) — see Option 4's table above. Close (~10-13%),
which is *interesting*, but it is one point checked against another family's
fit and proves nothing about whether the sail family shares the same
exponent. **Two more sail-family points, at different cell counts on the
same geometry/solver/rank/DV configuration, would answer whether 0.85 is a
property of the solver (DASimpleFoam vs DARhoSimpleCFoam would differ) or of
the adjoint machinery generally (in which case it would hold across both).
That is queued, not done** — building a second sail-family mesh resolution
needs new snappyHexMesh refinement-level work this session did not reach,
and the box was below the 24 GB same-weight-class threshold when this
section was written. This is the one open quantitative question the
envelope does not yet answer.

**THE PAIRING THAT MATTERS — memory and convergence must be read together,
not separately, or the hardware answer is wrong:**

- **On memory alone**, the ONERA-M6-family fit says a 400,000-cell adjoint of
  this kind needs roughly 67 GB, and A6 CRM's actual 579,072-cell mesh would
  need roughly 92 GB. Both are ordinary cloud instance sizes (e.g. AWS
  `r6i.8xlarge`/`x2iedn` class). **On memory alone, this workload is
  affordable today.**
- **On convergence**, it does not matter, because **this family's adjoint has
  not converged at any tested size**, including the smallest one tested
  (21,840 cells, 5.9 GB peak) — nowhere near any memory cap. A 128 GB machine
  would buy a larger `DIVERGED_BREAKDOWN`, not a working gradient.

**The honest statement, and the one this document should be read by:** *if
the conditioning problem (why does this compressible/transonic/shock-
containing solver family's adjoint break down at every tested size?) is
solved, here is what the hardware costs, and it is affordable. Until it is
solved, hardware is not the constraint — buying more RAM does not fix a
`DIVERGED_BREAKDOWN`.* The conditioning problem itself (candidate cause:
shock-sensitivity of the linearization, per the flow physics — untested this
session) is a separate investigation from memory sizing and is not
attempted here; it is the next thing worth doing, and it is a numerics
question, not a procurement one.

---

## Provisional hardware read — no longer provisional for the memory half; the convergence half is the actual blocker

**Superseded by the Headline finding and Option 4/5 above.** The short
version, restated once more because it is the number the owner asked for:

- **Memory is not the constraint.** The ONERA-M6-family fit
  (memory = 1.2125 x cells^0.8485, R²=0.9992, three clean same-family points)
  puts a 400,000-cell adjoint at ~67 GB and A6 CRM's 579,072-cell mesh at
  ~92 GB — both ordinary cloud sizes, not exotic hardware.
- **Convergence is the constraint, and it binds first, at every size
  tested.** Every ONERA-M6-family adjoint attempted this session and the
  prior one — 21,840 / 42,120 / 79,560 / 99,840 / 399,360 cells — has failed,
  either `DIVERGED_BREAKDOWN` or OOM, with breakdown occurring at cell counts
  small enough (21,840 cells, 5.9 GB) that memory was never close to
  limiting. **A bigger box does not fix this case's adjoint.**
- **This is a per-family finding, not a per-cell-count one.** The
  sail/incompressible family (`DASimpleFoam`) has a real, demonstrated
  working window (4k-64k cells confirmed, upper edge between 64k-156k, a
  different — coloring-stall, not breakdown — failure mode). A6 CRM shares
  ONERA M6's solver and flow regime (transonic, `DARhoSimpleCFoam`, Mach
  0.85) and should be **expected**, not assumed safe, to hit the same wall —
  stated as an inference from shared physics, since A6's adjoint has never
  been attempted.
- **What would actually move this forward**: not a hardware purchase, but an
  investigation into why the compressible/transonic/shock adjoint is
  ill-conditioned at every resolution — starting with whether the breakdown
  correlates with a shock-containing region of the flow, whether a different
  linearization state (e.g. a more-converged primal, a different PC) changes
  the reason code, and whether this is specific to `DARhoSimpleCFoam` or a
  property of transonic adjoints generally. That is a numerics question and
  is explicitly **not attempted in this document** — it is the next
  investigation this finding points to, not a task this D3 directive covers.

## What is still open, explicitly

- Option 3: **done, closed.** More ranks increases aggregate memory for this
  workload; not a viable lever.
- Option 4: **done, closed, and the conclusion inverted.** There is no
  cell-count boundary for the ONERA-M6 family — every tested size from
  21,840 to 399,360 cells fails (breakdown or OOM). The working/failing
  distinction is per-family (M6/compressible fails everywhere tested;
  sail/incompressible has a real window), not per-cell-count. A4's fine
  mesh (45,760 cells, primal-only) was not additionally re-checked this
  session — lower priority once the per-family framing landed; still open
  if someone wants a second incompressible-family data point near that size.
- Option 5: **done for the ONERA-M6 family** (three-point same-family fit,
  memory = 1.2125 x cells^0.8485, R²=0.9992). **Still open for the
  sail/incompressible family**: only one clean, uncensored point exists
  (63,920 cells, 13,089.7 MiB); its cross-family check against the M6 fit
  is close (~10-13%) but not a controlled measurement. Two more
  same-geometry sail-family points, at different mesh resolutions, would
  settle whether the 0.85 exponent is solver-specific or general — needs
  new snappyHexMesh refinement-level setup work not done this session.
- naca0015_sail_coarse's true (uncensored) peak RSS at 63,920 cells:
  **closed this session.** Re-measured at a 26g cap (previously censored at
  10g): 13,089.7 MiB, comfortably clear of the cap, `PetscConvergedReason: 2`
  (converged) confirmed on both CD and CL from the raw solver log. The
  10,240.0 MiB figure is retired.
- **New this session**: the measurement harness did not originally capture
  `PetscConvergedReason` at all — only exit codes and memory, which is
  exactly how the 79,560-cell probe was first misread as a success. Fixed
  in `d3_mem_run2.sh` (grep the full run log, not the truncated tail-60
  display copy — the first draft of the fix had that bug too, caught before
  it shipped on a run where it would have gone unnoticed). Every future
  measurement's summary now carries a `SOLVER STATUS: CONVERGED /
  DIVERGED / NO_CONVERGEDREASON_FOUND` line, and continuous (1 Hz)
  host MemAvailable/swap sampling for the run's full duration, not just
  before/after endpoints.
- **New this session**: why the M6-family adjoint is ill-conditioned at
  every tested resolution is not investigated here — flagged as the next,
  higher-value question (a numerics investigation, not a memory one) but
  explicitly out of scope for this directive.
- Hardware recommendation: **the memory half is no longer provisional**
  (see Option 5's fit and extrapolation). The overall recommendation
  remains conditional on the conditioning problem, per the Headline
  finding and the restated read at the end of Option 5 — not because more
  measurement is pending, but because the honest answer genuinely has two
  halves that cannot be collapsed into one number.

## Raw logs (this session)

Prior-session logs, under
`/tmp/claude-1000/-home-ubuntu-Certonomous/982d6244-5800-47f3-a450-80ce0b0a24b7/scratchpad/logs/`
(scratchpad, not committed — paths recorded here for traceability):
`A1_baseline_4032.log`, `A5_4800.log`, `sail_coarse_63920.log`,
`A1_nocoloring_4032{,_v2,_v3}.log`, `A1_sparsify_4032.log`,
`A3coarse_sparsify_99840.log`, `A3coarse_sparsify_fill1_99840.log`.

This session's Option 4/5 work, under
`/tmp/claude-1000/-home-ubuntu-Certonomous/982d6244-5800-47f3-a450-80ce0b0a24b7/scratchpad/`:
harness scripts `d3_mem_run.sh` (original) and `d3_mem_run2.sh` (adds
`SOLVER STATUS` extraction + continuous host-contention sampling); per-run
logs/summaries/host-memory CSVs under `d3_logs/opt5_*` and
`d3_logs/opt4_probe80k.*`. Case directories (mesh + full raw solver logs,
independently grep'd for `PetscConvergedReason` rather than trusted from any
summary): `/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-probe80k`
(79,560 cells, the corrected orphaned probe),
`/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-{n8_10920,n15_21840,n28_42120}`
(new sweep meshes), `/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse`
(pre-existing 99,840-cell mesh, same family, confirmed by `checkMesh`
signature match), and
`/home/ubuntu/Certonomous/demo-output/website/dafoam/work_sail/naca0015_sail_coarse`
(re-measured in place; `run_opt5_sail_coarse_uncap.log` is the raw log the
`PetscConvergedReason: 2` confirmation was read from). Solve registry
completion records (survive session interruptions):
`demo-output/website/solve_registry/d3_*`.

## 2026-08-08 retroactive annotations (ordered by the chief; dead-lever audit `DEAD_LEVER_AUDIT_2026-08-08.md`, 946e4a26)

**1. Transonic-PC dead lever.** Every M6-family adjoint measured in this record
echoed `transonicPCOption 2;` in its daOptions dump (e.g.
`A3-onera-m6-sweep-n15_21840/run_opt5_onera_n15_21840.log:410`). That value is
dead code for `DARhoSimpleCFoam` (`DAResidualRhoSimpleCFoam.C:173` accepts only
`== 1`; `== 2` exists only in `DAResidualTurboFoam.C:176`): **no archived M6
adjoint ran with an active transonic preconditioner** (entry-8 outcome blocks
08a87cc7, 5f0c328e). The envelope's conclusions are unaltered — the record
never claimed the transonic PC was tried — but the M6 `-5` wall documented here
was measured with that lever OFF; the PC-alone arm now running is the live test
of whether an active transonic PC moves it.

**2. Options 1–2 lost their solver logs (charter v1.5 §9 status).** The solver
logs for Option 1 (`adjUseColoring=False`, incl. the quoted
`Conflicting Colors Found!` FATAL block) and Option 2 (the sparsify arms'
option echoes and A3-coarse reason codes) lived in the session scratchpad
(`982d6244…/scratchpad/logs/`) and died with it — they are
**unreconstructible**. What survives: the 2-line collector stubs
(`d3_coloring_off_A1_v2/.v3`, `d3_sparsify_*`), whose exit codes, wall times,
and peak-RSS figures match this record digit-for-digit, plus an independent
surviving proof of the Option-1 lever class on A4
(`W4-a4-discriminators/d_np4scotch_nocolor.log:483` `adjUseColoring 0;`).
Per §9, Options 1–2's lever-activity and reason-code claims therefore ship
**unverifiable-from-logs** (memory/wall figures corroborated by stubs; lever
activity unsupported by any surviving runtime log). Options 4–5 and the
headline envelope are unaffected — their raw logs survive and were re-verified
line-by-line in the audit.
