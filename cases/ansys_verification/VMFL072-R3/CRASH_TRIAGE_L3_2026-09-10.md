# VMFL072-R3 L3 — CRASH TRIAGE, 2026-09-10

**A crash is a finding about the case, the method or the toolchain until triage
demonstrates otherwise** (SUPERVISION_CHARTER §3 check-2). This one is a finding, and it is
the most interesting thing this case has produced. Triaged personally by the
ansys-verification supervisor; no frozen file touched, no run directory altered.

## What happened

`pimpleFoam` at level **L3 (480x208)** terminated with a **core dump** at `Time = 1.10875`,
having written time directories through 0.8+. The log's own last line is
`timeout: the monitored command dumped core`. There is no `End` line.

The stack unwinds through, innermost first:

- `Foam::PBiCGStab::solve(...)`
- `libregionFaModels.so`
- `Foam::regionModels::areaSurfaceFilmModels::kinematicThinFilm::evolveRegion()`
- `libregionFaModels.so`
- `Foam::velocityFilmShellFvPatchVectorField::updateCoeffs()`

So the failure is **inside the finite-area surface-film (thin-film shell) solve**, not in
the primary flow solve and not in the mesh.

## Why this is a finding and not an infrastructure hiccup

**R3's entire reason for existing is a film remedy.** The registration's own cost_basis
records R3 as carrying the *"precursor-film remedy h0 1e-7 -> 1e-5 for the R2 dewetting
SIGFPE"*. R2 died of a dewetting singularity in this same film model; R3 raised the
precursor film thickness to cure it.

Measured outcome of that remedy across the ladder, from this session's runs:

| level | grid | outcome |
|---|---|---|
| L1 | 120x52 | completed, `End` present |
| L2 | 240x104 | completed, `End` present |
| **L3** | **480x208** | **core dump in `kinematicThinFilm::evolveRegion()`** |
| C1 | (coarse variant) | completed, `End` present |
| B2 | — | still running at triage time |

**The remedy is grid-dependent: h0 = 1e-5 is sufficient at 120x52 and 240x104 and
insufficient at 480x208.** That is a real numerics result about the thin-film model, not a
machine problem: the same binary, same environment and same precursor thickness succeeded
twice at coarser resolution minutes earlier. As the cell size falls, the precursor film is
no longer thick relative to the discrete dewetting scale, and the film solve loses it.

## Consequence for the gate — stated, not softened

The gate is evaluated at the finest level, and a Roache triple needs all three. With L3
dead there is no converged finest level, so under **rule 5 step 1** (any level not
iteratively converged -> `NOT A RESULT`) this ladder cannot yield a PASS whatever L1 and L2
say. **The frozen comparator decides the row, not this note** — nothing here is a verdict,
and no gate, threshold, cap or label moves.

## What the successor owes

A successor must treat the precursor thickness as **resolution-dependent** rather than a
single constant, or abandon the precursor-film approach for this case. Raising h0 globally
to whatever L3 tolerates would change the physics at L1/L2 and break the grid family's
self-similarity, so it is **not** a free fix: h0 is part of the model, and a triple whose
model changes per level is not a grid-convergence study. That tension is the finding.

## Housekeeping observed while triaging

No `RUN_RC` file exists for any VMFL072-R3 level. rc is therefore **NOT MEASURED** for all
five, and it must be reported that way rather than inferred from the logs. **No RUN_RC was
fabricated** — hand-writing one would be manufacturing an instrument input.

---

## ADDENDUM, same day — the exit code names the signal, and it is the SAME signal R3 was built to cure

Found after the section above was written, by reading the launcher's own completion
artifact rather than inferring from the log. **The launcher writes `RC.txt`, not `RUN_RC`**
(`launch_vmfl072_r3.sh:222-223`), so the earlier note that "no `RUN_RC` exists" was looking
for the wrong filename. Corrected here rather than above; nothing above is altered.

Measured `RC.txt` across the ladder:

