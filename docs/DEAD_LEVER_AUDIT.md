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

**Count: 14 lever/conclusion pairs — 9 ACTIVE-PROVEN, 2 ACTIVE-UNPROVEN (no log
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

**24 lever/conclusion pairs proven active from a runtime log by this pass**, all
line-quoted above: 14 hump-adjoint (§3.1), 10 hump-primal (the QCR pair with its
`Ccr1` discriminator, the five a1 points, `limitVelocity` active-and-inert in
all four W1 legs, `printCoeffs`, and the disclosed `AugmentedkOmegaSST`
substitution). The single most load-bearing chain in the hump corpus — the
five-point a1 ladder — is proven at every point.

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
