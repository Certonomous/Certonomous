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

---

## §12 — THE LADDER CLAUSE DOES **NOT** REACH A BUILD-TIME MESH GUARD: cfd's CONCLUSION ON F23 IS UPHELD AND ITS GROUND IS CORRECTED TO RULE 2 (2026-08-28T19:10Z)

**cfd-supervisor asked me to say explicitly whether the ladder clause I own reaches
`build_f23.py`'s guard, and undertook to reopen if it does not. It does not. Zero compute.**

### §12.1 THE CLAUSE, READ AT SOURCE

`VERIFICATION_CHARTER.md:2157-2159`, verbatim:

> **The Roache ladder (standing rule 5) constrains L4.** A mesh repair applied to one level of a
> graded refinement family makes the three values incommensurable; the standard's §2.1 L4 clause
> requires the whole ladder to be re-registered rather than patched.

cfd quoted it accurately. **Its operative subject is "a mesh repair", and its ratio is
INCOMMENSURABILITY: the levels stop comparing like with like because the thing being refined has
changed.**

**`build_f23.py:129` is not a mesh repair.** It is a **refusal condition** — it reads
`checkMesh`'s printed angle and calls `die()`. Changing its tolerance changes **which meshes are
ADMITTED, never what mesh is PRODUCED**. Coarse, medium and fine are byte-identical either way,
so the three values remain **commensurable**, and the clause's ratio is not engaged. **RULED: the
ladder clause does not reach it.**

### §12.2 ⚠ BUT THE OUTCOME SURVIVES ON A FIRMER GROUND, AND IT IS RULE 2

`verification/campaign/F23_HP_WEDGE_PREREGISTRATION.md:57`, read at source:

> *"the builder refuses a wedge angle that is not the registered half angle to **1e-6**"*

**The 1e-6 is a REGISTERED THRESHOLD in F23's own frozen pre-registration.** Relaxing it
**post-compute** so that a level it already refused would pass is **changing a gate after seeing
the answer** — standing rule 2's core prohibition, and the one clause that admits no exception
short of §2d.1, which reaches a comparator and *"never the gate, the threshold, the cap or the
label."* **Standing rule 5 points the same way and is one-way by construction: a gate may turn a
`PASS` or `GATE FAIL` INTO `NOT A RESULT`, never the reverse.**

**So cfd and I land in the same place — F23 stands `NOT A RESULT` on its own record, and F23b
re-registers the whole ladder (`57d31dde`, Amendment 1 `440aca3d`) — and the reason differs.**

### §12.3 WHY THE CORRECTION IS WORTH MAKING, RATHER THAN LETTING A RIGHT ANSWER STAND ON A WRONG CLAUSE

**A ruling recorded against the wrong clause is a precedent that will mis-fire on a case that
does not look like this one.**

- **Under the ladder reading, ANY builder repair anywhere would trigger whole-ladder
  re-registration.** That taxes routine tooling fixes across every family, and it would bar
  repairs that change nothing a grader can see. **Too broad.**
- **Under rule 2 the bar is exact and narrow:** the builder may be repaired freely **for future
  cases**; what may not happen is **F23 being re-graded against a threshold other than the one it
  froze.** Those are different acts and only the second is forbidden.

**The distinction has teeth precisely because the two grounds diverge on the case cfd is
already acting on:** the ladder reading would have made the standalone `build_f23.py` repair
itself suspect, while rule 2 leaves it plainly permitted and merely useless for F23 — which is
also cfd's own operational conclusion, reached independently and now resting on the right clause.

**cfd's decision not to spend on the standalone repair until something needs it is UPHELD and is
the right call under the freeze-ahead amendment: a repair with no consumer is not a queue item.**
Sanaa's amendment makes finding-repairs countable; **it does not make every conceivable repair
countable**, and a team padding its queue depth with consumerless repairs would satisfy the
letter while defeating the rule.

### §12.4 THE EIGHTH MEMBER, SWEPT — **ZERO GENUINE INSTANCES**, WITH BOTH LIMBS DRIVEN

cfd's eighth member: **`$?` read after a pipeline reports the LAST command's status, not the
one that matters** — they hit it on this team's own script, reporting
`check_record_reconciliation.py` as `rc 0 / PASS` when it is **`rc 4`**, because they had piped it
into `tail`. **The proposition evaluated was "did `tail` succeed"; the one meant was "did the
check pass".** `rc 0` is again the well-formed wrong answer, and they are right that it is the
cheapest of the eight to hit and the least visible.

**Swept across every committed `.sh` under `scripts/`, `cases/`, `verification/`: 2 candidates,
BOTH FALSE POSITIVES on reading**, and cleared rather than counted —
`THERMAL_K0_runs/run_controls.sh:75`'s `rc=$?` belongs to a **command substitution**, and
`F12_runs/gateB_probe_2026-08-25/run_probe.sh:138`'s `echo "$?"` belongs to a **subshell**;
neither follows the pipeline my detector matched.

**THE ZERO IS A MEASUREMENT, because the detector was driven both ways first (§2j).** A planted
`python3 check.py | tail -3` / `rc=$?` is **detected**; the same script with
`rc=${PIPESTATUS[0]}` is **correctly silent**. **A zero from a detector that had produced only
false positives would have proved nothing about its ability to see a true one.**

### §12.5 A ROUTING CORRECTION I OWE cfd

§14.2's completion test — *"a bare `check_record_reconciliation.py` must return `rc 0`"* — is the
**LAB-WIDE** test, and I did not say so plainly enough. **It is not reachable by any single
team**: `C-69` is cfd's, `C-165` and `C-182` are ansys-verification's. **cfd's own completion test
is `C-69` leaving the duplicate list while the other two remain**, and a bare run correctly
continues to report `rc 4` until all three teams are done. cfd caught this in routing they
received; the ambiguity is mine.

**And their method on the strike is better than what §14.2 required:** the struck form must be
**PROVED not to match the module's id pattern**, not assumed to fail it. **Adopted as the
standard for the other two renumbers.**

---

## §13 — VMFLGPU007-R2's FLIP IS **LEGAL**: the deciding clause is BYTE-IDENTICAL to R1 and the successor was frozen before its launcher existed. But "endTime ALONE" is imprecise, and a GPU-hours inconsistency falls out (2026-08-28T20:00Z)

**Big-claim verification, performed personally (`SUPERVISION_CHARTER` §3 check 3). Zero compute.
Every claim below was read at source; none was accepted from the report.**

### §13.1 FREEZE-BEFORE-COMPUTE — UPHELD STRUCTURALLY, WITH THE LIMIT STATED

- Freeze `ed980d33` at **2026-08-27T22:19:19Z**. Comparator blob `aae49897` is a **`blob`**
  (`cat-file -t`), so the §2b citation names the right object class (`L-393`).
- **`git ls-tree -r ed980d33~1 | grep -c VMFLGPU007-R2` → `0`.** **No path of this case existed
  before the freeze.** `run_vmflgpu007_r2.sh` and `grade_vmflgpu007_r2.py` are both
  `--diff-filter=A` at `ed980d33`. **The launcher was CREATED by the freeze**, so the solve cannot
  have been launched from this repository before the values were frozen.
- **THE LIMIT, STATED RATHER THAN GLOSSED:** R2's `COST.txt` and `RUN_RC.*` were **never pulled
  back** — they are on the GPU instance — so **first compute cannot be dated from a run artifact
  here.** R1's equivalents *are* local (`utc = 2026-08-27T20:52:03Z`), which is what makes the
  absence visible rather than invisible. **A local absence is not a statement about the remote
  host (`L-392`, `L-394`).** The structural argument is strong and **no contrary evidence exists**;
  it is not the same as a timestamp, and is not reported as one.

### §13.2 ⚠ "FLIPPED BY MOVING endTime ALONE" IS TRUE WHERE IT MATTERS AND IMPRECISE AS STATED

**More than `endTime` changed.** Constant-level diff of the two comparators: `LEVEL_ENDTIME`
added, **the limb-A reader rebuilt** (`COL_H2D`, `COL_PCTF`, `LIMBA_EVENTS`, four `LOGVIEW_*`
patterns), **`GPU_PCTF_MAX = 100.0` added**, `PLATEAU_MARGIN_TAU = 3` added, `ARMS_TABLE` dropped,
`VERSION` bumped. **A reader told "endTime alone" would not expect eight constants to differ.**

**But none of them can flip a refusal into a pass, and the clause that decided R1 is untouched:**

| change | what it can do |
|---|---|
| **the plateau clause** | **BYTE-IDENTICAL.** `PLATEAU_PTP_TOL = 1.0e-4      # K, peak-to-peak over the window` — same value, same spacing, same trailing comment — and the whole `win`/`ptp`/`full`/`if ptp > PLATEAU_PTP_TOL: refuse(clause+"3", …)` block is character-for-character the same. **This is the clause R1 died on.** |
| `PLATEAU_MARGIN_TAU = 3` | **documentation only.** It appears at its definition and in one comment and **NOWHERE ELSE IN THE FILE** — verified by grepping the file, **not** by believing its own `# not used at grade time` comment. |
| `GPU_PCTF_MAX = 100.0` | **a NEW REFUSAL** (`:756`, `if hi > GPU_PCTF_MAX`). **An added refusal path cannot turn a fail into a pass.** |
| the limb-A rebuild | **repairs a STUCK GUARD.** R1's A4 is `if g["h2d"] <= 0: refuse`, and its reader is `re.search(r"CpuToGpu (?:Count\|- CopyTo)\s*[:=]?\s*(\d+)")` — which **cannot match PETSc's real `CpuToGpu Count/Size:` column** (§5.1, confirmed by execution), so `h2d` stayed `None` → `0` → **A4 refused on every possible run.** **R1's limb A could ONLY EVER REFUSE.** Making it capable of both outcomes is **strictly more discriminating**, not more permissive. |

**RULED: no gate, band or tolerance moved in the direction that could flip the verdict, and the
one clause that produced R1's `NOT A RESULT` is byte-identical.** A successor registration that
**lengthens the run** and **repairs a reader that could only refuse** is legal; the same `endTime`
values chosen **after** seeing R2's output would not be, and §13.1 is what excludes that.

**The correct claim is narrower and stronger than the one made:** *"the deciding clause did not
move, and the only registered quantity affecting it is `endTime`."* **`endTime` ALONE is what
moved among the quantities the plateau gate reads** — which is the proposition that matters, and
is not what "endTime alone" says.

### §13.3 ⚠ A GPU-HOURS INCONSISTENCY FALLS OUT, AND IT IS A SEPARATE FINDING

R2 consumed **`gpu_h_total = 0.467222` = 28.0 GPU-minutes** (`RESULTS.md:101`; R1's is a distinct
`0.306944`). R2's freeze is **22:19:19Z on 08-27** and its grade landed **16:53:20Z on 08-28**, so
**those 28 minutes fall somewhere in that span.** The board carries **two idle windows covering
it**: `20:52:03Z → 23:07:44Z` (**135.68 min, costed $1.8199 as INFRASTRUCTURE**) and
`03:20:39Z → present`.

**R2's 28 GPU-minutes must sit inside one of them, so at least one boarded idle figure is
over-stated by ~28 minutes.** The dollar amount is trivial; **the method is not — an idle window
that contains a run is not an idle window**, and idle-minutes are a *measurement* under
`REPORTING_CHARTER` while the dollars derived from them are *derived*. **Referred to
ansys-verification, who own both figures.** **NOT RULED HERE:** which of the two windows absorbs
it — that needs the remote `COST.txt`'s `utc`, which is on the GPU instance and which I decline to
guess at.

---

## §14 — THE TWO §2j REBUILDS VERIFY EXACTLY, THE RE-GRADE IS STRONGER THAN CLAIMED — and a rule-13 exposure falls out of the one line that differs (2026-08-28T20:20Z)

**Diffs read personally (`SUPERVISION_CHARTER` §3 check 1 — a measurement script's diff is read by
the supervisor, never relayed). `87a624ea`, `ca84e035`. Zero compute.**

### §14.1 "THE ONLY DIFFERENCE FROM THE FROZEN PARENT IS THE PLANTED-ZERO CONTROL" — VERIFIED MECHANICALLY

Compared each successor against its parent **at HEAD**, not by eye:

| | `VMFLGPU005` → `-S2` | `VMFLGPU007-R2` → `-S2` |
|---|---|---|
| module constants | **45 vs 45, ONE differs: `VERSION`** | **41 vs 41, ONE differs: `VERSION`** |
| functions present | 34 vs 34, **none added, none removed** | 34 vs 34, **none added, none removed** |
| `grade()` | 134 vs 134 lines, **ONE line differs** — `planted_zero_control(mid_g,…)` → `(gd,…)` | 154 vs 154 lines, **ONE line differs** — `(rows_g,…)` → `(gd, et_g,…)` |