| level | rc | cap_core_min | finished (UTC) | reading |
|---|---|---|---|---|
| L1 | **0** | 1.5 | 16:12:39Z | clean |
| L2 | **0** | 9 | 16:16:14Z | clean |
| **L3** | **136** | 65 | 16:17:06Z | **SIGFPE** |
| C1 | **0** | 9 | 16:19:11Z | clean |
| B2 | — | 100 | still running | — |

**`rc = 136` is `128 + 8` — signal 8, SIGFPE, a floating-point exception.** It is not 124 and
not 137, so **this is not a cap-stop and not a kill**: the L3 cap was 65 core-min and L3 died
about two and a half minutes into its solve, nowhere near it. The cap is irrelevant to this
failure and must not be blamed for it.

**This matters because SIGFPE is exactly what R3 was built to eliminate.** The registration
records R3 as carrying the *precursor-film remedy h0 1e-7 -> 1e-5 for the R2 dewetting
SIGFPE*. R2 died of a dewetting SIGFPE; R3 raised the precursor thickness to cure it; and
**L3 has now died of a SIGFPE in the same film code path**
(`kinematicThinFilm::evolveRegion()` / `velocityFilmShellFvPatchVectorField::updateCoeffs()`).

So the honest statement of the finding is stronger than the section above put it:

> **R3's precursor-film remedy did not remove the dewetting SIGFPE. It moved it to a finer
> grid.** The remedy holds at 120x52 and 240x104 and fails at 480x208. A fix that survives
> two of three levels is not a fix; it is a resolution-dependent postponement, and it means
> the failure scales with the mesh rather than being cured by a constant.

That is also why raising `h0` again cannot be the successor's answer on its own: whatever
value survives 480x208 would, on this evidence, be expected to fail at 960x416. The
successor has to make the precursor thickness scale with the cell size, or stop using a
precursor film for this case. **No gate, threshold, cap or label moves on account of this
note, and nothing here is a verdict — the frozen comparator decides the row.**

---

## SECOND ADDENDUM — I OVERCLAIMED, AND A LANE WAS RIGHT TO PUSH BACK

Nothing above is altered. This corrects the STRENGTH of the claim, not its direction.

Above I wrote that the dewetting instability is **"grid-dependent"** and that the remedy
"holds at 120x52 and 240x104 and fails at 480x208". The second half is a measurement and
stands. **The first half is an inference from a single failing level, and I stated it more
firmly than one data point can carry.** One crash at one resolution is *consistent with*
grid-dependent dewetting; it does not establish it. Competing explanations that this
evidence does not exclude include a level-specific mesh pathology at L3, a Courant or
time-step interaction that happens to bite at that cell size, or a single unlucky cell.

**The defensible statement, which replaces the stronger one wherever it matters:**

> R3's precursor-film remedy **did not remove the dewetting SIGFPE at 480x208.** Whether
> the failure threshold scales with cell size is **UNTESTED** and would need a rung
> registered to test it.

The distinction has teeth for the successor. If the effect really is resolution-scaled,
`h0` must scale with cell size; if L3 has a local mesh pathology, that is a mesh fix and
`h0` is innocent. **Those two futures are not distinguishable from what is on disk**, and
choosing between them by assumption is exactly how a plausible story becomes a wrong one.

Recorded because the overclaim was mine and the correction came from a lane I had asked to
check my work. **The verdict is untouched either way**: a crashed L3 cannot satisfy strict
completion, so this triple is `NOT A RESULT` whichever explanation is true — which is
precisely why there was nothing to be gained by overstating it.

---

## DATED ADDENDUM — 2026-09-11T16:20Z — **THE GRID LABELS IN THIS DOCUMENT ARE WRONG, AND THEY PROPAGATED**

**Nothing above this section is rewritten; the line numbering above is unchanged (lines whose number changed above this section: 0).**

This document states the levels as **120x52 / 240x104 / 480x208** (lines 10, 36-38, 42-43, 103, 108). **Those figures are not what ran.** Measured from the run artifacts, not from this document:

