# M6J — THE `transonic no` FAMILY: L3, L2, L1. PRE-REGISTRATION.

**Item:** `M6J_TRANSONIC_FAMILY`
**Team:** cfd. **Lane:** `lab-lane`. **Supervisor:** `cfd-supervisor`.
**Origin:** the top lead named in `M6I_PARKING_RECORD.md` ADDENDUM 2 §A2.8 — R10 moved the Cp
more than any rung in M6I (32.8 % of a grid level on RMS, 64.2 % on bias) and **L2 and L1 under
`transonic no` were never run.**

## 🔴 STATUS: **DRAFT. NOT FROZEN. NO SOLVER MAY RUN UNDER THIS DOCUMENT.**
Pre-compute: **`verification/runs/M6J_runs/` does not exist.** Launch through the runner;
entries drafted fail-closed into `verification/queue/cfd/held/`.

## §0 — M6I STAYS PARKED. THIS IS A NEW ACT, NOT AN R11.

M6I's §0 is untouched: its ladder is exhausted and nothing here reopens it. M6J carries one
**lead** forward under a fresh registration, which is what `M6I_PARKING_RECORD.md` §6 means by
*"parked is not cancelled"*. **No M6I gate, threshold, band, cap or label is altered.**

---

## 1. 🔴 THE ROACHE TRIPLE IS **NOT** IN PLAY, AND THE DISPATCH'S PREMISE DOES NOT SURVIVE THE FROZEN DEFINITION

M6J is the first M6 act since R5 that is a **family**, so it is the first that *could* produce
a triple. **But the admissibility bar is far higher than one satisfied limb, and this document
states that before the run rather than discovering it after.**

`M6I_R1_SOLVE_PREREGISTRATION.md` ADDENDUM 3, frozen, reads: *"A level is **shock-bearing only
if S1 AND S2 hold at BOTH η = 0.65 and η = 0.90**."* That is **four conditions per level,
twelve across a family.** Measured:

| level (`transonic`) | S1 @0.65 ≥0.212 | S1 @0.90 ≥0.320 | S2 @0.65 <0.85 | S2 @0.90 <0.85 | shock-bearing |
|---|---|---|---|---|---|
| L3_TVD (yes) | 0.0690 ✗ | 0.0434 ✗ | 0.9531 ✗ | 0.9233 ✗ | **no** |
| L2 (yes) | 0.1031 ✗ | 0.0582 ✗ | 0.8851 ✗ | 0.9233 ✗ | **no** |
| L1 (yes) | 0.1098 ✗ | 0.0827 ✗ | 0.8851 ✗ | 0.9233 ✗ | **no** |
| **L3 R10 (no)** | 0.0822 ✗ | 0.0515 ✗ | **0.8150 ✓** | 0.9233 ✗ | **no** |

**R10's L3 passes 1 of 4. S1 fails by 2.6× at η 0.65 and 6.2× at η 0.90. NO LEVEL IN THIS
ACT'S ENTIRE HISTORY HAS EVER BEEN SHOCK-BEARING.**

**So: the triple is registered here as a CONDITIONAL OUTCOME THIS DOCUMENT DOES NOT EXPECT.**
If all three M6J levels clear all twelve conditions, ADDENDUM 3 clause 1 applies and the triple
is computed under rule 5. **Otherwise ADDENDUM 3 clause 2 governs — no three-level order, no
GCI, computed, quoted or implied, and the comparison is labelled *"TWO LEVELS, NO ASYMPTOTIC
RANGE DEMONSTRATED"*.** ADDENDUM 3 is frozen and is **not** being reinterpreted.

**What M6J is actually for, stated plainly:** a **clean one-change measurement of `transonic no`
across three grids**, each with an already-graded `transonic yes` counterpart at identical
schemes. That is worth 1,083 core-minutes on its own. The triple is a bonus, not the plan.

---

## 2. 🔴 THE SCHEME SET — THE GRADED FAMILY IS MIXED AND A TRIPLE CANNOT BE

Measured across the graded family:

| level | `div(phi,U)` | `div(phi,nuTilda)` |
|---|---|---|
| **L3** | `linearUpwind limitedGrad` | `upwind` |
| **L2, L1** | `limitedLinearV 1` | `limitedLinear 1` |

