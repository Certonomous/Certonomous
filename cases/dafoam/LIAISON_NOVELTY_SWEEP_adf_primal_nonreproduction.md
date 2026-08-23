# Liaison novelty sweep, FULL PROTOCOL — has anyone reported that DAFoam's forward-AD build does not reproduce the plain build's primal?

> **NOT FILED ANYWHERE. Nothing was posted, commented, opened, registered or uploaded.** Every
> request recorded below is a `GET`. No account was touched, no form submitted. Filing is
> **Sanaa's decision alone** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

Date: **2026-08-23**, all searches 19:39–19:58 UTC.
Target: `cases/dafoam/DEFECT_CANDIDATE_adf_primal_nonreproduction.md` (**D460**, committed `757eccf0`)
— the finding that `libDASolverADF.so` does not reproduce the plain build's primal on A6 N=16, and
its §8 adjacent finding, the `-1e10` false-convergence print.
Method: `docs/standards/PROBLEM_RESEARCH_PROTOCOL.md` v0.2, §1a and §5a.
Prepared by the DAFoam team, lab-lane, on the dafoam-supervisor's phase-1 brief.

**This sweep closes blocker 1 of the two named in D460's opening block.** It is the full-protocol
sweep the candidate said was missing: **101 recorded searches across 13 venues**, against the house
protocol's 63 across 10 (`LIAISON_NOVELTY_SWEEP_decomposition_defect.md` §1).

---

## 0. THE HEADLINE, STATED FIRST BECAUSE IT REVERSES THE PARTIAL SWEEP'S ANSWER

**D460 §9.4 says "No prior art was found for either finding." After the full sweep that sentence is
no longer correct as written, and the candidate must not be filed while it stands.**

The partial sweep covered 4 venues. It did not cover the **AD-patched OpenFOAM forks' own issue
trackers** — and that is exactly where the prior art lives. Two items, both authored by
**`friedenhe`**, the DAFoam lead maintainer:

| item | date | state | what it says |
|---|---|---|---|
| **`DAFoam/OpenFOAM-AD` #2** — *"PBiCGStab/DILU fvSolution generated wrong flow results"* | **2026-01-25** | **OPEN, 0 comments** | **"If PBiCGStab/DILU are used in fvSolution, both ADR and ADF flow solvers generate wrong results (flow variables blow up rapidly)."** |
| `DAFoam/OpenFOAM-v1812-AD` #2 — *"Seg fault when running SimpleFoam in parallel"* | 2020-11-22 | closed | **"It seems that this is related to the GAMG solver for pressure in system/fvSolution. Change it to smoothSolver fixes the problem."** |

Both quotes are **[verbatim, REST]** — pulled as raw JSON body/comment text from
`api.github.com`, not through a summarizing fetch. URLs, fetched 2026-08-23:
`https://github.com/DAFoam/OpenFOAM-AD/issues/2` and
`https://github.com/DAFoam/OpenFOAM-v1812-AD/issues/2`.

`DAFoam/OpenFOAM-AD` is the **current-generation** AD fork — it is the distribution DAFoam v5
migrated to, and therefore the generation that produced the `libDASolverADF.so` D460 measured. Its
tracker holds exactly **two** issues, both open, both by the maintainer, and **one of them is
"an AD build's primal flow solution is wrong and the linear solver in `fvSolution` is the lever."**
That is D460's defect family, reported upstream, seven months before D460 was written.

**What this does to D460 is set out in §5. In one line: the novelty claim must be narrowed, the
filing posture changes from "new defect" to "second instance of your open #2, at opposite
polarity, with a digit-level measurement", and sweep 1's design as sketched in D460 §7 is
confounded and has been redesigned.**

---

## 1. Controls, run first, because no count below is readable without them (L-234)

L-234 requires a nonsense-token control on **each search surface** before any count is read, and
the planted-zero principle (`CLAUDE.md` rule 3) requires that the reader also be shown able to see
a **presence**. Both directions were run on all three surfaces.

| surface | nonsense control `zzzqqxnonsensetoken12345` | positive control | floor | reading rule |
|---|---|---|---|---|
| GitHub REST `search/issues`, `repo:mdolab/dafoam` | **0** | `adjoint` → **96** | **0** | count is literal |
| GitHub REST `search/issues`, global | **0** | (see §2.9) | **0** | count is literal |
| GitHub Discussions HTML, `mdolab/dafoam` | **1** — #883 *"Have 30 minutes? Meet with us to share your DAFoam feedback!"*, **pinned** | `adjoint` → **26** | **1** | **effective = threads − 1** |
| WebSearch (US index) | **8 topically-plausible DAFoam links returned for a nonsense token** | — | **not zero** | **counts are worthless; only on-point content counts** |

**The Discussions floor of 1 reproduces L-234 exactly**, on the same pinned thread, 24 hours later.
Without it, the clean zeros `tangent`, `primalMaxRes`, `CODI_ADF`, `ADF-Deriv`, `PBiCGStab` and
`reproducible` would each have read as one hit.

**The WebSearch control is a new trap and is recorded as such.** The query
`zzzqqxnonsensetoken12345 dafoam adjoint forward AD primal` returned eight results — the DAOPTION
doxygen page, the verifications overview, the AIAA-J paper, the releases page — i.e. the engine
**discarded the nonsense token and answered the topic**. Consequence: **on the web venues a
returned page is not evidence the query was understood, and "the search returned DAFoam's own
docs" is exactly what a nonsense query returns.** Every web-venue disposition in §2.12 is therefore
recorded as *"no page whose content is on point"*, never as a hit count.

### 1a. A protocol correction, measured this pass