| level | this doc says | what actually ran (`LEVEL_APPLIED.txt`) | `log.blockMesh` | `log.makeFaMesh` |
|---|---|---|---|---|
| L1 | 120x52 | **64 x 16 x 1** | — | — |
| L2 | 240x104 | **128 x 32 x 1** | — | — |
| L3 | 480x208 | **256 x 64 x 1** | `nCells: 16384` | `Number of faces: 16384` |

480 x 208 = 99,840 cells; the level that crashed has **16,384**. The three independent artifacts agree with each other and disagree with this document, so the document is the thing that is wrong.

**Why it matters, beyond tidiness.** The central claim of this triage — *"the remedy holds at 120x52 and 240x104 and fails at 480x208"* — is structurally intact (the remedy did hold at the two coarser levels and did fail at the finest) but **every absolute grid number attached to it is wrong by roughly a factor of 2 per direction**, and so is the forward projection at line 108 that *"whatever value survives 480x208 would be expected to fail at 960x416."* The real next refinement is **512 x 128**, not 960 x 416.

**It propagated.** `docs/LAB_STATE.md` S-13d repeated *"the remedy did not remove the SIGFPE at 480x208"* on this document's authority. That board line is wrong for the same reason and is corrected in the ansys section at S-13g.

**The mechanism claim is UNCHANGED and still UNTESTED.** Whether the failure threshold scales with cell size remains untested; correcting the labels does not test it.

**One further control now on record, and it does NOT say what it might appear to say.** `B2` ran the **same 256 x 64 mesh as the level that crashed** and completed `rc=0`. That is NOT evidence that precursor thickness alone is the culprit: B2 differs from L3 in **three** variables at once — `H_IN` 3.8276110199e-04 vs 7.1084204656e-04, `U_IN` 0.997993736 vs 0.537381243, `DELTAT` 7.8125e-04 vs 1.25e-03. It establishes only that **the 256 x 64 mesh is not intrinsically fatal**. No single-variable control exists at fixed grid, and building one is the first thing R4 owes.

---

## DATED ADDENDUM — 2026-09-12 — **THE FAULTING FRAME IS NOT `updateCoeffs()`. IT IS FRAME #3, `DILUPreconditioner::calcReciprocalD`, AND THIS DOCUMENT'S UNWIND OMITS IT.**

**Version: v1.0 → v1.1.** *(This document carried no version line; `v1.0` denotes it as
committed at `c4b6fec4`, blob `30f6b8e9eb38b95c63657b45d8597eb3ce28857a`, and this
addendum makes it `v1.1`. The prior history is stated rather than invented: the original
section plus three appended addenda — same-day, SECOND, and 2026-09-11T16:20Z — are all
`v1.0`.)*

**Lines whose number changed above this section: 0.** Nothing above is rewritten,
renumbered or deleted. Drafted by an `ansys-lane-opus` lane at the
`ansys-verification-supervisor`'s direction, from the run artifacts, not from this
document.

### What this document says, and what is wrong with it

Lines 14–20 read *"The stack unwinds through, innermost first:"* and then list five
entries beginning `Foam::PBiCGStab::solve(...)` and ending
`Foam::velocityFilmShellFvPatchVectorField::updateCoeffs()`. Line 98 repeats the pair
`kinematicThinFilm::evolveRegion()` / `velocityFilmShellFvPatchVectorField::updateCoeffs()`
as the identification of the failure.

~~Those entries are the innermost frames of the unwind.~~ **STRUCK, NOT REWRITTEN.**
They are frames **#7/#8 through #12** of a **seventeen**-frame trace. **The list begins
four frames too late and therefore omits the frame where the floating-point exception is
actually raised.** The listed frames are correct as far as they go and the conclusion
drawn from them — that the failure is inside the finite-area surface-film solve — is
**not** disturbed. What is corrected is the **locus**, and the locus is what a successor
acts on.

**This omission propagated.** The wrong locus was carried into commit `b0d24bd22` (the
VMFL072-R4-A grading commit) on this document's authority. It is corrected here, at the
foot, and in register Rows #78 and #79.

### The complete unwind, verbatim from the artifact

