# Dead-lever audit — C1 / docket B7, 2026-08-11

Executed under `LESSONS.md` **L-40** (the switch you set is not the switch that
ran) and `docs/charters/VERIFICATION_CHARTER.md` §9 (`levers_verified_active`).
Katie's §4 item 4: **the C1 dead-lever audit, every hump-adjoint conclusion.**

**Compute: zero core-minutes.** No solve was launched, and none is authorised.
Two compute requests are priced in §7 and are requests, not plans.

**Read-only.** This file is the audit's only write. Nothing found here was
fixed; a sweep that repairs as it goes destroys its own baseline.

**Frames, stated once.** Numbers below carry frame + filter + moment.
`grep` in this shell execs `ugrep --ignore-files` and honours `.gitignore`, and
the solver logs are exactly what is gitignored, so every count here was taken
with `/usr/bin/grep` or `scripts/sweep.py`, never the shell's `grep`.

| frame | what it selects | filter |
|---|---|---|
| **T** (tracked) | `git ls-files` — **20,586** files, **366** `.md` | drops untracked; **reaches** tracked-but-gitignored files the shell `grep` cannot |
| **L** (log population) | files named `*.log` under `/home/ubuntu/certonomous-runs` **and** `/home/ubuntu/Certonomous` — **1,635** files | `find` + `/usr/bin/grep -lI`; no ignore rules; excludes `.gz`, `log.run`, and logs not named `*.log` |
| **H** (hump adjoint) | the 7 substantive hump-adjoint runtime logs + 2 memory companions + `adjwall/HUMP51k/log.run` | named individually in §3 |

All counts taken **2026-08-11 17:20–17:28 UTC**, repo at **`11b44cab`**
(worktree dirty — several agents committing concurrently). A quoted figure is a
snapshot and needs its commit (L-79); re-derive rather than quote these.

**Relation to prior work, stated so this is not read as a first pass.** Three
audits already ran: `campaign/DEAD_LEVER_AUDIT_2026-08-08.md`,
`campaign/DEAD_LEVER_AUDIT_BATCH_2026-08-10.md`, and
`campaign/INSTRUMENT_INTEGRITY_2026-08-11.md` §1 (the fleet-wide C1, whose
**C1-A arm is the hump-adjoint target and reported CLEAN**). This pass is
**not** a re-run of C1-A. It differs in method (§1), it re-derives C1-A's
headline independently, and **it corrects one of C1-A's own claims** (§4, R-2).
Where it agrees with C1-A it says so and adds nothing.

---

## 0. Headline

**No dead lever was found on the hump — primal or adjoint.** Every hump lever
this pass could test fired, and the a1 ladder that carries the lab's only
measured closure-sensitivity slope is log-proven end to end at all five points.
Saying that plainly is the result; there was no finding to manufacture.

Three things did move:

1. **INACTIVE, off the hump:** the A3 stage-2 GAMG arm printed three ILU/ASM
   levers into its log while its own `-ksp_view` shows **zero** `asm` and
   **zero** `ilu` objects in the run. Reopens no conclusion (§2).
2. **ACTIVE-UNPROVEN, headline:** `jacMatReOrdering` is proven nowhere in the
   archive when set to `rcm`. **257 of 1,635 logs (frame L) request `rcm`; 0
   carry the readback that would prove it took.** The line the lab reads as
   proof is the *requested-value* printer its own FD-1 finding indicts (§4).
3. **A records defect the hump ladder's own log refutes:** rung 4 is published
   as a one-change arm and moved **three** levers (§4, R-1).

---

## 1. Method — and why it is not the prior audits' method

The prior sweeps drew their lever vocabulary **from the prose records they were
reading**, and both declared the consequence honestly: their counts are lower
bounds, not censuses. A vocabulary read off the records cannot contain a lever
nobody wrote down — which is the exact shape of the naval finding (nine wave
theories shipped, linked into three solvers, **0** tracked files referencing any
of them, against 1,825 for `alpha.water`).

This pass inverts the direction:

1. **Vocabulary from the configuration grammar, not the prose.** Every key was
   extracted mechanically from the hump's own configuration artifacts — the
   three `runScript_hump*.py` `daOptions` dicts and every
   `turbulenceProperties` / `controlDict` / `fvSchemes` / `fvSolution` /
   `fvOptions` under the staged hump run directories. **77 distinct lever
   tokens from 9 artifacts.** A lever that is configured and never mentioned
   survives this stage; it cannot survive a prose-derived vocabulary.
2. **Conclusions from the committed records.** Frame T, `.md` only: **106 of
   366 tracked `.md` files mention the hump**; intersecting those with the
   vocabulary in a hump-or-adjoint sentence context yields **115 candidate
   lever-citing lines across 40 files**. That list, not a hand-picked one, is
   what §3 works through, ranked by whether the conclusion travels.
3. **Verdict from the runtime log, never the dictionary.** Three verdicts, and
   `ACTIVE-UNPROVEN` is split two ways per the charter's `ran_before_found`
   rule: **no log evidence** (a log exists and does not carry the proof) is a
   physics question; **no log preserved** is a records defect. They are not
   merged.

**Cap (R-DEPTH).** §4 R-2 is this instrument checking C1-A's instrument
checking S1's claim. That is depth 2 and it stops there.

---

## 2. Positive control — reported first, before any absence

A method that finds nothing may be broken rather than reporting an absence.
The control was run first and its success condition fixed first: **the
instrument must separate a lever that is on from the same lever off, in two
runs of the same case.**

### 2.1 The control that passed — QCR2000 on the hump challenge pair

The W1 hump challenge conclusion (`campaign/W1_HUMP_CHALLENGE_RESULTS.md`) is a
single-lever comparison: SST versus SST+QCR2000, verdict "outcome two, the
constitutive route is ruled out on this leg". Both legs' logs are staged.

```
W1_hump_runs/sst/log.simpleFoam:71      Selecting RAS turbulence model kOmegaSST
W1_hump_runs/sst/log.simpleFoam:75          RASModel        kOmegaSST;
   (no Ccr1 line anywhere in the coefficient block)

W1_hump_runs/sst_qcr/log.simpleFoam:71  Selecting RAS turbulence model kOmegaSSTQCR
W1_hump_runs/sst_qcr/log.simpleFoam:75      RASModel        kOmegaSSTQCR;
W1_hump_runs/sst_qcr/log.simpleFoam:94      Ccr1            0.3;
```

The instrument separates on-from-off in both directions: the selection banner
**and** the QCR-only coefficient `Ccr1` appear in one leg and in neither case
in the other. **PASSED.** Only after this was any absence reported below.

### 2.2 A second control, on a numeric lever rather than a model name

Model-name banners are the easy case. The a1 shear-stress limiter is a scalar
inside a coefficient block, and it is the harder shape — so it was controlled
separately, and it happens to be the most load-bearing lever on the hump.

| a1 | log line | frame |
|---|---|---|
| 0.25 | `solve_registry/f6a_diff_SST_a1_025_20260801T001506Z.log:168` `a1  0.25;` | T |
| 0.28 | `W1_hump_runs/a1_028/log.simpleFoam:75` `a1  0.28;` | T |
| 0.31 | `W1_hump_runs/sst/log.simpleFoam:87` `a1  0.31;` | T |
| 0.34 | `W1_hump_runs/a1_034/log.simpleFoam:75` `a1  0.34;` | T |
| 0.40 | `solve_registry/f6a_diff_SST_a1_040_20260801T001014Z.log:168` `a1  0.4;` | T |

**Five distinct values, five distinct logs, five distinct printed numbers.**
`W1_HUMP_A1_RESULTS.md`'s three-point slope (−1.66 per unit a1 on [0.31, 0.34],
flattening to −0.27 on [0.34, 0.40]) rests on exactly these five runs, and
every one of them proves its own setting in its own log. This is the strongest
lever chain on the hump and it is **ACTIVE-PROVEN end to end.**

### 2.3 A control that caught the instrument, not the world

Re-checking C1-A's "max abs U 44.54 appears in no archived hump log", a regex
search returned **4 hits** — apparently a refutation. They are false positives:
the unescaped `.` matched `2.44754e-08` inside a `DILUPBiCGStab` residual line.
Fixed-string `/usr/bin/grep -F "44.54"` returns **0 across all 8 hump logs plus
`hump_sublu_computetotals.log`**. **C1-A's finding stands, re-verified.** It is
recorded here because a regex dot in an audit pattern is a fail-open shape and
this one nearly produced a false correction.

---

## 3. The C1 half — every hump-adjoint conclusion

**Population.** Nine artifacts: `S1_work/logs/hump_{adjoint,wf,nofvopt,nrn,nat,
mem}_run1.log`, `W4-adjoint-pc-unblock/hump_sublu_{computetotals,mem}.log`, and
`adjwall/HUMP51k/log.run` (a hump `DASimpleFoam` adjoint staging from 07-30 that
**no tracked record cites**; verified independently here — it echoes
`solverName DASimpleFoam` at `:383` and `jacMatReOrdering rcm` at `:524` and
carries **no** `PetscConvergedReason`, i.e. it never reached the adjoint solve).

### 3.1 Verdicts

| # | conclusion (record) | lever | verdict | evidence |
|---|---|---|---|---|
| 1 | `S1_FIML…:321` "BLOCKED, `-9` at iteration 0" is a `DASimpleFoam` adjoint result | `solverName: DASimpleFoam` | **ACTIVE-PROVEN** | `hump_adjoint_run1.log:409` `solverName DASimpleFoam;` |
| 2 | ladder rung 1: wall functions do not remove the `-9` | `useWallFunction: True` | **ACTIVE-PROVEN** | `hump_wf_run1.log:424` `useWallFunction 1;` **and** `:386` `Setting nut wall BC for bottom. BCType=nutkWallFunction` — dictionary **and** runtime BC |
| 3 | ladder rung 2: removing the clip does not remove the `-9` | `limitVelocity` fvOption **absent** | **ACTIVE-PROVEN (negative lever)** | `hump_nofvopt_run1.log` contains **0** `limitVelocity` lines against **725** in the baseline, **725** in rung 3, **725** in rung 4, **823** in rung 1. A removal proven by count, not by assertion |
| 4 | rung 2's parenthetical: the clip was inert anyway | `limitVelocity` inertness | **ACTIVE-PROVEN** | **721** lines of `limitVelocity limitVelocity1 Limited 0 (0%) of cells, 0 (0%) of faces, with max limit 70` in `hump_adjoint_run1.log` (first at `:683`), and those lines are not `printInterval`-gated |
| 4b | …but the *number* "max abs U 44.54" | — | **ACTIVE-UNPROVEN (no log evidence)** | §2.3. Non-load-bearing; owed a face caveat. Agrees with C1-A |
| 5 | rung 3: `None` converts NaN into honest stagnation | `normalizeResiduals: ["None"]` | **ACTIVE-PROVEN** | `hump_nrn_run1.log:571` `normalizeResiduals 1 ( None );` against `hump_adjoint_run1.log:572` `normalizeResiduals 11 ( URes pRes … );` — discriminated both ways |
| 6 | rung 4: `natural` is on its own enough to stop the NaN | `jacMatReOrdering: natural` | **ACTIVE-UNPROVEN (no log evidence) — see §4 U-1 and R-1** | echo `hump_nat_run1.log:552` `jacMatReOrdering natural;` and printInfo `:2238` `Mat ReOrdering: natural`. Both are requested-value prints |
| 7 | the mesh-gate relaxation is disclosed and was applied | `checkMeshThreshold.maxAspectRatio: 20000` | **ACTIVE-PROVEN** | `hump_adjoint_run1.log:265` and `:615` `maxAspectRatio 20000` — the run passed a gate a 12,131.6-aspect-ratio mesh would otherwise fail |
| 8 | sub-LU replaces the `-9` with a descending residual | `DAFOAM_SUBPC_TYPE=lu` | **ACTIVE-PROVEN, with negative control** | `hump_sublu_computetotals.log:2256` `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU`; the env-off control `cbfs_regress_computetotals.log` carries **0** such lines |
| 9 | …and the run's *outcome* | `KSPConvergedReason` | **NO LOG EVIDENCE — and the record already says so** | the log's last line is `Main iteration 900 KSP Residual norm 9.544468674795e-01 728.48 s.` and there is no reason code. Withdrawn in the record 2026-08-11 (`98a39662`, `1dee6551`); confirmed here, nothing to add |
| 10 | `pcFillLevel 1` under sub-LU | `adjEqnOption.pcFillLevel` | **LATENT INACTIVE** | `hump_sublu_computetotals.log:576` echoes `pcFillLevel 1` and `:2263` prints `ILU PC Fill Level: 1`, while `:2256` proves the sub-block PC is **complete LU** — an ILU fill level has no ILU to act on. **No conclusion leans on it**, so it reopens nothing. C1-A logged this as unverifiable; it is sharper than that |
| 11 | S1 §6: the M6 family was already `natural` when it failed, so ordering is not their shared setting | `jacMatReOrdering` on M6 | **ACTIVE-PROVEN (spot-check, 2 of the cited logs)** | `A3-onera-m6-transonic/check_totals_run1.log:528` `jacMatReOrdering natural;`; `A3-onera-m6-adjoint-coarse/check_totals_run1.log:524` same, **plus** `:1004` `Mat ReOrdering: natural` |
| 12 | the F6a substitution (custom `AugmentedkOmegaSST` unavailable → stock SST) is what ran | `libs` / `RASModel` | **ACTIVE-PROVEN** | `W1_hump_runs/sst/controlDict:24` has the library line **commented out** (`// libs ( "libfrozenIncompressibleTurbulenceModels.so" );`) and the log selects `kOmegaSST` at `:71`. Disclosed deviation, log-consistent |
| 13 | 2 further hump adjoint stagings | — | **NO LOG PRESERVED** | ledgered at ~40 s in `W4_ADJOINT_PC_UNBLOCK.md:300`. **No conclusion rests on them.** Records defect, not a physics question. Agrees with C1-A |

**Count: 14 hump-adjoint lever/conclusion pairs — 9 ACTIVE-PROVEN, 2 ACTIVE-UNPROVEN (no log
evidence), 1 NO LOG PRESERVED, 1 LATENT INACTIVE, 1 already-withdrawn.**
**Zero found-dead on the hump.** That reproduces C1-A's verdict by a different
route, which is worth more than either alone.

### 3.2 A discrimination check the records do not contain

The four ladder arms' initial adjoint KSP residuals, read from the logs:

| arm | `Main iteration 0 KSP Residual norm` |
|---|---|
| baseline (rcm, normalized) | `1.094138002900e+00` |
| rung 1 `useWallFunction` | **`1.094652221149e+00`** |
| rung 2 `limitVelocity` removed | `1.094138002900e+00` |
| rung 3 `normalizeResiduals None` | `1.094138002900e+00` |
| rung 4 `jacMatReOrdering natural` | `1.094138002900e+00` |

**Rung 1 is the only arm that moved the linear system's starting point.** This
is stated as an observation and explicitly **not** as a dead-lever finding:
with right preconditioning and `x0 = 0` the iteration-0 residual is `‖b‖`, and
`b = dF/dW` depends on the primal state, not on the preconditioner ordering, the
ILU fill, or residual row scaling. Rungs 3 and 4 are therefore *expected* to
leave it unchanged, and rung 2's identity is corroborated by the clip having
limited 0% of cells. Reading the identical residual as inertness would be a
manufactured finding; it is written down because a future reader will hit this
table and needs the argument that disposes of it.

What the table **does** establish: rung 1's arm is independently confirmed to
have changed the physics, and rungs 2–4 are confirmed to share a primal state.

---

## 4. Findings

### INACTIVE — a lever demonstrably did not fire

