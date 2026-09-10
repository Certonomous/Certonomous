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

> [SUPERSEDED — see CORRECTION 2026-09-09 at the foot: with transonicPCOption 1, rungs 1/2 converge + are FD-verified; the wall is -3 stagnation at rung 3, not -5.]

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

---

## CORRECTION 2026-09-09 — the "-5 at every M6 size" reading above is STALE (pre-`transonicPCOption`)

**Nothing above is rewritten.** Per `CLAUDE.md` rule 6, the original table row
("too fine (conditioning) … every ONERA-M6-family point tested this session:
21,840 / 42,120 / 79,560 / 99,840 cells … `PetscConvergedReason: -5`") and the
paragraph beginning "The ONERA-M6 … family has never, at any tested size from
21,840 to 399,360 cells … produced a converged adjoint" are struck, not edited.
Every measured number in them stands as it was recorded. This note discloses
what later runs established; it overwrites none of it.

**Why they are stale.** The L48-63 table and paragraph — and the "-5 everywhere"
reads restated in Options 4/5 and the end-of-Option-5 hardware summary — were
all measured with the transonic preconditioner **OFF**. The 2026-08-08 annotation
already flagged this (`transonicPCOption 2;` echoed in every archived M6 dump is
dead code for `DARhoSimpleCFoam`, which accepts only `== 1`; no archived M6
adjoint ran with an active transonic PC). The live test the annotation named has
since been run, and it moves the wall.

**The current, verified picture** (two artifacts, cited by path; every number
below is read from them, not from this file):

1. **M6 rungs 1 and 2 CONVERGE and are FD-verified with `transonicPCOption 1`.**
   `/home/ubuntu/Certonomous/cases/dafoam/A3_RUNG3_N52_RESULT.md` (lines 62-63,
   88-89): *"rungs 1 (21,840) and 2 (42,120) converge and are FD-verified; the
   transonic-PC token remains the difference between double `-5` and convergence
   at both."* So the "never, at any size, produced a converged adjoint" claim is
   false as stated once the transonic PC is active. The fix **weakens** the PC —
   it drops `div(phid,p)` from the PC matrix — which is what lets the two coarse
   rungs converge.

2. **The real wall is `-3` STAGNATION at rung 3 (79,560 cells), NOT `-5`
   breakdown.** Same file, line 1 and lines 18-41: rung 3 CD runs to the 4000-iter
   cap and returns `-3` with a total residual reduction of only 1.31x (flat;
   3.79e-07 relative change over the last 2,700 iterations = stagnation), distinct
   from the earlier `-5` denormal collapse. The ceiling therefore sits **between
   42,120 and 79,560 cells**, and it is a **conditioning** wall, not a memory one:
   peak was **11.65 GiB against the 22 GiB cap** (line 50-51), MemAvailable never
   below 17 GB, no OOM.

3. **Strengthening the PC re-breaks it to `-5`.** L3 Richardson at rung 2 (the
   only change from the arm that converged there) sent both solves back to `-5`,
   collapsing to exactly 0.0 at iteration 200 (same file, lines 10-11). Consistent
   with a non-normal, near-indefinite transonic operator: the weakened (transonic)
   PC converges the coarse rungs; strengthening it (pcFillLevel 1 / Richardson /
   larger gmresRestart) or switching Krylov re-breaks it.

4. **A6 wing-alone adjoint is an ITEM VERDICT `PASS`, not an unattempted
   inference.** `/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A6/curriculum_D8R/RESULTS.md`
   (lines 13-24, 38-40): A6 CRM wing-alone (41,760 cells, N=16, twist-only) adjoint
   graded `PASS`, two rows (SHIPPED + PATCHED), **20/20 FD components PASS, 0 sign
   flips**. This directly overturns the L76-82 / end-of-Option-5 inference that A6
   "should be expected to hit the same conditioning wall as A3." **A6 wing-body
   (579,072 cells) has still had NO adjoint attempted** — that remains
   memory-predicted only, and the ~92 GB extrapolation is untested.

**Net.** The "conditioning wall at every M6 size" framing was an artifact of the
transonic PC being off. With it on, the M6 adjoint converges and FD-verifies at
21,840 and 42,120 cells; the wall is a `-3` stagnation bracketed between 42,120
and 79,560 cells with memory comfortable; and the sibling A6 wing-alone case is a
verified PASS. The memory-scaling measurements (Options 3/5) are unaffected — they
were never in dispute; only the convergence reads above are superseded.

---

## AMENDMENT 2, 2026-09-10 — document version 1.2. The 2026-09-09 correction is COMPLETED to the rule-6 form, the free-lever inventory is stated once, and a line-number defect introduced by that correction is disclosed

**lines whose number changed above this section: 0**

**Version record.** This document carried no explicit version line before today. The
history is reconstructed from its own commit trail and stated here, at the foot, without
touching a byte of the body: **v1.0** 2026-07-29 (`216fe7a8`, `3c9379de`, `5a2e49c6`) — the
D3 envelope through the Option 4/5 sweep; **v1.1** 2026-08-08 (`e9a651e9`, the retroactive
dead-lever annotations at L610) and 2026-09-09 (`fa124d95`, `CORRECTION 2026-09-09` at
L641); **v1.2** 2026-09-10 — this amendment. Nothing above this line is rewritten. The
struck passages named in `CORRECTION 2026-09-09` stay struck, not edited; every measured
number in them stands exactly as recorded.

### A. Why a second amendment exists at all

`CORRECTION 2026-09-09` (L641–L701) already carries the substance of the repair and is not
superseded by this one — it is **completed** by it. Three things it did not do, and this
amendment does:

1. It carries **no version bump and no `lines whose number changed above this section: 0`
   assertion**, which rule 6 requires because this file is cited **by line** by other
   records — including two pre-registrations (§D).
2. It leaves the **free-lever question** unanswered on this document's face, which is the
   question a cold reader will actually ask next: *if conditioning is the wall, what cheap
   thing has not been tried?* Reading the body alone, the honest-looking answer is "plenty";
   the measured answer is "one" (§C).
3. It **itself broke the line citations** it was written to protect (§D).

### B. The corrected picture, stated so it cannot be misread

A reader of the body's L48–L63 table and paragraph will conclude that the ONERA-M6 adjoint
has **never converged at any size**. That conclusion is **false**, and it is the single
most expensive false conclusion available from this file, because it invites two wrong
follow-on decisions — abandoning a line that works, or renting memory to fix a problem that
is not memory. What is true, every figure MEASURED and read from the artifact named beside
it, not from this file:

- **M6 rungs 1 (21,840 cells) and 2 (42,120 cells) CONVERGE and are FD-verified**, with
  `transonicPCOption 1` active.
  `cases/dafoam/A3_RUNG3_N52_RESULT.md:88-89`: *"rungs 1 (21,840) and 2 (42,120) converge
  and are FD-verified; the transonic-PC token remains the difference between double `-5`
  and convergence at both."* Rung 2's own record,
  `cases/dafoam/A3_RUNG2_N28_RESULT.md:1,13,20-30`, grades it **CONVERGED + FD PASS**: both
  adjoint solves `PetscConvergedReason: 2`, and all three FD components PASS —
  `patchV[1]` 0.0077 %, `twist[1]` 0.2740 %, `shape[115]` 0.0172 % (MEASURED).
- **The fix WEAKENS the preconditioner.** `transonicPCOption 1` drops `fvm::div(phid, p)`
  from the PC-matrix pressure equation — `cases/dafoam/R5_ADJOINT_CONDITIONING.md:299`,
  `cases/dafoam/A3_TPC1_ARM_PREREGISTRATION.md:34`, both against
  `DAResidualRhoSimpleCFoam.C:172-176`. It is a deliberate PC mismatch, not a stronger solve.
  This is why the body's instinct — that a harder-working preconditioner is the remedy — is
  backwards for this operator.
- **The real wall is `PetscConvergedReason: -3` STAGNATION at rung 3 (79,560 cells), not the
  `-5` breakdown the body's table records.** MEASURED, `A3_RUNG3_N52_RESULT.md:20-41`: CD
  runs to its 4,000-iteration cap; total residual reduction **1.31x**
  (2.121343646203e-02 → 1.615245992220e-02); residual change over iterations 1300→4000 is
  **3.79e-07 relative** — flat. The record distinguishes this from rung 2's *budget-limited*
  `-3` (1407x reduction, still descending, resolved by raising the cap), and the distinction
  was pre-registered before either was seen.
- **Memory is COMFORTABLE at the wall.** MEASURED, `A3_RUNG3_N52_RESULT.md:50-51`: peak
  container usage **11.65 GiB against a 22 GiB cap**, host `MemAvailable` never below 17 GB,
  no swap growth, no OOM. **Conditioning binds, not RAM.** This is the L-15 shape the
  compute charter names and `DAFOAM_CHARTER.md` §7 restates against this very rung.
- **The ceiling is BRACKETED, not located: it sits between 42,120 and 79,560 cells**
  (`A3_RUNG3_N52_RESULT.md:62-64`). The record explicitly declines to claim 79,560 is *the*
  boundary (`:91-94`), and declines to claim stagnation and the earlier `-5` share a
  mechanism (`:95-97`). Neither claim is made here either.
- **The sibling A6 case is a verified win, not a predicted loss.** A6 CRM **wing-alone**
  (41,760 cells) adjoint is an item verdict **PASS**, two rows, 20/20 FD components, 0 sign
  flips — `cases/dafoam/ladder-a/A6/curriculum_D8R/RESULTS.md:13-24,38-40`. This overturns
  the body's L76–L84 inference that A6 "should be expected to hit the same conditioning wall
  as A3". A6 **wing-body** (579,072 cells) has still had **no adjoint attempted**; it remains
  memory-predicted only, and that prediction is INFERRED, never measured.

**Two decisions this section exists to foreclose.** (i) *Renting memory does not buy a
converged M6 gradient at rung 3* — memory was never the binding constraint there, and
stagnation is expected to return at larger meshes with a better-resolved shock. Renting is
**necessary-but-not-sufficient**, and is defensible only as a way to measure peak RSS for
cases that currently OOM, which is a cost-model deliverable and not a gradient. (ii) *There
is no DAFoam GPU backend* — no CUDA/AMGX/PETSc-GPU path in the tree
(`docs/GPU_CAPABILITY_STATE.md:118`); "GPU for the adjoint solve" is a build project, not a
configuration change. Neither point is re-litigable from this document's body.

### C. The free-lever inventory — every entry verified at its own record before being written here

The body's Options 1–5 predate almost all of this. The cheap-lever well for rung-3
conditioning is, on the evidence, **essentially dry**. Each row was checked against the
artifact named, not carried from any board or brief:

| lever | state | evidence (MEASURED unless marked) |
|---|---|---|
| `renumberMesh` / CuthillMcKee | **already spent at mesh build, on every rung** | `/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-probe80k/logMeshGeneration.txt:346,366-378` — the 79,560-cell mesh, `renumber-method: CuthillMcKee [default]`, **band 73,452 before → 1,550 after**. It is therefore not the differentiator between the converging rungs and the stagnating one. |
| `adjStateOrdering: cell` | **already the baseline, not a lever** | `cases/dafoam/ladder-a/A3/curriculum_A3FL1/A3FL1_PREREGISTRATION.md:28`, citing `rung3_stage1.log:508` and `runScript_rung3.py:95` — `cell` on rungs 1, 2 **and** the stagnating rung 3. **Conflict disclosed:** `cases/dafoam/ladder-a/A3/original_memory_plan/PREREGISTRATION.md:159` calls it *"UNTRIED — never varied in any lab run"*. That entry is the older one and cites the pyDAFoam default rather than an M6 run log; A3FL1's line-cited log reading is the one this amendment relies on. |
| `pcFillLevel 0→1` | **spent** | residual improves only **1.859x** despite a ~7-order improvement in mid-cycle condition number — `cases/dafoam/ladder-a/A3/grading_confirmation/RESULTS.md:225-226`. |
| L3 Richardson (`globalPCIters`/`localPCIters` 3) | **spent, and withdrawn before rung 3 launched** | a material winner at rung 1 (−43 %/−45 % iterations) that **collapses to double `-5` at exactly iteration 200 — `gmresRestart`, the first restart boundary — at rung 2**; `grading_confirmation/RESULTS.md:232-235`, `A3_RUNG3_N52_RESULT.md:10-16`. |
| `gmresRestart 200→1000` | **spent, at rung 3 itself** | the restart challenge, `cases/dafoam/A3_RUNG3_RESTART_CHALLENGE_PREREGISTRATION.md:108-140` — **BRANCH B**, the restart effect is real but does not rescue the claim; **1.647x** against a pre-registered 10x bar (`grading_confirmation/RESULTS.md:227`), residual flattening at exactly iteration 1000. |
| `-ksp_type lgmres` | **spent** | `-3` at 400 iterations, residual 8.236875832365e-02 — **5.10x WORSE** than the control, and 3.88x above its own iteration-0 value: `cases/dafoam/A3_STAGE2_UNREACHABLE_CLASS_PREREGISTRATION.md:109-133`, `grading_confirmation/RESULTS.md:228`. |
| `-pc_type gamg` | **spent** | `-5` at 200 iterations, residual **7.554080154832e+179** — diverged catastrophically, 4-level hierarchy confirmed built; peak 7.0 GiB, memory never a factor: `A3_STAGE2_UNREACHABLE_CLASS_PREREGISTRATION.md:135-160`. |
| `asmOverlap 1→2` | **spent** | **1.062x worse** — `grading_confirmation/RESULTS.md:224`; `ladder-a/A3/original_memory_plan/PREREGISTRATION.md:160` records it already at its cheapest value with no headroom downward. |

`grading_confirmation/RESULTS.md:215-235` states the aggregate on its own face: **twelve
conditioning levers eliminated, with numbers**, including the diagnostics that refused to
discriminate — preconditioned κ = `sMax/sMin` = **9.57e+10** at rung 3, diagonal spread
**14.47 decades** at rung 3 against **14.40** at the *converging* rung 2, and a Hutchinson
non-normality ratio of **0.617** against a ≥3.0 bar, i.e. the stalling rung is *less*
non-normal than the converging one.

**Two honest qualifications, so this section is not over-read.** First, `lgmres` and `gamg`
were tested as **off-the-shelf members of their classes at documented defaults**, on
`dafoam-kspopts:v1`; the same record states plainly that this is evidence off-the-shelf AMG
fails here, *not* that a coarse-space method cannot work, and that a physics-appropriate
coarse space *"remains untested and is not cheap"*
(`A3_STAGE2_UNREACHABLE_CLASS_PREREGISTRATION.md:169-175`). Second, **one genuinely-untried
free lever remains**: `jacMatReOrdering: natural → nd`. Every A3 rung ran `natural`
(`A3FL1_PREREGISTRATION.md:27`, citing `A3-rung3-n52/rung3_stage1.log:449` and
`A3-rung2-n28-tpc1/runScript_tpc1.py:101`); `nd` has never run on M6. It is pre-registered
as A3FL1/A3FL2 (`cases/dafoam/ladder-a/A3/curriculum_A3FL{1,2}/`), and **as of this
amendment neither directory contains a RESULTS file** — so it is `PENDING`, and its
pre-registration's own prior expectation is pessimistic. **"Essentially dry" means one lever
left and a pessimistic prior on it — it does not mean zero.**

### D. Disclosure: `CORRECTION 2026-09-09` shifted body line numbers by +2, and this amendment does not repeat that

Commit `fa124d95` appended the correction at the foot (66 insertions) **but also inserted two
lines into the body at position 63** — the `[SUPERSEDED — …]` marker now at L65 and its
blank line. Every body line below L64 therefore moved down by two, and the assertion rule 6
requires was neither made nor makeable. This is not a cosmetic point: this file is cited by
line by records that were written against the pre-shift numbering, and several of those
citations now resolve to the wrong place. Measured examples, checked today:

- `cases/dafoam/ladder-a/A3/original_memory_plan/PREREGISTRATION.md:88` cites `:432` for the
  power law; the law now sits at **L434**.
- `docs/MEMORY_ARCHITECTURE.md:51` cites `:625-626` for *"died with it — they are
  unreconstructible"*; it now sits at **L627-628**.
- `verification/campaign/COLD_START_TEST_2026-08-11.md:245` cites `:622` for the lost-logs
  block, which now begins at **L623**.
- `verification/campaign/DEAD_LEVER_AUDIT_ROUND5_2026-08-14.md:81` cites `:611` for the
  2026-08-08 annotation, whose heading is now at **L610** and whose item 1 is at **L612**.

**No body line is renumbered to repair this, and none is renumbered by this amendment** —
un-inserting the marker would shift the numbers a *second* time and break the citations
written since. The defect is recorded here so a reader who finds an off-by-two citation
knows why, and so the next amendment to this file does not repeat it. The affected
citations are reported to the dafoam supervisor, not silently rewritten in the citing
documents, which are other teams' records.

**One executable check reads this file**: `scripts/self_audit.py:4392`
(`check_memory_scaling_law`) refits the published power law from the document's own three
measurement rows. It matches on **content regexes, not line numbers**, so it is unaffected by
either shift. This amendment deliberately introduces **no** two-column `| cells | MiB |`
table row and **no** second power-law sentence, so that check continues to read exactly the
three rows and the one law it was written to read.

### E. What is UNAFFECTED and still stands

The memory measurements are not in dispute and were never in dispute. **Options 3 and 5 —
the rank sweep and the bytes-per-cell scaling law, including the published fit and its three
measurement rows — stand unchanged**, as does the per-family window finding that a
compressible M6 mesh and an incompressible sail mesh of similar size behave differently, and
as does the coarse-end floor (the 10,920-cell M6 primal that will not converge, so there is
nothing to linearise about). What is superseded is **only** the convergence reading: the
L48–L63 table row and paragraph asserting `-5` at every M6 size and "never, at any tested
size, produced a converged adjoint", and the `-5`-everywhere restatements inside Options 4/5
and the end-of-Option-5 hardware summary. Those were measured with the transonic
preconditioner **off** — `transonicPCOption 2` is dead code for `DARhoSimpleCFoam`, which
accepts only `== 1` (the 2026-08-08 annotation at L612-621) — and they remain true statements
about that configuration and false as statements about this case.

*Drafted by a dafoam `lab-lane` under zero-compute instruction: no solver, container or
`mpirun` was invoked, and no number above was produced by this amendment. Every figure is
read from the artifact cited beside it. `cases/dafoam/A3_RUNG3_N52_RESULT.md` was read and
not modified.*