From `verification/runs/ansys_verification/VMFL072-R3/L3/log.pimpleFoam`, every
`#`-prefixed frame, transcribed exactly:

```
#1  Foam::sigFpe::sigHandler(int)                                                    libOpenFOAM.so
#2  ?                                                                                libc.so.6
#3  Foam::DILUPreconditioner::calcReciprocalD(Foam::Field<double>&, Foam::lduMatrix const&)   libOpenFOAM.so
#4  Foam::DILUPreconditioner::DILUPreconditioner(Foam::lduMatrix::solver const&, Foam::dictionary const&)   libOpenFOAM.so
#5  Foam::lduMatrix::preconditioner::addasymMatrixConstructorToTable<Foam::DILUPreconditioner>::New(...)     libOpenFOAM.so
#6  Foam::lduMatrix::preconditioner::New(Foam::lduMatrix::solver const&, Foam::dictionary const&)            libOpenFOAM.so
#7  Foam::PBiCGStab::scalarSolve(Foam::Field<double>&, Foam::Field<double> const&, unsigned char) const      libOpenFOAM.so
#8  Foam::PBiCGStab::solve(Foam::Field<double>&, Foam::Field<double> const&, unsigned char) const            libOpenFOAM.so
#9  ?                                                                                libregionFaModels.so
#10 Foam::regionModels::areaSurfaceFilmModels::kinematicThinFilm::evolveRegion()     libregionFaModels.so
#11 ?                                                                                libregionFaModels.so
#12 Foam::velocityFilmShellFvPatchVectorField::updateCoeffs()                        libregionFaModels.so
#13 ?                                                                                pimpleFoam
#14 ?                                                                                pimpleFoam
#15 ?                                                                                libc.so.6
#16 __libc_start_main                                                                libc.so.6
#17 ?                                                                                pimpleFoam
```

**Frame #1 is OpenFOAM's own SIGFPE handler, so the faulting frame is the one beneath it
that is not the libc trampoline: `#3`, `Foam::DILUPreconditioner::calcReciprocalD`.**
Frames #7–#12, which this document listed, are the frames that *reached* the fault, not
the frame that raised it.

### What `calcReciprocalD` does, and why the distinction has teeth

`calcReciprocalD` computes the **reciprocal of the matrix diagonal** — it inverts each
diagonal coefficient of the film region's `lduMatrix` to build the DILU preconditioner.
Frames #4–#6 are the preconditioner's **constructor** and its runtime-selection table.

**The fault therefore occurs during preconditioner CONSTRUCTION, before a single
iteration of the linear solve has been taken.** The solver did not iterate and diverge.
It was handed a matrix, began preparing to solve it, and faulted on the arithmetic of
inverting a diagonal entry.

### The immediately preceding solves CONVERGED — measured, not inferred

The last lines the log records before `[stack trace]`, from
`verification/runs/ansys_verification/VMFL072-R3/L3/log.pimpleFoam` at
`Time = 1.10875`, PIMPLE iteration 1, "Evolving kinematicThinFilm for region region0":

```
DILUPBiCGStab:  Solving for Uf_filmx, Initial residual = 0.904609955813, Final residual = 1.51497091834e-11, No Iterations 5
DILUPBiCGStab:  Solving for Uf_filmy, Initial residual = 0.917221506179, Final residual = 4.08296463953e-11, No Iterations 5
DILUPBiCGStab:  Solving for Uf_filmz, Initial residual = 0, Final residual = 0, No Iterations 0
DILUPBiCGStab:  Solving for hf_film, Initial residual = 0.822885618048, Final residual = 2.77695412161e-11, No Iterations 4
```

**The film height equation converged to a final residual of 2.78e-11 in four iterations,
immediately before the crash.** The film velocity components converged likewise. **This
is not a runaway that the solver failed to control; it is a healthy-looking film solve
followed at once by a matrix the preconditioner cannot invert.**

### The reading — NARROWED, NOT PROVEN

> A floating-point fault while taking the reciprocal of a diagonal is, on its face, a
> **zero or denormal diagonal coefficient in the film region's `lduMatrix`** — which is
> what one would expect from a film face whose height has collapsed, i.e. the dewetting
> this case has chased since R2.