**The family that produced M6I's verdict does not share a scheme set.** A Roache triple
requires three levels differing **only in h**; a mixed triple conflates discretisation order
with a scheme change.

**REGISTERED: the TVD set on all three levels** — `L3_TVD`, `L2` and `L1` carry a
**byte-identical `divSchemes` block, sha256 `223a8d2227d598e1`**, verified by this lane.

**`linearUpwind` is not available and that is measured, not preferred: `L2/ATTEMPT1_DIVERGED`
and `L1/ATTEMPT1_DIVERGED` both exist** — it diverged on both fine levels, which is why
ADDENDUM 8 moved them to TVD in the first place.

🔴 **AND THE COST OF THAT CHOICE IS AGAINST US: R10's evidence was obtained on L3 with
`linearUpwind`, NOT on the TVD set.** M6J-L3 therefore **re-establishes the effect on the
scheme set the family will actually use** before L2 and L1 are believed. Its counterpart is
`L3_TVD` (graded, `transonic yes`, identical schemes) — a clean one-change comparison. **If
M6J-L3 does not reproduce R10's direction against `L3_TVD`, the lead is weaker than the
parking record recorded and §5's branch (c) applies.**

---

## 3. 🔴 RANKS: 4 ON ALL THREE LEVELS — NOT 8 ON L1, AND HERE IS WHY