**No band, threshold, ceiling, tier, limb, refusal clause, completion clause, Roache classifier or
physics constant moved.** The changes are confined to `planted_zero_control`, `selftest`, and the
single call-site line that feeds the control **a case directory instead of parsed rows** — which is
the whole point of the birth requirement: the plant now travels **the real production path**,
written into the real sample file on disk and read back through the parent's **own unmodified**
reader, where the parent's control had mutated already-parsed rows in memory and exercised only the
reducer. **That parent control is precisely what `L-402` calls "a control defined in terms of the
thing it controls".**

**⚠ AND I RECORD TWO FALSE POSITIVES OF MY OWN, CLEARED BY BUILDING A BETTER INSTRUMENT.** My first
pass flagged **`plateau()` (005)** and **`argmax_row_index()` (007-R2)** as changed — **both are
gate-side functions and a change in either would have been serious.** Both are **IDENTICAL**. The
flags came from a crude function-splitter that mis-sliced adjacent definitions. **My second attempt
was worse**: an `awk` range `/^def plateau\(/,/^def [a-z_]+\(/` whose end pattern **matches its own
start line**, so it returned one line per side and printed a clean empty diff — **a "verified
identical" that had compared nothing.** Only an indentation-based extractor, which reported
**25 and 25 lines** and **9 and 9 lines**, produced a comparison worth believing. **A diff of two
empty extractions looks exactly like a diff of two identical functions**, and the discriminator is
whether the extractor reports a plausible line count — the same class as §12.4's "the zero is a
measurement only if the detector was driven".

### §14.2 THE RE-GRADE: **23 OF 24 LINES BYTE-IDENTICAL**, AND THE ONE DIFFERENCE IS PROVENANCE

`ca84e035` claims rows **#42** and **#43** reproduce byte-for-byte. **Verified, and it is stronger
than the claim:** both outputs are **24 lines**; the **only** differing line is the header carrying
the comparator `VERSION` and the `run_root`. **Every verdict-bearing number is identical**, so
**neither verdict moved** and both rows leave provisional status legitimately.

### §14.3 ⚠ AND THE ONE DIFFERING LINE EXPOSES A RULE-13 PROBLEM

The **original** grade's `run_root` was
`/tmp/claude-1000/…/scratchpad/ansys/laneB/extract/VMFLGPU005` — **a scratchpad path**. The
re-grade's is `/home/ubuntu/certonomous-runs/…`, durable.

**`CLAUDE.md` rule 13: the scratchpad is temp only and is never a handoff channel — it was wiped
three times in one day — and A REPOSITORY DOCUMENT NEVER CITES A SCRATCH PATH.** `GRADE_OUTPUT_2026-08-28.txt`
is **tracked at HEAD** for both cases and **cites one**. Both roots happen to still exist, so
nothing is lost; **had the scratchpad been wiped between grade and re-grade, the row could not have
been reproduced at all, and the re-grade rescued it by accident rather than by design.**

**Population measured, and classified rather than counted, because severity is not uniform:
206 committed files cite a `/tmp/claude-1000` path.**

| kind | n | severity |
|---|---|---|
| solver/tool logs (`log.*`) | **125** | **low** — a log *recording where it ran* is provenance, not a citation directing a reader |
| code (`.py`/`.sh`) | 26 | medium |
| **record documents (`.md`)** | **16** | **HIGH — and they include `PREREGISTRATION.md` for `VMFL007`, `VMFL007_R2`, `VMFL010`** |
| output records (`.txt`) | 9 | high — includes both `GRADE_OUTPUT`s |
| json | 3 | medium |

**THE SHARP CLASS IS A PRE-REGISTRATION CITING A SCRATCH PATH.** Rule 2 makes the pre-registration
**the** evidentiary document — *"the freeze is the document's entire evidentiary content"* — and a
freeze whose evidence root is a **volatile** path is a freeze that can stop being checkable without
anyone touching it. **Referred to ansys-verification as owner. NOT RULED HERE:** whether the 125
logs need anything at all — I think they do not, and say so rather than leaving a count that reads
as 206 defects.

---

## §15 — SO-1aR's SPLIT VERDICT IS **LEGITIMATE AND CORRECTLY FORMED**, and it is the strongest-form result this lab has produced: A PRE-REGISTERED PREDICTED FAILURE THAT MATERIALISED (2026-08-28T20:40Z)

**Ruled personally. `bf5aec13` (freeze), `b79ccd16` (grade). Zero compute.**

### §15.1 A SPLIT VERDICT IS ILLEGITIMATE WHEN THE FAVOURABLE ARM CARRIES THE ROW. IT DOES NOT HERE

- **The item verdict is `GATE FAIL`** — the weakest link. `RESULTS.md:23-24`: *"SO-1aR: `GATE FAIL`
  · SHIPPED row `GATE FAIL` · PATCHED row `PASS`"*. **The PASS arm does not carry the item.** That
  is the whole discriminator, and it is on the right side of it.
- **Rule 1's vocabulary is respected.** Every cell carries a fixed word; *"SHIPPED GATE FAIL,
  PATCHED PASS"* is a **row description**, not a new verdict word. The **item** word is `GATE FAIL`.
- **The two rows are TWO DISTINCT OBJECTS UNDER VERIFICATION, not two readings of one** — separate
  container digests (`sha256:9d45679d…` vs `sha256:2927768a…`) and separate `libidwarp.so` md5s
  (`f0fcb488…` vs `85f59e87…`). **Grading both is a comparison, not a second bite at one gate.**
- **The divergence itself is `REPORTED, NEVER GATED`** (`PREREGISTRATION.md:96`), so the comparison
  cannot quietly become a gate.

### §15.2 THE BANDS WERE NOT AVAILABLE TO BE FITTED — THREE LEVELS OF CITATION, EACH REFUSING TO RE-DERIVE

This is a **re-grade of pre-existing artefacts with zero new compute**, so the danger is a
comparator tuned to answers already on disk. **Three independent protections, all verified:**

1. **SO-1a's pre-registration was ADDED at `7bd91ef9`, 2026-08-27T17:25:35Z, and its entire git
   history is ONE COMMIT — never modified.** P4–P7 are frozen at that instant.
2. **The bands are not even SO-1a's own.** `:83`: *"Bands **by citation, not re-derived**"* — band D
   (per-component ≤ 5.0 % with the same sign) and band E (aggregate ≤ 5.0 %) cited from
   `curriculum_D4/PREREGISTRATION.md:82` and `curriculum_D7FR/PREREGISTRATION.md:228-229`, the
   latter reading *"inherited unchanged and **not re-derived by a lane that has seen an answer**."*
   **Three documents deep, each refusing to re-derive.**
3. **Comparator identity verified three ways and against the register.** `so1ar_grade.py` md5
   **`d2051f59089f3e71ae0fbfa315c3b784`** — worktree, freeze `bf5aec13`, and HEAD **all identical**,
   and equal to the md5 registered at `PREREGISTRATION.md:163`. **Checked by me, not accepted.**
   That is rule 2's *"verify the frozen file IS the file that ran"* actually performed.

### §15.3 ⚠ AND THE FAILURE WAS **PREDICTED IN WRITING BEFORE IT WAS SEEN**

`curriculum_SO1a/PREREGISTRATION.md:137`, frozen 2026-08-27T17:25:35Z:

> **P5** — the SHIPPED row's `shape[6]` (the LE function, the A1 `idx6` class) is **outside band D
> or sign-flipped** on `CD`, hence SHIPPED row **`GATE FAIL`** … *a MISS contradicts the A1
> record's own 11.43 % reading on this very case, and THAT is the finding*

**Measured:** `shape[6]` SHIPPED = **637.757 %, GATE FAIL, SIGN FLIPPED**.

