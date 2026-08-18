# Liaison novelty sweep — has anyone ever reported the decomposition-adjoint defect, or the rotation-guard defect beyond idwarp#57?

Date: 2026-08-04 (all searches and fetches run 18:32–18:55 UTC this day).
Method: `docs/standards/PROBLEM_RESEARCH_PROTOCOL.md` (v0.2 as of this pass — the
edits this pass forced are in that file's history).
Read-only discipline held: nothing was posted, no account touched, every URL cited
below was actually fetched this session. Quotes marked **[verbatim]** were pulled by
a dedicated verbatim fetch of the page; quotes without that mark came through a
summarizing fetch of the same page and are flagged **[via page summary]** — reliable
for content, not letter-for-letter.

Targets, from the directive:

- **Target D** (decomposition): the verified DAFoam v5 defect — parallel matrix-free
  transposed-Jacobian product wrong under scotch decomposition on a
  refinement-interface mesh; GMRES converges to 1e-6 on an operator that is not the
  transpose Jacobian; gradient off ~9%, converged-wrong
  (`UPSTREAM_BUG_REPORT_decomposition_adjoint.md`). Has this EVER been reported,
  hinted at, or worked around?
- **Target R** (rotation): the IDWarp `getRotationMatrix3d` degenerate-branch defect
  — any community trace beyond `mdolab/idwarp#57`?
- **Target S** (sub-LU): what upstream docs/threads say about
  `jacMatReOrdering`/adjoint-PC options vs the lab's sub-LU unblock (commit
  `1cd44c04`, `DAFOAM_SUBPC_TYPE=lu`); does anyone discuss the ILU singularity or
  recommend the sub-LU class of fix?

---

## 1. Query log — every search, every hit or explicit negative

63 recorded searches across 10 venues; ~25 further pages read in full. Searches were
run 2026-08-04 unless noted. "0" means the venue's own search returned zero results
for that query.

### Venue 1 — mdolab/dafoam issue tracker (REST: `api.github.com/search/issues?q=repo:mdolab/dafoam+<q>`, all states, issues+PRs)

| # | query | hits | disposition |
|---|---|---|---|
| 1 | `scotch` | 0 | negative |
| 2 | `decomposition` | 1 | **#101** — the sweep's issue-tracker near-miss, resolved below |
| 3 | `decomposePar` | 2 | #803 (PR, passes CLI args through, no defect), #9 (broken tarball, unrelated) |
| 4 | `check_totals` | 0 | negative |
| 5 | `gradient processors` | 0 | negative |
| 6 | `adjoint parallel wrong` | 0 | negative |
| 7 | `halo` | 0 | negative |
| 8 | `processor boundary` | 0 | negative |
| 9 | `nProcs gradient` | 0 | negative |
| 10 | `sensitivity mismatch` | 0 | negative |
| 11 | `mpirun` | 5 | #988 (purgeWrite housekeeping), #989 (v5 regression-test MPI crash, no gradients involved — read in full), #789 (option typo), #838 (CRM run error), #101 |
| 12 | `ILU` | 1 | #1011 (open, 2026-07-29, adjoint non-convergence on official tutorials — Target S, §4) |
| 13 | `kahip` | 0 | negative (the kahip feature landed via v5 merge `60699b5c`; confirmed via `search/commits`, 1 hit) |
| 14 | `"run it in serial"` | 0 | negative |

### Venue 2 — mdolab/dafoam Discussions (HTML search `github.com/mdolab/dafoam/discussions?discussions_q=<q>`, fetched unauthenticated — the REST gap of protocol trap #1 covered)

