# Liaison research memo — adjoint conditioning, what the rest of the world knows

Date: 2026-08-04. First research pass under Katie's standing directive of the same
date: when something breaks, the liaison researches it online and records the
method. The method half lives in `docs/standards/PROBLEM_RESEARCH_PROTOCOL.md`
(v0.1, written from this pass). This memo is the findings half.

**Citation discipline (LITERATURE_CHARTER.md):** every URL below was actually
fetched this session, 2026-08-04, and carries a tier. "READ IN FULL" means the
page or raw file was fetched and read. "SEARCH-EXCERPT" means only a search
result's own text was seen, and nothing beyond it is asserted. Source-code
claims are pinned to a sha or branch and dated. Zero-hit searches are recorded
as negatives, because a negative is a finding.

Targets, from the directive:

- **Target 1** — the #1 blocker: DAFoam v5 discrete adjoint,
  `KSPConvergedReason -9` (`DIVERGED_NANORINF`) at GMRES iteration 0 on NASA
  hump (51,626 cells) and CBFS (21,000 cells); separately `-5`
  (`DIVERGED_BREAKDOWN`) on ONERA M6 at every mesh size. Memory refuted. The
  dumped `dRdWTPC` is exactly singular under `scipy.spilu` (no pivoting) but
  solvable by `splu` (partial pivoting) to 2.5e-12.
- **Target 2** — A4's open mechanism: gradient depends on the parallel
  decomposition (scotch np=4: 8.95% error; simple 4x1x1: 0.00054%; np=1 clean;
  converged wrong answer, not a tolerance issue).
- **idwarp#57 status check** (read-only).

---

## Target 1 — leads, ranked by likelihood

### Lead 1.1 — the correction that reorders everything else: the ILU zero-pivot shift is ALREADY hard-coded, and has been since at least 2022

The obvious remedy for a zero pivot — `PCFactorSetShiftType` — is not a lever
we can pull, because upstream already pulled it. Main-branch
`DALinearEqn.C` (fetched raw from `mdolab/dafoam` main, sha `60699b5c`,
"Merge v5 into main", 2026-05-05) lines 270–272, immediately after the
hard-coded `PCSetType(MLRsubpc, PCILU)`:

```c
PCFactorSetPivotInBlocks(MLRsubpc, PETSC_TRUE);
PCFactorSetShiftType(MLRsubpc, MAT_SHIFT_NONZERO);
PCFactorSetShiftAmount(MLRsubpc, PETSC_DECIDE);
```

The same three lines were verified present at shas `d4ccdb4e` (2022-03-21),
`cdb0ca94` (v4 merge, 2025-01-30) and `522bada7` (2025-09-12), all fetched raw
this session. Source: https://raw.githubusercontent.com/mdolab/dafoam/main/src/adjoint/DALinearEqn/DALinearEqn.C
plus the per-sha raw fetches; commit list from
https://api.github.com/repos/mdolab/dafoam/commits?path=src/adjoint/DALinearEqn/DALinearEqn.C
(tier: READ IN FULL, all).