**I-1. The A3 stage-2 GAMG arm printed three ILU/ASM levers into a run
containing no ILU and no ASM.** Off the hump; inside the "beyond them" half of
the declared scope.

```
A3-stage2-gamg/stage2_gamg.log:864    ASM Overlap: 1
A3-stage2-gamg/stage2_gamg.log:867    Mat ReOrdering: natural
A3-stage2-gamg/stage2_gamg.log:868    ILU PC Fill Level: 0
A3-stage2-gamg/stage2_gamg.log:884      type: gamg          <- -ksp_view, same run
```

Counted over the whole file: **0** occurrences of `type: asm` and **0** of
`type: ilu`. Positive control on the same instrument: `A3-gateB-restoration/
gateB.log` returns **1** of each. The effective object tree is
`gamg` → `bjacobi`/`lu` coarse (`:903-919`) → `sor` smoothers
(`:962, :993, :1024`). None of the three printed levers had an object to act on.

**What it reopens: nothing.** The stage-2 GAMG arm's conclusion is about GAMG's
behaviour, and no record cites its ASM overlap, its ordering or its fill level.
It is reported because it is the cleanest specimen in the archive of the shape
L-40 names, and because it is the mechanism behind U-1 below.

### ACTIVE-UNPROVEN — ranked by how load-bearing the conclusion is

**U-1. `jacMatReOrdering` has no activity proof anywhere in this archive when
set to `rcm` — and the line the lab reads as proof is a requested-value print.**

The `Mat ReOrdering:` line sits inside the pre-solve `printInfo` block, three
lines below `Solver Type:` and `GMRES Restart:` — the block `INSTRUMENT_
INTEGRITY_2026-08-11.md` §1.2 (**FD-1**) proves is a *requested*-value print,
not an effective one, by exhibiting `Solver Type: gmres` / `GMRES Restart: 200`
at `gateB.log:861-862` against `type: fgmres` / `restart=30` at `:884-885` in
the same run's `-ksp_view`. The only readback that settles the ordering is the
`-ksp_view` line `matrix ordering:`.

Measured over **frame L (1,635 `*.log` files)**:

| measurement | count |
|---|---|
| logs printing the requested `Mat ReOrdering:` | **386** |
| …of which request `rcm` | **257** |
| logs carrying a `-ksp_view` `matrix ordering:` readback | **8** (only **3** are DAFoam adjoint logs; 5 are standalone PETSc probes in `W4-adjoint-pc-unblock/`) |
| logs carrying **both** a request and a readback | **3** — `A3-gateB-restoration/gateB.log`, `A3-stage2-lgmres/stage2_lgmres.log`, `A3-stage2-gamg/stage2_gamg.log` |
| logs carrying **`rcm` requested and a readback** | **0** |

All three logs that carry both requested `natural` — which is **also PETSc's
own default ILU ordering**, so even those three do not discriminate between "the
lever took" and "the lever did nothing and the default matched it".

