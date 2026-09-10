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