| # | query | hits | disposition |
|---|---|---|---|
| 15 | `alphaPorosity` | 21 | located **#102**, the converted form of issue #101 — resolved below |
| 16 | `scotch` | 0 | negative — **no discussion in the project's history mentions scotch** |
| 17 | `decomposition` | 6 | #952, #972, #885, #102, #380, #428 — all read or triaged below |
| 18 | `decomposePar` | 4 | #930, #263, #380, #428 — none report a gradient defect |
| 19 | `check_totals` | 4 | #946, #972, #905, #714 — all read below |
| 20 | `parallel gradient` | 13 | superset of the above plus #739, #503, #542, #466, #433, #250, #70 — none on point |
| 21 | `NANORINF` | 0 | negative |
| 22 | `zero pivot` | 0 | negative |
| 23 | `jacMatReOrdering` | 0 | negative (option discussed only under its prose name in #74/#952) |
| 24 | `ILU` | 10 | #1007, #1002, #972, #952, #885, #739, #506, #441, #351, #348 — convergence traffic only; none mention singularity or LU sub-blocks |
| 25 | `pcFillLevel` | 22 | includes #74, #379, #885 — the maintainer's remedy ladder, §4 |
| 26 | `finite difference adjoint disagree` | 0 | negative |
| 27 | `superlu OR mumps OR "direct solver"` | 0 | negative — **no thread has ever proposed a direct or sub-direct solve** |
| 28 | `gradient accuracy` | 13 | #714 read below |
| 29 | `verify total derivatives` | 7 | #905, #914 read below |
| 30 | `halo` | 0 | negative |
| 31 | `processor boundary` | 9 | first attempt returned a load-error banner (recorded, retried per protocol); retry: #972, #598, #74, #542, #504, #466, #428, #380, #390 — #598 and #504 read below |
| 32 | `different results parallel` | 6 | #1004, #138, #542, #504, #503, #102 — #504 read below |

### Venue 3 — mdolab/idwarp (Target R)

| # | query | hits | disposition |
|---|---|---|---|
| 33 | REST `rotation` | 1 | #103 — axisymmetric-capability feature request, unrelated |
| 34 | REST `warpDeriv` | 0 | negative |
| 35 | REST `useRotations` | 1 | #85 — `specifiedSurfaces` deformation question, unrelated |
| 36 | REST `sign` | 0 | negative |
| 37 | REST `derivative wrong` | 0 | negative |
| 38 | REST `decomposition` | 0 | negative |
| 39 | REST `verifyWarpDeriv` | 3 | **#57** (the known issue), #54 (PETSc-compat PR — read in full: mentions testflo tests passing, nothing about the failing derivative), #36 (testflo maintenance PR) |
| 40 | REST `inflate_cube` | 1 | #57 only |
| 41 | Discussions listing (`github.com/mdolab/idwarp/discussions`) | 3 total | #98 (BC definition), #93 (installation), #94 (saving FFD mesh) — none derivative-related |

### Venue 4 — mdolab/pyofm

| # | query | hits | disposition |
|---|---|---|---|
| 42 | full issue listing, all states (16 issues) | 16 | all build/packaging/API; zero adjoint, decomposition, or derivative content |

### Venue 5 — mdolab/MACH-Aero

| # | query | hits | disposition |
|---|---|---|---|
| 43 | REST `warpDeriv` | 0 | negative |
| 44 | REST `rotation guard` | 0 | negative |
| 45 | REST `decomposition gradient` | 0 | negative |
| 46 | Discussions `warpDeriv` | 0 | "There are no matching discussions" |

### Venue 6 — mdolab/adflow

| # | query | hits | disposition |
|---|---|---|---|
| 47 | REST `gradient processors` | 2 | #284 (slices/inverse design), #63 (turbulence advection order) — both unrelated |
| 48 | REST `adjoint decomposition` | 0 | negative |
| 49 | REST `partition gradient` | 0 | negative |

### Venue 7 — OpenMDAO/OpenMDAO

| # | query | hits | disposition |
|---|---|---|---|
| 50 | REST `check_totals mpi different` | 0 | negative |
| 51 | REST `"number of processors" gradient` | 0 | negative |

### Venue 8 — GitHub, global (all public repos)

| # | query | hits | disposition |
|---|---|---|---|
| 52 | `getRotationMatrix3d` | 0 | **zero issues/PRs anywhere on GitHub mention the function by name** |
| 53 | `verifyWarpDeriv` (global) | 3 | all three are the mdolab/idwarp items of query 39 |
| 54 | `"gradient depends on the number of processors"` | 0 | negative |
| 55 | `"different gradient" "number of processors" adjoint` | 0 | negative |
| 56 | `CoDiPack halo adjoint wrong` | 0 | negative |
| 57 | `search/commits repo:mdolab/dafoam kahip` | 1 | v5 merge `60699b5c` (2026-05-05) — kahip is now a shipped option, docs silent on it |

### Venue 9 — web + scholar (WebSearch, US index)

| # | query | on-point hits | disposition |
|---|---|---|---|
| 58 | `dafoam.github.io adjEqnOption jacMatReOrdering options documentation` | — | located the doc pages fetched in §4 |
| 59 | `adjointOptimisationFoam gradient different decomposePar parallel CFD-Online` | 0 | manual + generic parallel threads only; no decomposition-dependent-adjoint report for the NTUA adjoint either |
| 60 | `OpenFOAM adjoint sensitivity different serial parallel "number of processors" forum` | 0 | hits are the RWTH MPI-parallel discrete-adjoint OpenFOAM papers (scaling/memory, not wrongness) and SU2 hybrid-parallel adjoint — no forum thread reporting decomposition-dependent gradients |
| 61 | `"discrete adjoint" gradient "domain decomposition" inconsistent OR wrong OR "depends on" partitioning MPI` | 0 | literature on adjoint consistency of time-steppers and on DD preconditioner convergence vs partition shape; nothing reporting a partition-dependent discrete-adjoint gradient defect |
| 62 | `DAFoam gradient wrong parallel processors different scotch adjoint` | 0 | top hit is the DAFoam AIAA-J paper itself (<0.1% average adjoint derivative error at up to 1536 cores) — the published claim our measurement contradicts |
| 63 | `IDWarp getRotationMatrix3d OR useRotations derivative bug OR wrong` | 0 | only the source file itself and API docs; no report anywhere |

### Venue 10 — PETSc (Target S corroboration; §4)

petsc.org FAQ, `PCASM` manual page, and mail-archive petsc-users searches/threads —
itemized in §4 (4 fetches).

---

## 2. Threads read in full, and what each one is

All fetched 2026-08-04. dafoam numbers are `github.com/mdolab/dafoam/discussions/<n>`
unless marked "issue".

| thread | date | one-line content | bearing on Target D |
|---|---|---|---|
| issue #101 → **#102** | 2021-03 | "Sensitivities of alphaPorosity are messed up on mpirun" — np=4 sensitivity field looks unphysical vs serial; reporter guesses "maybe it's a domain decomposition issue". Maintainer (friedenhe, 2021-03-24): "We checked the sensitivity between the serial and parallel case and they matched." — the visual difference was **cell-ordering in the written field**, not the gradient **[via page summary]**. Issue was closed+locked by conversion; the answer lives only in the discussion. | Resolved near-miss: upstream *investigated* serial-vs-parallel equality once, on a v1-era topology case, and found it held. Not our defect. |
| **#946** | 2026-02-24 | PeriodicHill optimization diverges; user's check_totals shows 93.92% analytic-vs-FD error. Maintainer (friedenhe, 2026-02-26): **[verbatim]** "The PH case' derivatives are not accurate when running in parallel. You have to run it in serial." No mechanism offered. | **Strongest near-miss found anywhere.** Explicit maintainer acknowledgement that parallel derivatives are wrong for one case — scoped to the periodic-boundary case, no mechanism, no decomposition-method dependence, wrongness attributed to the case not the operator. |
| #379 | 2022-12 | Adjoint fails on >4 cores on HPC. Maintainer: "The periodic hill case is known to have issues when running in parallel (because it has periodic boundaries; we haven't gotten a chance to debug it yet)." Other cases "can run in parallel without an issue." **[via page summary]** | Same acknowledgement four years earlier: parallel trouble = coupled patches, known, undebugged. |
| **#972** | 2026-04-21 | DATurboFoam + cyclicAMI (v4.0.3): adjoint KSP false-converges (residual collapses to ~1e-313) then produces 1e11–1e15 sensitivities. Maintainer: cyclicAMI "does not appear to support parallel runs"; fixes = `singleProcessorFaceSets` (keep all AMI faces on one rank), `adjFieldCouplingColoring`, FS preconditioner. **[via page summary]** | Nearest *mechanistic* relative: a coupled-interface whose parallel adjoint treatment is wrong, worked around by removing the interface from the partition. But: AMI patches (not plain processor boundaries), v4 assembly path, and the symptom is garbage output — not a cleanly converged 9%-wrong gradient. |
| **#885** | 2025-09-22 | "As the number of computational cores increases, the convergence performance of the adjoint equation deteriorates." Diagnosis in-thread: more ranks → more off-diagonal blocks lost by block-ILU; user shows KAHIP partitioning improves the preconditioner; maintainer adds kahip support ("We have added this feature into a recent commit", 2025-12-09). asmOverlap 4 also helped. **[via page summary]** | Upstream's clearest acknowledgement that **decomposition affects the adjoint solve** — but strictly its *convergence rate*. Nobody in the thread reports, or checks, the converged gradient value against decomposition. |
| #952 | 2026-03-07 | SST adjoint converges slowly; maintainer recommendation includes "use the kahip decomposition", citing #885. **[via page summary]** | Decomposition-method advice exists upstream — for speed, never for correctness. |
| #714 | 2024-12-04 | Symmetric FFD points give asymmetric gradients after deformation; maintainer attributes to pyGeo FFD handling, present in v3 and v4; workaround = move point pairs together. No parallel content. | Not decomposition. (Adjacent to the lab's pyGeo/IDWarp chain findings, worth remembering.) |
| #905 | 2025-11-05 | NACA0012 check_totals errors >100%; resolved as FD step size + mesh first-layer height. Serial. | Not decomposition. |
| #914 | 2025-11-21 | dCD 1.27% analytic-vs-FD deviation; maintainer: "the gradient accuracy is very acceptable for practical aerodynamic optimization." **[via page summary]** | Documents upstream's acceptance threshold (~1%) — context for why a 9% defect with a benign-regime test matrix could live undetected. |
| #598 | 2024-03-01 | User-added output field shows `inf` at processor boundaries in a field-inversion model; fix = initialize from an existing field + `correctBoundaryConditions()`. | Processor-boundary *symptom* family, user-code cause. Not the adjoint operator. |
| #504 | 2023-10-23 | Custom objective returns 0 in parallel; cause = user interpolation assuming all ranks own boundary data (+ `Info` printing on rank 0 only). | Parallel-vs-serial difference, user-code cause. |
| #739 | 2025-01-16 | Parallel gradient run dies; maintainer: likely memory, lower ILU fill. | Not decomposition. |
| #1002 / issue #1011 | 2026-07 | Adjoint non-convergence on official DArhoSimpleCFoam tutorials (v5), documented remedy ladder tried and failing; maintainer converted to issue 2026-07-29 ("will check it out"), unresolved. | Target S, §4. |
| issue #989 | 2026-05-26 | v5 regression test MPI crash ("Node communicator(s) already created"), open, 0 comments. | Environment crash, not gradients. |
| idwarp PR #54 | 2021-07 | PETSc `VecGetValues` compatibility; testflo passes. | Confirms `verifyWarpDeriv` mentions in the tracker are maintenance-only. |

## 3. Verdicts

### Target D — the decomposition-adjoint defect

**No prior report found, under 63 recorded searches across 10 venues** (mdolab/dafoam
issues; dafoam Discussions; mdolab/idwarp issues+discussions; mdolab/pyofm;
mdolab/MACH-Aero issues+discussions; mdolab/adflow; OpenMDAO/OpenMDAO; GitHub global
search; web/scholar; PETSc lists). Specifically, no one has ever reported: a
DAFoam gradient that is *converged and wrong* under one decomposition and correct
under another; any scotch-vs-simple dependence (the word "scotch" appears in **zero**
issues and **zero** discussions in the project's history); any transpose-operator
inconsistency; or anything on a plain wall-bounded case without coupled patches.

What the community record *does* contain — and what makes the lab's report sharper,
not weaker:

1. Upstream **acknowledges parallel-wrong derivatives for exactly one case family**:
   periodic/AMI coupled patches (#379 2022, #946 2026 — "You have to run it in
   serial"; #972 2026 — AMI faces forced onto one rank). Every acknowledgement
   attributes the wrongness to the *coupled patch*, prescribes avoidance, and names
   no mechanism. The lab's Ahmed-body case has **no coupled patches**: it shows the
   same class of parallel adjoint wrongness arising from **ordinary processor
   boundaries**, which is precisely the thing upstream's known-issue lore says is
   safe ("other cases can run in parallel without an issue", #379).
2. Upstream **acknowledges decomposition affects the adjoint** — but only its
   convergence speed (#885, #952; kahip added 2025-12), never the converged value.
3. The one time serial-vs-parallel gradient equality was *checked* upstream (#102,
   2021, v1-era), it passed, and the discrepancy was an output-ordering artifact.
4. The docs make **no parallel-consistency claim and give no decomposition
   guidance at all** (§4), while the shipped default is scotch
   (`pyDAFoam.py` lines 590–591, main @ `e77f0c0c`, fetched raw 2026-08-04:
   `self.decomposeParDict = {"method": "scotch", ...}`) — i.e. the defect's
   triggering configuration is the default nobody is warned about. The only
   published statement is the AIAA-J paper's <0.1% average adjoint derivative error
   at up to 1536 cores (arc.aiaa.org/doi/10.2514/1.J058853, abstract level), which
   the lab's measurement contradicts on a measured case.
   *(Correction 2026-08-05, per `DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md`, commit
   bf6ac53b — paper since READ IN FULL: that abstract sentence is two disjoint
   experiments, a runtime-only Table 2 at 1536 cores and a 102,912-cell Table 3
   accuracy study at an unstated core count, both of the v1 explicit-FD-Jacobian
   architecture. No published accuracy claim covers the measured matrix-free
   operator in parallel; the lab's report fills a declared hole rather than
   contradicting a published measurement. The exposure point — scotch as the
   unwarned shipped default — stands.)*

### Target R — the rotation-guard defect beyond idwarp#57

**No other trace found, under 17 recorded searches across 6 venues.**
`getRotationMatrix3d` appears in **zero** GitHub issues/PRs globally;
`verifyWarpDeriv` appears in exactly three mdolab/idwarp items (#57 and two
maintenance PRs that don't discuss its failure); idwarp's three discussions, the
MACH-Aero tracker and discussions, pyofm, and the open web contain nothing.
`mdolab/idwarp#57` (open since 2021-07-14, zero comments — status re-confirmed in the
2026-08-04 pass recorded in `LIAISON_RESEARCH_adjoint_conditioning.md`) remains the
sole community record of the phenomenon the lab has root-caused and patched.

### Target S — the sub-LU unblock vs upstream's playbook

**No upstream doc, issue, or discussion mentions ILU singularity, zero pivots, or a
direct/sub-direct factorization — under 8 targeted searches plus 4 doc-page reads.**
The complete upstream remedy ladder for a non-converging adjoint, assembled from
every place it is stated, is: `renumberMesh -overwrite`; `pcFillLevel` 1→2;
`jacMatReOrdering` rcm→nd/natural; `gmresRestart`/`gmresMaxIters` up; `asmOverlap`
up; upwind schemes; (since 2025-12) kahip decomposition; and for transonic cases
`transonicPCOption`. Sources, fetched 2026-08-04:

- `dafoam.github.io/get-started-runscript.html` **[verbatim]**: "The 'adjEqnOption'
  dictionary contains the adjoint linear equation solution options. If the adjoint
  does not converge, increase 'pcFillLevel' to 2. Or try 'jacMatReOrdering' : 'nd'."
- `dafoam.github.io/get-started-faq.html` **[verbatim]**: "If your adjoint equation
  is not converging well. First, please make sure you run `renumberMesh -overwrite`
  to renumber the mesh and minimize the matrix bandwidth, which is found to help
  adjoint convergence." (then the option ladder above, then schemes).
- `dafoam.github.io/doxygen/html/classdafoam_1_1pyDAFoam_1_1DAOPTION.html`
  **[verbatim]**: adjEqnOption — "These options should work for most of the case.
  If the adjoint does not converge, try to increase pcFillLevel to 2, or try
  "jacMatReOrdering": "nd"".
- Discussions #74, #885, #952, #1002 (the live remedy threads).

Nothing in that ladder changes the sub-PC *type*; the ILU choice itself is never
questioned upstream. Meanwhile #1002/#1011 (2026-07, open, unresolved) shows users
exhausting the documented ladder on *official tutorials* and stalling — the failure
mode the sub-LU switch was built for is live upstream today.

The PETSc side supplies the missing precedent: switching failing ILU sub-blocks to
LU is the PETSc developers' own canonical escalation. petsc-users
`msg24474` (Barry Smith, 2015-03-26) **[verbatim]**: "The default preconditioner
with ILU(0) on each process is not appropriate for your problem and is producing
overflow. Try -sub_pc_type lu and see if that produces a different result." And
`msg26973` (Hong, 2015-10-27) demonstrates on a zero-diagonal system that ilu with
any shift "does not converge" while `-sub_pc_type lu -sub_pc_factor_shift_type
nonzero` converges in 24 iterations. The PETSc FAQ **[verbatim]**: "The convergence
of many of the preconditioners in PETSc including the default parallel
preconditioner block Jacobi depends on the number of processes." DAFoam hard-codes
`PCSetType(MLRsubpc, PCILU)` (DALinearEqn.C, pass-1 finding, sha-pinned in
`LIAISON_RESEARCH_adjoint_conditioning.md`), and the lab's W4 harness showed
`sub_`-prefixed *factor* options do land on the deployed factor yet leave the -9
(commit `1cd44c04`) — so the sanctioned remedy is unreachable without a source
change. **An upstream PR exposing the sub-PC type as an `adjEqnOption` key (default
ilu, unchanged behavior) would be novel, one option plumb, and is backed by both the
lab's measured unblock (CBFS -9 → converged in 667 iters, three FD-verified gradient
components) and named-PETSc-developer precedent.**

## 4. Strongest near-miss, named

Discussion **#946** (with its 2022 antecedent #379): a DAFoam maintainer stating, in
writing, "The PH case' derivatives are not accurate when running in parallel. You
have to run it in serial." — the only place in the community record where anyone
says a DAFoam parallel derivative is *wrong* rather than *slow*. It is scoped to one
periodic-boundary case, carries no mechanism, no decomposition-method dependence,
and no follow-up. It does not anticipate the lab's finding; it does confirm upstream
has already met — and parked — the outer edge of this defect class.

## 5. Readiness assessments

**Decomposition report** (`UPSTREAM_BUG_REPORT_decomposition_adjoint.md`): the sweep
converts the report's novelty clause from "we found no prior report" (pass 1's
handful of queries) to a citable exhaustive negative: *no prior report under 63
recorded searches across 10 venues, 2026-08-04*, with the scotch term at literally
zero occurrences in the project's history. It also arms the report against the two
likeliest maintainer replies: "known issue with coupled patches" — answered, the
measured case has no coupled patches, and the known-issue lore (#379/#946/#972)
explicitly exempts such cases; and "decomposition only affects convergence" —
answered, #885/#952 concern convergence rate while our KSP converges (reason 2,
true-residual 1.7e-07) to a wrong solution, which is the discriminating cross-residual
measurement. Recommended additions to the report before filing: cite #946 and #379
as prior *partial* acknowledgements (also useful precedent that gradient-wrongness
reports are taken and answered there), and note the scotch default of
`pyDAFoam.py:590` to establish exposure. The remaining gap is unchanged and is not a
novelty gap: reproducer on an official tutorial, and mechanism-to-a-line.

**Rotation report** (`UPSTREAM_BUG_REPORT_mesh_warpDeriv.md`): the sweep confirms
idwarp#57 is the sole community trace — zero mentions of the function name anywhere
on GitHub, zero derivative-related idwarp discussions, zero MACH-Aero traffic — so
the prepared comment-on-#57 strategy stands, now with a citable negative that nobody
else has hit-and-reported it in five years (consistent with the mechanism: the
defect needs a verifyWarpDeriv-grade check with a real or captured seed, which the
random-seed default hides). The report is submission-ready per its own checklist;
this sweep closes its last open external question. Both filings remain drafts
awaiting Katie's call; nothing was posted.

## 6. Files behind this sweep

- This memo (the query log is the record; raw JSON for every REST query under the
  session scratchpad `sweep/`, not committed — the queries above are exact and
  re-runnable).
- Protocol edits from this pass: `docs/standards/PROBLEM_RESEARCH_PROTOCOL.md` v0.2.
- Pass-1 record (methods + Target-1/2 leads this pass builds on):
  `LIAISON_RESEARCH_adjoint_conditioning.md`.