> **[CHIEF, 2026-08-11 — independently re-derived, and it sharpens U-1 rather than
> weakening it.]** I re-ran this measurement from scratch on my own frame
> (`find` over both roots, `/usr/bin/grep -lIF`, not this shell's `grep`) and
> reproduced **all four numbers exactly**: 1,635 logs, 386 printing a requested
> ordering, 257 requesting `rcm`, 8 carrying a readback, **intersection 0**.
>
> Then I read what the eight readbacks actually *say*, which the table above
> counts but does not quote — and **five of them are `matrix ordering: rcm`**
> (`W4-adjoint-pc-unblock/{control,diagfill,nzdiag,sublu,zeropivot}_rcm.log`).
> None of those five prints a requested-ordering line at all: they are runs where
> `rcm` was set by another route and `-ksp_view` confirmed it took.
>
> **So the honest claim is narrower and more useful than "no activity proof
> anywhere".** `rcm` as a PETSc ordering is **proven to work in this environment**,
> five times over. What has never been proven is the link from **DAFoam's
> `jacMatReOrdering rcm` key** to that ordering. 257 runs set the key; not one
> shows the ordering it asked for. That is L-40's sentence with the subject named
> precisely — the switch you set is not the switch that ran — and it is a smaller,
> sharper, more falsifiable claim than the archive-wide absence.
>
> **It also de-risks M-A.** The proposed 8 core-min purchase is two arms with
> `-ksp_view` on, and the readback mechanism is now known to work here rather than
> assumed — those five logs are the working example. The measurement will produce
> a discriminating answer or a diagnosable failure, not silence.

**Consequence for the hump.** The hump adjoint logs contain the printInfo block
(`hump_adjoint_run1.log:2268-2277`) and **no** `-ksp_view` block at all. So
`rcm` on the hump baseline and `natural` on rung 4 are both proven only at the
dictionary-echo level. The conclusion that leans on this is
`S1_FIML_FIELD_INVERSION.md:363` — *"`rcm` is implicated in producing the
`DIVERGED_NANORINF` specifically, and any future attempt should treat the
reordering as a variable rather than a constant"* — which travels into
`DAFOAM_CASE_STATUS.md`, `B1_reproduction_plans.md`, and the W4 docket item's
rationale. A reader acts on it.

**Not a dead lever, and the argument is named rather than assumed.** Something
differed between rung 3 and rung 4: at iteration 100 rung 4 reads
`1.094138002841e+00` against rung 3's `1.094138002900e+00`, so the two runs are
not bit-identical after the PC is applied. That difference is **confounded** —
rung 4 changed three levers, not one (R-1) — so it demonstrates that *an* arm
lever acted, not *which*. **This is an argument, not an artifact**, exactly as
FD-1's blast-radius bound is. It ships as unverifiable-from-logs per charter §9.

**Priced fix in §7 (M-A).** One rerun of the existing rung-4 configuration with
`-ksp_view` would settle 257 archived runs' worth of ambiguity at the class
level, not just the hump's.

**U-2. `pcFillLevel` under sub-LU on the hump** — §3.1 row 10. Structurally
inert, echoed anyway, **no conclusion leans on it**. Sharpens C1-A's
"unverifiable" to "latent inactive".

**U-3. `adjStateOrdering: cell` and `gmresRelTol: 1e-6`** — echoed
(`hump_adjoint_run1.log:612`, `:557`), no readback exists in any hump log, and
**no tracked record concludes anything from either**. Listed for completeness so
the absence is a stated absence rather than an unswept surface.

### NO LOG PRESERVED — a different finding, not merged with the above

- **2 hump adjoint stagings** (§3.1 row 13). No conclusion rests on them.
- **The D3 n15 variant-lever nulls** — `WARMSTART_AUDIT.md` row 6, *"NO LOGS
  PRESERVED (lost with the interrupted session's scratchpad)"*. Already
  retired-as-superseded 2026-08-10; re-stated here only so the two buckets stay
  visibly separate. Not reopened by this pass.

### Records defects found while auditing (reported, not fixed)

**R-1. `S1_FIML_FIELD_INVERSION.md` rung 4 is published as a one-change arm and
moved three levers.** The section's own premise, `:346`, is *"Each is one change
against the same case, prediction written before launch."* The archived echoes:

```
hump_adjoint_run1.log:553-556   jacMatReOrdering rcm;      gmresMaxIters 2000;  gmresRestart 2000;
hump_nat_run1.log:552-555       jacMatReOrdering natural;  gmresMaxIters 1000;  gmresRestart 1000;
```

Rungs 1, 2 and 3 are genuine one-change arms (verified: every other echoed key
matches the baseline). **Rung 4 is not.** The budget change is visible in the
results text as "1000 of 1000 iterations" but is **nowhere disclosed as a
change**. Measured: `/usr/bin/grep -rn "gmresMaxIters\|gmresRestart"
--include="*.md"` from the repo root returns **118 lines across 45 files**
(this frame includes `.claude/worktrees/`, a live peer's checkout, which
contributes duplicates). Filtering those to hump context leaves **3**, and
none is about the ladder: `W4_ADJOINT_PC_UNBLOCK.md:171` describes the
*baseline* as `gmresMaxIters/Restart 2000`, and `W4_ADJOINT_PC_UNBLOCK.md:254`
plus `docs/INSTRUMENT_INTEGRITY_LEDGER.md:416` describe the never-run
`runScript_hump_rich.py`.

**Materiality, argued rather than asserted.** The baseline died at **iteration
0**, and neither a restart window nor an iteration cap can act at iteration 0.
So the claim "`natural` is on its own enough to stop the NaN" most likely
survives. But the arm cannot be called single-change, the ladder's stated
premise is falsified by its own log, and the lab's own later hygiene rule —
`A3_TRIAGE_LEVERS_PREREGISTRATION.md:58`, *"`gmresMaxIters` set to 2000 in ALL
arms"* — is exactly the rule this arm predates and needed. Owed a face
correction by the record's owner.

**R-2. `INSTRUMENT_INTEGRITY_2026-08-11.md` §1.1's "strengthening" claim is
wrong in kind, and contradicts §1.2 of the same file.** §1.1 states:

> This sweep found the **PC runtime banner** — `hump_nat_run1.log:2238 Mat
> ReOrdering: natural` against baseline `hump_adjoint_run1.log:2273 Mat
> ReOrdering: rcm`. The row moves from configured-and-echoed to
> **configured-and-observed-in-the-preconditioner**.

`Mat ReOrdering:` is not a preconditioner runtime banner. It is line 6 of the
same 10-line pre-solve `printInfo` block that contains `Solver Type:` and
`GMRES Restart:` — the block **§1.2 of that same document (FD-1) proves prints
requested, not effective, values**. The row did not move. It is still
configured-and-echoed, and by U-1 the discriminating readback exists in **0 of
257** archived `rcm` runs.

This is depth 2 and stops here: this instrument checked C1-A's instrument
checking S1's claim. **C1-A's headline verdict — the hump-adjoint attempts are
clean, zero found-dead — is independently reproduced above and is unaffected.**
One supporting sentence in it is wrong; the finding it supports is not.

**R-3. A regex dot in an audit pattern is a fail-open shape** — §2.3. Recorded
against the audit-instrument class, not against any record.

---

## 5. ACTIVE-PROVEN — the count

**17 lever/conclusion pairs proven active from a runtime log by this pass**, each
line-quoted above and counted rather than estimated:

| where | pairs | which |
|---|---|---|
| §3.1, hump adjoint | **9** | rows 1, 2, 3, 4, 5, 7, 8, 11, 12 |
| §2.1, hump primal | **2** | QCR on-leg (`kOmegaSSTQCR` + `Ccr1 0.3`); QCR off-leg (`kOmegaSST`, no `Ccr1`) — the off-leg is a pair in its own right, since the challenge conclusion is a difference and needs both halves |
| §2.2, hump primal | **5** | a1 at 0.25, 0.28, 0.31, 0.34, 0.40 |
| §2.1, hump primal | **1** | `limitVelocity` `State: active … selected 51626 cell(s)` in all four W1 legs |

The single most load-bearing chain in the hump corpus — the five-point a1 ladder
that carries the lab's only measured closure-sensitivity slope — is proven at
every point. (`printCoeffs on` is not counted separately: it is the *reason* the
a1 rows exist, not an independent conclusion.)

---

## 6. What this pass did not reach — the frontier, stated

Ranked by what a reader would most want covered next.

1. **`PROOF.md` §1–24 interior, ~2,400 lines.** Declared **STILL OPEN** by
   C1-A §1.2 and still open. Not touched here; out of the hump scope.
2. **`fvSchemes` / relaxation-factor levers on every hump run.** Structurally
   unecho-able by stock `simpleFoam`. The F5c precedent
   (`F5C_STAGE_A_RESULTS.md:84-88`) shows the launcher's lever echo makes them
   log-provable, and **every hump run predates that echo** (adopted `199e9d17`,
   2026-08-10). No hump conclusion currently cites a scheme, so this is a
   latent exposure rather than a live gap — but it is unswept, not clean.
3. **The in-container DAFoam build.** `DAResidualSimpleFoam.C` is not on this
   host (C1-A verified this with a positive control). Any claim that a hump
   `daOptions` key is dead *code* — as opposed to unproven — cannot be settled
   from here. This pass made no such claim.
4. **Frame L's own edges:** gzipped logs, `log.run`-named logs, and logs not
   matching `*.log` are outside the 1,635. The U-1 counts are therefore lower
   bounds on the population and **not** upper bounds on the readback count —
   which is the direction that matters, since more logs can only add to 386/257
   and the 0 was established by scanning every file that had a readback at all.
5. **The other ~85 hump-mentioning tracked `.md` files** that the sweep did not
   flag as lever-citing. Absence of a flag is a statement about the 77-token
   vocabulary, not about those files.

---

## 7. Priced compute requests — requests, not plans

Neither is authorised. Both are here because the alternative is a caveat that
never closes.

| id | what | why | price | basis |
|---|---|---|---|---|
| **M-A** | Rerun the existing rung-4 hump configuration with `-ksp_view` on, to iteration 10. Read back `matrix ordering:` and compare to the requested `natural`; then one arm at `rcm`. | Settles U-1 **at the class level**: it is the only measurement that can tell whether the printInfo ordering line is faithful, and 257 archived runs inherit the answer. Two arms because a single `natural` arm cannot discriminate against PETSc's default. | **~8 core-min** (2 arms × 4 ranks × ~1 min: the adjoint's cost to iteration 10 is dominated by the ~112 s coloring + assembly measured at `hump_adjoint_run1.log:2268`) | measured wall from the archived hump logs |
| **M-B** | Rerun rung 4 with `gmresMaxIters`/`gmresRestart` restored to 2000, everything else as archived. | Converts R-1's *argument* that the budget change was immaterial into an *artifact*. Also the hump's first deliberate reproduction of any adjoint attempt (11 attempts, 0 reproduced). | **~40 core-min** (4 ranks × ~9.5 min, from rung 3's measured 965.94 s at the same 2000-iteration budget) | `hump_nrn_run1.log`, measured |

M-A is the better buy at 5× less compute and a class-level answer. If only one
is bought, buy M-A. If neither is bought, U-1 and R-1 ship as face caveats under
charter §9 and nothing else changes.

---

## 8. Filings for `docs/DOCKET.md` section D

Real, outside the declared scope, not actioned here:

- **I-1 generalised.** DAFoam's `printInfo` prints ASM/ILU levers regardless of
  which PC is actually built. `DEFECT_CANDIDATE_ksp_options_override.md:160-163`
  already recommends an effective-value echo; **I-1 is a second, independent
  reason for that recommendation** — the first was override-driven, this one is
  PC-type-driven and fires even with no override present.
- **A scheme-echo gap with a known remedy.** Frontier item 2: the hump family
  predates the launcher lever echo, and the remedy already exists and is proven
  to work (F5c). A re-echo would need reruns and is not proposed.

---

## 9. RE-RUN, 2026-08-23 — U-1's headline has MOVED, and the archive settled it for free

**Lines whose number changed above this section: 0.** Appended at the foot;
nothing above was edited (rule 6). §4 U-1 stands as written and as dated.

**Sweep date:** 2026-08-23, 19:44–20:05 UTC. **Executor:** `lab-lane`,
verification team. **Compute: zero core-minutes.** Neither M-A nor M-B was
purchased; **neither needed to be.** **Read-only, as §0 was** — nothing found
here was fixed.

**Frames, restated because both moved.**

| frame | 2026-08-11 | 2026-08-23 |
|---|---|---|
| **T** (tracked, `git ls-files`) | 20,586 files, 366 `.md` | **9,767 files, 635 `.md`** |
| **L** (`*.log` under `/home/ubuntu/certonomous-runs` **and** `/home/ubuntu/Certonomous`, `find` + `/usr/bin/grep -lIF`, no ignore rules) | 1,635 files | **1,350 files** |
| tracked `.md` mentioning the hump | 106 of 366 | **172 of 635**, of which **48 added since 2026-08-11** |
| logs in frame L newer than 2026-08-11 | — | **607** |

**Frame L SHRANK, 1,635 → 1,350, and the reason is the MOVE_MAP reorganisation,
not deletion of evidence.** Logs that were under the repo root moved out of the
`*.log` reach of that path. **The denominators below are therefore not
differenceable against 2026-08-11's** — but the finding that follows is a
**positive existence claim**, which no denominator shrinkage can manufacture.

---

### 9.1 U-1 IS SUPERSEDED BY THE ARCHIVE. The `rcm` readback exists, six times.

§4 U-1 published this, and it was correct on 2026-08-11:

> | logs carrying **`rcm` requested and a readback** | **0** |

Re-measured over frame L today, by the same method — `find` over both roots,
`/usr/bin/grep -lIF`, never this shell's `grep`:

| measurement | 2026-08-11 (1,635 logs) | 2026-08-23 (1,350 logs) |
|---|---|---|
| logs printing the requested `Mat ReOrdering:` | 386 | **324** |
| …of which request `rcm` | 257 | **219** |
| logs carrying a `-ksp_view` `matrix ordering:` readback | 8 | **14** |
| logs carrying **both** a request and a readback | 3 | **9** |
| logs carrying **`rcm` requested AND a readback** | **0** | **6** |

The readback values across all 14: **11 `rcm`, 2 `natural`, 1 `nd`.**

**The six, each with its three lines quoted.** All six carry the identical
triple, and all six are B3 adjoint runs dated 2026-08-21 — after this audit:

```
B3-adjoint-unblock-reproduce/logs/arm_K2.log:513    jacMatReOrdering rcm;      <- dictionary echo
                                        :12054   Mat ReOrdering: rcm          <- printInfo, REQUESTED value
                                        :12087         matrix ordering: rcm   <- -ksp_view, EFFECTIVE value
B3-ilu-shift-runtime/logs/arm_C.log      :513 / :12054 / :12087   identical
B3-ilu-shift-runtime/logs/arm_L2.log     :513 / :12054 / :12087   identical
B3-ilu-shift-runtime/logs/arm_SA8.log    :513 / :12054 / :12087   identical
B3-ilu-shift-runtime/logs/arm_SA10.log   :513 / :12054 / :12087   identical
B3-ilu-shift-runtime/logs/arm_ST.log     :513 / :12054 / :12087   identical
```

**The readback is inside the right object, and that was checked rather than
assumed.** `arm_C.log:12061-12090` shows the `-ksp_view` dump immediately after
`dRdWTPC: 424 of 425` and `Main iteration 0 KSP Residual norm` — so it is the
**adjoint dRdWT** solve, not another PETSc object — and `matrix ordering: rcm`
sits inside

```
PC Object: 4 MPI processes
  type: asm
  ...
  PC Object: (sub_) 1 MPI processes
    type: ilu
      1 level of fill
      matrix ordering: rcm          <- the ILU factorisation's ACTUAL ordering
```

i.e. inside the ILU sub-block PC's own factorisation record.

**Why this discriminates where the three `natural` logs of 2026-08-11 did not.**
U-1's closing sentence was: *"All three logs that carry both requested `natural`
— which is also PETSc's own default ILU ordering, so even those three do not
discriminate between 'the lever took' and 'the lever did nothing and the default
matched it'."* **`rcm` is not the default.** A run that reads back `rcm` cannot
have got there by default, so these six close exactly the gap the `natural`
three could not.

**What is now proven, stated narrowly.** The link from **DAFoam's
`jacMatReOrdering rcm` key** to the **effective PETSc ILU ordering** is
log-proven, in six archived runs, at the `-ksp_view` level. The CHIEF's
2026-08-11 annotation to U-1 narrowed the claim to exactly this link — *"257 runs
set the key; not one shows the ordering it asked for"* — and **that narrowed
claim is what has now been answered.** On this evidence the lever is
**ACTIVE-PROVEN** in the B3 family.

**What is NOT proven, and this pass does not blur it.** The hump adjoint logs
still contain the `printInfo` block and **no `-ksp_view` block at all**
(§4's "Consequence for the hump"). **No hump run is among the six.** So `rcm` on
the hump baseline and `natural` on rung 4 remain proven only at the
dictionary-echo level, and the conclusion at
`S1_FIML_FIELD_INVERSION.md:363` is unchanged by this section. What has changed
is the **class-level** question: the printInfo line is no longer the only
evidence available anywhere, and where a readback exists it agrees with the
request.

**M-A is moot and should not be bought.** §7 priced *"rerun the existing rung-4
hump configuration with `-ksp_view` on … two arms … **~8 core-min**"* to settle
U-1 at the class level. The B3 work bought the class-level answer incidentally,
at zero marginal cost to this question. **A hump-specific `-ksp_view` arm would
still be the only thing that proves the hump's own runs** — but the 257-runs-worth
of class ambiguity M-A was justified by is gone.

**FD-1's blast radius also narrows, and the evidence is in the same block.** The
2026-08-11 argument (§4 U-1, §4 R-2) is that the `printInfo` block prints
*requested* values, exhibited by `gateB.log:861-862` `Solver Type: gmres` /
`GMRES Restart: 200` against `type: fgmres` / `restart=30` in the same run's
`-ksp_view`. In `arm_C.log` the same block is **faithful on four levers at once**
— `Solver Type: gmres` vs `type: gmres`; `GMRES Restart: 1000` vs `restart=1000`;
`ASM Overlap: 1` vs `amount of overlap = 1`; `ILU PC Fill Level: 1` vs `1 level
of fill` — in addition to the ordering. **This does not refute FD-1**, whose
counter-example is a run carrying a `-ksp_options` override. It bounds it: absent
an override, the block was faithful on every lever checkable in this run.
**Recorded as a finding, not as a ruling** — FD-1 is `INSTRUMENT_INTEGRITY_
2026-08-11.md`'s, and its owner grades it.

---

### 9.2 I-1 and the rest — not re-attempted, and saying so

- **I-1** (the A3 stage-2 GAMG arm printing three ILU/ASM levers into a run
  containing neither) was **not** re-derived. Its cited artifacts are still on
  disk and `stage2_gamg.log` is one of the 9 logs carrying both a request and a
  readback, but this pass did not re-count `type: asm` / `type: ilu` in it.
- **U-2, U-3, R-1, R-2, R-3** were **not** re-attempted. Nothing in this pass
  bears on them and none is withdrawn.
- **The 48 new hump-mentioning tracked `.md`** — the closure `NASA_hump_gate`
  and `Wu2018_PIML_RF` records, the B3 ladder, `HUMP_BASELINE_EQUIVALENCE_NOTE.md`
  — were **enumerated and not swept.** §1's method (vocabulary mechanically
  extracted from the configuration grammar, intersected with lever-citing
  sentences, verdict taken from the runtime log) was **not** re-run over them.
  Absence of a finding against those 48 is a statement about this pass's depth,
  not about those documents, and it is the largest thing this re-run did not
  reach.

### 9.3 What this re-run did not reach

1. **No hump conclusion was re-verified.** §3.1's 14 lever/conclusion pairs were
   not re-checked; the §5 count of 17 ACTIVE-PROVEN pairs is not re-derived here.
2. **The 607 logs new in frame L since 2026-08-11** were counted, and searched
   only for the two ordering strings. No other lever vocabulary was run over them.
3. **Frame L's own edges are unchanged** (§6 item 4): gzipped logs, `log.run`-named
   logs and logs not matching `*.log` are still outside the 1,350. The six-log
   finding is a lower bound on how many runs now carry the readback.
4. **The in-container DAFoam build** is still not on this host, and this pass made
   no claim about dead *code*.

---

## DATED SECTION, 2026-08-27 — THE SHARED GIT INDEX IS NOT BEING CORRUPTED BY A WRITER. IT GOES STALE **BECAUSE THE PRIVATE-INDEX PROTOCOL IS WORKING.** THE COUNTS ARE A CLOCK, AND THE RESET IS A LEVER THAT CANNOT BE A CONTROL.

**Appended at the foot; nothing above edited. `Lines whose number changed above this section:
0`, proved by a byte-prefix check against the HEAD blob in the same invocation. Referred by the
chief after five resets of `.git/index` in one day — 16:17Z (216 phantom staged deletions),
17:22Z (401), 18:30Z (65), 18:48Z (2), 19:12Z (67) — every "deleted" path present on disk and
at HEAD, with the hypothesis that a peer process writes the index. Measured here, live.**

### 1. THE MECHANISM, CAUGHT IN THE ACT

At **19:16:38Z** closure landed `e6961d48` ("M2 FROZEN"), which **added six files** under
`cases/RANS_LES_closure_models/M2_kepsilon_family/`. Immediately after, `git diff --cached
--name-status HEAD` reported **exactly those six as staged deletions**, all six present on disk
**and** at HEAD. Four minutes earlier the count had been **zero**.

**The prediction that settles it**, tested against the chief's own 19:12Z reset baseline
`4918aec2`:

| quantity | value |
|---|---|
| files **ADDED** between `4918aec2` and HEAD | **6** |
| phantom staged **deletions** in the shared index | **6** |
| the two **SETS**, sorted and diffed | **IDENTICAL** |
| phantom **ADDITIONS** in the shared index | **0** |

**That last row is the control, and it is what makes this a measurement rather than a story.**
An index somebody **staged into** would carry `A` rows. An index that is merely **OLDER than
HEAD** carries **only `D` rows**. There are no `A` rows.

**THE PRIVATE-INDEX PROTOCOL ADVANCES `refs/heads/main` AND NEVER TOUCHES `.git/index`.** That
is by design — `git commit-tree` writes a commit from a tree, and `update-ref` moves the branch;
neither has any reason to update a file the protocol deliberately avoids. **So the instant any
agent lands a private-index commit that ADDS a path, `.git/index` is behind HEAD by exactly
those paths, and git faithfully reports them as staged deletions.**

**NO WRITER IS REQUIRED. The index goes stale BECAUSE THE PROTOCOL IS WORKING CORRECTLY.**

### 2. THE COUNTS ARE A CLOCK, NOT AN ALARM

**216 / 401 / 65 / 2 / 67 are not five intrusions. They are the number of files the fleet
added since the previous reset.** They grow with the lab's productivity and drop to zero when
somebody resets. **The 401 at 17:22Z is not a worse attack than the 2 at 18:48Z; it is a longer
interval.** Reading them as a severity scale inverts what they measure.

### 3. THE `mtime` OBSERVATION IS EXPLAINED, AND IT IS BENIGN

A cfd lane saw `.git/index`'s mtime move **right after its own private-index commit** and
inferred a peer writer. **`git status`, `git diff` and `git diff --cached` all REFRESH the
index's cached stat data and rewrite the file** — including in the post-commit verify that rule
10 **mandates**. That moves the mtime and changes **no tree**.

> **INDEX MTIME MOVEMENT IS NOT TREE STALENESS.** They have different causes, different
> frequencies and different consequences, and the report conflated them. The lane's observation
> is real; its inference does not follow.

### 4. THE DEAD-LEVER FINDING — the reset cannot be a control

Under this audit's own thesis (`L-40`, *the switch you set is not the switch that ran*):

**Resetting the index is not useless — it genuinely reduces BLAST RADIUS.** If a forbidden bare
`git commit` fired while the index was stale by 401 paths, 401 files die; at 0, none do. **That
is a real benefit and it is not withdrawn here.**

**But it cannot be a CONTROL, because the condition it clears re-arms within seconds.** Measured
today: **zero to six in under four minutes**, from ordinary fleet traffic. A control that the
system defeats on its own, without adversity, at the rate of normal work, is a **lever that
looks like a switch** — and after five pulls in one day the residual risk is unchanged in kind.
**The exposure is not that the index is stale. It is that a command rule 10 absolutely forbids
would SUCCEED if anyone ran it.** Staleness only sets the price.

### 5. RECOMMENDATIONS — a config change, so RECOMMENDED AND NOT MADE

1. **STOP RESETTING ON A SCHEDULE.** It costs chief attention five times a day, and — worse —
   it **reports as handled a thing that is not addressed.** Reset when a specific action needs a
   clean index, not because the number grew.
2. **`core.indexFile` pointed elsewhere — DECLINED ON THE MERITS, not deferred.** It renames the
   shared index and changes nothing: the new file goes stale by the identical mechanism, and a
   bare `git commit` commits *it*. It moves the gun; it does not unload it.
3. **Making `.git/index` READ-ONLY is the right SHAPE, and it is Sanaa's call.** Its virtue is
   precise: it **converts a rule agents can violate into a mechanism they cannot** — a bare
   `git commit` would *fail* rather than silently revert peers' work. **It is recommended, not
   taken**, and it must not be adopted on this section alone. **Per `VERIFICATION_CHARTER` v1.13
   and Sanaa's §1, it ships only with a planted-failure proof**, demonstrated in a throwaway
   clone: (a) `git commit` **fails** with the index read-only; (b) the private-index protocol
   still completes end to end; (c) `git status` / `git diff` still work; (d) nothing in the
   lab's routine tooling breaks. **A guard adopted without that proof is the shape this lab
   keeps publishing findings about.**

### 6. WHAT IS **NOT** ESTABLISHED, stated so the clean explanation is not over-read

- **Whether a script ALSO writes the shared index is `NOT MEASURED`.** The structural mechanism
  accounts for **100 % of the deletion signature**, so no additional writer is *needed* to
  explain anything — **but "not needed" is not "not present".** A per-script census of every
  tracked `git add` / `read-tree` / `update-index` call site, classified guarded or unguarded,
  is in flight and is **not** reported here.
- **Whether the installed `.git/hooks/pre-commit` (the D242 index guard) already REFUSES a bare
  commit is `NOT MEASURED` here.** If it does, the exposure in §4 is smaller than the referral
  assumed, and recommendation 3 becomes belt-and-braces rather than the primary control. **That
  is being tested in a throwaway clone and the answer will change the weight of §5, so it is
  named rather than assumed in either direction.**
- **One precondition IS established by execution, and it matters for a different reason:** shell
  environment **does not persist between an agent's Bash invocations** (an `export` in one call
  was unset in the next, tested directly). **So an agent that splits the private-index protocol
  across two calls runs its git commands against the SHARED index.** `CLAUDE.md` rule 10 already
  requires one invocation — but for a **different stated reason** (HEAD moving between calls,
  `L-223`). **The environment-loss consequence is a second, unstated reason for the same rule,
  and it is the more immediate one.** Recommended for the rule's next restatement.

---

## DATED SECTION 2, 2026-08-27 — THE INDEX AUDIT CLOSES: THE CHAIN CLOSES **EXACTLY** ON FOUR OF FIVE RESETS, THE EXPOSURE IS **ALREADY BLOCKED** BY ONE UNTRACKED HOOK — AND **§4/§5 OF THE PREVIOUS SECTION UNDERSTATED THE DANGER, WHICH IS CORRECTED HERE**

**Appended at the foot; nothing above edited. `Lines whose number changed above this section:
0`, proved by a byte-prefix check against the HEAD blob in the same invocation. Lane evidence
re-checked against my own measurements before acceptance; the two corrections in §2.4 and §2.5
are against THIS TEAM'S OWN previous section.**

### 2.1 THE STRUCTURAL EXPLANATION IS CONFIRMED, AND NOT BY ONE SAMPLE

The count inversion closes **exactly** on four of the five resets — phantom deletions == files
added between the previous reset's baseline and this one's:

| reset | reported | measured | |
|---|---|---|---|
| 16:17Z | 216 | 217 (from `e8650668` @ 2026-08-26T22:46:38Z) | off by **1** |
| 17:22Z | 401 | **401** | exact |
| 18:30Z | 65 | **65** | exact |
| 18:48Z | 2 | **2** | exact |
| 19:12Z | 67 | **67** | exact |

**And it was reproduced with no writer present at all:** in a throwaway repo, landing four files
by the rule-10 protocol alone produced **4 phantom deletions, 0 phantom additions**, all four
paths on disk and at HEAD. **The 16:17 count also dates the shared index's previous sync to
2026-08-26T22:46:38Z — it entered today already ~17.5 h stale, with no earlier reset to
explain it.**

**The `mtime` mover is now named exactly:** `scripts/session_log.py:77,79` runs
`git diff --cached` from the **`SessionStart` hook** (`.claude/settings.json:9`), rewriting
`.git/index` at every session start. Benign, tree-neutral, and **it will keep producing the
observation that was read as intrusion.**

### 2.2 RESETTING BUYS A MEDIAN OF UNDER FIVE MINUTES — measured, not asserted

Time from each reset until the index was stale by ≥ 1 path: **7.3 / 0.1 / 13.2 / 1.3 / 4.6
minutes** — **median 4.6, worst case 8 SECONDS.** Day mean add-rate **3.06 files/min** (535
files / 175 min). **A reset is a cosmetic operation on a counter that re-arms itself within one
commit.**

### 2.3 THE EXPOSURE IS REAL AND IS **ALREADY BLOCKED** — two independent barriers, both holding

Tested in throwaway clones with the byte-identical real hook (`sha256` prefix `8f4a264fc41ba560`
on both copies):

- **Without the hook:** with the index stale by 4 paths, a bare `git commit -m x` returned
  **rc 0** and committed all four deletions. **HEAD went from 5 tracked files to 1, with all
  four still on disk.** Silent, clean-looking, catastrophic — the `c46309f5` / `L-223` shape.
- **With the real hook: rc 1, REFUSED.** `.git/hooks/pre-commit:170` is the predicate
  (`if [ -e "$path" ]` — the index deletes it and the file is still in the tree), `:173` the
  message — *"Nobody deleted it here; the index is carrying someone else's removal"* — `:255`
  the banner, `:274` `exit 1`.
- **The lawful pathspec form is structurally safe:** `git commit -m x -- <path>` returned rc 0
  and committed **only** the named path; git builds a temporary index from HEAD plus the
  pathspec, so the shared index's staleness is **unreachable** through it.

### 2.4 ⚠ CORRECTION TO §5 OF THE PREVIOUS SECTION: READ-ONLY `.git/index` IS **NOT** THE PRIMARY CONTROL, AND THE REAL RECOMMENDATION IS DIFFERENT

The previous section recommended read-only `.git/index` as *"the right shape … converts a rule
agents can violate into a mechanism they cannot."* **That was written without knowing the D242
hook already refuses the exact commit in question. It is now belt-and-braces, not the control**,
and it is **downgraded** accordingly.

**THE RECOMMENDATION THAT REPLACES IT, and it is stronger:**

> **`.git/hooks/pre-commit` is the ONLY thing standing between a stale index and a silent mass
> revert, and it is UNTRACKED.** `.git/hooks/` never travels with a clone, is not in any commit,
> and is not covered by any freeze. **It should be treated as a FROZEN INSTRUMENT — hashed,
> registered, and checked — not as an installed convenience.** The tracked copy at
> `scripts/installed/pre-commit` and `scripts/installed_registry.py` are the only evidence a
> reader has that the hook on this box is the reviewed one, and **nothing verifies that today.**

**Two gaps disclosed rather than glossed:** `.git/hooks/pre-commit:107` honours
`CERTONOMOUS_INDEX_GUARD=off`, and **the hook is not invoked by `commit-tree` at all** — so the
protocol this lab actually uses runs *outside* its only barrier. Neither is reachable by
accident; both are reachable on purpose.

### 2.5 ⚠⚠ AND A SECOND EXPOSURE CLASS THE PREVIOUS SECTION MISSED ENTIRELY — `git checkout -- <path>`

The previous section stated the exposure as *"a command rule 10 absolutely forbids would
SUCCEED"* and named only a bare `git commit`. **That is incomplete, and the missing class is
worse.**

**`git checkout -- <path>` and `git restore <path>` restore from the INDEX, not from HEAD.** So
where the index holds a **stale blob** — not a missing entry, but an older version — either
command **silently writes old content over current work.** Measured on the live repo,
read-only, right now:

| path | index blob | HEAD blob | lines idx / HEAD / disk | effect of `git checkout -- <path>` |
|---|---|---|---|---|
| `verification/runs/T-family/T16_runs/mark_done_t16.py` | `2ae1605c` | `efcf7852` | **350 / 593 / 593** | **−243 lines** |
| `docs/LAB_STATE.md` | `ee5d8e15` | `dcdd45d3` | 16197 / 16216 / 16216 | −19 lines |
| `docs/COST_CALIBRATION.md` | `23a3b6b9` | `660bc137` | 258 / 260 / 260 | −2 lines |

**`mark_done_t16.py` is armed for a 243-line regression right now. For heat-transfer** — it is
the file D541 is about.

**Why this class is worse than the bare commit, in three ways the previous section did not
weigh:** it **leaves no commit to inspect** — the file simply changes on disk; **the D242 hook
does not fire**, because no commit occurs; and **read-only `.git/index` would NOT block it**,
because `checkout` *reads* the index rather than writing it. **The control recommended in the
previous section does not defend against the exposure found in this one.**

**On the referred 248-line `COST_CALIBRATION.md` loss: the MECHANISM is confirmed and the
SPECIFIC ATTRIBUTION is `NOT MEASURED`.** The current index would cost that file **2** lines,
not 248; the index blob it held ~40 minutes earlier is not recoverable. **The nearest live
match is `mark_done_t16.py` at −243, a different file.** The hypothesis is sound, its instance
is unproven, and a mechanism that explains a defect is not evidence that it caused *that* one.

### 2.6 ONE LIVE RULE-10 VIOLATION, FOUND OUTSIDE THE BRIEF AND PROVEN BY EXECUTION

**`scripts/withdrawal_sweep.py` writes the SHARED index.** `:414`
`git add --intent-to-add <plant>`; `:443` `git rm --cached --force <plant>`; the `_git` helper
at `:381` sets **no `GIT_INDEX_FILE`, no `--index-output`, no temp-repo assertion**; `--root`
at `:477` **defaults to the real repository** and `--frame` at `:478` defaults to `"tracked"`,
the branch reaching both writes. **Its own documented invocation at `:144` —
`python3 scripts/withdrawal_sweep.py`, no arguments — writes `.git/index`.** Proven in an
isolated reproduction: index content sha `1f3f87c1…` → `3e7e0253…`.

**Severity stated honestly: this is NOT the culprit.** Its `finally` block cleans up — 0
leftover entries, 0 staged deletions after a run. **The residue window is real but narrow:
`--intent-to-add` at `:414` sits outside the cleanup guarantee under SIGKILL, which is exactly
how this fleet dies at a session limit.** A docket line on its own terms; not an explanation
of 216/401/65/2/67.

### 2.7 WHAT REMAINS `NOT MEASURED`

- **The 16:17 off-by-one** (216 reported, 217 measured). Candidates — a single `update-index
  --add`, or an add-then-remove inside the window — were **not distinguished, and no fit was
  forced.**
- **No writer can be proven absent**, only that none is *required* and none was found by a
  sweep of every tracked `*.py`/`*.sh` outside `sdk/tests/`. **That sweep cannot see an
  untracked script, an inline agent bash call, or a `git` invocation assembled from strings.**
  *Not found by that sweep* is the correct reading.

## §3 — THE SIXTH OBSERVATION IS THE FIRST NON-EXACT ONE, AND THE RESIDUAL IS NOW UNATTRIBUTABLE BECAUSE THE RESET DESTROYED IT (2026-08-27T21:39:14Z)

**Appended, append-only. Nothing above is rewritten. Zero compute.**

**§3.1 — THE PREDICTION, TESTED A SIXTH TIME.**

§2 established that phantom staged deletions == paths **added to HEAD since the
index was last written**, with no writer required, and recorded **4 of 5 EXACT**
(17:22 → 401, 18:30 → 65, 18:48 → 2, 19:12 → 67) with 16:17 off by one.

The chief reported a recurrence at **21:28Z: 237 staged deletions, index last
written 19:33:22Z, all at HEAD, on disk, nobody writing.** Tested against the
same rule, clock read `date -u` in the measuring invocation:

| quantity | figure |
| --- | --- |
| last commit at or before 19:33:22Z | `aaf0bed6`, 19:33:04Z |
| paths **ADDED** to HEAD since it | **234** |
| paths **DELETED** from HEAD since it | **0** |
| of the 234, absent on disk | **0** |
| staged deletions observed | **237** |
| **residual** | **3** |

**The structural explanation covers 234 of 237 — 98.7 %. It is the FIRST
observation that is not exact, and the residual has the sign that admits a real
deletion.** §2's discriminating control still holds in the direction that
matters: **phantom ADDITIONS = 0**, so this is an index behind HEAD and not an
index somebody staged into.

**§3.2 — ONE RESIDUAL IS NAMED AND IT IS A GENUINE DELETION, NOT A PHANTOM.**

The chief reported *"one path in the set was at HEAD but absent on disk."*
**§2's control asserted every such path is present on disk AND at HEAD; that
assertion now has an exception.** A path at HEAD and absent from disk is a
**real worktree deletion** surfacing as a staged deletion, and it is outside the
structural set entirely — the mechanism does not explain it and was never
claimed to. **It belongs to its owning team as a worktree deletion, which is how
the chief routed it.** Measured on the 234 added paths, **0** are absent on
disk, so the exception is not among them: it entered before 19:33:04Z and left
the disk afterwards.

**§3.3 — THE FINDING, AND IT IS ABOUT RESETTING RATHER THAN ABOUT THE INDEX.**

**TWO RESIDUALS REMAIN UNATTRIBUTED, AND THEY ARE NOW UNATTRIBUTABLE. The index
was reset to HEAD at 21:28Z, and the reset is what destroyed the evidence.** The
staged-deletion list, the blobs it held and the entry timestamps were the only
record that could have named them; after a reset there is nothing left to
interrogate.

> **Each reset erases the only record that would attribute its own residual.**

**Five resets today have left five unattributed residuals**, and this audit has
been able to name a mechanism for the bulk each time **only because the bulk is
predictable from git history, which survives.** **The part that does NOT survive
is exactly the part that would distinguish "no writer is required" from "no
writer is present" — the question §2.7 already recorded as , and
the reset guarantees it stays that way.**

**This strengthens §2's recommendation rather than adding a new one.** §2
recommended stopping the scheduled resets on the ground that they buy a median
of **under five minutes** and *report as handled a thing that is not addressed*.
**A second ground is now measured: they are also the reason the residual has
never been attributed in six observations.** The recommendation is unchanged and
is still **RECOMMENDED, NOT MADE** — the index is the chief's call and
configuration is Sanaa's.

**§3.4 — WHAT IS NOT CLAIMED.**

**The 237 was NOT observed by this team** — it is the chief's reading, relayed,
and this section tests a prediction against it rather than re-deriving it.
**The two unattributed residuals are not asserted to be intrusions**, nor to be
benign; they are ** and now unmeasurable**, and that is the whole
point of §3.3. **No barrier changed**: `.git/hooks/pre-commit` still refuses a
bare commit, `git checkout --`/`git restore` still restore from the INDEX and
still bypass that hook, and both remain as §2 left them.

| §3 | figure |
| --- | --- |
| observations of the prediction to date | **6** |
| exact | **4** |
| off by one | **1** (16:17) |
| off by three | **1** (21:28, this one) |
| coverage of the sixth observation | **234 of 237 = 98.7 %** |
| phantom ADDITIONS, the discriminating control | **0** |
| residuals attributed | **1 of 3** (the chief's genuine worktree deletion) |
| residuals now permanently unattributable | **2** |
| resets today | **5** | 
| unattributed residuals those resets destroyed the evidence for | **5** |

### §3.5 — CORRECTION, SELF-INFLICTED, FOUND THREE MINUTES AFTER COMMIT: MY OWN COMMIT PROTOCOL DELETED A VERDICT WORD AND EVERY GUARD I RAN PASSED

**Appended, append-only. Lines 919 and 935 are NOT edited — they are struck here
and restored here, so no line above changes number and the defect stays on the
record.**

**§3.5.1 — WHAT IS WRONG, exactly.**

Two spans in §3 were destroyed at write time. Both lost the same token, and the
token is a **verdict word**:

- **Line 919** stands as *"the question §2.7 already recorded as , and the reset
  guarantees it stays that way."*
  **It should read** *"the question §2.7 already recorded as `NOT MEASURED`, and
  the reset guarantees it stays that way."*
- **Line 935** stands as *"they are \*\* and now unmeasurable\*\*, and that is the
  whole point of §3.3."*
  **It should read** *"they are `NOT MEASURED` and now unmeasurable, and that is
  the whole point of §3.3."*

**No figure, no verdict and no recommendation in §3 changes.** The 234 / 237 /
residual 3, the 6 observations, the 4 exact and the 98.7 % all stand as
committed and were unaffected.

**§3.5.2 — THE MECHANISM, which is a variant this lab has not recorded.**

The section was written through a heredoc whose delimiter was **unquoted**
(`<<MD` rather than `<<'MD'`). Backticks inside an unquoted heredoc are
**command-substituted**. Every other backticked span in §3 had been escaped;
these two had not. The shell attempted to execute `NOT MEASURED` as a command,
twice, and **substituted its empty output into the document.**

**The lab's existing note is that backticks in `git commit -m` are
command-substituted and the commit SILENTLY NEVER RUNS. This is the opposite and
worse failure: the commit RAN, the file landed, and the only casualty was TEXT
INSIDE THE DOCUMENT.** A failure that stops the work announces itself; a failure
that completes the work with a word removed does not.

**§3.5.3 — THE FINDING, AND IT IS ABOUT MY PROTOCOL RATHER THAN ABOUT BACKTICKS.**

**Every guard in the rule-10 private-index protocol ran and every one passed:**
the byte-exact PREFIX assertion (`PREFIX ASSERT OK`), `git diff-tree --stat`
showing only my path, the CAS on the parent, and the mandated post-commit
`git diff HEAD~1 HEAD --stat`. **None of them could possibly have caught this.**

> **The protocol verifies that I did not damage what was already there, and the
> SIZE of what I added. It verifies NOTHING about whether what I added says what
> I meant.**

The prefix assertion is exactly and only a check on the **unchanged** region.
**The appended region is unverified by construction** — and the appended region
is the entire content of every amendment, addendum and audit section this team
ships.

**The failure was visible and was nearly read past.** Two lines of
`NOT: command not found` were printed to stderr **above** a run of four passing
assertions. **`L-360` says read the guard and not just the line it guards; this
adds: read the STDERR above a passing guard, because a guard that passes is the
most effective place to hide an error message.**

**§3.5.4 — THE RULE TAKEN, applied to this team's own commits from here.**

1. **A heredoc writing document text uses a QUOTED delimiter** — `<<'MD'` — and
   a variable that must expand is spliced afterwards, never by unquoting the
   whole document.
2. **The private-index protocol gains a CONTENT assertion on the ADDED region**:
   a set of tokens the new text must contain is asserted present in the built
   blob **before** `commit-tree`, not merely that the old text is intact.
   **A verdict word is the first thing that set should carry**, because a
   missing verdict word is the one deletion that changes what a record says
   without changing whether it parses.
3. **A non-zero stderr line anywhere in a commit invocation aborts it**, even
   when every explicit assertion passes.

**Recommended to the chief for lab-wide adoption, NOT imposed** — the
private-index protocol is `CLAUDE.md` rule 10 and its wording is Sanaa's.

| §3.5 | figure |
| --- | --- |
| spans destroyed | **2** |
| distinct token lost | **1**, and it is a verdict word — `NOT MEASURED` |
| figures, verdicts or recommendations changed | **0** |
| guards in the protocol that ran | **4** |
| guards that passed | **4** |
| guards CAPABLE of catching it | **0** |
| minutes between commit and discovery | **~3** |
| lines whose number changed above this section | **0** |

## §4 — THE FILING GATE IS BLIND TO EXACTLY THE FILES IT EXISTS TO CATCH, THE INSTRUMENT ARGUES THE POINT AGAINST ITSELF IN ITS OWN VIOLATION TEXT, AND A FIGURE I PUBLISHED TODAY INHERITED THE BLINDNESS (2026-08-27)

**Appended, append-only. Nothing above is rewritten. Zero compute. Raised by
closure-supervisor, routed by the chief, verified here at source; no patch made —
`scripts/check_filing.py` is outside this team's folder scope and the diff read
belongs to its owner.**

**§4.1 — THE MEASUREMENT.**

`docs/papers/closure/.gitignore` is **tracked at HEAD** and contains `*.pdf` and
`*.txt`. Measured:

| quantity | figure |
| --- | --- |
| files in `docs/papers/closure/` **on disk** | **73** |
| files in `docs/papers/closure/` **at HEAD** | **2** |
| **PDFs on disk** | **35** |
| **PDFs at HEAD** | **0** |

`scripts/check_filing.py:100` enumerates via
`git ls-tree -r HEAD --name-only`. **So rules R8 (paper naming) and R9 (missing
`.txt` sidecar) evaluate ZERO of the 35 closure PDFs.**

**The silence is BLINDNESS, NOT A CLEAN BILL, and closure planted the control that
proves it:** the same run emits **12 R8 and 9 R9 findings elsewhere**, so the
reader is not inert — it simply cannot see that directory. **Two genuine R9
violations are concealed**, verified here: `Emory2013_structural_uncertainty_rans.pdf`
and `Iaccarino2017_eigenspace_perturbations.pdf` are both on disk, **neither has a
`.txt` sidecar, and neither is at HEAD** — so their contents are invisible to every
text sweep of this library, **which is the precise harm R9 exists to prevent.**

**§4.2 — THE INSTRUMENT MAKES THIS ARGUMENT ITSELF, AT ONE CALL SITE, AND THEN
DOES NOT MAKE IT AT THE OTHER. THAT IS `CLAUDE.md` RULE 14 VERBATIM.**

`_loose_root_files()` is documented *"Every FILE sitting directly at the
repository root, **read from the disk**. This **deliberately does NOT ask git**"*,
and gives the reason: *"git status is blind to ignored files by design."* **R1
even carries an `include_untracked` switch, so the disk-reading capability already
EXISTS inside the instrument.**

**And R1's violation text states the principle in the instrument's own words:**

> *"Being matched by `.gitignore` does NOT excuse it — **ignored means invisible
> to git, not filed**."*

**The script prints that sentence for R1 and then, two rules later, asks git for
the papers census.** `CLAUDE.md` rule 14: *a lesson is not applied until EVERY
call site asserts it.* **This is that rule with the instrument's own prose as the
evidence.** The lab's standing note *"gitignored is not filed — a cleanliness
check that asks git is blind to exactly the clutter it hunts; read the disk"*
**already existed and the gate still asks git.** **A documented lesson with a live
counter-example in the instrument that documents it is a dead lever, which is why
this section is in this audit.**

**§4.3 — THE SPEC THE CHIEF ASKED FOR, AND THE SPLIT RESOLVES MORE SIMPLY THAN IT
LOOKS.**

The proposed split is *disk for filing rules, HEAD for citation rules.* **Applied
to this instrument the split has nothing on one side of it.** Every rule it
carries — **R0** portable name, **R1** root clean, **R2** docs upper, **R3**
scripts lower, **R5** asset subdir, **R6** run tree, **R7** campaign record,
**R8** paper name, **R9** sidecar — asks **where a file sits, what it is called,
or whether its companion exists.** **Not one is a citation-resolution rule.**

> **THE TEST: a rule about WHERE A FILE SITS, WHAT IT IS NAMED, or WHETHER ITS
> COMPANION EXISTS is a DISK question. A rule about whether a RECORD RESOLVES —
> does this sha exist, does this cited path exist at the commit that cited it —
> is a HEAD question.** `check_filing.py` contains **ten of the first kind and
> none of the second**, so **it should enumerate DISK throughout**, and
> `_tracked()` should survive only for any rule later added of the second kind.

**THE FIX IS NOT "WALK THE DISK", AND SAYING SO IS THE POINT:** an unbounded walk
pulls in `.git/`, virtualenvs and run trees. **Each rule walks the DISK UNDER THE
ROOT IT GOVERNS**, with an exclusion list — and **R8/R9's root is exactly
`docs/papers/`, which is small, bounded and the entire subject of the defect.**

**THE PLANTED CONTROL, and both limbs are required (charter v1.13):**
**POSITIVE** — a PDF placed under a scratch papers directory **matched by a
`.gitignore`** and carrying **no `.txt` sidecar** must be **FOUND by the fixed
enumerator and MISSED by the current one**; a fix that does not demonstrate the
current instrument missing it has not been shown to change anything.
**NEGATIVE** — a correctly named, correctly sidecarred PDF must be flagged by
**neither**, so the fix is shown to discriminate rather than to flag everything it
can now see. **And a MUTATION limb**: removing the sidecar from the negative
control must **move** its verdict.

**§4.4 — ⚠ A FIGURE I PUBLISHED TODAY INHERITED THIS BLINDNESS, AND THE
DISTINCTION MATTERS.**

At `commit:aaf0bed6` this team recorded *"`scripts/check_filing.py` reads **FAIL,
34 violations across 7 rules**… 21 of the 34 are missing paper `.txt` sidecars"*,
offered as evidence of *a standing FAIL in the lab's own filing gate.* **The
reading reproduces at HEAD — still `FAIL: 34 filing violations across 7 rules`.**

**But 34 is a FLOOR, not a count.** It excludes **35 closure PDFs entirely**, at
least two of which are genuine R9 violations. **The true figure is `NOT
MEASURED`, and the direction of the error is known: upward.**

**This is the sixth coverage-as-census instance this team has published against
itself today — and it is the first one this team did not author.** The previous
five were defective scans of its own making. **This one was a number taken from
somebody else's instrument without asking what its census was** — which is `L-92`
(*`git ls-files` answers what is in the INDEX; only the repository answers what is
in the repository*) **applied to a script rather than to a command.** **Quoting an
instrument's output is inheriting its denominator, and the denominator is the part
that does not appear in the output.**

**§4.5 — NOT CLAIMED.**

**No patch is made and no diff is read as a supervisor check** — the instrument
belongs to another team's scope and `check_filing.py --selftest` is required on
any rule edit. **Closure reported 108 files on disk and 71 PDFs; I measure 73 and
35.** The discrepancy is **not resolved here** and I do not adopt either figure
over the other — closure's sweep may carry a wider frame — **but the finding is
identical under both, and the defect does not depend on which is right.** **How
many additional R8/R9 violations the fix would surface is `NOT MEASURED`;
naming two is a floor, not a count**, and this section refuses to repeat in its own
correction the error it is correcting.

| §4 | figure |
| --- | --- |
| closure PDFs on disk / at HEAD | **35 / 0** |
| R8+R9 rules evaluating them today | **0** |
| concealed R9 violations named | **2** (a floor) |
| control proving blindness, not cleanliness | **12 R8 + 9 R9 findings elsewhere in the same run** |
| enumeration call sites | **2** — one reads DISK and says why, one reads HEAD |
| rules wanting DISK / wanting HEAD | **10 / 0** |
| gate reading, unchanged and now known to be a floor | **FAIL, 34 across 7 rules** |
| coverage-as-census instances published by this team today | **6** — the first not of its own authorship |

## §5 — THE INERT-GUARD CLASS HAS TWO POLES, AND THE ansys FAMILY'S NEWEST SPECIMEN IS AT THE POLE THIS AUDIT WAS NOT WATCHING (2026-08-27)

**Appended, append-only; nothing above rewritten. Referred by the chief from
ansys-verification's own post-compute disclosure. Verified here by execution. Zero
compute. No verdict moves and nothing is repaired.**

### §5.1 THE SPECIMEN, CONFIRMED BY EXECUTION

`cases/ansys_verification/VMFLGPU007/grade_vmflgpu007.py:475` reads the
host-to-device count with

    re.search(r"CpuToGpu (?:Count|- CopyTo)\s*[:=]?\s*(\d+)", line)

**Driven here against real and fixture column shapes:**

| line | result |
| --- | --- |
| `CpuToGpu Count/Size: 12 4.096e+04` — **PETSc's real column** | **NO MATCH** |
| `CpuToGpu - CopyTo (Count/Size): 12 4.096e+04` — **also real** | **NO MATCH** |
| `CpuToGpu Count: 12` — fixture shape | MATCH |
| `CpuToGpu - CopyTo 12` — fixture shape | MATCH |

**`/Size` sits between `Count` and the digits, and the pattern allows only optional
whitespace, `:` or `=` there.** So `h2d` stays `None`, is returned as **0** at
`:480`, and `if g["h2d"] <= 0` at `:499` **is always true.** **Clause A4 refuses on
every possible run.**

### §5.2 ⚠ THE CORRECTION TO THE REFERRAL: THIS IS NOT A DECORATIVE GUARD. IT IS ITS MIRROR IMAGE, AND THE MIRROR IS WORSE

The referral filed A4 as *"a fourth decorative guard."* **The direction is opposite
and the distinction is the point of this audit.**

| pole | behaviour | failure mode |
| --- | --- | --- |
| **DEAD LEVER** (this audit's original subject) | **cannot FIRE** — passes everything | **false confidence**; produces **silence** |
| **STUCK GUARD** (A4) | **cannot PASS** — refuses everything | produces **a false FINDING** |

> **THE UNIFYING CLASS, and it is what belongs on the list: A GUARD WHOSE VERDICT IS
> INDEPENDENT OF THE DATA IT PURPORTS TO READ.** A dead lever and a stuck guard are
> the two signs of the same quantity. This audit has been enumerating one sign.

**AND THE STUCK POLE IS THE MORE DANGEROUS OF THE TWO HERE, for a reason specific to
this lab.** A dead lever emits nothing and a reader learns nothing. **A4 emits
prose:** *"the GPU arm reports ZERO host-to-device transfers. A solve that never
staged a buffer to the device did not use it."*

**That is a substantive physics claim about where the linear algebra ran, and it is
manufactured entirely by a regex that cannot match its input.** **A silence invites a
question; a confident false finding closes one.** `L-364` — the planted-zero doctrine
generalised from a zero to a verdict — reaches this exactly: **`h2d = 0` is a zero
from a reader never shown able to see a non-zero, and the refusal built on it is that
zero wearing a conclusion.**

### §5.3 NOT REPAIRING IS CORRECT, AND THE GROUND IS RULE 2 RATHER THAN CONVENIENCE

Gates close at first compute. The defect was found **post-compute**, and **`IG3`
refused first and independently on a plateau clause — a physics refusal that precedes
limbs A/B/C.** **So a repair could only ever produce a MORE FAVOURABLE verdict on a
case already refused**, which is precisely the move rule 2 exists to prevent. **The
team disclosed it, declined to repair it, and said why. That is the correct handling
and it is recorded as correct.**

### §5.4 THE FAMILY COUNT: THE REGISTER SAYS **THREE**, THE REFERRAL SAYS **FOUR**, AND THE DIFFERENCE IS NOT RECONCILED

The register's own dated note enumerates **three**: VMFLGPU007 Amendment 1 (the y+
reader, **caught by a smoke BEFORE compute**), VMFLGPU002 Amendment 5 (the limb-A
tell, *"frozen guaranteed to refuse"*), and A4. **The referral says fourth.**
**UNRECONCILED — recorded, not repeated, and neither figure adopted over the other**
(the same handling this team gave the 50-of-109 queue figure).

**But the register's own three carry a sub-structure worth naming: TWO OF THE THREE
ARE AT THE STUCK POLE.** VMFLGPU002's *"frozen guaranteed to refuse"* and A4 are the
same defect; only the y+ reader was caught before it could fire. **So the stuck pole
is not an isolated specimen in this family — it is the majority of it.**

**And the family's stated root cause is exact and generalises:** *"no smoke of this
family has ever produced a real PETSc `-log_view` table, so the reader was only ever
exercised on its absent-table path, never on its parse path."* **A SMOKE THAT CANNOT
PRODUCE THE ARTIFACT A READER PARSES DOES NOT TEST THAT READER** — the same finding
this audit recorded at §4 about a filing gate that cannot see the files it hunts, and
`COMMIT_INTEGRITY_STANDARD` G1 about controls whose scenario production never takes.
**Three instruments, three teams, one shape.**

### §5.5 VMFLGPU004 — THE REGISTER'S FIRST `BLOCKED` ROW, AND ITS CITATIONS ARE THE MODEL

**Audited as referred. The citations hold and the method is better than the finding.**

Six absences on manual **pp. 233–234**, and the decisive property is **how** they
were established: **each was read from the manual PDF PAGES THEMSELVES under rule 15,
never from the `.txt` sidecar** — on the stated ground that **an empty field in a
sidecar is equally consistent with a text-extraction failure**, so the sidecar could
not settle it.

**AND THE ABSENCE CLAIM CARRIES A POSITIVE CONTROL: VMFLGPU005, on the very next
page, prints its Betts & Bokhari citation normally** — proving the empty `Reference`
cell is **genuine and not an extraction artefact.**

> **That is standing rule 3 applied to a DOCUMENT: an absence claim from a reader
> shown able to see a presence, in the same source, at the same time.** It is `L-385`
> — *a null that cannot distinguish "does not exist" from "not readable here"* — met
> head-on rather than reasoned around. **Ratified, and named here as the model for
> any future absence claim from a primary source.**

**TWO FURTHER PROPERTIES OF THAT ROW, both correct:**

- **`BLOCKED` is the right word and the row says which kind.** *"RUNNABLE on this
  toolchain — not blocked on capability. It is blocked on EVIDENCE."* **Blocked-on-
  evidence and blocked-on-capability are different states and the register
  distinguishes them.** `NOT A RESULT` would have been wrong — nothing ran, and
  **zero compute was spent.**
- **It refuses to launder a new justification into an old claim.** An earlier
  infeasibility claim was ruled FALSE and the case reopened; the row **re-blocks on
  fresh evidence and expressly does not assert that this reasoning is the withdrawn
  claim's**, recording the old ground as **unestablished** rather than as vindicated.
  **That is the discipline this lab keeps failing at in the other direction, and it
  is worth citing when it is done right.**

**NOT CLAIMED:** this team **did not re-open the manual PDF** and did not
independently re-read pp. 233–234; the six absences are **ansys's readings,
audited for METHOD and internal consistency, and their method is what is
ratified here.** The `PASS` count is unaffected and **stays at 6.**

## §6 — THE GLOB SWEEP INVERTS ITS OWN PREMISE: the shape we went looking for is nearly ABSENT from committed code, and the defect that IS pervasive wears a different coat (2026-08-27)

**Appended, append-only; nothing above rewritten. Zero solver core-minutes;
read-only at HEAD. Two claims verified personally at source before boarding, and
one of the lane's framings did not survive.**

### §6.1 THE HEADLINE, AND IT IS NOT WHAT THE REFERRAL EXPECTED

**`grep <glob> | tail -1` for a `Time =` reading exists in EXACTLY ONE committed
instrument.** An independent targeted cross-check confirms it: every F-series runner
F15–F26 already reads **one named file**.

> **THE DEFECT heat-transfer AND cfd MEASURED LIVES IN INTERACTIVE HABIT, NOT IN THE
> COMMITTED INSTRUMENTS.** That is worth knowing precisely because it is the opposite
> of what a three-team alarm implied, **and it means the `MONITOR_STANDARD` clause is
> mostly PROPHYLACTIC rather than remedial.**

**What IS pervasive is the same defect wearing a different coat: A MULTI-MEMBER SET
REDUCED TO ONE MEMBER BY AN ORDERING THAT IS NOT THE ORDERING THE PHYSICS MEANS.**
Not a race — a **stable wrong answer**, which is the more dangerous pole
(§5, and `MONITOR_STANDARD`'s `--sort` trap).

| | count |
| --- | --- |
| files at HEAD | 16,756 |
| instrument files swept (ext ∪ shebang ∪ mode 755) | **1,590** |
| sites reviewed | **284** |
| **DANGEROUS** — value reaches a verdict or a completion decision | **18** (7 files) |
| DEGRADED — display, ETA, progress | 12 (6 files) |
| UNDECIDED | 4 (+3 cardinality questions) |
| SAFE, with a stated reason | 250 |

### §6.2 THE WORST FINDING: A READER DEFECT THAT WOULD PUBLISH AS A PHYSICS CLAIM — VERIFIED PERSONALLY

`so1c_chain_driver.sh:206` runs `grep -ah … "$SO1B_BASE"/MESH_*.log | head -4` — **the
one true ugrep multi-file read in the lab — and it is verdict-bearing.** It writes the
**reference side** of `G-MESHID`.

**Read at source:** `so1c_grade.py:925` is
`out["verdict"] = "PASS" if set(mine) == set(ref) else "GATE FAIL"`, and the GATE FAIL
reason string is **`MESH_REGENERATION_IS_NOT_DETERMINISTIC`**. The function's own
docstring says an inequality *"IS A MESH-REGENERATION-DETERMINISM finding."*

> **SO A DEFECT IN THE READER WOULD BE PUBLISHED AS A PHYSICS FINDING ABOUT MESH
> NON-DETERMINISM.** §5's stuck-guard class exactly: **a parser artefact wearing a
> conclusion.** And the prose is pre-written, so the false finding arrives
> *fluent*.

**AND BOTH SIDES OF THE COMPARISON ARE DEFECTIVE.** The `mine` side at
`so1c_grade.py:907-908` is `for cand in sorted(glob.glob(...)): mine_src = cand` —
**for-last-wins over a LEXICOGRAPHIC sort.** So the check compares a
**nondeterministically-selected reference** against a **lexicographically-last own
value**, and calls disagreement a property of the mesh generator. **For dafoam.**

### §6.3 A DETERMINISM VERDICT THAT CAN PASS WITHOUT TESTING ANYTHING

`scripts/verify_warm_replay.sh:305` and `:341` set **both** `before` and `after` from
`ls "$OUTDIR/$act"/transcript.* | head -1`. If the replay writes a **new** transcript
name, `head -1` returns the same old file twice, the diff is empty, and the verdict is
**a false `IDENTICAL`**. Multi-member is not speculation — `audit_transcripts.sh:128`
states `transcript.txt` and `transcript.md` can coexist, and `ls` sorts
lexicographically so `.md` wins deterministically. **For cfd.**

### §6.4 A DEFECT THE LAB ALREADY DIAGNOSED, WROTE DOWN VERBATIM, AND LEFT STANDING

`F3_runs/successor_triple_2026-08-26/instrument.py:145-152` names it exactly:
*"F3's runners use `sorted(glob.glob(...))[-1]` — a LEXICOGRAPHIC sort … `9.0` sorts
after `10.0` and the LATEST time is silently the WRONG one."* **It was re-authored
correctly THERE and the ORIGINALS ARE UNREPAIRED AT HEAD** —
`run_wedge_case.py:94,:131`, `run_cone_case.py:92,:121`, `DPW8_V2_runs/run_case.py:90`.

**Beside each sits a worse, UNFLAGGED twin:** `glob.glob(...)[0]` — **unsorted, index
0, no cardinality guard** — feeding `p_wall_mean` and `beta_computed_deg`. The
`or glob.glob("*p*.raw")` fallback **is itself an admission the set can hold
several.** **A diagnosis recorded in a successor and not propagated to its parents is
a dead lever with a paper trail. For cfd.**

### §6.5 ⚠ A CORRECTION TO THE SWEEP'S OWN FRAMING, MADE BY MY CHECK

The lane reported `VMFL021`/`VMFL022` as *"the two members that skipped the house
guard"*, the family pattern being `if len(...) != 1: refuse(...)`.

**Measured myself: `VMFL011` carries the SAME SHAPE** —
`sorted(glob.glob(.../postProcessing/resid/*/solverInfo.dat))` — and my guard-count
pattern returns **0** for it as it does for 021 and 022.

> **So "only two skipped it" is NOT SUPPORTED. At least THREE graders carry a
> `sorted(glob.glob(...))` over function-object start-time directories with only a
> not-empty guard.** Whether the rest of the family guards cardinality **in a form my
> pattern missed is `NOT MEASURED`** — and that is the coverage-as-census question
> again, so the candidate set is **wider than reported, not narrower.** **For
> ansys-verification to resolve on its own files.**

### §6.6 WHAT IS SAFE, AND THE MOST IMPORTANT ROW IS A NEGATIVE RESULT

- **`mark_done_*.py` (24 files) ARE SAFE BY CONSTRUCTION** —
  `sorted(float(x) for x in os.listdir(...))` sorts **numerically after float
  conversion**, fully overriding `listdir`'s arbitrary order. **`CLAUDE.md` rule 4's
  completion rule IS NOT EXPOSED.** **This independently confirms heat-transfer's own
  controlled audit by a different method, and it is the finding that most needed to
  be false and is not.**
- **`scripts/queue_runner.py` is CLEAN, and it was READ rather than inferred.** All
  four glob sites feed **full iteration**; the cap/overrun decision runs off a
  **named** status file plus epoch arithmetic, with no log read and no `Time =` in
  1,455 lines.
- **The ansys VM graders are the lab's REFERENCE IMPLEMENTATION** — cardinality-1
  refuse, and VMFL076 takes its last time from `re.findall` over **one** file's text
  in **document order**. **The correct pattern is already written down inside this
  lab.**

### §6.7 PRIOR ART THE REMEDY MUST FOLLOW

`sdk/scripts/replay_monitor_rules.py:94-106` already fixed this class and recorded the
doctrine: *"**The fix is not a wider glob.** A list of patterns is the same defect
with more entries (`L-49`)."* Its repair derives the corpus **from content** — an
`Exec :` banner — not from a filename pattern. **Same principle as the `-J1`
refutation: ordering a bad set is not a fix, because the SET is the defect.**

### §6.8 WHAT THE SWEEP COULD NOT DO, STATED PLAINLY

- **21 sites were read in full; the other 250 were classified by STRUCTURAL FAMILY
  MEMBERSHIP**, verified against one exemplar per family. **That is the honest
  residual and it is not small.**
- **The sweep MISSED `so1c_grade.py:907`** — the `mine` side of §6.2's own headline
  finding — **and it was found by reading, not by a hit.** The six `[0]`-index twins
  in §6.4 likewise.
- **The detector FAILED THREE OF FOUR PLANT LIMBS before repair**, including one
  false positive on a safe named-file read. **It was fixed only because the plant
  existed.** After repair all three positive limbs fired and the safe limb stayed
  silent. **This is the clearest case this lab has yet produced for `L-363`: the
  plant was not decoration, it was the only thing that found the reader broken.**
- Three cardinality questions **modulate severity but not existence** — each settled
  by one `ls | wc -l` on a live run root, **not enumerated here** (zero-compute).

---

## §7 — THE THREE CARDINALITY QUESTIONS §6.8 LEFT OPEN ARE NOW ENUMERATED; ansys's SWEEP IS RATIFIED BY AN INDEPENDENT INSTRUMENT THAT AGREES TO THE UNIT; AND MY OWN §6.5 CORRECTION OF THEM WAS WRONG (2026-08-28)

**Zero compute.** Instrument: `verification/credibility/ordering_key_census.py`, written for
this section, structural (AST) rather than textual, with a four-limb planted control driven
before any number below was believed.

### §7.1 THE HEADLINE: TWO INDEPENDENT INSTRUMENTS, DIFFERENT METHODS, THE SAME 19 IN THE SAME 9

`c7176346` (ansys) reported **19 hazard sites in 9 files** by regex. This section's instrument
walks the **AST**, resolves **name bindings** (`f = sorted(glob.glob(pat)); ... f[-1]`),
resolves **name-bound glob patterns** (`pat` defined on the previous line), attributes every
`len(x) != 1` guard **to the set it actually measures**, and discards wildcard-free globs whose
cardinality is 1 by construction. It returns **19 distinct binding sites across 9 grader
files** — `VMFL002`, `VMFL004`, `VMFL004-R2`, `VMFL011`, `VMFL011-R2`, `VMFL011-R3`,
`VMFL021`, `VMFL021-R2`, `VMFL022` — **the same count and the same file set**, reached by a
method with no step in common with theirs. (50 subscript *uses* resolve to those 19 *bindings*;
the binding is the right unit, because one bad read serves many lines.)

**ansys's sweep is RATIFIED.** Agreement between two instruments that fail in different ways is
worth more than either number alone.

### §7.2 ⚠ AND §6.5's CORRECTION OF THEM WAS WRONG, IN THE DIRECTION THAT FLATTERED THIS TEAM

§6.5 said the candidate set was **wider** than ansys reported — *"at least THREE, not only
two"*. That was right about `VMFL011` and it was **right for the wrong reason**: it rested on a
grep whose guard-count returned 0. Run today, the same textual approach returns **13 files**,
four of which — `VMFL010`, `VMFL017`, `VMFL017/R2`, `VMFL059` — are **benign on reading**:
`glob.glob(os.path.join(level_dir, "log.simpleFoam"))[0]` has **no wildcard**, so the set it
indexes has at most one member and the read is exact. **The excess was my instrument's, not the
lab's.** ansys's count was correct and this team's widening of it was noise dressed as rigour.

The previous correction ran against ansys and this one runs for them. **A team that only ever
corrects other teams downward is not auditing, it is scoring.**

### §7.3 THE LOAD-BEARING CLAIM — "ZERO LANDED VERDICTS EXPOSED" — IS CONFIRMED, WITH A LIVE POSITIVE CONTROL, AND THE CONTROL FIRES WIDER THAN ANSYS REPORTED

Every function-object directory under every level of the **eight hazard cases that ran** was
counted on disk: `VMFL002`, `VMFL004`, `VMFL004-R2`, `VMFL011`, `VMFL011-R2`, `VMFL011-R3`,
`VMFL021`, `VMFL022`. **Zero directories hold more than one start-time subdirectory.** The
lexicographic bug therefore **cannot fire on any landed verdict**. `VMFL021-R2` never ran.

**That zero is evidence and not an absence, because the same scan was driven on ground that
holds a non-zero** — and it found **six** multi-member sites, not the one ansys named:

| site | start-time dirs | lexicographic `[-1]` | numeric `[-1]` |
|---|---|---|---|
| `VMFL076-R2/L1/postProcessing/sampleLine` | 40 | `950` | `2000` |
| `VMFL076-R2/L2` | 40 | `950` | `2000` |
| `VMFL076-R2/L3` | 40 | `950` | `2000` |
| `VMFL076/L1` | 40 | `950` | `2000` |
| `VMFL076/L2` | 60 | `950` | `3000` |
| **`VMFL076/L3`** | **100** | **`950`** | **`5000`** |

ansys named `VMFL076-R2/L1` only, at a ratio of 2.1×. **`VMFL076/L3` is 5.26× and was not
named.** The hazard is **LATENT and armed by the first restart**, exactly as ansys ruled — and
the ground that would arm it is already sitting in the neighbouring case at a hundred
directories.

### §7.4 ⚠ THE ONE CORRECTION THAT MATTERS: ansys UNDERSTATED ITS OWN REFERENCE IMPLEMENTATION, AND MIS-ATTRIBUTED THE GUARD THAT SAVES IT

`c7176346` states that the `VMFL076-R2` grader *"is one of the 12 cardinality-guarded ones so
it REFUSES instead of misreading"*. **Read at source, that is wrong on the mechanism, and the
truth is better.** `grade_vmfl076.py:669-685` does not refuse on 40 directories. It

- iterates **all** of them with `os.listdir(root)`,
- converts each name with **`float(name)`** — a numeric key,
- accumulates `(t, path)` pairs and calls **`out.sort()`**, sorting **numerically**,
- and returns the **whole list**.

**It reads the hard input correctly.** The `len(hits) != 1` refusal at `:678` is a guard on the
inner `gateLine*T*.xy` **file** set inside each time directory — **a different set entirely**
from the start-time directories that carry the hazard. `G3` refuses only on **zero** time
directories.

**The distinction is load-bearing in both directions.**

- **For ansys:** a grader that *refuses* on the hard input is a **guard** — it stops. A grader
  that *reads it right* is a **reference** — it proceeds, correctly. Ansys claimed the weaker of
  the two about its own code.
- **Against the sweep's method:** if the "12 cardinality-guarded SAFE" sites were classified by
  the presence of a `len(...) != 1` refuse, then **the classifier may be crediting a guard over
  one set with the safety of another.** A site can carry a prominent cardinality guard on an
  inner glob and still be **unguarded on the outer set that decides the answer**. **Whether the
  other 11 are safe for the reason claimed is `NOT MEASURED`** — the count is not disturbed,
  the *reason* is.

**AND THE REPAIR SHAPE IS NOW NAMED, FROM TWO INDEPENDENT ARRIVALS.** `float(name)` + numeric
sort is exactly the shape §6.6 found in the **24 `mark_done_*.py`**
(`sorted(float(x) for x in os.listdir(...))`) — the instruments that carry `CLAUDE.md` rule 4.
Two families, no contact, same answer. **That is the lab's reference ordering key**, and any
repair under §6.7 adopts it rather than inventing a third. Repair remains barred in **frozen**
comparators post-compute (rule 2) and belongs in successors and unfrozen graders, as ansys
ruled.

### §7.5 THE LAB-WIDE FIGURE, AND WHAT IT IS NOT

Across `cases/`, `verification/`, `scripts/`, `models/` and `harness/`: **77 unguarded
ordering-key sites in 28 files** — **50 ansys**, **15 `verification/runs/`**, **12
`cases/dafoam/`**. **This is a CANDIDATE list, not a hazard count.** Every site still needs the
two readings the instrument cannot do: whether the ordered set is ever multi-member in practice,
and whether the chosen member is the one the physics means. §7.3 is what that reading looks like
when it is done.

### §7.6 THE INSTRUMENT FAILED FIVE LIMBS BEFORE IT WORKED, AND ONE FAILURE WAS THE DANGEROUS KIND

Recorded because the failures are the finding, and because **four of the five share one root
cause**.

| # | pass | what it did | direction |
|---|---|---|---|
| 1 | ansys's first two regexes | returned 0 on files proven to carry the shape | false zero |
| 2 | this team's grep census | returned 0 on `VMFL021`/`VMFL022` — same files | false zero |
| 3 | first AST pass | matched only `sorted(...)[i]`; real code binds first, then indexes | false zero |
| 4 | guard/type filter | called `sorted(set_of_floats)[-1]` a lexical hazard | false positive |
| 5 | **wildcard test** | **read only the glob call, missed `pat` bound one line above — declared 7 CONFIRMED hazard files BENIGN** | **false NEGATIVE** |

**Limbs 1, 2, 3 and 5 are one defect wearing four coats: a reader of code that assumes the
interesting expression is syntactically local.** It is the same shape as the finding under
audit — *a set reduced by an ordering that is not the one meant* — turned on the auditor.
**Pass 5 is the one to be frightened of.** Limbs 1–3 failed **loudly**, returning zero against
ground truth a human already held. Pass 5 failed **quietly and plausibly**: it took a set of 13
files that had already been measured, and **silently deleted 7 confirmed positives**, leaving a
smaller, cleaner, entirely wrong number that no downstream reader could have questioned. **A
false zero on known ground truth announces itself. A false shrink of an already-measured set
looks like the audit converging.**

It was caught only because a **prior measurement existed to contradict it** — `VMFL021` had been
read by hand at `:120-134` before the filter was written. **Not by the control:** all four
control limbs passed at the moment pass 5 was wrong, because none of them was a hazard site whose
pattern was bound on a previous line. **The control was correct and insufficient.** The missing
limb — a hazard whose glob pattern is **bound on the previous line** — was added afterwards as
limb **E** of the committed six-limb `--selftest`, so that the next reader inherits the trap
rather than rediscovering it. All six limbs are driven and pass: **A** bind-then-index,
**B** direct subscript, **C** wildcard-free literal (silent), **D** cardinality guard on the
same set (silent), **E** pattern bound on the previous line, **F** the `float(name)` + numeric
sort repair shape (silent). **Limbs C, D and F are the discriminating half** — an instrument
that fired on all six would be a hazard counter that counts everything.

---

## §8 — THE GPU-EXCLUSIVITY CLAUSE IS A DEAD LEVER ON **100 %** OF THE QUEUE POPULATION, AND THE REASON NOTHING IS RUNNING IS THAT **QUEUE-READY DEPTH IS ZERO FOR ALL FIVE TEAMS** (2026-08-28T16:10Z)

**Zero compute. Measured on the live box, every enumerator named. Cross-team, under this
team's audit mandate.**

### §8.1 THE DEAD LEVER

`docs/standards/RUNNER_GPU_CLAUSE.md` is a frozen behaviour spec written before its code, and
`scripts/queue_runner.py:307-341` implements it carefully — `HOLD` on `GPU-BUSY`, a distinct
`GPU-PROBE-FAILED` because *"a zero from a reader not shown able to see a non-zero"* is standing
rule 3, an `INERT` verdict logged on a no-device host *"because a clause that is quiet when
absent is indistinguishable from a clause that is quiet when passing"*, and an L-314 planted
proof with mutants. **It is among the better-built guards in this repository.**

Its trigger, `:320`:

```python
    if str(entry.get("gpu", "")).strip().lower() != GPU_EXCLUSIVE:
        return "PASS", "entry declares no `gpu: exclusive`; the clause does not apply to it"
```

**Measured across every `*.json` in `verification/queue/`: the key `"gpu"` appears in ZERO
entries.** The clause therefore returns `PASS` on **every entry that exists**, and has never
returned anything else.

**And the two entries it most exists for are the two that do not set it.**
`ansys-verification/held/VMFLGPU001.json` and `VMFLGPU001-R2.json` are the lab's only queued GPU
cases — both carry `cap_gpu_h: 2.0` and `host: ip-172-31-44-162`, the GPU instance — **and
neither declares `gpu: exclusive`.** A clause built to stop two GPU cases colliding is inert on
the only two GPU cases in the queue.

**This is §5's class exactly, and it is the harder pole to see: not a guard that cannot fire,
but a guard whose TRIGGER FIELD nothing writes.** The code is correct, the spec is correct, the
planted proof passes — the mutants flip their controls because `--selftest` **injects** entries
that set the field. **A selftest that supplies its own trigger tests the clause and not the
population.** Same root as §5.4's finding that no smoke ever produced a real PETSc `-log_view`
table: **an instrument exercised only on inputs its author constructed has not met the inputs
the lab actually files.**

**Remedy is not in this clause.** It is in `QUEUE_ENTRY_STANDARD` / `queue_entry_check.py`:
**an entry carrying `cap_gpu_h` or naming a GPU host must be required to declare `gpu`**, so the
field cannot be omitted by an author who does not know it exists. Referred to `cfd` (validator)
and `ansys-verification` (the two entries).

### §8.2 ⚠ AND THE OPERATIONAL FACT UNDERNEATH IT, WHICH IS LARGER: THE QUEUE IS EMPTY

`list_entries()` at `:434-442` globs **`root/<team>/*.json`** — `d.glob`, **not** `rglob`. Only
the team directory's **top level** is queue-ready. Subdirectories are not scanned.

| team | queue-ready (`<team>/*.json`) | parked (`held/`) | `launched/` |
|---|---|---|---|
| ansys-verification | **0** | 2 | 5 |
| cfd | **0** | 0 | 15 |
| closure | **0** | 0 | 4 |
| dafoam | **0** | 7 | 31 |
| heat-transfer | **0** | 0 | 57 |

**Queue-ready depth is ZERO for every team.** Sanaa's standing directive §2 —
**"FREEZE-AHEAD ≥ 3: every team keeps at least three frozen, queue-ready registrations at all
times. A starved queue is a planning defect."** — is violated by **all five teams, at zero**.

**`held/` is not a queue and must not be counted as one.** `VMFLGPU001.json`'s own
`_held_reason` says so — *"HELD, NOT DROPPED. `verification/queue/ansys-verification/held/` is
outside `scripts/queue_runner.py`"* — **and I checked the claim rather than accepting it**,
because it is a claim by the party it benefits: `glob` does not descend, so the entry's text is
**correct**. `SKIP_DIRS = ("launched", "refused")` at `:113` does not name `held` and reads as
though it might be scanned; it is vestigial to this function, which never walks.

**⚠ THE COUNTING TRAP, AND I FELL INTO IT FIRST.** My first reading of freeze-ahead counted
`held/` and reported **dafoam 7 — OK, four teams below 3**. That is wrong in the direction that
excuses: it credits a team with seven ready registrations for seven that the runner cannot see.
**The correct figure is 0 for dafoam too, and 0 for everyone.** A directory that looks like a
queue, is named like a queue, and is not scanned is worse than an empty one, because it makes a
starved queue read as a stocked one.

### §8.3 WHAT THIS EXPLAINS, AND WHAT IT DOES NOT

**Explains:** the runner (pid **1120800**, alive **22.6 h**) is healthy and has had **nothing to
launch**. The GPU instance has been **idle 12.81 h** since `03:20:39Z` — **$10.31 derived** at
the pre-registration's placeholder `$0.8048/GPU-h` (`DERIVED, NOT MEASURED`; the box cannot read
its billing, `COMPUTE_BUDGET_CHARTER` §5, and the console figure is still owed). Under Sanaa's
§2 that is an **auto-boarded defect**. The CPU box carries only two solvers, both launched long
before the queue drained (`T3_R_ff` pid 411911, 8 ranks, **43.3 h**; `T16_MC_f` pid 1716924,
**13.8 h**).

**Does NOT explain, and is not offered as an excuse:** the fleet was killed at ~`23:15Z` by the
account's weekly usage limit, so no supervisor has been awake to refill a queue. **The empty
queue is a consequence of that, not an independent planning failure by any team** — and it is
boarded anyway, because *"a starved queue is a planning defect"* is a state, not a verdict on
who is at fault, and the state is what the next supervisor awake needs to see first.

**The one thing every team should read from this section:** on waking, **file queue-ready
entries at `verification/queue/<team>/`, not into `held/`** — and the two GPU cases need
`gpu: exclusive` added before either is made ready, or §8.1's lever stays dead on exactly the
run it was built for.

---

## §9 — THE 27 NON-ansys CANDIDATE SITES ARE READ AND RULED; A **NEW DEFECT CLASS** IS FOUND THAT IS NOT ABOUT ORDERING AT ALL; AND §7.5's PUBLISHED FIGURE IS CORRECTED UPWARD BECAUSE MY INSTRUMENT WAS BLIND TO A SHAPE (2026-08-28T16:40Z)

**Zero compute. Lane reading, supervisor verification of both big claims at source
(`SUPERVISION_CHARTER` §3 check 3 — verified before belief, not after relay).**

### §9.1 THE RULING ON THE 27

**LIVE 0 · LATENT 9 · BENIGN 17 · DISPLAY-ONLY 1.**

**The zero-LIVE result is the absence of an INTERSECTION, not the absence of a hazard.** Across
**5,039** function-object directories lab-wide, **774 are multi-member** and **492** have
`sorted(kids)[-1] != sorted(kids, key=float)[-1]` — the disk is thoroughly armed
(`verification/runs/ansys_verification/VMFLGPU003/gpu/L3_80x160/postProcessing/bisector`, 3,500
dirs, lexicographic `'999'` against numeric `'3500'`). **Restricted to the seven FO names the
27 sites actually read**, 664 directories yield 90 multi-member and **exactly 2** divergent —
both `postProcessing/forceCoeffs1` at n=3, `lex='5000'` vs `num='10000'`
(`verification/runs/W1_runs/medium`, `/home/ubuntu/certonomous-runs/w1-bump-nasa-grids/medium`)
— and **neither is reachable from any of the 27.** The same reader over all FO names in the
same pass returned 492, **so the 2 is a measurement and not a blind scan.**

**The 12 `cases/dafoam/` sites are BENIGN for a reason that is not the obvious one.** They are
**not** cardinality-1 by construction — a re-run of an arm adds a second log. They are benign
because **the ordering key IS the ordering the physics means**: the launchers
(`so1c_run_arm.sh:472-475`, `d8r_run_arm.sh:295-298`) write `${ARM}_${STAMP}.log` with a
**fixed-width zero-padded ISO-8601 UTC stamp** after an identical prefix, so lexicographic order
**is** chronological order. **That is limb F's repair shape reached by naming convention instead
of a numeric key** — a third independent arrival at the same answer, after the 24
`mark_done_*.py` and `grade_vmfl076.py`.

**Its one residual, demonstrated rather than assumed:** on a same-second tie the sort falls
through to a **variable-width pid tail**, and `…T010000Z_100.log` sorts **before**
`…T010000Z_99.log`. Reaching it needs two launches of one arm inside one second, which the
serial chain drivers make unreachable — **but that is a reading, `NOT MEASURED`.** Severity if
it fired is not cosmetic: the chosen log's missing `TERMINAL[arm]` produces `refuse("G1")`, a
**rule-4 completion decision.**

**The 9 LATENT are all `verification/runs/` F3/F4/DPW8/F3S sites** whose FO dirs are
single-member today and whose values reach `grade_f3.py` / `grade_f3s.py` verdicts
(`beta_computed_deg`, `p_wall_mean`, `cd_computed`). **The F3S multi-member dirs (156–406) are
non-divergent for a FRAGILE reason worth recording: every time falls in 0.002–3.12 s and
4.5–6.0 s, so no `9.x` ever stands against a `10.x`. That is the VALUE RANGE, not the code** —
a longer run arms them.

### §9.2 ⚠⚠ THE SHARPEST DEFECT IN SCOPE IS **NOT ABOUT ORDERING**, AND IT SITS IN A **FROZEN** GRADER — VERIFIED PERSONALLY

`verification/runs/F3_runs/successor_triple_2026-08-26/grade_f3s.py:239`, read at source:

```python
    cands = sorted(f for f in os.listdir(d) if f.endswith(".raw") and "p" in f)
    ...
    path = os.path.join(d, cands[0])
```

with the same selector twice in its driver — `run_f3s.py:255` and `:287`,
`sorted(glob.glob(os.path.join(surfd, "*p*.raw")))[0]`.

**The `[0]` is a red herring. The defect is that the SELECTOR is not unique, and the code
assumes it is.** OpenFOAM's `surfaces` writer emits **one file per field**, so a time directory
genuinely holds `p_coneSurface.raw`, `rho_coneSurface.raw`, `T_coneSurface.raw`. **`"p" in f`
matches exactly one of those ONLY because no surface name and no other sampled field name
happens to contain the letter `p`.**

**Driven, not argued** — the ASCII ordering decides which wrong file wins:

| surface name | files matching `"p" in f` | `sorted(...)[0]` | |
|---|---|---|---|
| `coneSurface` | 1 | `p_coneSurface.raw` | correct |
| `wedgeSurface` | 1 | `p_wedgeSurface.raw` | correct |
| **`rampSurface`** | **3** | **`T_rampSurface.raw`** | **⚠ TEMPERATURE** |
| **`upperSurface`** | **3** | **`T_upperSurface.raw`** | **⚠ TEMPERATURE** |

`'T'` is 84 and `'p'` is 112, so **`T_` sorts first and wins.** Rename the surface to anything
carrying a `p` — `rampSurface`, `upperSurface` — or add `p_rgh` or `Cp` to `fields`, and
**a temperature field is read into `p_wall_mean` and graded against a pressure band.** It is
dimensionally silent and numerically plausible: nothing in the record would look wrong.

**AND THE PREMISE THE SELECTOR RESTS ON IS ALREADY FALSE ELSEWHERE ON THIS DISK.** Enumerating
every `.raw` basename under `F3_runs` and `/home/ubuntu/certonomous-runs`:
**`wallShearStress_plate.raw`** and `wallShearStress_bottomWallDownstream.raw` are non-pressure
names **containing `p`**. The uniqueness is therefore **not a property of the lab's naming
convention** — it is a property of **which fields that one `surfaceSampleDict` happens to
write**, which is exactly the kind of premise nobody re-checks when editing a dict.

**CLASS, and it is new to this audit: A SELECTOR ADMITTING MORE THAN ONE MEMBER WHERE THE CODE
ASSUMES EXACTLY ONE — DISAMBIGUATED BY LUCK OF NAMING RATHER THAN BY A GUARD.** Its relatives
here (`§6`, `§7`) are about **which member of a set is chosen**; this one is about **the set
having members it was never meant to contain.** The cure is the cure §7.4 already named for a
different reason: **a cardinality guard on the set that decides the answer** —
`len(cands) != 1 → refuse` — which `grade_vmfl076.py:678` already does for its inner file set
and which this grader does not.

**NOT REPAIRED, and the ground is rule 2.** `grade_f3s.py` is a **frozen comparator** and F3S
has computed. A post-compute edit is barred. **Disclosed, declined, reasoned** — as with §5.3.
Repair belongs in a successor; the driver `run_f3s.py` is the unfrozen half and is `cfd`'s.

### §9.3 ⚠ §7.5's FIGURE IS CORRECTED UPWARD: THE INSTRUMENT WAS BLIND TO A SHAPE, AND IT WAS **THIS TEAM'S OWN HEADLINE FINDING**

§7.5 published **77 candidate sites in 28 files**. **That was an understatement**, and the
omission was found **by a lane reading code, not by the instrument.**

`so1c_grade.py:907-909` is

```python
    for cand in sorted(glob.glob(os.path.join(root, "MESH_*.log"))):
        mine_src = cand
```

— a **LAST-WINS selection with no subscript anywhere.** Ordering decides the answer exactly as
`[-1]` does, and **nothing is indexed**, so a subscript-based detector is *structurally* blind.
**Confirmed by running the census against that file: not flagged.**

**The sting is that this is the `mine` side of `G-MESHID`, this team's own headline dafoam
finding, recorded at §6.2 and on the board since 2026-08-27.** §6.11 already noted the earlier
sweep *"MISSED `so1c_grade.py:907` — the `mine` side of its own headline finding — found by
reading". **The successor instrument reproduced the same blind spot from a different direction,
and again a human reading found it.** Twice is a pattern: **the shapes this lab's detectors miss
are the ones its readers keep finding, which is an argument for reading, not for a third
detector.**

**Corrected.** `visit_For` now detects assign-in-loop-over-sorted, and the shape is **limb G of
a committed seven-limb `--selftest`** (all seven pass; **C, D and F must stay silent**).

**Recounted lab-wide: 78 sites in 28 files** — 50 ansys, 15 `verification/runs/`, **13**
`cases/dafoam/` (was 12).

**AND THE HONEST SIZE OF IT, STATED SO THE CORRECTION IS NOT OVERSOLD: closing the blind spot
added exactly ONE site.** The gap was **real and qualitatively serious** — the census's 77 was
**not a superset of the lab's known ordering-key defects**, which is a disqualifying property
for a census — and it was **quantitatively worth one row**, on a defect already known by other
means. **Both facts are the finding.** A correction that reported only the first would inflate
it; one that reported only the second would excuse it.

### §9.4 RELAYED, NOT RULED — `cases/dafoam/` IS NOT THIS TEAM'S TERRITORY

**`SO1a`'s run root now EXISTS** — 5 arm logs stamped 2026-08-28T02:17–02:28Z at
`/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient`. The dafoam record
at `3fa8cc22` states *"no SO1a, SO1b or SO1c run root exists and zero such containers have ever
existed"*, verified at 23:1xZ. **That was true when written; SO1a has since run.** SO1b and
SO1c roots remain absent, so **the rule-2 condition as it applies to those two still holds.**
Relayed to `dafoam` as a fact whose consequences are theirs.

### §9.5 `NOT MEASURED`

- Whether two launches of one dafoam arm can land inside one second (the pid tie-break's arming
  condition). Read and judged unreachable; **the case was not constructed.**
- Whether `DPW8_V2_runs` L4 is gated anywhere but `analyse_l4_diag.py`, whose `:465` reads
  *"NOT gate verdicts. L4 remains NOT GATED."* Its two sites are classed **LATENT on the
  verdict-shaped path — the conservative call.** If L4 is permanently ungated they fall to
  DISPLAY-ONLY and **LATENT drops from 9 to 7.**
- Whether the 11 remaining ansys "SAFE" sites are safe **for the reason claimed** — open since
  `3c751f8a` §7.4, unchanged.
- The lane records **a false zero of its own**: an inner-set scan used `**` globs without
  `recursive=True` and returned *"0 dirs scanned"* for F4 and all four F3S sites. **A reader
  defect, not a finding** — re-measured with explicit paths (126 and 1,173 dirs) and a positive
  control on the same code path before any `1` was trusted. **Recorded because a lane that
  reports its own dead reader is doing the thing this audit exists to make normal.**

---

## §10 — THE WEDGE-ANGLE SWEEP: **ONE EXPOSED SITE LAB-WIDE, AND IT HAS ALREADY FIRED.** The predicate is ruled, the N-convention turns out not to matter for any case that has been built, and my own first matcher missed a site (2026-08-28T18:40Z)

**Predicate supplied by cfd-supervisor, who separated first-hand measurement from relay
unprompted and told me which was which. Swept and ruled by verification-supervisor. Zero
compute, read-only.**

### §10.1 THE MATCHER, VALIDATED BEFORE IT WAS BELIEVED (§2j, canonized four hours earlier)

The control is a **real `checkMesh` log written by the real producer** — not a fixture:
`verification/runs/F23_HP_WEDGE_runs/{coarse,medium,fine}/log.checkMesh`, lines 92–93.

| level | printed angle | Δa (deg) | **M = Δa / TOL** | class | cfd's anchor |
|---|---|---|---|---|---|
| coarse | `0.0400002766821` | 2.766821e-07 | **0.2767** | LATENT | 0.277 |
| medium | `0.0400007984975` | 7.984975e-07 | **0.7985** | LATENT | 0.799 |
| **fine** | `0.0400027202903` | 2.720290e-06 | **2.7203** | **ARMED** | 2.72 |

**Reproduced independently to four figures**, and the fine log carries **`Mesh OK.`** — the guard
refuses a mesh OpenFOAM's own checker passes, which is the finding itself.

**`TOL = 1e-6` was BACK-SOLVED from cfd's three anchors before I looked for it, then found at
source** — `cases/F23_HP_WEDGE/build_f23.py:129`. An independently derived constant landing on the
literal in the code is a stronger check than reading the literal first.

**Negative limb driven:** a real `checkMesh` log with no wedge
(`certonomous-runs/A3-onera-m6-adjoint-probe80k/log.checkMesh`) parses **zero angles** and is
reported **not-applicable, never "clear"** — cfd's clear-condition 2 makes those two
indistinguishable unless they are separated by construction.

### §10.2 ⚠ THE N-CONVENTION QUESTION DOES NOT REACH ANY BUILT CASE, AND cfd's HOLD IS THEREFORE UNNECESSARY — a narrowing in their favour

cfd held the one-patch-vs-both-patches question open (Part 2, relay, unverified; a factor of 2 on
every margin) and advised noting which verdicts would flip. **None would.**

**Δa is MEASURED as `printed − nominal`, straight from the log. `N` appears nowhere in it.** The
closed form `1.527e-15·N/sin(a)` is a **predictive screen for meshes not yet built**; every case
in the population has a `checkMesh` log, so **every margin in this sweep is measured, not
predicted, and no verdict here depends on the unresolved convention.** Additionally `checkMesh`
prints **per patch** — `wedge1` and `wedge2` carry identical values — so the reading is per-patch
by construction.

**The factor-of-2 exposure survives only for forecasting an unbuilt level**, where cfd's own
caveat already dominates: measured occupancy **falls** with N (0.1158 / 0.0836 / 0.0712), so
`Δa ∝ N` is an **upper bound, not a fit**, and the screen over-estimates at large N.

### §10.3 THE SWEEP: **1 EXPOSED, AND MY FIRST MATCHER FOUND IT ALONE BECAUSE IT WAS TOO NARROW**

**Population:** 1,084 `checkMesh` logs; **206 carry a printed wedge angle**, across 7 campaigns
(T-family 114, ansys 55+17, F9 7, F3 7, F23 3, supersonic-cone 3).

**EXPOSED — 1 site, and it is REALISED rather than latent:**

`cases/F23_HP_WEDGE/build_f23.py:129`
```python
        if abs(float(ang) - EX.HALF_ANGLE_DEG) > 1e-6:
```
A **literal constant**, N-independent, applied to the **checkMesh-printed** angle. It **has already
fired**, refusing F23's fine level (`F23_HP_WEDGE_RESULTS.md:72`). Per cfd's point B, a *relative*
tolerance would be exposed identically — the floor grows with N while the reference (the half
angle) is constant — and reads as though someone had thought about scaling. **No relative-form
site exists in this lab; the count is reported separately as required and it is zero.**

**⚠ AND I RECORD THAT MY FIRST CODE MATCHER WAS TOO NARROW.** Keyed on `Wedge .* with angle`, it
returned **exactly one file**. Broadening to any wedge-angle-versus-nominal comparison surfaced
**nine** candidates including **`T17_runs/analyse_t17.py:344`**, whose refusal string —
*"level %s wedge angle %s is not the registered %g"* — is the **same shape as F23's**. **A sweep
returning 1 on its own positive control is not thereby correct; it is unfalsified.** The narrow
pattern would have reported the true answer for the wrong reason.

**CLEARED, each with the condition it meets, by reading rather than by pattern:**

| site | why clear |
|---|---|
| **`T17_runs/analyse_t17.py:344`** | **condition 2** — `m["wedge_deg"]` is a `%.17g` round-trip of the **registered** value (written at `:459`) compared against the registration. **Register vs register; no mesh roundoff enters.** Its `1e-15` looks like the worst exposure in the lab and is **correct**, because it guards a float round-trip, not a measurement. **The most misleading row in the sweep.** |
| `VMFL036/grade_vmfl036.py:421` | **condition 3** — computes its own angle from mesh points (`tan_meas = maxz/maxy`), never parses a printed one |
| `VMFL033/make_blockmeshdict.py`, `T15_runs/build_t15.py`, `T8_runs/build_t8.py`, `F3_runs/make_wedge_case.py` | **condition 2** — builders: they **write** the angle and never read it back |
| `VMFL007/grade_vmfl007.py:746`, `grade_f3s.py:139` | **different quantity** — a reported wedge *bias* and a *shock* angle `beta_deg`, neither the wedge patch angle |

### §10.4 RULING ON cfd's Q2: **"FINEST BUILT LEVEL" MEANS BUILT-AT-ALL, INCLUDING A REFUSED BUILD.** cfd is upheld, on a stronger ground than they offered

cfd argued that "built-and-passing" would classify F23 — the case that generated the finding — as
LATENT at M = 0.799, and *"a predicate that cannot classify its own founding case is not a
predicate."* **Upheld. The stronger ground is circularity.**

**The guard runs AFTER the mesh is built.** `checkMesh` executed, printed
`0.0400027202903`, and printed **`Mesh OK.`**; `build_f23.py:129` then refused. **The mesh exists
and the build succeeded — the GUARD refused.** To read "built" as "built-and-passing" is to
**filter the predicate's input set by the very guard whose exposure the predicate measures**: the
guard's refusals would remove exactly the cases that prove it over-tight, and the predicate could
never return ARMED for any guard that actually fires.

**That is `L-402`'s shape — Sanaa's, canonized this afternoon as §2j — applied one level up: a
control defined in terms of the thing it controls is not a control, and a PREDICATE whose input is
filtered by the mechanism under test is not a predicate.** Registered.

### §10.5 NOT MEASURED

- The **one-patch-versus-both-patches** convention (cfd Part 2, relay, unverified by either of
  us). **Immaterial to every verdict above** (§10.2), and it remains open for forecasting.
- Whether the **206 wedge logs' cases** each register a nominal I have correctly inferred. Margins
  are quoted **only for F23**, where the nominal is read from
  `exact_f23.py:83` (`HALF_ANGLE_DEG = 0.04`). For the other 203 I assert **no margin** — only
  that **no code compares their printed angle to a nominal**, which is the exposure question.
- **`MESH_STANDARD` v1.8 DOES NOT EXIST** and I have ruled nothing against it. HEAD carries
  **v1.7, 1,223 lines**, verified by content hash (`git rev-parse HEAD:<path>` against
  `git hash-object`, **not** through the index — see §11). cfd's clause is an unlanded draft at
  `verification/campaign/CFD_MESH_STANDARD_WEDGE_ANGLE_CLAUSE_DRAFT_2026-08-28.md`.

---

## §11 — `git diff HEAD` IS BLIND TO 293 FILES ON THIS BOX RIGHT NOW: cfd's RETRACTION IS UPHELD, MEASURED, AND LARGER THAN THEY REPORTED (2026-08-28T18:40Z)

**cfd-supervisor retracted, unprompted, an instrument claim they had previously given the chief.
Verified here by execution rather than accepted, because it bears on this team's own method.**

### §11.1 THE MECHANISM, CONFIRMED WITH A WORKED EXAMPLE

The shared index stages **308** whole-file deletions. Once the index holds no entry for a path,
the working-tree copy is **untracked**, and **`git diff` skips untracked files entirely** — so
`git diff HEAD` compares HEAD against nothing and reports the file **wholly deleted**.

Driven on `cases/F17c_kovasznay_floor/STATUS.F17c_KV40_FLOOR`:

| instrument | reading |
|---|---|
| `git diff HEAD --numstat` | `0  1` — **one line deleted, file gone** |
| `git rev-parse HEAD:<path>` | `d0a85fffcd41fc46680f5b20bf723bd264202397` |
| `git hash-object <path>` | `d0a85fffcd41fc46680f5b20bf723bd264202397` |

**Byte-identical to HEAD, and reported as deleted.**

### §11.2 ⚠ THE POPULATION IS 293, NOT AN ANECDOTE

**Of the 308 staged deletions, 293 are byte-identical to HEAD on disk.** `git diff HEAD` will
report **293 present, unchanged files as deleted** to anyone who asks it right now. cfd found the
defect on two files; **the exposed set is two orders of magnitude larger**, and every reading is
**stably wrong**, not intermittently — the dangerous pole (§6.1).

**A second limb, also confirmed:** the index holds `docs/standards/MESH_STANDARD.md` at blob
`5ae2a3dc…` against HEAD's `20098035…`. **`git show :<path>` returns a different document than
`git show HEAD:<path>`, silently.**

### §11.3 THE INSTRUMENT THAT IS IMMUNE, AND WHY

```
git rev-parse HEAD:<path>        vs        git hash-object <path>
```
**Content hashes on both sides; the index is not in the comparison.** For diffs of committed
state, `git diff-tree -r A B` and `git diff HEAD~1 HEAD` are equally immune — both compare
**trees**, never the index.

**THIS TEAM'S OWN COMMITS ARE SOUND, AND I CHECKED RATHER THAN ASSUMED.** Every commit today used
the private-index protocol: a **private** `GIT_INDEX_FILE`, `read-tree` from HEAD, the assertion
by `git diff-tree $H $T` (**tree-to-tree**), and post-commit verification by `git diff HEAD~1 HEAD`
(**commit-to-commit**). Re-verified tree-to-tree at `82365c76`, `1d299270`, `0d461139`: insertions
only, correct paths, nothing foreign. **The pre-commit `git diff HEAD --numstat` zero-deletion
checks WERE index-dependent and could have been blind — but `docs/LAB_STATE.md` has an index
entry, so those readings were meaningful.** That is luck in the same sense §2.6 recorded luck, and
it is recorded as luck: **the assertion that carried the weight was the tree-to-tree one.**

### §11.4 THE PATTERN cfd ASKED ME TO RULE ON — SIX INSTRUMENTS IN ONE DAY, ONE SHAPE

cfd reports six of their instruments failing this way today: ugrep's parallel ordering,
`head -5` over 541 matches, `grep -m1` on a version token, a directory-layout assumption,
`git ls-files`, and now `git diff HEAD`. **Ruled: they are one class, and this audit already
carries its two halves under different names.**

**THE CLASS: AN INSTRUMENT THAT ANSWERS A DIFFERENT QUESTION THAN THE ONE ASKED, AND WHOSE WRONG
ANSWER IS THE WELL-FORMED ONE.** Every member returns a valid, plausible, confidently-shaped
value. None errors. None returns an obvious null.

**The discriminator that unifies them, and it is checkable: NAME THE PROPOSITION THE INSTRUMENT
ACTUALLY EVALUATES, THEN COMPARE IT WORD BY WORD WITH THE ONE YOU MEANT.**

| asked | actually evaluated |
|---|---|
| "does this file differ from HEAD?" | "does this file differ from **the index**, which has no entry for it?" |
| "what is the last `Time =`?" | "what is in **whichever file the scheduler returned last**?" |
| "is this tracked?" | "does **the shared index**, which the private-index protocol never updates, know it?" |
| "was this reader shown a non-zero?" | "was it shown a non-zero **in a shape the plant contains**?" (`L-402`, §2j) |

**Not a new rule — `L-394` is this class for HOSTS, `L-395` for CONTROLS, `L-401` for DECLARED
BLINDNESS, and Sanaa's `L-402`/§2j for the general case.** What is new is cfd's evidence that
**one supervisor hit six distinct members in a single day**, which makes it the lab's dominant
failure mode rather than a recurring curiosity. **The clause belongs in `MONITOR_STANDARD` and
cfd is drafting it; this section is the ruling that it IS one class, with the discriminator
above.** Their draft is theirs to land.

**AND THE PART WORTH SAYING PLAINLY: cfd retracted this against their own earlier advice to the
chief, unprompted, and separated measurement from relay under their own name when the relay would
have looked stronger.** A lab where that is normal finds these; one where it is not, does not.
