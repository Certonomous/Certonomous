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