Where it applies: any docket item phrased "try `-pc_factor_shift_type
nonzero`" is dead on arrival — it is almost certainly already on in our
deployed v5. Where it does not: **our deployed container's copy has not been
read**. First action before anything else: read
`src/adjoint/DALinearEqn/DALinearEqn.C` inside the lab's DAFoam container and
confirm lines equivalent to the above exist. Five minutes, and it decides
whether every downstream inference here stands.

What NANORINF-despite-shift means, per PETSc's own developers:
`DIVERGED_NANORINF` "means it found a zero pivot either in the factorization
**or in the first attempt to do a triangular solve**" (Barry Smith), and "ILU
is defined by having no pivoting" (Matthew Knepley) — petsc-users thread,
https://www.mail-archive.com/petsc-users@mcs.anl.gov/msg26971.html (tier: READ
IN FULL). `MAT_SHIFT_NONZERO` can complete a factorization whose triangular
solves then overflow — which fits iteration-0 failure, and fits R5's measured
14–16-order diagonal spread on the M6 family. The shift treats the symptom at
the pivot; it does not make the factors usable.

### Lead 1.2 — the in-daOptions lever that matches our own splu-vs-spilu evidence: `jacMatReOrdering`

Our decisive measurement is that the dumped PC matrix is singular under no-pivot
`spilu` but fine under pivoting `splu`. Pivoting is elimination-order freedom.
The only elimination-order lever DAFoam exposes without recompiling is
`adjEqnOption: {"jacMatReOrdering": ...}` — accepted values in v5 source:
`natural`, `nd`, `rcm`, `1wd`, `qmd` (`DALinearEqn.C` lines 280–306, READ IN
FULL). Upstream's own inline advice, `pyDAFoam.py` lines 516–518 (fetched raw,
main): *"If the adjoint does not converge, try to increase pcFillLevel to 2, or
try `jacMatReOrdering: "nd"`"*. The maintainer repeats both in discussion #74,
https://github.com/mdolab/dafoam/discussions/74 (tier: READ IN FULL): pcFillLevel
2, `jacMatReOrdering` "rcm" or "natural", asmOverlap 1, localPCIters 1, plus
`normalizeStates` scaling and mesh advice (mean y+ ~30 with wall functions to
cut aspect ratio).

Note for the record: **`gmresPCMatOrdering` does not exist in v5** — grep of
the fetched main-branch `pyDAFoam.py` finds no such key. The v5 name is
`jacMatReOrdering`, default `rcm`.

What to try, cheapest first, on the hump (smallest NANORINF case): sweep
`jacMatReOrdering` over `nd`, `qmd`, `1wd`, `natural` at `pcFillLevel: 1`, then
the winner at `pcFillLevel: 2`. A different elimination order that dodges the
structural zero pivot is the exact in-code analog of what `splu`'s pivoting did
offline. Zero recompile, one daOptions line per run.

### Lead 1.3 — PETSc's purpose-built fix is unreachable at runtime; the patch site is one line

PETSc's dedicated remedy for zero-on-the-diagonal ILU is
`-pc_factor_nonzeros_along_diagonal` (API: `PCFactorReorderForNonzeroDiagonal`)
— recommended alongside the shift by Barry Smith in the petsc-users thread
above, and by the PETSc FAQ for "detected zero pivot" (https://petsc.org/release/faq/,
tier: READ IN FULL; shift-type manual page:
https://petsc.org/release/manualpages/PC/PCFactorSetShiftType/, READ IN FULL —
`-pc_factor_shift_type`, `-pc_factor_shift_amount`).

It cannot be reached from `PETSC_OPTIONS` in DAFoam: `KSPSetFromOptions(ksp)`
is called once, at `DALinearEqn.C:138`, **before** the ASM sub-KSPs exist; the
sub-PCs are then configured purely by API calls (lines 262–309), so
`-sub_pc_factor_*` options are never read. R5 already established the PC
*family* is compiled in; this extends it: the sub-PC *factor options* are too.

If Lead 1.2's ordering sweep fails, the minimal source patch is one line next
to the existing shift calls (line ~270):
`PCFactorReorderForNonzeroDiagonal(MLRsubpc, 1.0e-10);` — the direct
in-solver analog of our splu result. That is a recompile of `libDASolver.so`,
so it goes to the docket as a proposal, not a casual edit.

### Lead 1.4 — for the hump and CBFS specifically: v5 has a fixed-point adjoint that bypasses GMRES+ILU entirely

v5 exposes `adjEqnSolMethod: "fixedPoint"` (default `"Krylov"`),
`pyDAFoam.py` lines 326–327, with `fpMaxIters`, `fpRelTol`, `fpMinResTolDiff`,
`fpPCUpwind` under `adjEqnOption`. Implementation entry:
`DASimpleFoam.C:216ff` ("Solving the adjoint using consistent fixed-point
iteration method...") — i.e. it is implemented for `DASimpleFoam`, exactly the
solver class of the hump and CBFS cases (both incompressible SA). Fetched from
the shallow clone of `mdolab/dafoam` main this session (tier: READ IN FULL).
If the Krylov path's ILU is structurally unfactorable on these cases, the
fixed-point path never builds it. One daOptions line; gradient still must pass
the lab's FD verification rule before anything is claimed.

### Lead 1.5 — for ONERA M6 (`DARhoSimpleCFoam`, the `-5` family): `transonicPCOption: 1`, apparently never set here

What it does, from source (`DAResidualRhoSimpleCFoam.C:172–176`, READ IN FULL):
when assembling the **PC matrix only**, it drops the `fvm::div(phid, p)` term
from the pressure equation — *"for PC we do not include the div(phid, p) term,
this improves the convergence"* — i.e. it deliberately **simplifies** the PC
toward diagonal dominance rather than strengthening it. The official transonic
NACA0012 tutorial sets it: `"transonicPCOption": 1` at line 74 of
https://raw.githubusercontent.com/DAFoam/tutorials/main/NACA0012_Airfoil/transonic/runScript.py
(tier: READ IN FULL), alongside `"adjEqnOption": {"gmresRelTol": 1.0e-6,
"pcFillLevel": 1, "jacMatReOrdering": "rcm"}`. The maintainer recommends it for
transonic cases in discussion #74. R5's record does not mention it, and the
default is `-1` (off, `pyDAFoam.py:389`).

This is philosophically aligned with R5's own §3 finding that *strengthening*
the PC (fill 1, Richardson) reintroduced collapse: the MDO-lab lineage
consistently weakens/approximates the transonic PC instead. Same lore in
ADflow's options (https://mdolab-adflow.readthedocs-hosted.com/en/latest/options.html,
tier: READ IN FULL): `approxPC: True` (approximate Jacobian for the adjoint
PC), `viscPC: False` (drop cross-derivative terms in the PC), `matrixOrdering:
RCM`, `adjointSubspaceSize: 100` — the ADflow default PC is deliberately a
*worse* Jacobian that factors *better*. The `useAD` doc block in `pyDAFoam.py`
cites the same Kenway et al. 2019 review the lab already holds (INTERNAL tier,
via R5).

What to try on the M6 reproducer: `transonicPCOption: 1` on top of the
confirmed-sane `normalizeResiduals=None` baseline, before any further fill/
Richardson experiments. Also nearly free: `adjEqnOption: {"KSPCalcSingularVal":
1}` prints `sMax/sMin` from `KSPComputeExtremeSingularValues`
(`DALinearEqn.C:406–412`) — a direct conditioning readout to put beside R5's
matrix-scale measurements.

### Negative results, recorded

- GitHub issue search `repo:mdolab/dafoam NANORINF`: **0 hits**; `repo:mdolab/dafoam
  adjoint diverged`: **0 hits** (api.github.com/search/issues, 2026-08-04).
  Caveat learned this pass: the REST issue search does **not** index GitHub
  Discussions, where DAFoam's traffic actually lives; discussions were searched
  separately via web search and github.com/search?type=discussions.
- No upstream thread was found reporting DIVERGED_NANORINF or a zero-pivot ILU
  failure in DAFoam itself. The zero-pivot literature is all PETSc-side. If the
  lab pins the hump/CBFS singular-PC mechanism, an upstream report would be
  novel — docket-proposal candidate (charter §6, trigger 3/4 analog), posting
  only on Katie's call.

---

## Target 2 — A4's decomposition-dependent gradient: candidate mechanisms, each with a discriminating experiment

No upstream report of a decomposition-dependent DAFoam gradient was found
(searches recorded above and in the protocol doc; GitHub discussions searched
for gradient×processors variants — nothing on point). Upstream's published
position is the opposite: the DAFoam AIAA-J paper reports average adjoint
derivative error under 0.1% at up to 1536 cores
(https://arc.aiaa.org/doi/10.2514/1.J058853 — tier: SEARCH-EXCERPT, abstract
level only; nothing further asserted from it). A pinned mechanism here
contradicts a published upstream claim → LITERATURE_CHARTER §6 trigger 3, a
proposal is mandatory once A4 closes.

### Mechanism M1 — ASM+ILU is decomposition-dependent by construction, and ill-conditioning converts "same tolerance" into "different answer"

PETSc FAQ, verbatim territory (https://petsc.org/release/faq/, READ IN FULL):
"convergence of many preconditioners in PETSc, including the default parallel
preconditioner block Jacobi, depends on the number of processes" — the
*algorithm* changes with the partition, not just the arithmetic order. On its
own this only changes the iteration path. But with conditioning at the scale R5
measured (diagonal spread 1e14–1e16), a relative-residual stop of 1e-6 leaves a
solution ball whose diameter scales with the conditioning — two partitions can
both "converge" to points 8.95% apart in a derived functional. And note the
acceptance gate: `DALinearEqn.C:422–434` passes a solve when
`relResRatio = finalRes/initRes/gmresRelTol < gmresTolDiff` with
`gmresTolDiff` defaulting to **100** — a run printing "Residual tolerance
satisfied" may sit two orders above nominal tolerance.

**Discriminating experiment:** cross-residual. Take the scotch-np4 adjoint
vector ψ, reconstruct to serial ordering, and evaluate the true residual
‖b − Aᵀψ‖ under the np=1 operator. If small: same operator, same system —
the difference lives inside the ill-conditioned tolerance ball (M1), and
tightening `gmresRelTol` to 1e-10 must shrink the 8.95%. If large: the
*system itself* (operator or RHS) differs with decomposition — M2/M3. Also
flip on `KSPCalcSingularVal: 1` for both partitions and log sMax/sMin.

### Mechanism M2 — inter-processor connectivity in the PC/partials assembly, exercised harder by scotch's irregular boundaries

`DAJacCon.C` (main, shallow clone, READ IN FULL) contains bespoke
inter-processor boundary connectivity machinery — `neiBFaceGlobalCompact`,
"calculate the connectivity across processors", repeated "check whether this
face is coupled (cyclic or processor?)" branches (lines ~352–1088). A simple
4x1x1 decomposition has planar processor patches; scotch produces corners
where a cell's distance-2 stencil crosses **two** processor boundaries. A
defect there changes `dRdWTPC` — which, in the Jacobian-free reverse-AD mode,
is *only* the preconditioner and cannot move a truly converged answer. So M2
produces the observed signature only via M1's loose-gate amplification, or via
any partial that is actually computed by coloring/FD
(`adjUseColoring`/`adjPartDerivFDStep`, `pyDAFoam.py:383,527`) rather than AD.

**Discriminating experiment:** dump `dRdWTPC` (`-ksp_view_pmat binary:` — the
R5 technique, already proven) under scotch-np4 and simple-4x1x1, permute both
to global cell ordering, and diff the assembled entries. Identical matrices
exonerate M2 entirely; differing entries localized at processor-corner cells
convict it. Secondary: rerun the smallest A4 case with `adjUseColoring: False`
under scotch-np4 — if the gradient snaps to the np=1 value, the coloring path
is the carrier.

### Mechanism M3 — the difference enters upstream or downstream of the linear solve: RHS (dFdW) or the mesh-derivative chain (IDWarp warpDeriv)

If the cross-residual test (M1) says the system differs, the candidates are
the RHS and the total-derivative chain. IDWarp is the standing suspect this
lab already has under indictment (`ROOTCAUSE_getRotationMatrix3d.md`,
`UPSTREAM_BUG_REPORT_mesh_warpDeriv.md`): upstream's own
https://github.com/mdolab/idwarp/issues/57 (READ IN FULL via API) reports
`verifyWarpDeriv` errors of 216–218% on the `inflate_cube` test where "errors
should be ~<1e-4" — i.e. upstream's warp-derivative verification already fails
somewhere, and scotch-vs-simple changes exactly what IDWarp's parallel
algebra sees (point ownership, halo layout). Separately, a force-objective
integration defect at processor-adjacent wall faces would already move the
*primal* objective.

**Discriminating experiments:** (a) bitwise-compare the primal objective value
np=1 vs scotch-np4 — if it moves beyond roundoff, stop: the defect is in the
primal-side integration, not the adjoint. (b) Compare dObj/dXv (volume-mesh
coordinate gradient, upstream of warpDeriv — the lab already has the np=1
harness: `a5_dobjdxv_np1_run1.log`) between np=1 and scotch-np4. dObj/dXv
matching while dObj/dFFD differs convicts the IDWarp/DVGeo leg; dObj/dXv
already differing puts it back inside DAFoam's adjoint/partials (M1/M2).

Run order that spends least: M3(a) bitwise primal check (free, logs may already
exist) → M1 cross-residual (one np=1 matvec harness) → M3(b) dObj/dXv at np=4
scotch → M2 PC-matrix diff → M2 coloring-off run (most expensive).

---

## idwarp#57 — status check, as directed

https://api.github.com/repos/mdolab/idwarp/issues/57, fetched 2026-08-04:
**open, zero comments, no activity of any kind since creation on 2021-07-14**
(created 15:09:49Z, last updated 15:09:57Z — eight seconds later, same day).
Nothing was posted, per the read-only rule. The lab's prepared comment
continues to await Katie's call; five years of upstream silence is itself a
datum for her decision on whether a comment or a full issue-with-reproducer is
the right instrument.

## Docket-proposal triggers fired by this reading (charter §6)

1. **Concrete untried settables exist** → propose the Target-1 ladder:
   deployed-source shift check (5 min, gates everything) → `jacMatReOrdering`
   sweep on hump → `transonicPCOption: 1` + `KSPCalcSingularVal` on M6 →
   `adjEqnSolMethod: fixedPoint` on hump/CBFS → (only if all fail) one-line
   `PCFactorReorderForNonzeroDiagonal` source patch.
2. **A published claim contradicts our measurement** (upstream <0.1% at 1536
   cores vs A4's 8.95% at np=4) → propose the M1/M2/M3 discriminating ladder
   above, in the stated cost order.
3. **No upstream report exists for either pinned mechanism** → once pinned,
   propose upstream filings (hump singular-PC; A4 decomposition dependence),
   drafted for Katie's call, nothing posted before it.