**That reading is NARROWED BY THIS EVIDENCE AND IS NOT PROVEN BY IT, and the distinction
is the same one the SECOND ADDENDUM above insisted on.** What is measured is the faulting
*operation*. **No artifact in any of these runs reads the diagonal back**, so the value
that was inverted is not on disk, and the step from "reciprocal of a diagonal faulted" to
"a film cell dewetted" is an inference with no instrument behind it. Establishing it
would need a rung registered to dump the film `lduMatrix` diagonal, or the film height
field, at the faulting step — which does not exist.

**What is NOT changed by this addendum:** whether the failure threshold scales with cell
size remains **UNTESTED**, exactly as the SECOND ADDENDUM corrected. Identifying the
faulting frame does not test it.

### THE SAME SEVENTEEN FRAMES APPEAR IN FIVE CRASHES ACROSS THREE FREEZES

Every `#`-prefixed frame was extracted from each crashed run's `log.pimpleFoam`, diffed
pairwise and hashed. **All five traces are byte-identical** — md5
`db7e4dd672c2663ef45ff6d7b2306065`, seventeen frames each, `diff` reporting no difference
on any pair:

| run | freeze | level/rung | artifact |
|---|---|---|---|
| VMFL072-R2 | R2's freeze | L3 | `verification/runs/ansys_verification/VMFL072-R2/L3/log.pimpleFoam` (`rc=136`) |
| **VMFL072-R3** | `305e4962` | **L3** | `.../VMFL072-R3/L3/log.pimpleFoam` (`rc=136`) — **this document's subject** |
| VMFL072-R4-A | `bb76616d` | A1 | `.../VMFL072-R4-A/A1/log.pimpleFoam` (`rc=136`) |
| VMFL072-R4-A | `bb76616d` | A2 | `.../VMFL072-R4-A/A2/log.pimpleFoam` (`rc=136`) |
| VMFL072-R4-A | `bb76616d` | A3 | `.../VMFL072-R4-A/A3/log.pimpleFoam` (`rc=136`) |

**This is a characterised recurring defect of OpenFOAM's finite-area film shell at this
operating point, not a per-case nuisance** — and it is worth more than this one case.

**The honest limit, stated so the next reader does not overread the table:** byte-identical
traces establish **the same code path and the same faulting operation**, five times, across
three freezes. They do **not**, alone, establish a single common root cause — identical
symbol names are exactly what one expects from the same binary reaching the same path, and
a shared path can in principle be reached by different causes. What makes the table strong
is its breadth (three freezes, four distinct `h0` values, two meshes), not the byte
equality by itself.

### ⚠ WHY THIS DOCUMENT IS AMENDED AND THE R4-A PRE-REGISTRATION IS NOT — the principle, not the exception

The VMFL072-R4-A pre-registration carries a stale self-description: its first lines still
read *"(DRAFT, NOT YET FROZEN)"* and *"STATUS: DRAFT. UNTRACKED."* while it is the
committed freeze at `bb76616d`. **That document is NOT being amended and this one is.
That is a rule, not an inconsistency:**

> **AMEND WHERE NOTHING IS PINNED. DISCLOSE WITHOUT MUTATION WHERE A PIN EXISTS.**

The pre-registration's blob `1202781e62a9f9fae7c1e62f3c0b76a934dc74fd` is **pinned by
`CLAUDE.md` rule 2's disk-versus-freeze hash equality** — the grading path's integrity
rests on that blob still hashing equal to the committed one. Appending even a correct
addendum would change the blob and **break a live integrity check in order to fix a
cosmetic line**. The stale header is therefore disclosed in the register rows and left
untouched in the file.

**No comparator, freeze guard or hash assertion pins this triage document.** There is no
check to break, so the correction lands where corrections belong: in the document that is
wrong, at its foot, dated, with the original text struck rather than rewritten.

*Ruling recorded by the `ansys-verification-supervisor`, 2026-09-12, so that a future
reader meets the principle and not only this instance of it.*