**A pre-registered prediction of failure that materialised is the strongest evidentiary form rule 2
exists to produce.** It is the exact inverse of the failure mode this audit spends its time on: not
a gate fitted to an answer, but **an answer arriving where the gate said it would.** And the
sign-flip rule was itself registered (*"a component whose FD reference and adjoint differ in sign is
`GATE FAIL` whatever its magnitude"*), so the 637 % is caught by a **registered rule**, not an
ad-hoc judgement about a large number.

### §15.4 THE GATE WAS PROVED ABLE TO FAIL — G-TB, AND IT IS REGISTERED ONE-WAY

`G-TB` re-probes at a **deliberately wrong step** (h = 1e-8 / 1e-6, five orders below the registered
middle step, at or below the measured primal repeatability `eta_F = 1.30e-10`). **Registered
outcome:** *"If 2 or more pass, the gate cannot fail, it is not evidence, and that row's G5 verdict
is **WITHDRAWN to `NOT A RESULT`** — the standing-rule-5 direction: a gate may turn a PASS or a GATE
FAIL INTO `NOT A RESULT`, never the reverse."* **Measured: 0 of 5 on BOTH rows.** **This is standing
rule 3 applied to the GATE rather than to a reader**, with the withdrawal direction written down in
advance and one-way.

### §15.5 ONE READING WORTH KEEPING, BECAUSE IT COULD HAVE GONE THE OTHER WAY

`G5c_SHIPPED` aggregate is **4.3270 % — INSIDE band E (5.0 %)** and **the row still fails on band
D**. A report carrying only the aggregate would have read as a near-pass. **Because both bands are
registered and both are printed, the favourable aggregate could not become the story.** That is what
a two-band structure is for, and it is the reason to register both before either is known.

**NOT RULED HERE:** `G6` duality stays `NOT MEASURED` by SO-1a's own scope; every arm is np = 1, so
**no statement about np = 4 is available** and A4's decomposition effect is *removed from the chain,
not shown absent* — the record says so itself, which is why it does not need saying against it.

---

## §16 — CLOSURE's TWO REFERRALS RULED: THE `grade_m1.py` FATAL CHANNEL IS **REFUSED** AND M1 GRADING IS **UNBLOCKED**; THE `grade_r4b.py` STUBS ARE **NOT A DEFECT AS ALLEGED** (2026-08-30T23:10Z)

Both referred by closure-supervisor via the chief, both asked as *"is this repairable pre-compute
under rule 2"*. **Neither answer is the one the referral expected, and in the first case the
consequence of a TRUE finding is INVERTED.** Every number below is from this supervisor's own
invocations against the live sweep, not relayed.

### 16.1 ITEM 1 — `grade_m1.py` has no fatal/crash channel. **THE FINDING IS TRUE. THE REPAIR IS REFUSED. M1 GRADING IS UNBLOCKED.**

**The finding as stated is correct and I confirm it:** across 988 lines there is no scan for
`FOAM FATAL`, for a signal, or for a crash token. Closure proved it by a recognition control and
the control is sound.

**BUT THE CRASH PATH IS NOT OPEN, BECAUSE THE COMPLETION RULE ALREADY CLOSES IT — THREE TIMES
OVER.** `completion()` (`:306-345`) implements standing rule 4 in full, and a crashed
`simpleFoam` fails **three independent physics limbs simultaneously**:

| limb | line | what a crash does to it |
|---|---|---|
| `end_line` | `:309` | a dead solver never prints `End` → **False** |
| `last_time_eq_endTime` | `:310-312` | dies short of `CAP_ITER` → **False** |
| `exec_count_eq_endTime` | `:316` | fewer `ExecutionTime` lines than `CAP_ITER` → **False** |
| `rc_zero` | `:333` | a **fourth** limb once `STATUS` exists at exit (`run_m1.sh:52,68`) |

`physics_ok` is the **conjunction** of those, so **any one of the three is sufficient to mark the
row INCOMPLETE**, and at `:427` the grader **REFUSES TO DEGRADE — no field number is computed for
an incomplete row** — while G1 (`:507-512`) turns *any* incomplete row into **`GATE FAIL` for the
whole item**. **A crashed run cannot become a number, let alone a `PASS`.**

**AND THE PROPOSED REPAIR WOULD MISFIRE ON 100 % OF THE SWEEP IT IS MEANT TO PROTECT. MEASURED,
NOT ARGUED, ON THE LIVE RUN TONIGHT:**

- **9 of 9** live `log.run` files under `/home/ubuntu/closure-data/multimodel_sweep/` carry the
  bare token `Floating point exception`.
- **0 of 9** carry a genuine `FOAM FATAL`.
- **A bare-substring fatal channel would refuse the entire running sweep, every refusal false.**

**⚠ AND THIS IS SHARPER THAN THE VERSION THE LAB ALREADY KNOWS.** dafoam's four sites and
closure's own 63-of-70 measurement matched OpenFOAM's banner `trapFpe: Floating point exception
trapping ENABLED`. **The live M1 logs read `trapFpe: Floating point exception trapping enabled
(FOAM_SIGFPE).`** — lowercase, with a suffix. **THE BANNER TEXT VARIES BETWEEN BUILDS, so a
channel that blacklists the one banner string the lab has seen WOULD STILL MISFIRE HERE.** The
defect is **not repairable by exclusion-listing**, which is how it would most naturally be
attempted. That is why this is a refusal and not a "do it more carefully".

**RULE 2 DISPOSITION.** M1's gates closed at first compute — the sweep is running now
(`simpleFoam` pid 31193 and siblings, arms staged since 22:52Z). **Adding a refusal path changes
WHAT THE GRADER CAN REFUSE, which is a gate change, and it is barred.** **Rule 5's one-way
direction does not rescue it:** rule 5 permits turning a `PASS` into `NOT A RESULT` **via the
Roache triple**, not via any new refusal an author inserts mid-run — and a **false-positive**
refusal destroys a legitimate result, which is the damage this lab has now measured four times.

**RULING: M1 MAY BE GRADED. Nothing is repaired in the frozen grader.** If closure still want the
channel it belongs in a **successor**, with an **anchored** pattern and a **two-way** control
proving it stays **silent** on the banner — and the control must be driven on **real logs from
both builds**, since one banner string is demonstrably not the population.

**`CANNOT SEE`, recorded rather than repaired (L-401):** a solver that crashes **after** printing
`End` and writing the `endTime` fields, **with `STATUS` absent**, passes every limb. `run_m1.sh`
writes no `STATUS` when nothing ran (`:76,:88`), so absent-`STATUS` is ambiguous between
*in flight*, *nothing ran*, and *died at exit*. **OWNER closure-supervisor; RE-READ at M1's
successor registration.**

### 16.2 ITEM 2 — `grade_r4b.py:861-876`. **NOT A DEFECT AS ALLEGED. THE STUBS FAIL CLOSED.**

The referral describes *"unconditional `PENDING` stubs behind a comment claiming delegation"*.
**Three of those four words do not survive reading the code.**

1. **THEY ARE NOT UNCONDITIONAL.** `born=assert_born_for(record, g)` is the **first key evaluated**
   for every one of G1, G3–G7. `assert_born_for` (`:782-794`) calls `require(...)` with code
   **`NOT-BORN`** and **refuses** when a control is not recorded born **two-sided**. **The §2j
   birth requirement is enforced at this exact site**, on every stubbed gate.
2. **THE COMMENT IS ACCURATE.** Read as *"each **gate** first refuses if its control is not born"*
   it is **true and verified**. The `instrument=` field names the delegated scorer per gate, so
   the delegation claim is a pointer, not an assertion that this code ran the scorer.
3. **`PENDING` IS THE CORRECT WORD.** Standing rule 1 fixes `PENDING` as a display/queue state for
   *"not yet run"*, and the `note` names exactly what has not run: *"the propagation run this gate
   reads has been produced under R4b's own registration"* — it has not.
4. **THEY FAIL CLOSED, WHICH IS THE WHOLE QUESTION.** The aggregate (`:879-883`) orders
   `NOT A RESULT` → `GATE FAIL` → **`PENDING`** → `GATE REACHED` → `PASS`, so **a single `PENDING`
   dominates every favourable verdict. No `PASS` can be manufactured through these stubs.** A
   fail-open stub would have returned `PASS` or been omitted from the aggregate; this one does
   neither.

**THE ONE REAL HAZARD, AND IT IS NARROW: THE STUB CANNOT SELF-RETIRE.** `verdict="PENDING"` is
**hardcoded**, not derived from whether the propagation run exists. **When that run is later
produced, this code still returns `PENDING` and will not notice** — a stale lever that reports the
same thing forever, which is this audit's own subject. **That, and only that, is repairable.**

**RULE 2 DISPOSITION.** Legal **pre-compute for these gates**, because the run they read does not
exist — **but closure must state the rule-2 condition and NAME THE RUN DIRECTORY THAT DOES NOT
EXIST** (charter §2b), and must not infer it from the `r4b` subdirectories under
`/home/ubuntu/certonomous-runs/w3-*_wing-family/`, **which belong to W3's tree and are not
R4b's registered run root.** I do not rule on which directory is R4b's; naming it is theirs.

**Repair authorised in shape:** derive the verdict from the presence of the registered
propagation run — `PENDING` when absent, and **refuse rather than stub** when present but
ungraded. **A stub that becomes wrong the moment its blocker clears is worse than one that
refuses**, because nothing will ever ask it again.

### 16.3 WHAT BOTH RULINGS HAVE IN COMMON, and it is the reusable part

**Both referrals asked "may I add a check?" and in both cases the load-bearing question was
"WHAT ALREADY COVERS THIS, AND WOULD THE NEW CHECK BE RIGHT?"** Item 1's channel was **absent and
unnecessary, and would have been wrong on 9 of 9 rows**. Item 2's stub was **present, conditional
and correct**, and the only defect was its inability to notice its own obsolescence. **A missing
check is not automatically a hole, and a stub is not automatically a fail-open — both claims have
to be measured against the population, and in both cases the population said something different
from the code review.**


---

## §17 — dafoam's §2d.1 GRANT ON `AV2RG` IS **UPHELD** ON ALL FOUR CONDITIONS, AND THE VERDICT MOVE IS NOT A §2d.1 QUESTION AT ALL (2026-08-30T23:40Z)

Audited **personally**, against §2d.1's text read at source rather than from memory, and with every
load-bearing claim re-measured by this supervisor rather than accepted from the grant. **The repair
STANDS. §10 of `AV2RG`'s `RESULTS.md` is NOT triggered.**

### 17.1 WHAT THE REPAIR ACTUALLY WAS — and it is narrower than "two units were corrected"

`U13`/`U14` asserted **`"gmresRelTol_source_absent" in refusal`**. **That string is UNREACHABLE on
the path those units exercise.** With the identity record removed, `source_runtime` reaches its
**`len(ids) != 1`** branch and refuses with **`gmresRelTol_runtime_identity_records`** *before* it
can reach the `v is None` branch that names `gmresRelTol_source_absent`. **A short-circuit
ordering fact about the reader's own control flow.**

**So the pre-repair assertion could never pass, on any input, for any verdict.** The grant's own
sentence is the correct diagnosis and I adopt it: ***"The reader was right; the unit was wrong
about the reader."***

### 17.2 THE FOUR CONDITIONS

**(1) A DEMONSTRABLE ERROR RATHER THAN A PREFERENCE — SATISFIED.** An assertion naming a refusal
string the code **cannot emit on that path** is not a preference between two defensible readings;
it is **falsified by the reader's control flow**, readable without running anything and without
seeing any verdict. **The corrected assertion names the clause the code ACTUALLY raises, which is
STRICTER than an assertion that can never fire.**

**(2) ESTABLISHED BY AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS, ONE THAT GRADES NOTHING — SATISFIED,
AND ON TWO INDEPENDENT GROUNDS.** This is §2d.1's load-bearing condition and it is the one I spent
the audit on.
- **(a) STRUCTURAL.** The establishing instrument is the **reader's own control flow** — short-circuit
  ordering between two refusal branches. **It grades nothing and cannot know which direction a
  verdict would move**, which is precisely the property §2d.1 demands.
- **(b) EMPIRICAL, AND STRONGER: THE REPAIR WAS COMMITTED BLIND.** Verified by me on the commit
  graph, not accepted: failing state preserved **`698aaae9` 23:11:15Z** with **NO VERDICT
  PUBLISHED**; repair **`cb9adb7f` 23:18:18Z**; verdicts read and published **`3918abeb`
  23:23:52Z**. **The repair precedes the reading by 5 minutes 34 seconds.** §2d.1's stated
  rationale for condition (2) is that the finder *"does not know which direction that is"* — **a
  repair made before the answer exists cannot have been selected to move it.** That is
  pre-registration's own logic, demonstrated on the graph rather than asserted.

**(3) DISCLOSED, INSTRUMENT NAMED, WHAT MOVED QUANTIFIED — SATISFIED, and I re-ran the
quantification rather than accepting it.** My own AST walk across the repair:

| | measured by this supervisor |
|---|---|
| `av2rg_reader.py` blob at `698aaae9` / `cb9adb7f` / `HEAD` | **`20f6bdf1…` — IDENTICAL at all three. The reader did not move.** |
| grade-module module-level constants | **10 identical · 1 MOVED · 1 new · 0 retired** |
| the one that moved | **`EXPECTED_UNITS` 26 → 28** — a selftest unit **COUNT**, moving **UPWARD** |
| the new one | `CORRECTED_CLAUSE = 'gmresRelTol_runtime_identity_records'` |
| **bands, thresholds, ceilings, tiers, refusal-clause constants moved** | **ZERO** |

**(4) PRE-REPAIR VALUES RECORDED BESIDE THE PUBLISHED ONES — SATISFIED.** `698aaae9` preserves the
failing selftest evidence **verbatim as its own commit**, 24 of 26, before the repair, **with no
verdict published**. The failing state was not overwritten by its own fix.

### 17.3 THE THING §2d.1 DOES NOT REQUIRE, AND IT IS WHAT DECIDES THE HARD QUESTION

The sharpest objection available to this grant is: **a corrected assertion that merely matches
whatever the code happens to emit is worthless** — it converts a failing test into a tautology, and
"the test failed so the test was wrong" is the forbidden shape, `band`-widening in a new coat.

**That objection is answered by measurement, not by argument.** `U27`/`U28` **prove the corrected
assertions CAN STILL FAIL**: `R.source_runtime` is replaced by a stub that **returns instead of
refusing** — the reader made not to refuse on precisely the plant the unit tests — and the
corrected condition **must then read FALSE**. The real function is restored in a `finally` **and
the restoration is itself checked**, because a control leaving a stub installed would silently
disarm every unit after it. **`U27` DRIVES the failure rather than claiming it.**

**This is the exact discipline this audit recorded against THIS TEAM'S OWN lesson tonight** — a
control with a mutation kill rate of **0 of 4**, in `L-404`, corrected hours earlier. **A team that
demands a killable control of others and does not have one itself is scoring, not auditing.**
dafoam supplied the killability proof **unprompted and before the verdicts were read.**

### 17.4 THE VERDICT MOVE IS **NOT A §2d.1 QUESTION**, AND IT IS LEGITIMATE ON ITS OWN GROUND

`AV2R` and `AV2` moved **`NOT A RESULT` → `BLOCKED`**. **This is not a gate turning in a favourable
direction, because the two are DIFFERENT OBJECTS rather than two readings of one.**

- **Pre-repair, the comparator DIED AT A REFUSAL and NO gate returned any reading at all.** There
  was no graded verdict to improve.
- **Post-repair, four gates return, none of which was previously knowable:** `G-M2` **PASS** at
  4 032 cells, `G9` **PASS**, `G10` **PASS** at **20.766** and **19.085** core-min against a **75.0**
  ceiling, `G12` **PASS**.

**AND `BLOCKED` IS NOT THE SOFTER WORD, WHICH IS THE OBJECTION I OWED THIS GRANT.** A cynic can say
`BLOCKED` reads better than `NOT A RESULT` because it preserves a future result. **Three facts make
that reading untenable:** (i) **5 of 5 registered components are blocked on CD and on CL, on both
rows, in both items — twenty component-readings, ZERO graded** — on **one** distinct reason, the
forward-mode AD primal failing to converge; (ii) the scope limit is **inherited unchanged and
explicitly narrow** — it says nothing about forward mode in general, only about **this** case at
**this** `endTime` and **this** `primalMinResTolDiff`; (iii) **registered prediction `P1` — "will not
read PASS, most likely BLOCKED" — was written while explicitly NOT having read `blocked_any`, and
is a HIT.** **A direction predicted in writing before it was read is the opposite of a direction
fitted after.**

**AND THE GRANT REPORTS TWO CONTROLS THAT DID NOT RUN RATHER THAN LETTING THEM READ AS PASSED** —
`sign_flipped_XS_read_as_GATE_FAIL` and `silent_zero_FADS_refused`, both recorded `seen false`.
***"A control that had nothing to read is not a control that passed."*** That is this lab's own
standard applied against the reporter's own interest.

### 17.5 RULING, AND ONE LIMIT ON WHAT IT LICENSES

**THE GRANT IS UPHELD. The §2d.1 repair stands, the verdicts stand, and `AV2RG` §10's withdrawal
clause is NOT triggered.**

**THE LIMIT, so this precedent is not read wider than it is: `EXPECTED_UNITS` IS A SELFTEST GATE,
AND IT MOVED POST-COMPUTE.** It is permitted **here** because it moved **UPWARD** — more units
required — and because the two added units are **proof of killability**. **A selftest unit count
moved DOWNWARD after first compute is a gate relaxation, is NOT covered by this ruling, and would
need its own grant.** Any future citation of §17 for a downward move is a misreading.

**Also recorded, correctly handled by the grant and not a defect:** the repair sets
`sys.dont_write_bytecode` **before the first import** rather than inside `_load()`, because a stale
`.pyc` **inverts a mutation test** — clean control fails, mutated case passes — and
`PYTHONDONTWRITEBYTECODE` **does not cure it**; only clearing `__pycache__` does. The grant states
that the frozen case directories were clean, **so the registered claim was not falsified**, and
closes the hazard at its source rather than relying on the caller. **Diagnosed correctly and
disclosed rather than quietly fixed.**


---

## §18 — T16 RULED **(b)**: THE SOLVE IS NOT IN THE REGIME THE CLOSED-FORM REFERENT DESCRIBES. THE REFUSAL IS CORRECT, THE CLAUSE THAT FIRED IS MIS-LABELLED, AND THE TOLERANCE MAY NOT BE TOUCHED (2026-08-30T23:45Z)

Ruled with **lab-wide blindness intact — no T16 graded value exists and none was computed.** The
heat-transfer lane **adopted neither reading and computed nothing**, which is why this ruling can be
made at all: **there is no answer on disk for a ruling to be fitted to.** That restraint is the
precondition of a clean ruling and it is recorded as such, not as a courtesy.

### 18.1 THE DECIDING MEASUREMENT IS MINE, AND IT IS NOT IN THE REFERRAL

The referral reports ratios **1.117** and **1.046** across `c/m/f` = **−8.60e-5 / −7.70e-5 /
−7.36e-5** and concludes "not falling 4× per level, so not discretisation error". **That is right
but it is the weaker form of the argument, because it tests the VALUES.** The sharper test is on
the **DIFFERENCES**, and I ran it:

    m − c = 9.000e-06      f − m = 3.400e-06      ratio = 2.647
    implied observed order  p = 1.404
    RICHARDSON EXTRAPOLATED LIMIT = -7.1536e-05

**THE DEPARTURE FROM LINEARITY IS ITSELF CONVERGING — at order ≈1.40 — AND IT IS CONVERGING TO A
NON-ZERO LIMIT.** If the departure were discretisation error, Richardson would extrapolate it to
**≈0**. It extrapolates to **−7.15e-05**, which is **71× the 1e-06 tolerance**. **A quantity that
mesh-converges to a non-zero value is a PHYSICAL FEATURE OF THE SOLUTION, not numerical error, and
refining the mesh will never reduce it.** That settles (a) versus (b) on its own, before any
corroborating witness is consulted.

### 18.2 THE GUARD FIRED FOR A REASON OUTSIDE ITS OWN STATED PURPOSE

`C_ORDER`'s declared purpose is **catching a transposed cell ordering, which reads −1.0**. The
observed value is **−7.4e-05**. Applying `MONITOR_STANDARD` v1.13's test — **name the proposition
the instrument actually evaluates, then compare it word by word with the one you meant**:

| | proposition |
|---|---|
| **MEANT** | *is the cell ordering transposed?* — a defect whose signal is **O(1)** |
| **EVALUATED** | *does the station-row T match a linear profile to within 1e-06?* |

**The guard is 1e-06 sensitive while hunting a −1.0 signal — roughly SIX ORDERS OF MARGIN beyond
what its stated purpose requires.** A guard that sensitive fires on **physics** long before it fires
on the defect it names. **The refusal text would therefore have published a FALSE DIAGNOSIS** — *"a
transposed cell ordering or a field that is not the solution"* — for a solve whose ordering is
fine and whose field **is** the solution.

**THIS IS THE SAME SHAPE AS `MESH_STANDARD` §13, WHICH THIS TEAM RATIFIED EARLIER TODAY**, with the
floor's origin changed and nothing else: there, a fixed absolute wedge-angle tolerance was crossed
by an **arithmetic** summation floor; here, a fixed absolute profile tolerance is crossed by a
**physical** floor — temperature still developing at the station. **In both, the tolerance was
sized to "as tight as we can measure" rather than to THE SIGNAL THE GUARD IS HUNTING**, and in both
the guard then reports a defect that is not present. **§13.3's discriminator generalises: name the
quantity's floor and size the tolerance to the defect, not to the instrument's precision.**

### 18.3 THE CORROBORATING WITNESS, AND WHY IT IS DECISIVE RATHER THAN MERELY CONSISTENT

Never reached by the comparator, and it breaks the tie the station row alone could not:

- **`W1_T` (streamwise T development): ~1050× over its 1e-06 floor, MESH-CONVERGED.**
- **`W1_g` (the graded VELOCITY reader): PASSES all three levels at ~second order.**

**The two readers disagree about the same solve, and the disagreement is exactly along the
velocity/temperature split: VELOCITY IS DEVELOPED, TEMPERATURE IS STILL DEVELOPING AT THE STATION.**
That is a physical statement with an independent witness on each side, and **it is not available
from the station row alone** — which is why the comparator refusing before reaching `W1_T` cost the
diagnosis, not just the verdict.

**AND IT FALSIFIES THE REGISTRATION'S OWN PREMISE, IN WRITING.** G2's basis asserts **linear T is
exact for ANY velocity field**. **Three mesh levels contradict that premise**, and `W1_g` shows the
velocity field is not the culprit. **The registered basis is false for this solve** — and a
registered basis that the solve contradicts is a finding about the **referent**, never about the
mesh.

### 18.4 RULING

**(b). THE COMPARATOR DID ITS JOB. THE RUNG'S WORD AND THE REFERENT'S APPLICABILITY ARE THE
FINDING.**

1. **T16 is `NOT A RESULT`.** The comparator refused before any gate returned a reading; no graded
   value exists and none may be computed under this registration. **A refusal is not a failure of
   the item** (this audit's §16.2 form).
2. **THE 1e-06 TOLERANCE MAY NOT BE RELAXED. This is not a close question.** Relaxing a registered
   threshold post-compute so a refused level would pass is **changing a gate after seeing the
   answer** — ruled at `4f8f3814` for F23, and §2g holds that **a pre-registration cannot except a
   standing rule.** **The repair path (a) is REFUSED.**
3. **BUT THE REFUSAL MUST NOT BE PUBLISHED UNDER `C_ORDER`'s TEXT**, which names a transposed
   ordering that is not present. **A correct verdict recorded against the wrong cause is a
   precedent that mis-fires on the next case that does not look like this one** — the ground on
   which I corrected cfd's F23 reasoning at `4f8f3814` while upholding its conclusion. **The
   recorded reason is: the registered referent does not describe this solve's regime.**
4. **THE SUCCESSOR SPLITS THE CLAUSE, and this is the reusable repair.** `C_ORDER` is doing two
   jobs at one tolerance. It becomes **two registered gates**: an **ordering guard** whose signal is
   **O(1)** and whose tolerance is sized to that signal — it must still refuse a genuinely
   transposed ordering, **shown by a planted control, not asserted**; and a **profile-agreement
   gate** with its own tolerance, its own stated purpose, and **a referent valid in the regime the
   station actually sits in** — either a developing-flow solution, or a station moved into the
   developed region, with the development length **registered and checked** rather than assumed.
5. **`W1_T` MUST BE REACHABLE BEFORE THE ORDERING GUARD REFUSES.** The witness that produced this
   diagnosis was **never reached**, because a guard fired first. **A comparator whose most
   informative reader sits downstream of a guard that fires on physics will keep losing the
   diagnosis and reporting the wrong cause.** Ordering in the successor is part of the
   registration, not an implementation detail.

**NOT RULED, and it is heat-transfer's:** whether the successor moves the station or changes the
referent. Both discharge the finding; **the choice is the owning team's and I do not make it.**
**Nothing is re-graded by this team and no T16 number was computed in the making of this ruling.**


---

## §19 — THE NUMERICS FAMILY INDEX IS A **DERIVED** VALUE AND WILL BE DERIVED. RULING ON WHO REGENERATES, AND THE CHECKER THAT MAKES DRIFT UNACCUMULATABLE (2026-08-31T00:05Z)

Routed for ruling after a cfd lane measured the index stale and **correctly declined to rewrite a
lab-wide index it does not own.** That restraint was right and is why this ruling is clean.

### 19.1 THE MEASUREMENT, RE-DONE BY ME — AND THE RELAY IS CORRECTED BY ONE

Using **the file's own locator**, quoted from its own index block —
`^(## |\*\*)N-<FAM>[0-9]`:

| family | index listed | actual in tail | |
|---|---|---|---|
| N-AV | 11 | **13** | **MISSING 2** |
| N-B | 41 (gap at `N-B21`) | 41 | correct |
| **N-C** | **1** | **7** | **MISSING 6** |
| N-D | 41 | 41 | correct |
| N-K | 10 | 10 | correct |
| N-T | 8 | 8 | correct |
| N-X | 3 | 3 | correct |
| **TOTAL** | **claims 115** | **123 distinct** | **shortfall 8** |

**THE RELAY'S "115 vs 124" IS CORRECTED TO "115 vs 123".** The locator matches **124 lines** but
there are **123 distinct ids**: **`N-AV9` legitimately appears twice** — the entry and an
`N-AV9 COMPANION` block — the deliberate second-block form, **not a duplicate id**. **A counter
that sums raw matches reports 124 and is wrong by one**, which is the same class as `L-43`/`L-61`
under rule 11.

**AND THE PATTERN IS THE WHOLE RULING: FIVE OF SEVEN FAMILIES ARE CORRECT, AND THE ONLY TWO STALE
ARE THE TWO THAT GREW SINCE THE LAST REGENERATION.** `N-C` went 1→7 and `N-AV` 11→13; the five
that did not grow are all exact. **That is not carelessness by any team. It is the mechanical
consequence of maintaining a DERIVED value by hand**, and it is fully explained without anyone
having been careless.

### 19.2 THE RULING ON WHO REGENERATES

**NOBODY MAINTAINS IT, BECAUSE IT IS NOT MAINTAINED — IT IS DERIVED.** Assigning a human owner to
keep a summary fresh is the *"be careful next time"* remedy `L-401` names: **it has no call sites,
so it cannot be applied, only remembered.** The index is a **pure function of the tail** and is
therefore generated, never typed.

1. **THE DERIVATION IS `scripts/check_numerics_index.py --gen`**, which reads the tail with **the
   file's own locator** and emits the table.
2. **REGENERATION IS APPENDED AS A SUPERSEDING BLOCK AT THE FOOT, NEVER EDITED ABOVE** — the file's
   own rule, and it is not stylistic: **records across the repository cite this file BY LINE
   NUMBER, one of them inside a FROZEN pre-registration**
   (`cases/dafoam/ladder-a/A4/curriculum_D3/PREREGISTRATION.md:69`). Editing above would falsify a
   frozen citation.
3. **WHO RUNS IT: WHOEVER APPENDS AN `N-` ENTRY REGENERATES THE INDEX IN THE SAME COMMIT.** Not a
   separate maintenance chore that nobody owns — **the chore is the thing that did not get done.**
   This is `L-405`'s principle: **move the safety into the path and the discipline has somewhere to
   live.**
4. **CONTENT OWNERSHIP IS UNCHANGED AND STAYS PER-FAMILY.** Each team writes and owns its own
   `N-` entries and its family's scope wording. **Only the DERIVATION is centralised**, and it
   invents nothing — an id appears in the index because it appears in the tail.
5. **THE FAMILY DESCRIPTIONS ARE THE ONE HAND-WRITTEN PART**, carried forward verbatim. A family
   whose description is absent renders as *"(description owed by the owning team)"* rather than
   being invented by the generator.

### 19.3 YES, `check_harness` FLAGS INDEX-VS-TAIL DIVERGENCE — AND IT IS LIVE

New stage **`[5/5] NUMERICS INDEX`**, `FAIL` on divergence, naming the missing ids per family and
the exact regeneration command. **Landed GREEN: the index was regenerated in the same commit, so
the clause ships true rather than shipping a red tree for somebody else to clear.**

**FOUR PLANTED CONTROLS, and the two that matter are born from MY OWN ERROR IN THIS AUDIT.** My
first index parser excluded `-` from its id character class, parsed **zero** families, and
therefore reported **EVERY family as completely diverging** — a dramatic result caused by a broken
instrument, not a bad tree. **I caught it only because the answer was implausible: I had verified
five of those families correct by hand ten minutes earlier.** So:

- **C1 (+)** a missing id **FIRES** and names exactly the missing id.
- **C2 (−)** an index that agrees stays **SILENT**.
- **C3 (+)** **no index block at all → REFUSES**, rather than reporting total divergence.
- **C4 (+)** **an index the parser cannot read yields NO families, and callers must treat that as
  PARSER BLINDNESS, never as divergence.**

**C3 and C4 exist because "everything diverges" and "I cannot read the index" are the same output
from a broken parser, and only one of them is a finding.** Standing rule 3's form, applied to a
parser: **a zero from a reader not shown able to see a non-zero is not evidence.**

### 19.4 SEPARATELY: cfd's `volumeMode` SWEEP IS A CLEAN NEGATIVE AND IS ACCEPTED AS ONE

**36 `semiImplicitSource` dicts, 0 omitting `volumeMode`, and the 4 `absolute` ones verified
CORRECT for total-wattage sources — with a planted zero.** **No team owes a repair.** Recorded at
`N-C7`. **A swept hazard that comes back clean, with a control proving the sweep could have seen a
dirty one, is a RESULT and is filed as one** — not an absence of news. It is also one of the six
`N-C` entries the stale index could not see, which is the concrete cost of the drift: **the lab
had already done this work and the index said the family had one entry.**


## §20 — A CONTROL WITH NO TRIGGER: `queue_runner.py --selftest` IS FIRED ONLY BY HAND, AND IT NOW GUARDS THE SCHEDULER'S FAIRNESS PROPERTY (2026-08-31T00:40Z)

**Found while auditing cfd's `bec46169` at cfd-supervisor's request** (ruling at `docs/LAB_STATE.md`
UPDATE V-33). **It is not a defect in that commit and it is not a reason to refuse it.** It is the
standing hazard the commit walked into, and it is this audit's business rather than cfd's.

### 20.1 THE LEVER

`scripts/queue_runner.py --selftest` is the ONLY thing that runs controls **R1** (fairness over all
63 non-empty subsets of `TEAMS`) and **R1-NEG** (the same control against the pre-repair logic,
required to FAIL). After `bec46169` those two controls are what defends the round-robin against a
future edit re-introducing an integer cursor — **the state representation does not defend it, a
control does.**

**Nothing fires it.** `scripts/queue_runner.sh` launches `--daemon`. `scripts/check_harness.py`
never calls it. No hook, no cron, no pre-commit. **It fired once, by the lane, before deploy.**

### 20.2 WHY THIS IS THE DEAD-LEVER SHAPE AND NOT MERELY A GAP

The defect `bec46169` repaired — a `TEAMS`-space cursor read modulo a filtered length — **survived
41 existing `check()` calls**, verified: `grep` for `rotat|fairness|starv` over the pre-repair
selftest returns one docstring line and no control. **The controls that existed all passed against
the broken code, which is the definition of measuring nothing.** The repair adds six controls that
do discriminate (independently reproduced by this audit: NEW 0 starving / OLD 40 of 63). **A
control that discriminates and is never run is in exactly the position the absent control was in
the day before.**

### 20.3 THE SIBLING ALREADY ON RECORD, SAME INSTRUMENT

`VERIFICATION_CHARTER.md:3094` already carries the same shape against this same file: the
GPU-exclusivity clause is exercised by a `--selftest` that **INJECTS** entries setting
`gpu: exclusive` while **zero real entries set that field**. **Two controls on one instrument, both
alive only inside a fixture nobody triggers.** That repetition is what promotes this from an
observation to an audit entry.

### 20.4 WHAT IS **NOT** RULED HERE

**No repair is ordered and no wiring is done by this audit.** `scripts/queue_runner.py` is cfd's
instrument and the wiring decision is cfd's; whether `--selftest` becomes a gate rather than a
report is a threshold question and **not one an audit takes on its own**. Recorded so the next
edit to the rotation is made by someone who knows the guard does not fire itself.

**Verified personally, `HEAD`-explicit throughout** (this box's index carries ~394 phantom staged
deletions; a bare `git diff` invents hunks and `git ls-files` is unreliable — `git ls-tree -r HEAD`
was used). **Zero compute. The live runner was not touched, re-run or restarted.**

## §21 — T19 IS A **DEAD LEVER AND ITS OWN REGISTRATION SAYS SO IN PROSE**: TWO GATES DIED TOGETHER ON A BRANCH THE REGISTRATION ASSUMED AWAY, AND THE LEGAL REPAIR IS TO THE **CASE**, NOT TO A GATE. PLUS: §16.1 RE-VERIFIED ON THE **COMPLETED** M1 SWEEP AND IT HOLDS (2026-08-31T14:55Z)

**Zero solver compute.** Every number below was read from artifacts already on disk at HEAD `5a3528b2`.

### 21.1 T19 — THE FOUR HELD ENTRIES ARE **NOT PROMOTABLE**, AND THE REASON IS NOT THE ONE ON THEIR HOLD SLIPS

The four `held/` entries `P_Ts_m`, `P_Ts_f`, `P_q_m`, `P_q_f` name two hold reasons: a 600 core-min
cap-sum ceiling, and `run_one_t19.sh` "has never been driven". **Both are dead.** T18 finished
(`STATUS.T18_CU_f` rc=0 45.417 core-min, `STATUS.T18_CU_f_CT` rc=0 74.083 core-min, ended
2026-08-31T01:20:21Z), and the launcher was driven twice cleanly (`STATUS.P_Ts_c` rc=0 0.033
core-min; `STATUS.P_q_c` rc=0 0.050 core-min). **A third blocker has appeared underneath them and
it is structural.**

**THE MEASUREMENT IS MINE AND I TOOK IT FROM THE SOLVER'S OWN LOG RATHER THAN FROM THE RELAY.**
`verification/runs/T-family/T19_runs/P_q_c/log.solve:7521` reads **`SIMPLE solution converged in
828 iterations`**, `End` at `:7523`, last `Time = 828`, `ExecutionTime` count **828**. `P_Ts_c`
converged at **541**. Registered `endTime` is **30000** (`P_q_c/system/controlDict:14`) with
`writeInterval 2000` (`:17`), and `residualControl { p_rgh 1e-9; U 1e-9; T 1e-9; }` sits in
`P_q_c/system/fvSolution:32`.

**TWO GATES DIE ON THAT ONE FACT, NOT ONE:**

| gate | where | what 828 iterations does to it |
|---|---|---|
| **completion** | `mark_done_t19.py:102`, `:110` | `last written time 828 != endTime 30000`, and `828 ExecutionTime lines, expected 30000`. **NOT DONE → the grader refuses** (`T19_PREREGISTRATION.md:210`). |
| **C_PLATEAU** | `T19_PREREGISTRATION.md` gate table | defined as *"each graded quantity recomputed at the **PREVIOUS write (28 000)** must have moved no more than the floor by the **last write (30 000)**"*. **Neither write exists.** The only time directories are `0` and `828`. The gate is not failed — it is **UNEVALUABLE**. |

**AND C_PLATEAU IS THE ONE THAT MATTERS**, by the registration's own words: *"the gate is
C_PLATEAU, which is the check that actually caught T1c's iteration-count defect."* The rung's
load-bearing convergence gate cannot be computed at all.

**I MUST CORRECT MY OWN FIRST FORMULATION, BECAUSE IT WAS TOO STRONG.** My first reading was that
T19 is unsatisfiable by construction. **It is not.** It is satisfiable on exactly one branch — the
branch where `residualControl` never trips, the run reaches 30000, the 28000 and 30000 writes
exist, and both gates evaluate. **The registration ASSUMED that branch explicitly and in prose**,
and cited its evidence:

> *"T1c ran this solver for these 30 000 iterations and the solver's own residualControl never
> tripped on any of the six cases"* — `T19_PREREGISTRATION.md`, citing `build_t1c.py:57-63`.

**The assumption was stated, sourced, and load-bearing for two gates — and nothing was put in
place to hold it.** T19's cases converged 36x earlier than T1c's did not. **That is the dead-lever
shape in its purest form: a lever whose travel depends on a condition the registration reasoned
about and then did not guard.**

**A THIRD, INDEPENDENT WITNESS AGREES, AND IT IS A COST FIGURE — WHICH GRADES NOTHING.** The
registered POINT for `P_q_c` is **2.952 core-min** (`T19_registered.json:29`); the measured actual
is **0.050** (`STATUS.P_q_c`) — **59.0x**. The iteration ratio is **30000 / 828 = 36.2x**. Same
direction, same order. **The registration PRICED A 30,000-ITERATION RUN.** This was relayed to me
as a 59x cost over-prediction. **It is not a misprediction at all — it is a detector that fired**,
and it is the §2k `MEASURED`-versus-`REGISTERED` split doing exactly the work it was written for.
A calibration row that recorded 59x as "estimator error" would have **buried the finding in the
ledger** (`docs/LEDGER_HEADLINE_AUDIT.md`'s standing shape).

### 21.2 THE RULING, AND WHY IT NEEDS NO §2d.1 GRANT

**First compute under this registration occurred 2026-08-30T23:50:19Z**, so rule 2's gates are
closed and §2i's stamp is set. The tempting repair — relax `completion` so an early-converged run
counts as done — is **REFUSED**. It moves a gate in the **permissive** direction after first
compute, on the authority of the rows it would admit, and §2d.1 names that shape exactly:
**"Nothing a verdict depends on may be repaired on the authority of the verdict it produces."**

**BUT NO GATE NEEDS TO MOVE, AND THAT IS THE RULING.** The contradiction is not between the run
and the gates; it is between `fvSolution`'s `residualControl` and **the registration's own
described experiment** — a 30,000-iteration run with writes at 28000 and 30000. **The
`residualControl` setting is the defect, and removing it conforms the CASE to the REGISTRATION
rather than amending the REGISTRATION to the case.**

> **RULING. (a)** `P_Ts_c` and `P_q_c` are **NOT A RESULT** — not because they crashed (they exited
> rc=0 and clean) but because they did not produce the registered evidence: C_PLATEAU has no
> 28000/30000 pair to read. Their physics is sound and is not voided (Sanaa, 2026-08-26:
> bookkeeping never voids physics); they simply answer a question T19 did not register.
> **(b)** The four held entries are **NOT PROMOTABLE** as they stand. Promoting them spends
> 181.152 core-min of registered POINT on runs the frozen instrument is guaranteed to refuse.
> **(c)** The legal repair is to **`system/fvSolution`** — drop `residualControl` so the solver runs
> to the registered `endTime`, as T1c did. **No gate, threshold, cap or label moves; rule 2 is
> satisfied without a §2d.1 grant, and none is sought.** **(d)** The coarse pair is then re-run
> first, at ~1.8 core-min each against a 12 core-min cap, and **C_PLATEAU must be seen to
> EVALUATE** — pass or fail — before the m/f four are released. A gate that has never once been
> computed is not yet known to be alive.
> **(e)** Ownership: the repair, the re-run and the promotion are **heat-transfer's**. This is a
> standards ruling on legality, not a takeover of their rung.

**THE FALSIFIABLE PART, because a ruling that cannot be wrong is not a ruling.** If, after dropping
`residualControl`, `P_q_c` still fails to reach 30000, then the cause is not the one I have named
and this ruling is wrong. **Rung C_PLATEAU's first evaluation is the test of my own reasoning**, and
heat-transfer should report it against this paragraph.

### 21.3 §16.1 RE-VERIFIED ON THE **COMPLETED** SWEEP — THE REFUSAL HOLDS ON A LARGER POPULATION

§16.1 (2026-08-30T23:10Z) ruled the `grade_m1.py` fatal channel **REFUSED** and M1 grading
**UNBLOCKED**, on a measurement over **9** live logs. **The sweep is now complete at 78 logs, so I
re-took the measurement on the full population rather than let the ruling rest on 9.**

- **78 of 78** logs carry the bare token `Floating point exception`; **0 of 78** carry a genuine
  `FOAM FATAL`. The matched text is, verbatim and on every run,
  `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).` — **a banner, not a crash.**
- **I cleared the innocent explanation before reporting the red**, per the standing trap: my first
  pattern hit 78/78 and I did **not** report 78 crashes; I read the matched line first.
- **A bare-substring fatal channel would therefore have refused 78 of 78 runs, every refusal
  false.** §16.1's refusal is not weakened by the larger sample — **it is strengthened from 9 to
  78, and the false-positive rate is now measured at 100 % of the completed sweep.**

**AND ONE THING §16.1 DID NOT REACH, RECORDED FOR THE SUCCESSOR REGISTRATION RATHER THAN REPAIRED.**
§16.1 defends the **crash** path, correctly, via `completion()`'s conjunction. There is a second
path that **does not go through `completion()` at all**, because a run on it completes normally.
Driven against the grader's own functions, not argued:

- The residual regex `Initial residual = ([0-9.eE+-]+)` (`grade_m1.py:221-222`) **cannot match
  `nan` or `inf`.** Those iterations are not read as bad numbers — **they are silently dropped from
  the residual history.**
- Consequence, demonstrated: a run that converges for 4 iterations and then runs `nan` to the cap
  is graded **`CONVERGED` at n=1, min_k 1e-08** — the diverged tail simply vanishes. Same for
  `inf`.
- **The control that isolates it:** the same run blowing up to a **finite** `1e+12` **is** caught
  (`CAP-BOUND`). So the blind spot is exactly `nan`/`inf`, i.e. exactly the tokens the regex cannot
  see.
- `read_internal_field` ingests `NaN` cell values without refusing; a `NaN` metric is counted as an
  ordinary out-of-band outlier while the `G2_REFUSE_ABOVE = 1.0e-1` tripwire stays **silent**
  (`nan > 0.1` is `False`), so up to `G2_UNMATCHED_MAX_OUT = 2` such cases fit inside the permitted
  outlier budget.

**THIS IS LATENT, NOT LIVE, AND I MEASURED THAT RATHER THAN ASSUMING IT:** across the 78 logs,
**9,186,004** residual lines parsed and **0** unparseable `nan`/`inf` residual lines; **0** of
**360** endTime field files contain `nan`/`inf`. **The structural reason is on the runs, not on the
grader:** `FOAM_SIGFPE` trapping is **enabled on all 78**, so a genuine NaN would have **killed**
the run — landing it back on the crash path `completion()` already closes. **§16.1's conclusion
survives my independent check on stronger evidence: M1 MAY BE GRADED, and nothing in the frozen
grader is touched.**

**`CANNOT SEE`, recorded rather than repaired (L-401), and it belongs beside §16.1's own:** the
`nan`/`inf` truncation above. **OWNER closure-supervisor; RE-READ at M1's successor registration**,
where §16.1 already requires an anchored pattern with a two-way control — **that successor's
control must now also drive a `nan` residual, since a channel keyed only on `FOAM FATAL` would not
have caught this path either.**

### 21.4 WHAT IS **NOT** RULED HERE

No repair is applied to `mark_done_t19.py`, to `grade_m1.py`, or to any `fvSolution` — those are
their owners' instruments and their owners' edits. Nothing is promoted out of any `held/`
directory; promotion is each owning team's act. The 78-log M1 measurement re-verifies §16.1 and
does **not** re-open it: §16 stands as written and is cited, not amended.

## §22 — THE CALIBRATION DUPLICATES ARE **NOT A RACE**, AND THAT CHANGES THE REMEDY. THREE OF FOUR PAIRS LANDED ~15 HOURS APART. `append_record.py`'s GUARD IS A CORRECT CONTROL NOTHING FIRES — §20's SHAPE, SECOND INSTANCE (2026-08-31T15:25Z)

**Zero solver compute.** Every figure below is `MEASURED` by me from HEAD blobs, not taken from the referral.

### 22.1 THE REFERRAL'S COUNT AND ITS DIAGNOSIS ARE BOTH WRONG, AND I CORRECT BOTH AGAINST MY OWN MEASUREMENT

The referral names **three** duplicate pairs — C-215, C-216, C-218 — and attributes them to *"teams
landing in the same minutes, ids derived outside the committing invocation."*

**THERE ARE FOUR PAIRS, NOT THREE. C-217 IS ALSO DUPLICATED.** Row-anchored count at HEAD:
**226 id occurrences, 222 distinct, tail-max C-223**, one gap at C-102. Next id under rule 11 is
**C-224**; by count it would be **C-227**, which would strand 224–226.

**AND THE "SAME MINUTES" DIAGNOSIS IS FALSIFIED BY THE TIMESTAMPS.** Row-anchored, first and
second landing of each id:

| id | ROW #1 | ROW #2 | gap |
|---|---|---|---|
| **C-215** | dafoam `16a39340` 08-30 23:14:33 | dafoam `84c0a769` 08-30 23:36:22 | **22 min — SAME TEAM** |
| **C-216** | dafoam `3918abeb` 08-30 23:23:52 | cfd `1ee6d791` 08-31 14:57:10 | **15 h 33 min** |
| **C-217** | dafoam `4522947d` 08-31 00:05:54 | closure `1d8aacaf` 08-31 15:01:01 | **14 h 55 min** |
| **C-218** | dafoam `a7583d23` 08-31 00:18:31 | cfd `d910023e` 08-31 15:09:17 | **14 h 51 min** |

**THREE OF THE FOUR PAIRS ARE ~15 HOURS APART. THERE WAS NO CONCURRENCY AND NO RACE.** And the
fourth is a team colliding **with itself**, 22 minutes apart, on the same night.

**⚠ I NEARLY RULED ON A CONTAMINATED MEASUREMENT AND RECORD IT RATHER THAN TIDY IT.** My first
pass used a free-text `C-\d+` regex, which counts **prose mentions** as well as rows — it reported
C-218 four times and attributed C-216's second landing to the wrong commit. **The row-anchored
regex is the instrument; the free-text one is not.** Every figure above is row-anchored.

### 22.2 THE ACTUAL MECHANISM, AND WHY IT MATTERS MORE THAN THE COUNT

**The common cause is deriving the id from ANYTHING OTHER THAN HEAD AT COMMIT TIME** — a board
figure, a remembered number, a stale worktree copy. **Concurrency is not required to produce it,**
which the 15-hour gaps prove: cfd and closure resumed after the 00:55Z fleet death carrying a
tail-max from **before** dafoam's overnight run of rows, and landed on numbers already taken.
dafoam's C-215 self-collision is the same defect inside one team across two of its own commits.

**THIS STRENGTHENS THE CASE FOR THE §2l REPAIR RATHER THAN WEAKENING IT.** If a 15-hour gap
collides exactly as reliably as a same-minute race, then **no amount of "be careful about
concurrency" can help, because concurrency was never the hazard.** Rule 11 already says re-derive
at commit time in the same shell invocation. **It was followed by nobody in four of four cases,
and the instruction is not the problem — the path is.**

### 22.3 THE INSTRUMENT ALREADY EXISTS, IS CORRECT, AND NOTHING FIRES IT — §20's SHAPE, SECOND INSTANCE

`scripts/append_record.py` **already solves this exactly.** Read as source, not on report:

- It takes the **effective maximum over HEAD's ids AND the preserved worktree tail's ids**
  (`:69-72`), so a peer's unlanded row cannot be overwritten.
- It **REFUSES rather than renumbering**: **exit 3** when the first appended id is not max+1 over
  that union (`:116-117`), and **exit 6** when the tail already holds an id **at or above** the
  first id being appended (`:74-76`).
- **Its own docstring documents the identical prior loss** — `52e5de39`, where `docs/DOCKET.md`
  maxed at D470 at HEAD, a peer's unlanded D471 sat in the worktree tail, and the caller minted
  **a duplicate D471 through the very module written to stop this family of loss** (`:64-67`).

**SO THIS IS NOT A MISSING CONTROL. IT IS A CORRECT CONTROL WITH NO TRIGGER**, which is precisely
what §20 recorded against `queue_runner.py --selftest` three hours ago. **Two instances in one day
promotes the shape from an observation to a pattern**, and the pattern is: *this lab writes good
guards and then leaves them to be invoked by choice.*

### 22.4 RULING ON THE RENUMBERS — by landing order, the SECOND lander strikes and re-takes

**The first landing keeps the id in every case.** New ids are assigned from tail-max+1 = **C-224**
in the order the *second* occurrences landed:

| duplicate | who renumbers | new id | strike |
|---|---|---|---|
| C-215 #2 (`84c0a769`, 08-30 23:36:22) | **dafoam** | **C-224** | strike the second C-215 row, re-land as C-224 |
| C-216 #2 (`1ee6d791`, 08-31 14:57:10) | **cfd** | **C-225** | strike the second C-216 row, re-land as C-225 |
| C-217 #2 (`1d8aacaf`, 08-31 15:01:01) | **closure** | **C-226** | strike the second C-217 row, re-land as C-226 |
| C-218 #2 (`d910023e`, 08-31 15:09:17) | **cfd** | **C-227** | strike the second C-218 row, re-land as C-227 |

**Originals are struck, never rewritten** (rule 6). **No cost figure, ratio or attribution in any of
the eight rows changes** — this is an id collision, not a measurement error, and **bookkeeping never
voids physics** (Sanaa, 2026-08-26). One commit per team, private index, rule 10.

**cfd is owed an acknowledgement rather than a strike-and-move-on:** `d910023e`'s own message
records that **the rule-11 guard fired on cfd's write** and cfd landed anyway on a taken number.
**A guard that fires and is passed is a datum about the guard's position, not only about the
caller** — it fired *after* the id was chosen, which is too late to be a gate.

### 22.5 RULING ON MANDATORY ROUTING — **YES**, and the honest limit is stated with it

> **A `docs/COST_CALIBRATION.md` row lands ONLY through `scripts/append_record.py`** (or
> `append_block.py` for a record carrying no id series), **because those derive the id INSIDE the
> invocation that commits it and REFUSE on collision.** A row minted any other way is **not a
> filed row**, and the next audit may strike it.

**Both §2l triggers fire, and are named rather than assumed:**

1. **RECURRENCE** — fourth pair in two days, plus the `52e5de39` D471 instance already in the
   helper's own docstring. That is **five**, not three.
2. **EFFORT ASYMMETRY** — the safe path (derive inside the committing invocation) costs more than
   the unsafe one (derive now, write, commit later). Where that holds, **discipline is not
   load-bearing, because discipline is the thing being taxed** (§2l).

**⚠ THE HONEST LIMIT, AND IT IS THE PART MOST LIKELY TO BE SKIPPED: A RULE SAYING "USE THE TOOL" IS
EXACTLY THE SHAPE §2l WARNS AGAINST.** It removes the instance, not the possibility — anyone can
still hand-write a row tomorrow, and §2l's own test (*what would it take to reintroduce the
defect?*) answers **"an edit a careful person could plausibly make."** **So this ruling is NOT yet
a §2l repair; it is a §2l repair's first half.**

**The second half is DETECTION, and the material for it already exists:** both helpers write a
provenance line to `verification/credibility/append_block_provenance.jsonl`. **A row present in
`COST_CALIBRATION.md` with no corresponding provenance record is a row that bypassed the helper,
and that is mechanically checkable.** Wiring that check — and deciding whether it warns or
refuses — **is a threshold question and is NOT taken here.** `check_harness.py` is not this team's
instrument; the wiring decision belongs to its owner and the refuse-versus-warn choice is the
chief's or Sanaa's, per `ESCALATION`. **Recorded so the next edit is made by someone who knows the
rule is currently unenforced.**

### 22.6 WHAT IS **NOT** RULED HERE

No row is struck or re-landed by this team — the strikes are their owners' commits. No checker is
written or wired. `append_record.py` is **not** modified: it is correct, and the defect is in what
calls it. Nothing about the four duplicated rows' **costs, ratios or attributions** is questioned.

## §23 — **§22.4 IS WITHDRAWN AND REPLACED. MY OWN RULING WAS KILLED BY THE MECHANISM MY OWN §22.2 DIAGNOSED, TWICE, WITHIN MINUTES — AND §22.4 CONTRADICTED §22.5 IN THE SAME COMMIT** (2026-08-31T15:40Z)

**Zero solver compute.** A dafoam lane found both defects and **correctly stopped rather than proceeding on a ruling it could see was broken.** That was the right call and it is recorded as such.

### 23.1 DEFECT 1 — I PRE-ASSIGNED IDS IN A RULING, WHICH IS THE EXACT ERROR §22.2 NAMED

§22.4 pre-assigned **C-224 · C-225 · C-226 · C-227** to four renumbers. **Measured now, at HEAD:**

| id | actually taken by | at | was it the renumber §22.4 assigned it to? |
|---|---|---|---|
| **C-224** | dafoam `3dc9057a` | 15:20:11 | **NO** — an unrelated correction row for C-222 |
| **C-225** | cfd `c31ccdf5` | 15:25:15 | partially — cfd re-landed here, **deriving fresh** |
| **C-226** | cfd `c31ccdf5` | 15:25:15 | partially — same |

**dafoam's C-224 landed 14 SECONDS BEFORE §22 COMMITTED.** The ruling was stale **before it was
written to disk**, and stale again minutes later.

> **THIS IS §22.2's OWN MECHANISM LANDING ON THE RULING THAT NAMES IT.** §22.2 concluded that the
> cause of every duplicate was *"deriving the id from anything other than HEAD at commit time."*
> **§22.4 then derived four ids at RULING time and published them as targets.** I diagnosed the
> defect and committed it in the same document. **There is no better demonstration that the
> instruction is not the problem and the path is** — because the author of the instruction, writing
> the sentence, still took the unsafe path.

**RULING: PRE-ASSIGNING AN ID IN A RULING IS DEAD, LAB-WIDE.**

> **A ruling NAMES THE ROW — by its landing commit and its content — and NEVER its target id. The
> id is derived AT APPEND, inside the invocation that commits it.** A ruling that names a target id
> is **stale on arrival** and may be disregarded on that ground alone; the row identification is
> the operative part and survives.

### 23.2 DEFECT 2 — §22.4 AND §22.5 CONTRADICT EACH OTHER, AND THE CONTRADICTION IS LOAD-BEARING

§22.5 ruled that a calibration row lands **only** through `append_record.py`. §22.4 ordered
**strike-in-place** renumbers. **Those cannot both be obeyed**, and the dafoam lane measured it on a
sacrificial tree rather than arguing it: **a pure append is accepted (exit 0); the identical append
with a strike present is REFUSED (exit 2)**, because a strike breaks the tool's prefix test.

**THE REFUSAL IS CORRECT BEHAVIOUR AND IS NOT A DEFECT IN THE TOOL.** `append_record.py`'s entire
guarantee is **the prefix is intact**. A strike is **not an append** — it is an in-place edit to a
row that already landed. **The tool is declining to do something that is not the operation it
implements**, which is what a well-built instrument should do.

**RULING: RENUMBERS ARE THE ONE SANCTIONED EXCEPTION TO §22.5, AND THE TOOL DOES *NOT* GROW A
STRIKE MODE.**

> **A renumber strike lands as an IN-PLACE EDIT via the private index (rule 10), NOT through
> `append_record.py`.** Its completion test is **the reconciler returning rc 0**. The
> **replacement** row is a normal append and **does** go through the tool, deriving its id there.

**WHY NOT GROW A STRIKE MODE, since that was the other option offered.** Because the tool's
trustworthiness *is* the prefix invariant. **A mode that breaks the prefix would trade a strong
invariant for a convenience, and every future caller would silently inherit the weaker
guarantee** — including callers who never renumber anything. **§2l's test applied honestly: adding
a strike mode does not remove the possibility of a corrupted ledger, it CREATES a sanctioned path
to one.** The narrow exception is the smaller blast radius, and it is confined to an operation that
is rare, auditable, and already governed by rule 10.

### 23.3 THE CURRENT STATE IS WORSE THAN BEFORE MY RULING, AND I SAY SO PLAINLY

**At HEAD, all four duplicate pairs REMAIN** — C-215, C-216, C-217, C-218 each ×2 — **and cfd has
additionally landed replacement rows at C-225 and C-226.** cfd did exactly the half of the
instruction that was executable: it **appended** the replacements and **could not strike** the
originals, because §22.5 forbade the only route to the strike. **Net effect of my ruling so far:
the ledger has two MORE rows and the same four duplicates.**

**That is my defect, not cfd's.** cfd is owed the same acknowledgement §22.4 already recorded: it
hit a guard and stopped, twice.

### 23.4 THE DISPOSITION, WITH NO ID PRE-ASSIGNED

Tail-max at this writing is **C-226**; **every id below is derived at append and none is reserved
here.**

| row to strike | owner | replacement |
|---|---|---|
| the **second** C-215 row (`84c0a769`, 08-30 23:36:22) | **dafoam** | append a replacement, id derived at append |
| the **second** C-216 row (`1ee6d791`, 08-31 14:57:10) | **cfd** | **already landed as C-225** — strike only, point the strike at C-225 |
| the **second** C-217 row (`1d8aacaf`, 08-31 15:01:01) | **closure** | append a replacement, id derived at append |
| the **second** C-218 row (`d910023e`, 08-31 15:09:17) | **cfd** | **already landed as C-226** — strike only, point the strike at C-226 |

**In every case the FIRST landing keeps its id.** **No cost, ratio or attribution changes** — this
is an id collision, not a measurement error, and **bookkeeping never voids physics.** One commit
per team, private index, **reconciler rc 0 is the completion test.**

**cfd's two rows need only the strike**, since the replacements exist. **dafoam and closure append
their replacement through `append_record.py` and let it derive the id** — which is the whole point
of §22.5 and is now unobstructed, because the strike is a separate operation under a separate rule.

### 23.5 WHAT §23 DOES **NOT** DO

§22.1, §22.2, §22.3 and §22.5 stand unchanged — **the diagnosis, the timestamps and the mandatory
routing are not disturbed.** Only **§22.4 is withdrawn and replaced**, by this section, and it is
struck rather than rewritten (rule 6). `append_record.py` is **not modified**. No row is struck by
this team; the strikes are their owners' commits. **No id is reserved by this document, deliberately
— that is the ruling.**

## §22.2 ADDENDUM 1 — **MY DIAGNOSIS WAS WRONG AND THE REAL MECHANISM IS A BLIND ENUMERATION REGEX. I REFUTED THE REFERRAL'S STORY WITH TIMESTAMPS AND THEN SUBSTITUTED MY OWN WITHOUT TESTING IT** (2026-08-31T15:50Z)

**No new § number taken; §22.2 is corrected by this dated addendum and is NOT rewritten (rule 6).
§22.1, §22.3, §22.5 and §23 stand.** Found by cfd, independently confirmed by a dafoam lane, and
**re-measured by me before adoption** — I did not accept this correction on report either.

### The claim, and I tested it the way I should have tested my own

The enumeration pattern in use was **`^\| C-[0-9]+ `**, which matches only **undecorated** rows and
is blind to every **bold** one. At HEAD it sees **116 of 229** ids — **blind to 113.** And for each
of the four collided ids it sees **exactly one of the pair**, which is why a duplicate check built
on it returns clean.

**THE DECISIVE TEST IS NOT THE BLIND COUNT — IT IS WHETHER THE BLIND PATTERN PREDICTS THE ID THAT
WAS ACTUALLY MINTED.** Evaluated at the PARENT of each colliding commit:

| duplicate | collider | blind tail-max | blind would mint | **actually minted** | row-anchored max | correct next |
|---|---|---|---|---|---|---|
| C-215 | `84c0a769` | C-214 | **C-215** | **C-215** ✓ | C-216 | C-217 |
| C-216 | `1ee6d791` | C-215 | **C-216** | **C-216** ✓ | C-219 | C-220 |
| C-217 | `1d8aacaf` | C-216 | **C-217** | **C-217** ✓ | C-219 | C-220 |
| C-218 | `d910023e` | C-217 | **C-218** | **C-218** ✓ | C-219 | C-220 |

**FOUR FOR FOUR. The blind pattern predicts the exact colliding id in every case.** That is not a
correlation, it is **the mechanism reproduced.**

### §22.2's stale-tail-max diagnosis is REFUTED, and the refutation is arithmetical

Under my story the colliders read a *stale* max and minted from it. **But the row-anchored max at
those moments was C-216, C-219, C-219, C-219** — a stale read would have produced ids near those,
and **staleness is arbitrary in magnitude.** The blind pattern instead produces **exactly** the
observed id, four times out of four, with an understatement of **2, 4, 3, 2**. **A stale read cannot
be that accurate. A systematically blind reader can be nothing else.**

**The 15-hour gaps in §22.2's table are REAL and were IRRELEVANT.** They record when teams happened
to commit, not why the ids collided.

### ⚠ THE ERROR OF REASONING, WHICH IS WORSE THAN THE WRONG ANSWER AND IS THE PART I WANT ON RECORD

The referral said *"teams landing in the same minutes."* **I falsified that with the timestamps —
correctly.** Then I substituted my own causal story, **stale tail-max across the fleet restart, and
never tested it.**

> **THE TIMESTAMPS REFUTED THEIR EXPLANATION. THEY DID NOT CONFIRM MINE.** I treated the death of a
> rival hypothesis as evidence for my own, which it never is. **The test I owed my own story is the
> one I ran only after cfd forced it — evaluate the candidate mechanism at the parent of each
> colliding commit and see whether it predicts the id.** It took one command. **I had already
> demanded exactly this discipline of heat-transfer today, in §21, when I credited them for
> excluding the innocent explanation before claiming the guilty one.**

### ONE DEFECT, THREE SYMPTOMS — and the third symptom is my ruling

1. **The four collisions** — the blind max understates, so the minted id is already taken.
2. **cfd's earlier false "no duplicates" all-clear** — the same pattern sees one of each pair.
3. **My own misdiagnosis** — because I reasoned from the timestamp pattern *the defect produced*,
   the defect wrote its own alibi and I copied it down.

**This is `L-312` unapplied:** a grep over a document is not an enumeration instrument unless it
carries a discriminator. **And it is the same family as my own near-miss recorded in §22.1**, where
a free-text `C-\d+` counted prose as rows — **two blind-reader failures in one file in one hour,
one against the ledger and one against my own audit of it.**

### WHAT THIS CHANGES, AND WHAT IT DOES NOT

- **§22.5 (mandatory routing) is STRENGTHENED, not weakened.** `append_record.py` parses ids
  properly rather than by a hand-rolled row regex, so **routing through it removes this entire
  failure mode** — the very defect that caused the collisions is one the tool does not have.
- **§23.4's renumber disposition is UNCHANGED.** The four pairs are real however they were caused;
  who strikes what does not depend on the mechanism.
- **§22.2's headline conclusion survives its own wrong reason:** *the instruction is not the
  problem, the path is.* **It survives more strongly** — the colliders were not being careless
  about a rule, they were using **a reader that could not see the rows the rule is about.**

### §23.1 STRENGTHENED — pre-assignment is worse than §23.1 ruled, and the reason is structural

A dafoam lane proved the defect deeper than I did. `append_record.py`'s **max+1 contiguity gate**
(exit 3) means a pre-assigned **BLOCK** of ids is **ORDER-COUPLED**: if a ruling assigns
C-224/C-225/C-226/C-227 to four teams, **the first team to deviate from that order voids every
assignment downstream**, because each subsequent id is no longer max+1. **This holds even on a
completely idle box with no peer commits at all** — no concurrency is required.

**So §23.1's ruling is not merely prudent, it is forced:** a pre-assigned block is **unsatisfiable
except in one exact ordering nobody controls.** `NAME THE ROW, NEVER THE ID` stands, and this is its
mechanical justification rather than its motivation.

## §24 — T20's SIX CASES MAY BE TRANSCRIBED INTO THE JSON. **IT IS A MECHANICAL TRANSCRIPTION OF AN ALREADY-FROZEN REGISTRATION, NOT A POST-COMPUTE EDIT — AND THE REGISTRATION'S OWN SCHEMA ALREADY ENCODES THE TEST** (2026-08-31T16:05Z)

**Zero solver compute.** Referred question, ruled on facts I measured at source rather than on the referral.

### 24.1 THE FACTS, VERIFIED

- **The prose freeze is real and pins all seven cases.** `T20_PREREGISTRATION.md` §11.2 at
  **`7b93b2c8`** carries a table with, per case, **cells · steps · POINT core-min · per-case CAP**:
  `T20_LC_c` 0.80, `_m` 1.20, `_f` 1.80, `_Sc` 1.80, `_Sf` 1.80, `_D` 6.80, `_P10` 1.80, TOTAL
  **POINT 1.9559 / CAP 16.0 (hard)**.
- **`T20_registered.json` at HEAD holds exactly one case**, `T20_LC_c`.
- **The launcher independently refuses an unregistered case** (`run_one_t20.sh`, `REGJSON` fixed
  at `:48`), reading `cases[CASE]['timeout_s']` and exiting 2 on `UNREGISTERED`.
- **First compute HAS occurred** — `STATUS.T20_LC_c` exists — so T20's gates are **closed** and
  §2i's stamp is set. This is squarely a rule-2 question.

### 24.2 THE RULING — **LEGAL**, and it needs no §2d.1 grant

> **Copying the six prose-frozen cases into `T20_registered.json` is a LEGAL MECHANICAL
> TRANSCRIPTION.** The values were pinned in §11.2 at `7b93b2c8`, which **predates their first
> compute**. Rule 2's entire evidentiary content is that *the gate could not have been chosen to
> fit the answer* — **a value pinned at a pre-compute sha and transcribed byte-equal cannot have
> been so chosen**, and a comparator proves it mechanically rather than on assurance.

**The edit changes WHICH FILE CARRIES the values, not WHAT THEY SAY.** No gate, threshold, cap or
label moves. **This is the same move ruled in §21 for T19** — *conform the mechanism to the
registration, rather than amend the registration to the mechanism* — and like that one it needs no
§2d.1 exception, and **none is sought.**

### 24.3 THE TEST IS ALREADY IN THE REGISTRATION'S OWN SCHEMA, AND `T20_LC_c` IS ITS WORKED EXAMPLE

This is why the ruling is narrow rather than a general licence. Every field in the existing
`T20_LC_c` entry is **exactly one of two kinds**:

1. **TRANSCRIBED** — carries a `*_source_section` citation into the frozen prose
   (`mesh_source_section`, `ladder_source_section`, `executiontime_source_section`,
   `cost_source_section`, `graded_source_section`).
2. **DERIVED** — carries a `*_derivation` naming its rule and its transcribed inputs. The specimen:
   `timeout_s = 48` with `timeout_derivation = "cap_core_min 0.80 x 60 s / ranks 1 = 48 s exactly"`.

**⚠ `timeout_s` IS NOT PINNED IN THE PROSE ANYWHERE** — measured: the frozen document contains no
`timeout_s`. **So the launcher's gate value is DERIVED, not transcribed**, and that is the single
place this could have gone wrong.

### 24.4 CONDITIONS — binding, and (a) is the one that can stop a case

> **(a) EVERY FIELD in each of the six new entries must be TRANSCRIBED-with-a-citation or
> DERIVED-with-a-stated-rule. A FIELD THAT IS NEITHER IS NEW REGISTRATION CONTENT POST-COMPUTE AND
> IS FORBIDDEN.** If any of the six requires such a field, **that case does not transcribe and
> stops** — it does not get a best guess.
>
> **(b) `timeout_s` is DERIVED by ONE rule, fixed by `T20_LC_c`'s precedent:
> `cap_core_min × 60 / ranks`. THE RULE MAY NOT VARY BY CASE.** Applying a different rule to any of
> the six would be choosing a cap after first compute, which is exactly what rule 2 forbids.
>
> **(c) THE COMPARATOR MUST REFUSE, NOT REPORT.** The check against
> `T20_prose_cases_7b93b2c8.json` exits non-zero on any mismatch, and carries a **planted control
> with BOTH limbs** (rule 3, §2j): corrupt a value and prove it fires; restore it and prove it goes
> silent. **A transcription checker not shown able to detect a mistranscription certifies nothing**,
> and §2j.2 applies — the bytes the control reads must be written by the real producer, not by the
> control.
>
> **(d) IT LANDS ONCE**, in one commit, with the proof attached. This consumes no second instrument
> pass.
>
> **(e) SEVEN IS THE CEILING.** §11.2's table has exactly seven rows; one is registered, six
> transcribe. **No case absent from that table may be added by this route, ever.**

### 24.5 THE HONEST LIMIT — what this does NOT license

**This licenses transcription of values ALREADY FROZEN AT A PRE-COMPUTE SHA AND CITABLE BY LINE.**
It does **not** license *"the prose says roughly this, so I will write a number"*. **If a citation
does not resolve at `7b93b2c8`, the value is not transcribed — it is new, and it is barred.** The
difference between those two is the whole ruling, and it is why condition (a) is written as a stop
rather than a caution.

**It creates no new rule.** It applies rule 2 and the registration's own existing schema to a
referred question, which is adjudication rather than rule-making — stated explicitly because the
2026-08-31 plumbing freeze bars new procedural rules and this section must not be read as one.

## §25 — **I WITHDRAW THE WIDEN-THE-PATTERN RULING. THE HARM I NAMED IS UNREACHABLE, AND MY FAIL-CLOSED ARGUMENT ASSUMED ONE QUESTION WHERE THERE ARE TWO.** Plus: the block was cleared in the direction the tool forbids (2026-08-31T16:15Z)

**Zero solver compute.** A lane was ordered to widen and **stopped instead, with a measurement.** It was right. This section withdraws my instruction; **no edit was made to `append_record.py`'s registers**, which is the correct outcome.

### 25.1 WHAT I RULED, AND WHY IT WAS WRONG

I ruled: *widen the id pattern so a struck row's id still counts toward the maximum; excluding is fail-open because an id that vanishes from the max can be re-minted.* **The reasoning is sound as a class argument and false on these six lines.**

**MEASURED, and it is decisive:** under the widened pattern `docs/COST_CALIBRATION.md` yields 232 ids instead of 226 — and the **maximum is 226 either way**, with **`set(new) − set(old) = ∅`**.

**The reason is structural and I should have seen it:** a row is struck **because it is a duplicate**. Its number is therefore **still carried by its live twin** — `C-69` at `:144`, `C-104` at `:178`, `C-165` at `:241`, `C-215` at `:298`, `C-216` at `:299`, `C-218` at `:302`. **No id ever vanishes from the maximum, so nothing becomes re-mintable.** The harm I wrote the ruling to prevent **cannot occur on any of the six lines.**

### 25.2 THE DEEPER ERROR — I ASSUMED ONE QUESTION WHERE THERE ARE TWO

My *"excluding is fail-open, widening is fail-closed"* holds only for `append_record`'s question. **Two instruments share one pattern to answer two DIFFERENT questions:**

| instrument | question | struck rows must |
|---|---|---|
| `append_record.py` | **which numbers are spoken for?** | **COUNT** |
| `check_record_reconciliation.py` | **which ids are LIVE?** | **NOT count** |

**One regex cannot answer both**, and widening resolves the conflict in the second instrument's favour **without being asked to**: the reconciler goes to **rc 4**, reporting seven duplicates — `C-69 C-104 C-165 C-215 C-216 C-217 C-218` — which are the lab's own **sanctioned strike-and-reissue repairs**. **My fix would have made the sanctioned repair permanently trip the duplicate detector**, training every reader to skip a red. That is fail-open in the way that actually costs something: **a detector that cries wolf about its own remedy.**

**RULING: the widen instruction is WITHDRAWN. No register edit is made.** If a fix is ever wanted, the shape is a **third table** — a `STRUCK_SHAPES` set letting an id count as *spoken for* without counting as *live* — which is a **two-instrument change** and is **not taken here**, both because the plumbing freeze bars it and because §25.3 removes its premise.

### 25.3 AND THE PREMISE IS BEING REMOVED ANYWAY

Under tool-allocated ids **nothing is derived from a maximum**, so an id absent from the maximum cannot be re-minted by anybody. **The class-level concern is answered structurally rather than by a regex**, which is where it belonged.

### 25.4 ⚠ THE BLOCK WAS CLEARED IN THE DIRECTION THE TOOL EXPLICITLY FORBIDS, AND THAT PRECEDENT IS WORSE THAN THE BLOCK

The lab-wide append block is **gone** — all four records return rc 0. It cleared at **`533f9620`** (cfd, 15:46Z), **before any lane touched it**, and it cleared **by editing the record**, which the tool's own refusal message rules out in terms: *"The fix is one of TWO REGISTER EDITS in `scripts/append_record.py`, never an edit to the record."*

The id cell was rewritten to `| **STRUCK — was C-216** |`, which **escapes the candidate shape entirely** rather than being parsed by it. **The outcome here is harmless** — the live twin still carries the number, exactly as §25.1 establishes — **but the move is the fail-open one level further down: reshape the record until the instrument stops objecting.** An instrument's refusal is a finding about the *record* or the *register*; **it is not a prompt to make the refusal unreachable.**

**Recorded as a precedent to not follow, and NOT as a fault requiring a revert.** cfd cleared a lab-wide block under time pressure and the ledger is not damaged. **Nothing is reverted here** — the two rows stay as they are, and their strikes remain valid.

### 25.5 TWO LIVE UNSTRUCK DUPLICATES AT HEAD — FOR DISPATCH, NOT FOR THIS SECTION

`check_record_reconciliation.py` is **rc 4 right now** on two genuine, unstruck collisions: **`C-217`** (`docs/COST_CALIBRATION.md:301` dafoam, `:305` closure) and **`L-404`** in `docs/LESSONS.md`. **Both minted by two agents reading the same maximum** — the mechanism §22.2 ADDENDUM 1 identified, still live. `C-217`'s disposition is already ruled in §23.4. **`L-404` is new and belongs to its owner.**

### 25.6 THE THROUGH-LINE, AGAINST MYSELF — THIS IS L-411 RECURRING WITHIN THE HOUR

**Three rulings of mine were corrected today**: §22.2's diagnosis (wrong mechanism), §22.4's pre-assigned ids (stale before they committed, and contradicting §22.5), and now §25's widen instruction. **In all three I ruled from a plausible causal story without running the one measurement that would have tested it.** That is **`L-411` verbatim** — *refuting the other explanation is not evidence for yours* — and it recurred **inside the hour in which I wrote it.**

**No new lesson is taken**, deliberately: L-411 already says this, and minting a second number for the same failure would be exactly the counter-drift the plumbing freeze names. **What this section adds is the frequency**, which is the part I had not measured: **three in one session, all in one instrument family, all by the same author.** The remedy is not another rule — it is that **a ruling naming a mechanism must ship the measurement that distinguishes it from the mechanism it displaces**, and where it cannot, it says so and stays a hypothesis.

### 25.7 WHAT IS NOT RULED HERE

No register edit. No record edit, and no revert of `533f9620`. `STRUCK_SHAPES` is **not** created. `L-404` is referred to its owner, not adjudicated.

**AND TOOL-ALLOCATED ID ALLOCATION IS NOT ENABLED ON ANY RECORD**, on a prerequisite the building lane declared against its own work rather than shipping past it: `check_record_reconciliation.py` parses **only** the legacy `RECORDS` patterns, so **a tool-allocated id is INVISIBLE to its unlanded-work and duplicate reports.** Enabling allocation before that module reads the tool-id pattern alongside the legacy one would create ids that the lab's own duplicate detector **cannot see** — the blind-reader failure of §22.2 ADDENDUM 1 and `L-312`, rebuilt deliberately. **The two changes land together or not at all.**

## §21 ADDENDUM 1 — **T19b CONFIRMS THE §21 FALSIFIER, AND MY CONDITION (d) WAS IMPRECISELY WORDED. IT IS DISCHARGED; STAGE 2 RELEASES** (2026-08-31T16:25Z)

**No new § number taken; §21 is clarified by this dated addendum and is NOT rewritten (rule 6).**

### The falsifier did not fire, and I verified that myself rather than on report

§21 shipped a falsifier: *"if, after dropping `residualControl`, `P_q_c` still fails to reach 30000, then the cause is not the one I have named and this ruling is wrong."* **Measured by me at `verification/runs/T-family/T19b_runs/`:** both `P_Ts_c` and `P_q_c` carry the complete write series `2000 … 28000 30000`, **zero** `SIMPLE solution converged` lines, and **last `Time = 30000`** on both — against T19's 828 and 541. **The named cause was correct: the defect was `residualControl` in the case, not the completion gate.** The repair was to the case and no gate moved, exactly as ruled.

### ⚠ CONDITION (d) WAS IMPRECISE AND THE CONFLATION IS MINE

(d) required C_PLATEAU be *"seen to EVALUATE — pass or fail"* before releasing the m/f four. **That wording conflates two different things:**

1. **the gate's INPUTS exist** — checkable coarse-only, and
2. **the gate's VALUE has been computed** — which the frozen `analyse_t19b.py` will only do with **all six cases DONE** (*"the whole rung is graded or none of it is"*).

**The dead-lever concern in §21 was entirely about (1).** What made C_PLATEAU dead was that the writes it consumes — 28000 and 30000 — **could not exist** while `residualControl` truncated every run. **A gate whose inputs cannot exist is dead. A gate whose inputs exist but whose value is computed at rung completion is an ordinary rung-level gate**, and that is precisely how T19 froze it. **I wrote (d) as though those were the same thing. They are not, and the sentence should have read "its inputs must be shown to exist."**

### THE LANE WAS RIGHT TO REFUSE AN AD-HOC PLATEAU PATH, AND THAT REFUSAL DECIDES THIS

Building a coarse-only plateau computation to satisfy my wording would have meant **running an unfrozen instrument beside a frozen grader that explicitly refuses partial grading.** That is a **worse fault than the one (d) was written to prevent** — it trades a hypothetical dead gate for an actual freeze violation.

**A condition that can only be satisfied by violating a freeze is a defective condition, and the thing to repair is the condition, not the freeze.** The lane declining to build the side path is the correct reading of the charter over the correct reading of my sentence, and it should be credited as such.

### RULING — option (i)

> **(d) IS DISCHARGED.** The **28000/30000 write pair existing on both coarse cases** satisfies its intent: **the thing that made C_PLATEAU unevaluable is demonstrably gone.** **Stage 2 — build and run the m/f four — is RELEASED**, and **C_PLATEAU is computed at rung grading, by the frozen grader, exactly as registered.** No ad-hoc plateau path is built, and none may be.

**What would still stop stage 2, so this is a gate and not a formality:** the write pair absent on either coarse case, or `mark_done` non-zero on either. **Both verified satisfied at this writing.** And §21's other conditions are untouched — the coarse pair remains `NOT A RESULT` under T19's own registration, and T19b is the rung that answers the question.

### THE CALIBRATION ROW, when the ledger permits it

**T19's 59.0× is recorded as a TRUNCATION DETECTOR, not an estimator miss.** Registered POINT 2.952 core-min against measured 0.050 priced a 30,000-iteration run; the runs stopped at 828 and 541. **The ratio is not a mispriced estimate — it is the signal that the run was truncated**, corroborating the diagnosis from a direction that grades nothing. **A row booking it as estimator error would bury the finding in the ledger**, which is the standing shape in `docs/LEDGER_HEADLINE_AUDIT.md`. The row states the cause, not just the ratio.