`PROBLEM_RESEARCH_PROTOCOL.md` §1a states that plain `curl` to `github.com` HTML **hangs from this
host** and that the web-fetch tool must be used for Discussions. **That is no longer true.**
`curl -sSL -A "Mozilla/5.0" "https://github.com/mdolab/dafoam/discussions?discussions_q=<q>"`
returned a 260 KB page in under a second, 22 times in a row, on 2026-08-23. This matters for
evidence quality, not convenience: curl + a regex over `/mdolab/dafoam/discussions/[0-9]+` yields a
**deterministic, re-runnable, exactly reproducible thread-number list**, where the summarizing fetch
gave **inconsistent counts on the same page** — asked for `libDASolverADF` it reported
"0 distinct threads" while simultaneously describing a thread link on the page. Every Discussions
count in §2.2 is counted from fetched HTML, and the thread numbers are printed so the count can be
audited. *(Proposed protocol edit is in this directory's DRAFT files; editing the protocol is not
this lane's call.)*

A second, smaller correction: §1a says an "error while loading" banner means retry. The literal
string is present in the page template on **every** fetch, so a naive `grep` for it fires 22 times
out of 22. The retry is harmless but the test as written is useless — it must key on an **empty
results region**, not on the banner string.

---

## 2. Query log — every search, every hit, every explicit negative

All 2026-08-23. `hits` for REST venues is `total_count` from `api.github.com/search/issues`
(`state=all`, issues **and** PRs). Raw JSON for every REST query was written to the session
scratchpad and is **not** committed; every query below is exact and re-runnable.

### 2.1 Venue 1 — `mdolab/dafoam` issues + PRs (REST, 25 queries + 2 controls)

| # | query | hits | disposition |
|---|---|---|---|
| C1 | `zzzqqxnonsensetoken12345` | **0** | **control — floor is 0 here** |
| C2 | `adjoint` | **96** | **positive control — the reader can see a presence** |
| 1 | `forward AD` | 2 | #154 *Added forward AD* (PR 2021-06-28), #155 *Fix forward AD* (PR 2021-06-30). Feature exists, patched once; neither describes non-reproduction. |
| 2 | `useAD` | 0 | negative |
| 3 | `ADF` | 0 | negative |
| 4 | `CODI_ADF` | 0 | negative |
| 5 | `forward mode` | 2 | #833 *A question about the accuracy of the gradient* (open, 2025-05-21) — the near-miss, §4; #322 unrelated |
| 6 | `tangent` | **0** | negative |
| 7 | `codipack` | 1 | #586 (GPU/OGL feature request) — unrelated |
| 8 | `NaN forward` | 0 | negative |
| 9 | `ADF-Deriv` | 0 | negative |
| 10 | `libDASolverADF` | **0** | negative |
| 11 | `seedIndex` | 0 | negative |
| 12 | `primalMinIters` | **0** | negative — **§8 has no issue-tracker trace** |
| 13 | `primalMaxRes` | **0** | negative |
| 14 | `satisfied the prescribed tolerance` | 1 | #1011 (adjoint convergence on tutorials) — not the `-1e10` signature |
| 15 | `-10000000000` | **0** | negative — **the §8 tell has never been posted** |
| 16 | `primalMinResTolDiff` | 0 | negative |
| 17 | `false convergence` | 0 | negative |
| 18 | `DARhoSimpleCFoam NaN` | 0 | negative |
| 19 | `transonicPCOption` | **0** | negative |
| 20 | `GAMG` | **0** | negative — **the word appears in zero issues/PRs in the project's history** |
| 21 | `reproducib` | 0 | negative |
| 22 | `deterministic` | 0 | negative |
| 23 | `round-off` | 1 | #1013 (a slice-count input name fix) — unrelated |
| 24 | `dvName` | 0 | negative |
| 25 | `primal diverge` | 0 | negative |

### 2.2 Venue 2 — `mdolab/dafoam` Discussions (HTML, 22 queries + 2 controls; read with the −1 floor)

Counted from fetched HTML by distinct `/mdolab/dafoam/discussions/<n>` links; thread numbers printed
so the count is auditable. #883 is the pinned control thread and is present in **every** row.

| # | query | threads | **effective** | disposition |
|---|---|---|---|---|
| C3 | `zzzqqxnonsensetoken12345` | **1** | **0** | **control — floor, #883 pinned** |
| C4 | `adjoint` | 26 | 25 | **positive control** |
| 26 | `forward AD` | 24 | 23 | OR-match on common words; no title on point |
| 27 | `useAD` | 9 | 8 | includes #714, the source of issue #833 |
| 28 | `ADF` | 17 | 16 | OR-match noise |
| 29 | **`CODI_ADF`** | **1** | **0** | **clean negative** |
| 30 | `forward mode` | 23 | 22 | OR-match noise |
| 31 | **`tangent`** | **1** | **0** | **clean negative** |
| 32 | `codipack` | 9 | 8 | includes #1008 (AD for custom topology-opt variables) — not ADF-vs-plain |
| 33 | **`ADF-Deriv`** | **1** | **0** | **clean negative** |
| 34 | `libDASolverADF` | 2 | 1 | **#1015** — read in full, §3; MPI_ABORT / node-communicator, not on point |
| 35 | `seedIndex` | 7 | 6 | ordinary option traffic |
| 36 | `primalMinIters` | 2 | 1 | #970 *cyclicAMI problem* — unrelated. Effectively negative. |
| 37 | **`primalMaxRes`** | **1** | **0** | **clean negative** |
| 38 | `satisfied the prescribed tolerance` | 9 | 8 | convergence traffic; none carries the `-1e10` sentinel |
| 39 | `primalMinResTolDiff` | 13 | 12 | ordinary option traffic |
| 40 | `GAMG` | 6 | 5 | #421, #478, #646, #885, #972 — solver/convergence traffic; **none contrasts an AD build against a plain build** |
| 41 | `NaN primal` | 5 | 4 | #511, #602, #855, #984 — ordinary divergence traffic |
| 42 | `transonicPCOption` | 6 | 5 | ordinary option traffic |
| 43 | **`PBiCGStab`** | **1** | **0** | **clean negative — and see §5: the maintainer's own OpenFOAM-AD #2 is about PBiCGStab, and it has never been mentioned in DAFoam Discussions** |
| 44 | `smoothSolver` | 3 | 2 | #478, #972 |
| 45 | **`reproducible`** | **1** | **0** | **clean negative** |
| 46 | `DARhoSimpleCFoam` | 12 | 11 | ordinary solver traffic |
| 47 | `blow up` | 4 | 3 | #106, #515, #524 — ordinary divergence traffic |

**Caveat, carried forward from the partial and re-confirmed:** Discussions search **ORs**
multi-word queries, so large counts are weakly relevant. **The evidential weight sits on the
single-token clean zeros** — `CODI_ADF`, `tangent`, `ADF-Deriv`, `primalMaxRes`, `PBiCGStab`,
`reproducible` — not on the large counts.

### 2.3 Venue 3 — `mdolab/idwarp` (REST, 4 queries)

| # | query | hits | disposition |
|---|---|---|---|
| 48 | `forward mode` | 0 | negative |
| 49 | `AD` | 6 | #57 (the known rotation defect), #106, #89, #63, #66, #62 — Tapenade maintenance PRs; none on primal reproduction |
| 50 | `NaN` | 0 | negative |
| 51 | `primal` | 1 | #80 *Unable to write grid* — unrelated |

### 2.4 Venue 4 — `mdolab/pyofm` (REST, 2 queries)

| # | query | hits | disposition |
|---|---|---|---|
| 52 | `AD` | 0 | negative |
| 53 | `forward` | 0 | negative |

### 2.5 Venue 5 — `mdolab/MACH-Aero` (REST, 3 queries)

| # | query | hits | disposition |
|---|---|---|---|
| 54 | `forward AD` | 0 | negative |
| 55 | `tangent` | 0 | negative |
| 56 | `NaN` | 1 | #81 *Problems about ANK & NK* — ADflow solver traffic, unrelated |

### 2.6 Venue 6 — `mdolab/adflow` (REST, 4 queries)

ADflow is the lab-sibling code with its own forward-mode AD, so a reproduction defect there would
be strong analogue evidence.

| # | query | hits | disposition |
|---|---|---|---|
| 57 | `forward mode AD` | 9 | all Tapenade build/derivative-fix PRs (#404, #396, #319, #311, #224, #121, #174 …); **none reports a forward-AD build failing to reproduce the plain build's primal** |
| 58 | `tangent` | 2 | #396, #231 — unrelated |
| 59 | `forward AD NaN` | 2 | #311, #107 — derivative fixes, not primal reproduction |
| 60 | `reproducib` | **0** | negative |

### 2.7 Venue 7 — the AD libraries themselves: `SciCompKL/CoDiPack`, `SciCompKL/MeDiPack` (REST, 10 queries)

**MeDiPack was named in D460 §9.4 as not covered. It is covered here.**

| # | query | repo | hits | disposition |
|---|---|---|---|---|
| 61 | `OpenFOAM` | CoDiPack | **0** | negative |
| 62 | `GAMG` | CoDiPack | **0** | negative |
| 63 | `reproducib` | CoDiPack | **0** | negative |
| 64 | `forward primal differs` | CoDiPack | 0 | negative |
| 65 | `round-off` | CoDiPack | **0** | negative |
| 66 | `RealForward` | CoDiPack | 2 | #26 (double3 struct), #1 (postfix increment on `ActiveReal`, 2016) — **#1 is an arithmetic-correctness defect in the forward type, but a resolved 2016 operator-overload bug, not a solver-level non-reproduction** |
| 67 | `OpenFOAM` | MeDiPack | **0** | negative |
| 68 | `forward` | MeDiPack | 1 | #2 *AMPI with RealForward* (2019) — parallel MPI wrapper, not primal reproduction |
| 69 | `NaN` | MeDiPack | 0 | negative |
| 70 | `reproducib` | MeDiPack | **0** | negative |

**The AD libraries' own trackers have never discussed OpenFOAM, multigrid, or reproducibility.**

### 2.8 Venue 8 — `DAFoam/OpenFOAM-v1812-AD` (REST, 4 queries + complete listing)

**Named in D460 §9.4 as not covered. This is one of the two venues that changed the answer.**
Complete listing, all states: **15 items**. All 15 read at title level; #2, #3, #4, #5, #9, #11,
#13, #14 read in full.

| # | query | hits | disposition |
|---|---|---|---|
| 71 | `forward` | 3 | #4, #3, #2 — **all three read in full, §3** |
| 72 | `ADF` | 0 | negative |
| 73 | `GAMG` | 1 | **#2 — the 2020 maintainer GAMG comment, §0 and §3** |
| 74 | `NaN` | **0** | negative — **NaN has never been posted to this tracker** |

The complete listing is itself the strongest statement this venue can make, and it is a **pattern**,
not a negative: eight of fifteen items are *"X is not differentiated properly"* defects —
`MPI_Alltoall` (#1), `meshWave` (#5), `processorFvPatchField` (#9), `cyclicAMI` (#11),
`faceSkewness`/`faceOrtho` (#13), `atan2` infinite recursion → SegFault (#14, **open**), plus #3 and
#4. **The AD distribution has a documented history of AD-arithmetic and AD-plumbing defects, five of
them still open.** That is context that raises, not lowers, the prior on D460's "AD correctness"
class — and it is context the candidate does not currently carry.

### 2.9 Venue 9 — `DAFoam/OpenFOAM-AD` (REST, complete listing) — **THE DECISIVE VENUE**

**Not covered by the partial sweep, and not even named in D460 §9.4's list of gaps.** This is the
AD-enabled OpenFOAM distribution DAFoam v5 migrated to. Complete listing, all states: **2 items,
both open, both authored by `friedenhe`.**

| # | item | date | disposition |
|---|---|---|---|
| 75 | **#2 *PBiCGStab/DILU fvSolution generated wrong flow results*** | 2026-01-25, open, 0 comments | **PRIOR ART OF THE SAME FAMILY. See §5.** |
| — | #1 *Using `double` type for MPI functions causes seg fault in parallel* | 2026-01-07, open | An AD-plumbing trap: `if(dataType == MPI_DOUBLE)` cannot distinguish the primitive `double` from the AD `scalar`. Not D460, but the same class of "the AD build silently is not the plain build". |

### 2.10 Venue 10 — GitHub global search, all public repositories (REST, 8 queries)

| # | query | hits | disposition |
|---|---|---|---|
| 76 | `libDASolverADF` | **0** | **the library name appears in zero issues/PRs anywhere on GitHub** |
| 77 | `ADF-Deriv` | 11 | all noise from token-splitting (hosts files, unrelated PRs); **zero on point** |
| 78 | `CODI_ADF` | **0** | negative |
| 79 | `"satisfied the prescribed tolerance"` | 1 | #1068, a JuMP interface issue — unrelated |
| 80 | `"forward AD" OpenFOAM primal diverges` | 0 | negative |
| 81 | `DASolverADF` | **0** | negative |
| 82 | `"primalMinIters"` | **0** | negative |
| 83 | `"primalMaxRes"` | **0** | negative |

### 2.11 Venue 11 — `OpenMDAO/OpenMDAO` (REST, 2 queries)

| # | query | hits | disposition |
|---|---|---|---|
| 84 | `forward AD CFD primal NaN` | 0 | negative |
| 85 | `tangent mode differs` | 0 | negative |

### 2.12 Venue 12 — open web, forums, literature (WebSearch, 5 searches + the nonsense control)

**Read under §1's rule: counts are meaningless here; only on-point content counts.**

| # | query | disposition |
|---|---|---|
| C5 | `zzzqqxnonsensetoken12345 dafoam adjoint forward AD primal` | **CONTROL — 8 topically-plausible DAFoam links returned for a nonsense token.** See §1. |
| 86 | `DAFoam forward mode AD ADF build primal different from plain build NaN transonic DARhoSimpleCFoam` | **No on-point page.** Returned DAFoam's own docs, the AIAA-J paper, `OpenFOAM-v1812-AD`'s README. **Confirms upstream posture:** the docs state the ADF build exists to verify the JacobianFree adjoint, i.e. it is the sanctioned reference. |
| 87 | `CFD Online forum OpenFOAM automatic differentiation build gives different flow solution than standard build GAMG` (also run restricted to `cfd-online.com`) | **No on-point thread.** The only AD thread found on CFD-Online is a generic 2006-era "Automatic Differentiation" post. **CFD-Online and the OpenFOAM forums were named in D460 §9.4 as uncovered; they are covered here and are negative.** |
| 88 | `"discrete adjoint" OpenFOAM CoDiPack forward mode primal solution differs round-off multigrid stopping criterion` | **No on-point paper.** Returns the discrete-adjoint-OpenFOAM literature (Towara & Naumann; SU2 hybrid-parallel adjoints; STAMPS) — all about adjoint construction and cost, none about the AD build's *primal* differing from the plain build's. |
| 89 | `CoDiPack forward mode OpenFOAM primal solution differs from double precision build multigrid relative tolerance` restricted to scholar/arXiv/ResearchGate/Springer/ScienceDirect | **No on-point paper. Google Scholar and the literature venues were named in D460 §9.4 as uncovered; they are covered here and are negative.** One adjacent item worth having: *"On floating point precision in computational fluid dynamics using OpenFOAM"* (ScienceDirect, S0167739X23003813) — background on precision-driven trajectory divergence in OpenFOAM, **not** prior art. |
| 90 | `mdolab mailing list OR google group DAFoam forward AD verification "useAD" primal blows up reference unavailable` | **No mailing list exists.** DAFoam directs all user traffic to GitHub Discussions; the search surfaces only Discussions threads and Zenodo release records. **D460 §9.4 lists "the mdolab mailing lists" as an uncovered venue — the correct disposition is that the venue does not exist**, which is a stronger closure than a zero. It also surfaced the confirmation that *"DAFoam has migrated to the new AD-enabled OpenFOAM distribution, OpenFOAM-AD"* — which is what sent this sweep to venue 9. |

### 2.13 Venue 13 — the remaining `DAFoam` organisation trackers (REST, 5 complete listings)

| # | repo | items (all states) | disposition |
|---|---|---|---|
| 91 | `DAFoam/tutorials` | 35 | build/tutorial maintenance; #7 *Segmentation fault for CRM wing tutorial* (2022, closed) is the only CRM item and is not AD-related |
| 92 | `DAFoam/DAFoam.github.io` | 100 (page-1 cap) | documentation PRs only; zero defect traffic |
| 93 | `DAFoam/workshops` | 1 | an mpirun optimisation question — unrelated |
| 94 | `DAFoam/test_of_ad` | **0** | **the AD test repository has never had an issue filed** |
| 95 | `DAFoam/verifications` | **0** | **the verification repository has never had an issue filed** |

Six further queries (#96–#101) were the authorship/verbatim confirmations of §0's two quotes and the
full-body reads of `OpenFOAM-v1812-AD` #5, #9, #11, #13, #14, recorded in §3.

**Total: 101 recorded searches across 13 venues, 2026-08-23.**

---

## 3. Threads read in full, and what each one is

| thread | date | content | bearing on D460 |
|---|---|---|---|
| **`DAFoam/OpenFOAM-AD` #2** | 2026-01-25, **open** | **[verbatim, REST]** *"If PBiCGStab/DILU are used in fvSolution, both ADR and ADF flow solvers generate wrong results (flow variables blow up rapidly). … If you comment out PBiCGStab/DILU and use GAMG/GaussSeidel in fvSolution, the flow solution is correct."* Author `friedenhe`, 0 comments, reproducer attached (`Channel.zip`), incompressible `simpleFoamADR`. | **The prior art. §5.** |
| `OpenFOAM-v1812-AD` #2 | 2020-11-22, closed | Seg fault running SimpleFoam in parallel, "for both forward and reverse modes". Maintainer, 2020-12-07 **[verbatim, REST]**: *"It seems that this is related to the GAMG solver for pressure in system/fvSolution. Change it to smoothSolver fixes the problem. However, we still get a warning saying gAverage returns zero field."* Root cause later attributed elsewhere (2020-12-22): a bug in `reduce` in `UPstream.C`, fixed at `c0dfb152`. | **The only place in the entire community record where a maintainer links GAMG-for-pressure in an AD build to a failure and names `smoothSolver` as the fix. It is our polarity.** Superseded as a root cause, and it was a *parallel segfault*, not a serial NaN — so it is not prior art. **It is why this lane's registered sweep-1 arm uses `smoothSolver`, not the `PBiCGStab/DIC` D460 §7 sketched.** |
| `OpenFOAM-v1812-AD` #3 | 2020-12-22, closed | Dot-product test passes serial, fails parallel. Maintainer: *"forward-mode has no problem communicating derivatives between processors"*; cause was `MPI_send`/`MPI_recv` missing in Pstream. | Establishes that forward mode has been checked against FD and reverse mode before — and passed. Consistent with D460 §5 (the tangent was converging onto the adjoint). |
| `OpenFOAM-v1812-AD` #4 | 2020-12-24, closed | `dRdXv` dot products mismatch in parallel; *"The FD and forward-mode AD do not match very well either."* Fixed at `63417a30` — `initGeometry`/`calcGeometry` in `processorPolyPatch.C` were undifferentiated. | Same family; parallel-only; our arms are np=1. |
| `OpenFOAM-v1812-AD` #14 | 2024-12-09, **open**, 0 comments | *"The atan2() function will result in infinite recursion and eventually throw a Segmentation Fault"* — proposed fix is to scope it as `codi::atan2()`. | **An open, unfixed AD-arithmetic defect in a math primitive of the AD OpenFOAM.** Not D460, but it is direct evidence that "the AD build computes arithmetic differently from the plain build, and sometimes wrongly" is an established, live condition upstream. |
| `OpenFOAM-v1812-AD` #5, #11, #13 | 2021–2023, **all open** | `meshWave`, `cyclicAMI`, `faceSkewness`/`faceOrtho` "not differentiated properly in parallel". | The pattern of §2.8. Parallel-scoped, so none bears directly on an np=1 finding. |
| `OpenFOAM-AD` #1 | 2026-01-07, open | Passing a primitive `double` to an MPI function seg-faults, because `if(dataType == MPI_DOUBLE)` cannot tell the AD `scalar` from a `double`. | The AD build and the plain build are not interchangeable at the type level, by the maintainer's own account. |
| `mdolab/dafoam` Discussion #1015 | 2026-08-18, 0 comments | **[via page summary]** v5.1.0 regression tests fail with `Node communicator(s) already created` / MPI_ABORT in Docker and Singularity. | The `libDASolverADF` Discussions hit. **Not on point** — an MPI/environment failure, the same family as issue #989. |
| `mdolab/dafoam` issue #833 / Discussion #714 | 2025-05-21, open | A user asking how to FD-verify gradients, noting *"in the verification section, you introduced forward-mode differentiation to check the correctness of the gradients."* | **The near-miss, unchanged from the partial sweep.** §4. |

---

## 4. Near-misses, ranked by which maintainer reply they defuse

**1. `DAFoam/OpenFOAM-AD` #2 — defuses "this is just your case being unstable."** A maintainer has
already written down that AD builds produce wrong, rapidly-diverging flow solutions as a function of
the `fvSolution` linear solver. D460 does not need to establish that the phenomenon is real; it
needs to establish that it also occurs at the *opposite* solver polarity, on a compressible
transonic case, and to hand over the digit-level entry point.

**2. `OpenFOAM-v1812-AD` #2's GAMG comment — defuses "GAMG is the known-good configuration."**
`OpenFOAM-AD` #2 names GAMG/GaussSeidel as the correct setting. A maintainer reading D460 would
reasonably reply "but GAMG is what works." The 2020 comment is the counterweight: the same
maintainer once identified GAMG-for-pressure in an AD build as the trigger and `smoothSolver` as
the fix. **Both quotes must appear in any filing, together, or the report walks into its own
contradiction.**

**3. Issue #833 / Discussion #714 — defuses "nobody uses forward mode."** A user is reaching for FD
verification precisely because the documentation points them at forward-mode differentiation. If the
ADF primal is unavailable on compressible cases, that user is being sent to an instrument that is
not there. **Raises the value of filing; is not prior art** — the thread never mentions ADF-vs-plain
divergence, NaN, or the primal.

**4. `OpenFOAM-v1812-AD` #14 (`atan2`, open) — defuses "the AD arithmetic is fine, look elsewhere."**
Only if sweep 1 returns the AD-correctness branch. Held in reserve; it is not evidence for that
branch on its own.

---

## 5. Verdict of the sweep, and what it does to D460

> **PRIOR ART OF THE SAME DEFECT FAMILY WAS FOUND, in 101 recorded searches across 13 venues on
> 2026-08-23, with controls on all three search surfaces.**
>
> **No prior report of D460's specific finding exists** — nobody anywhere has reported that the
> forward-AD build fails to reproduce the plain build's primal, nobody has measured an
> AD-versus-plain divergence at the 8th significant figure of the energy equation, and the §8
> `-1e10` false-convergence print has **zero** trace in any venue (`primalMaxRes`, `primalMinIters`
> and `-10000000000` are clean zeros in issues, Discussions and GitHub-global alike).
>
> **But `DAFoam/OpenFOAM-AD` #2 is an open maintainer-authored report that AD builds generate wrong,
> rapidly-blowing-up flow solutions as a function of the `fvSolution` linear solver.** That is
> D460's family. D460 §9.4's sentence *"No prior art was found for either finding"* is, after a
> full-protocol sweep, **not sustainable for the primal finding**. It remains correct for §8.

### 5a. What must change in D460 before it is filing-ready — for the supervisor, not for this lane

`CLAUDE.md` rule 6 and `VERIFICATION_CHARTER` §6b: **the candidate is committed and is not edited by
this lane.** These are the required changes, and making them is the supervisor's call:

1. **§9.4's novelty sentence must be narrowed** to: no prior report of *this measurement*; prior art
   *of the family* exists and is open.
2. **§9.4's "not covered" list must be struck** — mdolab mailing lists (do not exist), CFD-Online,
   the OpenFOAM forums, Google Scholar, `OpenFOAM-v1812-AD` and MeDiPack are all covered here, and
   `DAFoam/OpenFOAM-AD` — the venue that mattered — was not on the list at all.
3. **§11 "Suggested tone if filed" must be rewritten.** The filing is no longer *"here is a new
   defect."* It is *"here is a second instance of your open `OpenFOAM-AD` #2, at the opposite
   solver polarity, on a compressible transonic case, with the divergence located to the 8th
   significant figure of the energy equation at iteration 1."* That is a **better** report: it
   attaches to an issue the maintainer already owns, and it supplies the digit-level entry point
   #2 lacks.
4. **§7 sweep 1 must not be run as sketched.** See §5b. **This is the load-bearing consequence.**

### 5b. Sweep 1 as D460 §7 sketches it is confounded, and this sweep is why

D460 §7 sweep 1 says: re-run ARM F with `p` switched from `GAMG` to **`PBiCGStab`/`DIC`**, and read
"NaN persists" as **AD correctness**.

**That reading is not available, for two independent reasons found in this sweep:**

- **`PBiCGStab` is the configuration the maintainer has already reported as breaking AD builds**
  (`OpenFOAM-AD` #2, open). If ARM F NaNs under PBiCGStab, the outcome is fully explained by a
  *separately reported, already-known* defect and says nothing about D460's mechanism. The
  "NaN persists → AD correctness" row of §7's table would be **wrong**.
- **`DIC` is a symmetric-matrix preconditioner.** The transonic `DARhoSimpleCFoam` pressure equation
  carries `fvm::div(phid, p)` and is asymmetric — which is exactly why upstream #2 pairs PBiCGStab
  with **DILU**, the asymmetric preconditioner. `PBiCGStab/DIC` is likely to be refused by OpenFOAM
  before it computes anything.

**The discriminating arm must use a solver that is neither `GAMG` nor `PBiCGStab`/`DILU`.**
`smoothSolver`/`GaussSeidel` is that solver: it is non-multigrid, so it has no value-dependent
V-cycle stopping rule to amplify an 8th-digit difference; it is not the PBiCGStab/DILU pair upstream
reports as broken; it is already the configuration this very case uses for every other equation, so
it is the least-novel possible choice; and it is the fix the maintainer himself named in 2020.

**The redesigned, costed, prediction-first sweep 1 is pre-registered at
`cases/dafoam/d460_sweep1_solver_family/PREREGISTRATION.md`. Nothing has been launched.**

---

## 6. What this sweep does NOT establish

1. **That D460's finding is novel.** §5 — the family is reported. Only the measurement is unreported.
2. **That `OpenFOAM-AD` #2 and D460 share a mechanism.** They share a family and a lever. Whether one
   cause produces both is exactly what is unknown, and no search can settle it.
3. **Any claim about the DAFoam v5 image's own source.** No container was launched for this sweep;
   every source claim above is an upstream tracker quote, not a read of the deployed file.
4. **Coverage of non-English or non-indexed venues**, private lists, or Slack/Discord surfaces.
5. **That the Discussions counts are complete.** GitHub's Discussions search ORs multi-word queries
   and is not documented; the counts are reproducible, not authoritative. The weight is on the
   single-token zeros.
6. **Anything about `OpenFOAM-AD`'s source.** #2's `Channel.zip` reproducer was **not** downloaded
   and not run. Doing so would be a compute item with its own pre-registration.

## 7. Files behind this sweep

- This memo. Raw JSON for every REST query and the fetched Discussions HTML were written to the
  session scratchpad and are **not committed** (`CLAUDE.md` rule 13 — scratch is temp, and no
  repository document cites a scratch path). Every query above is exact and re-runnable; the
  Discussions thread numbers are printed so each count can be audited without the HTML.
- Pre-registration this sweep forced: `cases/dafoam/d460_sweep1_solver_family/PREREGISTRATION.md`.
- Proposed record rows for the supervisor: `cases/dafoam/d460_sweep1_solver_family/DOCKET_DRAFT.md`
  and `.../LESSONS_DRAFT.md`. **This lane does not append to `docs/DOCKET.md`,
  `docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md` or `docs/LAB_STATE.md`.**

**Nothing in this file has been sent, filed, posted, uploaded or pushed. Filing is Sanaa's alone.**

---

## ADDENDUM 2026-08-23 — §0's "current-generation fork" claim is now verified from upstream source, not inferred

*Appended, not rewritten. Nothing above this line changed; lines whose number changed above this
section: 0. This addendum strengthens §0 and §2.9 and alters no disposition.*

§0 and §2.9 assert that `DAFoam/OpenFOAM-AD` is the AD fork **DAFoam v5 migrated to**, and therefore
the generation that produced the `libDASolverADF.so` D460 measured. When first written that rested
on a **[via page summary]** line from a web search — the weakest tier in `LITERATURE_CHARTER` §3,
and too weak to carry the headline of a sweep.

It is now **verified at tier 2 of `PROBLEM_RESEARCH_PROTOCOL.md` §1 — upstream source, fetched
raw**. `raw.githubusercontent.com/DAFoam/DAFoam.github.io/main/pages/mydoc/mydoc_installation_source.md`,
fetched 2026-08-23, lines 317 and 360 **[verbatim]**:

```
There are three versions of OpenFOAM to compile: original, reverse-mode AD (ADR),
and forward-mode AD (ADF).
...
wget https://github.com/DAFoam/OpenFOAM-AD/archive/refs/heads/v2506-ad.tar.gz -O OpenFOAM-AD.tgz
```

and lines 400 and 411, which build the forward variant from that same tree:

```
sed -i 's/export WM_AD_MODE=.*/export WM_AD_MODE=ADF/g' etc/bashrc
./renameAD.sh platforms/linux*ADF --ADF --commit
```

**The branch is `v2506-ad`, and the lab's image carries OpenFOAM v2506** (`TOOLCHAIN_INVENTORY.md`
§1). So the repository whose issue #2 reports *"both ADR and ADF flow solvers generate wrong
results"* is not merely an adjacent fork — **it is the tree the ADF library under test was built
from.** The prior-art finding of §0 and §5 stands on source, not on a search summary.

**Still not established, and not claimed:** that the *deployed* `libDASolverADF.so`
(md5 `44538ed4ac157ecb5dbb6850cf4bde64`) was built from this exact branch at this exact commit. That
would need a build-provenance read inside the container, which no part of this sweep opened.

---

## ADDENDUM 2026-08-23 (second) — COMPLETION AUDIT of this sweep, five venue gaps found, four closed, and a NEW analogue prior-art item from mdolab's own tree

*Appended at the foot, not rewritten. Nothing above this line changed; **lines whose number changed
above this section: 0**. This addendum adds venues and searches. It **alters no disposition recorded
above**: every §2 row, every count and §5's verdict stand exactly as written.*

> **NOT FILED ANYWHERE. Nothing was posted, commented, opened, registered, uploaded or contacted.**
> Every request recorded below is a `GET`. No account was touched, no form submitted. Filing is
> **Sanaa's decision alone** (`CLAUDE.md` rule 7). Prepared by the DAFoam team, lab-lane,
> 2026-08-23, 20:44–21:05 UTC, on the dafoam-supervisor's filing-readiness brief.

### A1. The quota audit — the house standard is MET and EXCEEDED, and 0 searches are OWED

Blocker 1's standard is the house protocol's **63 searches across 10 venues**
(`LIAISON_NOVELTY_SWEEP_decomposition_defect.md` §1). Re-derived mechanically from this file, not
taken from its own headline:

| measure | value | how derived |
|---|---|---|
| individually tabulated query rows | **95** | `grep -oE '^\| [0-9]+ \|'` → #1…#95, **no gaps, no duplicates** (checked as a set against `range(1,96)`) |
| prose-recorded searches | **6** | #96–#101, §2.13 closing paragraph — the authorship/verbatim confirmations and the full-body reads of `OpenFOAM-v1812-AD` #5, #9, #11, #13, #14, all itemised in §3 |
| **total recorded searches** | **101** | 95 + 6 |
| control rows | **5** | C1–C5 |
| venues | **13** | `### 2.1`–`### 2.13` |

**DONE = 101 of 101 claimed; OWED against the 63/10 quota = 0.** The claim in §1's opening paragraph
is sustained on a mechanical re-count. **Caveat, stated because it is the honest one:** #96–#101 are
recorded as prose, not as auditable table rows with a query string and a hit count, so they are
weaker evidence than #1–#95. The count stands; six of its members are not independently re-runnable
from this file.

### A2. What the quota does NOT close — five substantive venue gaps found by this audit

A count is not coverage. Auditing *which* venues were reached found five that were not:

| gap | why it matters to D460 | disposition |
|---|---|---|
| **G1** the `DAFoam` org was **sampled, not enumerated** — §2.8/§2.9/§2.13 reached 7 repos | a defect report's novelty claim over an org must rest on the org, not on the repos someone thought of | **CLOSED** — org enumerated, 21 repos, all covered. §A3 |
| **G2** mdolab's **differentiated-build** repos (`complexify`, `CMPLXFOIL`) were never searched | complex-step is the closest possible analogue to forward-AD: a differentiated build that must reproduce the plain build's primal | **CLOSED — and it produced the find of this addendum.** §A4 |
| **G3** the **SU2 tracker** was never searched (§2.12 #88 covered only its literature) | SU2 is the other production AD-CFD code and uses the same CoDiPack | **CLOSED**, negative. §A5 |
| **G4** **OpenFOAM's own upstream tracker** was never searched, in any form | D460 §3's mechanism is a claim about GAMG's value-dependent V-cycle stopping rule — an OpenFOAM behaviour, not a DAFoam one | **BLOCKED — venue not reachable from this box.** §A6 |
| **G5** **non-English venues**, declared uncovered by this file's own §6.4 | DAFoam has a substantial Chinese-language user base | **CLOSED**, negative. §A7 |

### A3. Venue 14 — the `DAFoam` organisation, ENUMERATED rather than sampled (REST, #102, #103)

`api.github.com/orgs/DAFoam/repos` → **21 repositories**. §2.8, §2.9 and §2.13 covered **7** of them
(`OpenFOAM-AD`, `OpenFOAM-v1812-AD`, `tutorials`, `DAFoam.github.io`, `workshops`, `test_of_ad`,
`verifications`). The remaining **14 were never named**.

| # | query | result | disposition |
|---|---|---|---|
| 102 | `orgs/DAFoam/repos` complete listing | **21 repos**; only 5 carry any open issue, and **all 5 were already covered** | the sampling was lucky, not sound |
| 103 | complete all-states issue+PR listing of all **14** uncovered repos | **25 items total, every one closed**: `dafoam_mcp_server` 5, `user_guide_files` 4, `v3-pages` 4, `reg_test_files` 3, `mdo_agent_work` 2, `pvOptGUI_tutorials` 2, `validations` 5; **`HiSA4DAFoam_v1812`, `Hisa4DAFoam`, `cfmesh`, `docker`, `doxygen`, `files`, `v4-pages` = 0 items each** | **zero on point.** All 25 are documentation, packaging, tutorial or dependency-bump traffic |

**The `DAFoam` organisation is now exhaustively covered, 21 of 21 repositories.** §5's verdict is
unchanged; its foundation is now an enumeration instead of a sample.

### A4. Venue 15 — mdolab's DIFFERENTIATED-BUILD repos, and **the new analogue prior art** (REST, #104–#109)

`mdolab` holds **30** repositories; §2.1–§2.6 reached 5. Two of the remaining 25 are the closest
analogue in existence to D460's question — **`complexify` and `CMPLXFOIL`, mdolab's complex-step
differentiation tooling**, in which a *differentiated* build of a solver must reproduce the *plain*
build's primal in its real part. Controls first (`CLAUDE.md` rule 3, L-234):

| # | query | hits | disposition |
|---|---|---|---|
| C6 | `repo:mdolab/complexify zzzqqxnonsensetoken12345` | **0** | control — floor is 0 |
| C7 | `repo:mdolab/CMPLXFOIL zzzqqxnonsensetoken12345` | **0** | control — floor is 0 |
| C8 | `repo:mdolab/CMPLXFOIL complex` | **7** | **positive control — the reader can see a presence** |
| 104 | `repo:mdolab/complexify` complete listing | 15 | numpy-2 / packaging maintenance. **#13 *Update abs complex safe routine for numpy2*** is an arithmetic-correctness item in the differentiated type — same class as CoDiPack #1 (§2.7 row 66), not on point |
| 105 | `repo:mdolab/CMPLXFOIL derivative` | 4 | **#28 — read in full, below** |
| 106 | `repo:mdolab/CMPLXFOIL NaN` | 1 | #31 — read in full, below |
| 107 | `repo:mdolab/pygeo forward AD` | 1 | #56 (OpenVSP wrapper) — unrelated |
| 108 | `repo:mdolab/pyhyp NaN` | 3 | #79, #80, #85 — mesh-generation segfaults, unrelated |
| 109 | `repo:mdolab/baseclasses AD` | **0** | negative |

#### **`mdolab/CMPLXFOIL` #28 — *"Match complex version convergence tolerances to real version"*** (#110, full-body read)

2024-07-17, **merged**, author **`eytanadler`** (mdolab). **[verbatim, REST]**:

> *"In some cases, the primal (real) version of XFOIL converges fine, but then the gradient
> evaluation with the complex version does not converge. Optimizers very much dislike when the
> primal succeeds and the gradient fails. Most just crash.*
>
> *One of the reasons I found for this happening is that **the tolerances of the real and complex
> XFOIL versions do not match**. This PR fixes this problem. This does not solve all of the
> situations where the primal succeeds and gradient fails, but it helps many of them."*

**Why this matters, stated precisely.** This is **analogue prior art of the family, from mdolab's
own tree** — the lab that authors DAFoam. It is a recorded instance of the exact shape D460
measures: *a differentiated build of a solver failing to converge where the plain build converges*,
with the identified lever being **the convergence/stopping tolerance, not the differentiated
arithmetic**, and the accepted fix being to make the two builds' stopping rules agree.

**It is on D460's CONDITIONING / DIAGNOSABILITY side.** D460 §3 infers that a value-dependent
multigrid stopping rule turns an 8th-significant-figure AD difference into divergence; #28 is an
independent, merged, maintainer-authored instance of a differentiated build diverging because its
stopping rule did not match the plain build's. **It raises the prior on the conditioning branch and
supplies the precedent for the remedy** (match the stopping rules across builds), which is the
documentation-plus-warning ask §5a item 3 anticipates.

**What it is NOT:** it is a different code (XFOIL, Fortran, **complex-step**, not OpenFOAM/CoDiPack
forward-AD), a different equation set, and it reports a *gradient evaluation* failing rather than the
primal *differing at the 8th digit*. **It is not prior art of D460's finding and it does not narrow
§5's novelty statement any further.** It is a near-miss of the first rank and belongs in any filing.

#### `mdolab/CMPLXFOIL` #31 — *"Tests fail when using new `ifx` compiler"* (#111, full-body read)

2024-12-19, **OPEN**, 6 comments. The complex (differentiated) build's derivative tests fail under
`ifx -O1`/`-O2` and pass under `-O0`, **identically across `-fp-model` `fast`, `precise` and
`strict`** (measured table posted by `eirikurj`, 2025-01-14). Contributor `A-CGray` notes ifx's
documented complex-number and default-NaN-checking differences from ifort.
**Bearing on D460:** context, not prior art — direct evidence that a differentiated build's
agreement with its plain counterpart is fragile to the *floating-point environment* and not only to
the AD source transformation. It does **not** support either branch of §7's decision rule.

### A5. Venue 16 — `su2code/SU2`, the other production CoDiPack AD-CFD code (REST, #112–#117)

§2.12 #88 covered SU2's *literature*; its **tracker** was never searched. A forward-mode
primal-reproduction defect in SU2 would be strong analogue evidence.

| # | query | hits | disposition |
|---|---|---|---|
| C9 | `repo:su2code/SU2 zzzqqxnonsensetoken12345` | **0** | control — floor is 0 |
| C10 | `repo:su2code/SU2 adjoint` | **339** | **positive control** |
| 112 | `forward mode primal differs` | **0** | **clean negative** |
| 113 | `direct differentiation NaN` | **0** | **clean negative** |
| 114 | `AD build different result` | 25 | OR-match noise (`#877` rough-wall BC, `#948` PyAMG, `#2025` SU2_DOT_AD turbomachinery); **none reports an AD build's primal differing from the plain build's** |
| 115 | `reproducib` | **0** | **clean negative** |
| 116 | `CoDiPack multigrid` | 2 | #643, #648 — linear-algebra library discussions, unrelated |
| 117 | `#2712` *Fix multigrid agglomeration* full-body read | — | 2026-01-18, author `bigfooted`: a Nishikawa–Diskin agglomeration **feature** PR. **Not AD-vs-plain. Unrelated.** |

**SU2's tracker has never recorded a differentiated build failing to reproduce the plain build's
primal.** This strengthens §5's novelty statement for the measurement.

### A6. Venue 17 — OpenFOAM's OWN upstream tracker: **BLOCKED, and recorded as BLOCKED, not as a zero**

D460 §3's mechanism is a claim about **GAMG**, which is OpenFOAM's, not DAFoam's. No part of the
101-search sweep touched an OpenFOAM-native tracker. This audit tried, and **could not read it**:

| # | attempt | result |
|---|---|---|
| 118 | `develop.openfoam.com/api/v4/...` (ESI GitLab REST), 7 queries incl. a nonsense control and a `GAMG` positive control | **HTTP 403, Cloudflare interstitial (`"Just a moment..."`, 5,530 B of HTML) on every request, including the bare project lookup.** No reading obtained |
| 119 | the same tracker via the web-fetch tool, issue `#2054` | **HTTP 403 Forbidden** |
| 120 | `bugs.openfoam.org` (Foundation Mantis) | HTTP 302; not pursued to a reading |

**No count from this venue is recorded, in either direction.** `CLAUDE.md` rule 3 applies at venue
level: a control that cannot be run is not a floor, and a venue that returns 403 to every request has
not been shown able to return a presence. **Venue 17 is `BLOCKED`.** Closing it needs a route past
Cloudflare — an escalation item, not a search.

Two adjacent readings *were* obtained, by open web search, and are recorded at that weaker tier:

- **ESI issue #2054, *"Question about GAMG solver strategy (only V cycles currently)"*** exists on
  that tracker (title read from the search index; **body not read** — 403). Named so a future
  attempt has a target.
- OpenFOAM's own release notes state **[via search summary, tier 3]** that GPU/parallel operation
  ordering *"is now non-deterministic and this will affect the truncation error, with noticeable
  solution differences in some solver combinations."* **Adjacent, not prior art** — it concerns
  operation ordering across ranks, where D460's arms are np = 1 and undecomposed. Recorded because a
  maintainer may raise it, and because it shows the project already accepts that ordering-level
  round-off produces visible solution differences.

### A7. Venue 18 — non-English venues, this file's own §6.4 gap (WebSearch, #121–#123)

Read under §1's rule: **counts here are meaningless; only on-point content counts.**

| # | query | disposition |
|---|---|---|
| 121 | `DAFoam 前向自动微分 ADF 求解器 结果不一致 发散 NaN` | **No on-point page.** Returned generic Chinese AD tutorials (阿里云, 知乎), DAFoam's own docs and doxygen, and unrelated PyTorch-NaN posts — the engine answered the topic, exactly as C5 predicted |
| 122 | `DAFoam useAD forward mode 算例 发散 GAMG 压力求解器 自动微分 编译 结果 不同` | **No on-point page.** Returned an AI-compiler AD tutorial, a Guangzhou-supercomputer OpenFOAM case list, `cfd-china.com` mesh-convergence threads and arXiv AD papers |
| 123 | CFD-Online, DAFoam-specific forward-AD divergence (three passes) | **No on-point thread.** Surfaced only the 2019 *"Introducing DAFoam"* announcement, the generic *"Automatic Differentiation"* and *"Using Algorithmic Differentiation in OpenFoam"* threads §2.12 #87 already dispositioned |

**§6.4's non-English gap is closed for Chinese-language surfaces and is negative.** It remains open
for any venue this US-indexed engine does not reach, and for private lists, Slack and Discord.

### A8. Two measured method traps, recorded because they invalidate evidence elsewhere

1. **The web-search tool's `allowed_domains` restriction was NOT HONOURED**, twice, measured. A
   search restricted to `develop.openfoam.com` returned ten `arxiv.org` PDFs; a search restricted to
   `cfd-online.com` did the same. **Consequence: "I searched venue X" is not established by passing
   X to the domain filter.** Every domain-restricted disposition in §A6 and §A7 is therefore recorded
   as *"no page whose content is on point"* and never as venue coverage. This extends §1's WebSearch
   trap from the *query* to the *venue restriction*.
2. **The nonsense-token control fires on this surface too.** `zzzqqxnonsensetoken12345 solver issue`
   restricted to `develop.openfoam.com` returned **ten topically-plausible OpenFOAM issue links**
   (external-solver #27, #44, #33, #39; Development/openfoam #2340, #633). L-234's floor is not 1
   here — it is *a full page of plausible results*, and no count from a web surface is readable.

### A9. Running totals, and what this addendum does to §5 and to filing readiness

| | before this addendum | added here | **total** |
|---|---|---|---|
| recorded searches | 101 | **26** (#102–#127 as numbered above, incl. 3 full-body reads and 3 BLOCKED attempts) | **127** |
| controls | 5 | **6** (C6–C11) | **11** |
| venues | 13 | **5** (14, 15, 16, 17, 18) | **18**, of which **17 read and 1 `BLOCKED`** |

**§5's verdict is UNCHANGED and is not restated here.** `DAFoam/OpenFOAM-AD` #2 remains the prior
art of the family; no prior report of D460's specific measurement exists in any of the 18 venues;
the §8 `-1e10` false-convergence finding remains a clean zero everywhere, now including SU2,
`complexify`, `CMPLXFOIL` and the 14 newly-enumerated `DAFoam` repos.

**Filing readiness — assessment for the dafoam-supervisor, whose call this is:**

1. **Blocker 1's quota is met** (127 ≥ 63 searches, 18 ≥ 10 venues) and the `DAFoam` org is now
   enumerated rather than sampled.
2. **§5a's four required D460 changes are unaffected** — this addendum adds no new required change
   to items 1, 2 and 4. **Item 3, the filing tone, gains a second exhibit:** `CMPLXFOIL` #28 shows
   mdolab has already met, accepted and fixed the "differentiated build will not converge where the
   plain build does, and the stopping tolerance is the lever" shape in its own code. It belongs
   beside `OpenFOAM-v1812-AD` #2's GAMG comment in §4's near-miss ranking, at rank 2 or 3.
3. **One venue is `BLOCKED`** (§A6) and it is the one nearest D460's mechanism claim. Whether that
   blocks filing is the supervisor's judgement, not this lane's.
4. **Nothing here is a substitute for sweep 1.** The class question — conditioning vs AD correctness
   — is decided by compute, and that compute is `BLOCKED` on the separate finding reported to the
   supervisor against `d460_sweep1_solver_family/PREREGISTRATION.md` assertion A1-P.

**Nothing in this addendum has been sent, filed, posted, uploaded, registered or pushed to any
external service. The defect candidate remains NOT FILED. Filing is Sanaa's decision alone.**