The dispatch offered L1 at 8 ranks. **This lane registers 4, and the reason is not throughput.**
All three levels carry `numberOfSubdomains 4; method hierarchical`. **Running L1 at 8 means
editing `decomposeParDict` — a second change** — and the R6/R7 comparison that settled the
pressure-floor question rested on **sha256-identical partitions and starting fields.** At 4
ranks every M6J level's decomposition is byte-identical to its graded counterpart's, so **the
only difference from the graded family is `transonic no`.** L1 at 4 ranks is 245,760 cells per
rank, a load L1 has already run to completion. The cost in core-minutes is unchanged; only wall
time doubles, and **nothing is killed on clock** (Sanaa directive #17).

---

## 4. THE ONE CHANGE, AND THE THREE BASELINES

**`system/fvSolution` and `system/fvSolution.startup`: `transonic yes;` → `transonic no;`**

| M6J level | staged from | cells | endTime | graded counterpart (`transonic yes`, identical schemes) |
|---|---|---|---|---|
| `M6J_L3` | `L3_TVD` | 15,360 | 3000 | `L3_TVD`, `m6i_grade_L3_TVD.json` |
| `M6J_L2` | `L2` | 122,880 | 5000 | `L2`, `m6i_grade_L2.json` |
| `M6J_L1` | `L1` | 983,040 | 8000 | `L1`, `m6i_grade_L1.json` |

**NOT carried forward:** R9's `nNonOrthogonalCorrectors 5` (stays **2**) and R8's `kOmegaSST`
(stays **`SpalartAllmaras`**) — both closed rungs that moved nothing, and either would confound
the formulation against its baseline. **Also unchanged:** `limited corrected 0.33`,
`pMinFactor 0.2`, `pMaxFactor 2.0`, every `div` scheme, every relaxation factor, `fvOptions`,
`writeInterval 200`, `purgeWrite 2`, `decomposeParDict`. **Added:** the verdict-inert
`clipCount` instrument.

**Pre-launch assertions, per level:** `constant/` byte-identical to the source; **exactly 3**
differing files in `system/` (`fvSolution`, `fvSolution.startup`, `controlDict`); **exactly 3**
changed/added lines; **exactly 1** new file (`system/clipCount.fo`); `nNonOrthogonalCorrectors`
still 2; `RASModel SpalartAllmaras`; the three pre-existing functionObjects byte-identical.
**And every launcher assert simulated against the staged case before arming** — that class of
defect refused this ladder twice (R8's model assert, R10's `transonic` assert).

---

## 5. THE PREDICTION — ALL THREE BRANCHES REGISTERED BEFORE THE RUN

**What is known: one measurement, on the coarsest grid, on a different scheme set.** R10-L3
(`linearUpwind`): RMS −32.8 % of a grid level, bias −64.2 %, S2 satisfied at η 0.65, S1 failed
by 2.6×/6.2×. **What is not known: anything about L2 or L1 under `transonic no`.**

- **(a) S2 HOLDS ACROSS THE FAMILY.** All three levels clear S2 at both stations and the S1
  limbs improve monotonically → the lead is real and resolution-robust. **If all twelve
  conditions clear, ADDENDUM 3 clause 1 opens the triple.** *This document does not expect
  twelve; it expects at most improvement.*
- **(b) S2 HOLDS ON L3 AND IS LOST ON L1.** **Registered now as a FINDING, not a
  disappointment:** a formulation benefit that disappears under refinement is a
  **resolution-dependent artefact**, and it would mean R10's result was a coarse-grid effect
  that the parking record's A2.8 over-weighted. That is a real result about the lead and it is
  written down **before** the run so it cannot be read as a let-down afterwards.
- **(c) M6J-L3 DOES NOT REPRODUCE R10's DIRECTION against `L3_TVD`.** Then the effect is
  scheme-dependent as well, the lead is weaker than recorded, and **L2 and L1 are not run** —
  §7's cost is not spent chasing an effect the coarse level already failed to confirm.

**Branch (c) is checked first and gates the other two.**

---

## 6. THE CURE GATE — TRANSCRIBED UNCHANGED

**D1** ≥ **0.1401**; **D2** ≥ **0.0880**; **D3** `x_shock_cfd` must leave **0.8851** forward.
**S1** ≥ 0.212 / ≥ 0.320; **S2** < 0.85; **B1** ≤ 0.050 on 12 rows; **B2** ≤ Δ_local.
Graded by **`scripts/grade_m6_agard_cp.py`, blob `e9d5c04b` at `4c931d97c`**, hash-verified in
the same shell invocation as each run; planted control must print `reader_saw_the_plant: true`.

🔴 **D2/D3 MISLOCATE AND THE DISCLOSURE TRAVELS:** the comparator resamples onto experimental
orifices whose intervals widen aft (**0.0501c at 0.4752 against 0.0701c at 0.8851**), so its
argmax picks the widest aft interval, not the steepest feature. **No reader may take `x_shock`
from it as a physical shock position** (parking addendum `801391c00`, Defect B). **S2 is a
`x_shock` limb and inherits this — which is precisely why §1 does not treat R10's single
satisfied S2 as evidence of a shock.**

---

## 7. COST (rule 12)

**Measured law, derived from the family's own three runs at 4 ranks:**
L3 `5.47/(15,360×2,800) = 1.272e-07`; L2 `69.87/(122,880×4,800) = 1.185e-07`;
L1 `949.53/(983,040×7,200) = 1.342e-07` core-min per cell-iteration. **Mean 1.27e-07**, and
R10 measured `transonic no` at the same stage-2 cost as `transonic yes` (5.47 vs 5.47).

| level | cells × iterations | **predicted core-min** | wall at 4 ranks | **cap** |
|---|---|---:|---:|---:|
| M6J_L3 | 15,360 × 3,000 | **5.9** | 0.02 h | **17.7** |
| M6J_L2 | 122,880 × 5,000 | **78.0** | 0.33 h | **234** |
| M6J_L1 | 983,040 × 8,000 | **998.8** | 4.16 h | **2,996** |
| **total** | | **1,082.6** | | **3,248** |

**Caps are 3× the prediction, which covers the worst ratio this family has ever measured —
R9's ×2.65 against an estimate of ×1.6.** A crossing grades the row `NOT A RESULT`; the cap is
never raised; **nothing is killed on spend or clock.** `cost_basis`: **MEASURED** in
core-minutes from each run's logs; dollars **DERIVED, NOT MEASURED** at $0.0513/core-h
→ ≈ $0.93 for the family. **Checkpoints every 200 iterations** (`writeInterval 200`,
`purgeWrite 2`) — on L1 that is ≈ 6 minutes of wall, well inside the 30-minute requirement.
**`memory_footprint_gb` per level, transcribed from the frozen R1 table: L3 0.5, L2 1.0,
L1 4.0** — declared, not measured, as that table says of itself. **R9's gate-B omission is not
repeated.**

---

## 8. WHAT THIS DOES NOT DO

1. **Does not reopen M6I** (§0) or alter any frozen gate, band, cap or label.
2. **Does not reinterpret ADDENDUM 3** — §1 quotes its four-condition bar and accepts clause 2
   as the expected outcome.
3. **Does not carry R9's correctors or R8's SST forward** (§4).
4. **Does not claim R10's result generalises** — §5 registers all three branches including the
   two that say it does not.
5. **Does not run L2 or L1 if branch (c) fires** (§5).
6. 🔴 **Does not fix the known-false `LAUNCH.log` line.** The launcher hard-codes
   `SA transonic=yes equations.p=1` in an echo and **will print `transonic=yes` on every M6J
   run**, directly under the widened assert's truthful `registered transonic formulation: no`.
   It is a measurement script and not this lane's to edit. **No successor may read that log
   line as evidence of this act's formulation.**

*Drafted by a cfd `lab-lane`, 2026-09-13. NOT FROZEN — NOT COMMITTED — NO RUN AUTHORISED.
No agent's message is Sanaa's consent. Submissions parked.*

---

# ADDENDUM 1 — 2026-09-13, cfd-supervisor. THE STATUS LINE OF THIS DOCUMENT CONTRADICTS THE ACT IT AUTHORISED. MY THIRD SELF-CONTRADICTORY FREEZE. AND THE L1 CAP CLAUSE IS SUPERSEDED.

**Version 1.0 → 1.1. Lines whose number changed above this section: 0.**
**No gate, threshold, band or label is altered.**

## A1.1 THE STATUS LINE IS FALSE AND WAS FALSE AT THE MOMENT I COMMITTED IT

This document still reads **"🔴 STATUS: DRAFT. NOT FROZEN. NO SOLVER MAY RUN UNDER THIS
DOCUMENT"** and **"`verification/runs/M6J_runs/` does not exist"** — in the very blob committed
at `63f5792` under the subject "M6J FROZEN", under which three solvers then ran.

**The freeze is evidentially sound and that is not in question:** blob `1cdb80db` matches the
working tree with zero diff, and the commit at **08:46:51Z preceded the first solver at
08:49:31Z by 2 min 40 s.** Rule 2 is satisfied by the timestamps and the hash. **The text says
the opposite of what the evidence says**, and rule 6 forbids editing it, so it is corrected
here.

**This is the third document I have frozen tonight carrying an internal contradiction** — R5's
`endTime`, R7's line count, and now this. All three were caught by a lane, none by me. **My §3
check reads gates, cost and the pre-compute condition; it does not read the document's own
status line against the act it governs.** That is the gap, stated for the third time.

## A1.2 THE L1 COST CAP — §7's CLAUSE IS SUPERSEDED, AND NOT BY ME

§7 reads *"A crossing grades the row `NOT A RESULT`; the cap is never raised."*

**M6J_L1 is measured at 1,777.6 core-min at `Time = 3412` of 8000 — 178 % of its registered
998.8 at 42.7 % of the run — and projects to ≈3,973.6 against a cap of 2,996, crossing at
≈21:23Z.** The projection is an extrapolation from a rate stable to 3.6 % over 3,200 iterations
and is **labelled as a projection, not a measurement.**

**§7's clause does not govern, and the ruling that supersedes it is already on record:**
Sanaa's **directive #17** (no run stopped by time or budget cap) and her universal rule of
2026-08-26 (**bookkeeping never voids physics**), applied by the chief earlier today in these
terms: *"cap crossings are recorded, never a verdict input."*

**So M6J_L1's crossing is RECORDED IN THE COST ROW AND IS NOT A VERDICT INPUT.** Its Cp numbers
are graded on the physics limbs and the completion rule alone. **The run is not stopped.**

## A1.3 THE COST LAW WAS BUILT ON ONE DATAPOINT AND THE PENALTY IS GRID-DEPENDENT

The registered law (mean 1.27e-07 core-min/cell-iteration) came from three `transonic yes` runs
plus **a single `transonic no` point at L3 that showed no penalty at all** (5.47 vs 5.47).
Measured stage-2 rates under `transonic no`:

| level | core-min/cell-iter | × the registered law |
|---|---|---|
| M6J_L3 | 1.565e-07 | **1.23×** |
| M6J_L2 | 3.624e-07 | **3.06×** |
| M6J_L1 | 4.909e-07 | **3.66×** |

**The `transonic no` penalty grows with refinement — 1.2× coarse, 3.7× fine.** A one-point
calibration on the coarsest grid was the wrong basis, **and that, not contention, is the
dominant term.** Contention is named and bounded rather than absorbed: L2 ran wholly overlapped
with L1's startup, yet **uncontended L1 measures 3.66× against contended L2's 3.06×**, so
concurrency did not inflate L2 above what an uncontended level shows.

## A1.4 THE PARKING RECORD'S BASELINES ARE UNRECONCILED — MINE, AND UNRESOLVED

`M6I_PARKING_RECORD.md:24` quotes span-avg rms **0.3323 / 0.2045 / 0.1423** and biases
0.1344 / 0.0531 / 0.0248. **Recomputing from the graded artifacts under five averaging
conventions — arithmetic mean, rms-of-rms, station-first, `n_graded`-weighted, per-surface —
reproduces none of them.** The arithmetic means are **0.2759 / 0.1661 / 0.1097**.

**I published those figures.** Either the parking record used a convention nobody has since
identified, or the grade JSONs were regenerated after it was written. **It is not settled and
must not be treated as settled.** M6J's own table is internally consistent — both families
recomputed from artifacts under one definition — and that is the table to use.

---

# ADDENDUM 2 — 2026-09-13, lab-lane under cfd-supervisor. **M6J_L1 IS RE-RANKED 4 → 16 AND RESUMED FROM A VERIFIED CHECKPOINT. §3's RANK CHOICE IS DISCLOSED AS WEAKENED FOR L1, AND THE RE-PARTITION IS A PERTURBATION, NOT A NO-OP.**

**Version 1.1 → 1.2. Lines whose number changed above this section: 0.**
*(Verified, not asserted: `git show HEAD:<this file> > BASE; head -n 273 <this file> | cmp - BASE`
returns identical — 273 lines and 15,694 bytes, the whole document through ADDENDUM 1 §A1.4.)*

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** The cure gate of §6, the
four-condition shock-bearing bar of §1, ADDENDUM 3 of `M6I_R1_SOLVE_PREREGISTRATION.md`, the
bands, `endTime 8000`, `writeInterval 200`, `purgeWrite 2`, the schemes, the solvers, the
relaxation factors and the `transonic no` formulation are **all untouched and were asserted
byte-identical on disk before the stop** (md5 of `system/{controlDict,fvSchemes,fvSolution}`
equals their `.registered` copies). It changes **the rank count on L1 only, and the core-minute
accounting that follows from it.**

## A2.1 WHAT WAS DONE, AND ON WHOSE INSTRUCTION

Sanaa directed that M6J_L1, running at 4 ranks with ≈8 h remaining, be resumed at 16 ranks on a
box with **96 cores and ~60 of them idle**, under her standing rule of 2026-08-26 that **idle
compute is a failure**. The act, in order:

1. **Identified** the solver by `/proc/1489103/cwd`, not by name: `mpirun -np 4 rhoSimpleFoam
   -parallel`, cwd `verification/runs/M6J_runs/M6J_L1`, started 2026-09-13T09:51:01Z, rank pids
   1489113–1489116. Liveness taken from the rank pids and the log mtime, never from log content.
2. **Chose the checkpoint t = 3800**, verified complete on **all four** ranks — the full field
   set `{T U alphat nuTilda nut p phi rho}` plus `uniform/` and `yPlus`, 10 entries per rank, every
   file mtime inside the single write burst `17:07:54.779–.865Z`. The solver was at `Time = 3884`
   and its next write was `t = 4000`, ≈116 iterations away, so **no write was in progress** and no
   partially-written time directory was a candidate.
3. **Stopped it by explicit pid** — `kill -TERM 1489103`. **`pkill` was not used and is
   forbidden here**: its pattern matches its own invoking shell. All five pids were gone in 3 s.
   **Verified in the same breath that nothing else was touched:** 46 solver pids before, 41
   after, the difference **exactly** the five M6J pids, **zero** new pids, and all eight
   surviving runs — the seven `SUBOFF_A1H_DRIFT/L1M_SWEEP/BETA_*` and `SUBOFF_A1/SOLVE_L2` —
   still **advancing**, with log mtimes within 3 s of the check.
4. **Reconstructed** t = 3800 (`reconstructPar -time 3800`, rc = 0), **moved the four 4-rank
   processor directories aside into `processors_4rank_PRE_RERANK/` — moved, never deleted** —
   and **re-decomposed** at 16 (`decomposePar -time 3800`, rc = 0), 16 × 61,440 = 983,040 cells.

**The graceful route was checked first and is unavailable on a running solver here, which is
stated rather than skipped:** the case carries `runTimeModifiable false`, so `stopAt writeNow`
in `controlDict` is never re-read; and the installed `etc/controlDict` has
`writeNowSignal -1` and `stopAtWriteNowSignal -1`, so no signal triggers a clean write. Signal
handlers are bound at solver start, so neither could be enabled after the fact. **`SIGTERM` was
therefore the only stop available.** It cost **iterations 3801–3886 — 86 steps — which the
resume recomputes.** `log.rhoSimpleFoam.stderr` is **0 bytes**: no MPI message, no `FOAM FATAL`,
no signal report. `FAILURE_CONTEXT.1.txt` and `RC.txt = 1` exist **because the launcher writes
them on any non-zero stage rc and a SIGTERM is one**; they are the deliberate stop, not a crash,
and `DELIBERATE_STOP_2026-09-13.txt` in the case directory says so beside them.

## A2.2 🔴 §3's REASON FOR 4 RANKS IS **WEAKENED FOR L1**, AND THAT IS A METHOD COST, NOT A BOOKKEEPING ONE

§3 did not register 4 ranks for throughput. It registered them because *"at 4 ranks every M6J
level's decomposition is byte-identical to its graded counterpart's, so **the only difference
from the graded family is `transonic no`**"*. **At 16 ranks that sentence is no longer true of
L1.** The L1 one-change comparison against its graded `transonic yes` counterpart now differs in
**two** ways: the formulation, and the partition. **This document will not pretend otherwise.**

**What bounds the damage is measured, not argued.** The new decomposition is `n (2 2 4)` against
the registered `n (2 2 1)` — hierarchical cuts x, then y, then z, so the registered 2×2 x–y cut
planes are **unchanged** and only z-cuts are added. **That nesting was verified from the mesh
itself, not asserted:** `cellProcAddressing` was read for all 4 old and all 16 new subdomains and
each new subdomain lies wholly inside **exactly one** old subdomain, with the unions exact —

| registered 4-rank subdomain | = union of new 16-rank subdomains | exact |
|---|---|---|
| 0 (245,760 cells) | 0, 4, 8, 12 | ✓ |
| 1 (245,760 cells) | 1, 5, 9, 13 | ✓ |
| 2 (245,760 cells) | 2, 6, 10, 14 | ✓ |
| 3 (245,760 cells) | 3, 7, 11, 15 | ✓ |

and the global cell set is identical (983,040). **No registered processor boundary moved; three
z-planes were added inside each.** That is the smallest partition perturbation available at 16
ranks, and it is why `(2 2 4)` was chosen over `(4 4 1)` or `(4 2 2)`, which move the x–y planes.

## A2.3 🔴 THE HAZARD, STATED AS A PERTURBATION AND NOT SMOOTHED AWAY

**The resumed run is NOT bit-identical to an uninterrupted one, and nesting does not make it so.**
Added interior boundaries change GAMG agglomeration, the parallel reduction order and therefore
the linear-solve path. On a steady solve converging to a fixed point the difference **should** be
within round-off of the converged answer, **but that is an expectation, not a measurement, and it
is registered here before the run rather than claimed after it.**

**Registered in advance:** the residual history across the resume seam will be read, and **a
visible jump at `Time = 3801` is reported as a finding about restart/partition sensitivity — it
is not noise, and it will not be smoothed, trimmed or averaged out.** The pre-resume series is
preserved for exactly this comparison: `log.rhoSimpleFoam` is not overwritten, and the 4-rank
decomposition survives verbatim under `processors_4rank_PRE_RERANK/`.

**Completion-rule note.** The launcher's resume path writes a **new** segment,
`log.rhoSimpleFoam.resume.1`, rather than appending to `log.rhoSimpleFoam` — and it must, because
its `run_stage` opens the log with `>` and appending in place would **truncate** the 201–3886
step record. This is gradeable: `scripts/solver_log_set.py:51–57` defines `log.<solver>.<anything>`
as a continuation and unions **distinct physics steps** across segments. Measured now:
segment 1 = `{1..200}`, segment 2 = `{201..3886}`, **union `{1..3886}`, zero gaps, zero overlap**;
the resume contributes `{3801..8000}`, closing the set to `{1..8000}`. **Iterations 3801–3886
will appear in two segments; they are one physics step each and are counted once.**

## A2.4 COST — BOTH SEGMENTS AT THEIR OWN RANK COUNT (rule 12)

**Measured from the launcher's own per-stage wall clock, at the ranks each stage actually ran:**

| segment | ranks | iterations | wall s | **core-min** | basis |
|---|---:|---|---:|---:|---|
| 1 — first-order ramp | 4 | 1–200 | 3,377 | **225.13** | MEASURED |
| 2 — registered schemes | 4 | 201–3,886 | 26,809 | **1,787.27** | MEASURED |
| **spent to date** | | **1–3,886** | | **2,012.40** | **MEASURED** |
| 3 — resume | **16** | 3,801–8,000 | *pending* | **2,040 – 2,910 (projected)** | **PROJECTED** |
| **L1 total** | | | | **≈ 4,050 – 4,920** | mixed |

Stage-2 measured **7.2732 s/iteration at 4 ranks = 0.4849 core-min/iteration**
(`4.93e-07` core-min/cell-iteration, which corroborates ADDENDUM 1 §A1.3's `4.909e-07`
independently). The segment-3 band spans **100 % down to 70 % parallel efficiency** at 61,440
cells/rank; the 80 % case is **2,546 core-min, 2.65 h wall**. **Projections are labelled
projections.** Dollars **DERIVED, NOT MEASURED** at $0.0513/core-h: L1 ≈ **$3.46 – $4.21**.

🔴 **THE RE-RANK BUYS WALL TIME AND SPENDS CORE-MINUTES, AND THE LEDGER SAYS SO.** The 4-rank
counterfactual for the same 4,200 iterations is **2,036 core-min and 8.49 h wall**; 16 ranks is
**2,040–2,910 core-min and 2.1–3.0 h wall.** At anything below perfect scaling this is **more
core-minutes for less wall**, i.e. **a real cost, not a free lunch** — justified only because
~60 cores are otherwise idle and Sanaa's 2026-08-26 rule makes idleness the worse failure.
**The idle-capacity argument does not make the core-minutes disappear and they are not netted
against it.**

**§7's cap clause remains superseded exactly as ADDENDUM 1 §A1.2 recorded** — Sanaa's directive
#17 and *"bookkeeping never voids physics"*. L1's projected total of ≈4,050–4,920 core-min
crosses the §7 cap of 2,996. **That crossing is RECORDED IN THE COST ROW AND IS NOT A VERDICT
INPUT. The run is not stopped on spend or clock.** Rule 12's estimate-versus-actual comparison
is owed at completion and will be filed in `docs/COST_CALIBRATION.md`, with the re-rank named as
its own attribution line rather than absorbed into the misprediction term.

## A2.5 WHAT THIS ADDENDUM DOES **NOT** DO

1. **Does not touch L3 or L2**, which stay at 4 ranks with `n (2 2 1)`. The registered file is
   kept verbatim as `system/decomposeParDict.4rank.registered` beside the 16-rank one.
2. **Does not alter a gate, threshold, cap, label or band**, and does not reopen ADDENDUM 1.
3. **Does not resolve §A1.4's unreconciled baselines**, which remain open.
4. **Does not claim the triple is any nearer.** §1's four-condition bar is untouched. But if all
   twelve conditions ever did clear, **L1 at 16 ranks against L2 and L3 at 4 is a declared
   confound in that triple** and must be disclosed there, not rediscovered.
