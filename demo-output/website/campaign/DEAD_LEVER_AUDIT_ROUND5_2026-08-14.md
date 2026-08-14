# Dead-lever audit — ROUND 5, 2026-08-14

Katie's line: *"Dead-lever audit continues — hump-adjoint conclusions explicitly
included; found-dead reopens."*

**Compute: zero core-minutes.** No solve was launched and none was authorised.
Every measurement below came from archived logs, from the ledger, or from a
mutation test on the SDK that runs in under a second.

**Repo at `94307129`**, worktree dirty (concurrent agents). Counts taken
2026-08-14 20:40–21:10 UTC. A quoted figure is a snapshot and carries its
anchor (L-79); re-derive rather than quote.

**Tooling frame, stated once (L-75).** The shell's `grep` here execs
`ugrep --ignore-files` and honours `.gitignore`, so gitignored run archives are
invisible to it. Every count below was taken with `git grep` (tracked frame) or
`/usr/bin/grep` (filesystem frame), never the shell's `grep`. Where a count
could not reach something, §7 says so.

---

## 0. The repository's own definition of a dead lever

Taken from the source rather than assumed. Three prior rounds state the same
operating rule verbatim, and it is `LESSONS.md` **L-40**:

> THE SWITCH YOU SET IS NOT THE SWITCH THAT RAN (`LESSONS.md` L-40; charter §9
> `levers_verified_active`): **a solver option cited by a conclusion's reasoning
> is evidence only when the archived RUNTIME LOG proves it was active —
> presence in an input dictionary proves nothing.**

The classification legend is `DEAD_LEVER_AUDIT_2026-08-08.md:176-179`:
**V = VERIFIED** (log line proves activity), **U = UNVERIFIABLE-FROM-LOGS**,
**FD = FOUND-DEAD**. FOUND-DEAD is reserved, by that round's own words, for the
case where *"the archive positively proved a cited switch was dead code"*.

Three refinements were added by Round 3 and are binding here:

1. **L-43 corollary** — a found-dead verdict is a claim about IMPLEMENTATION,
   and implementation hides in `.H` includes. A false found-dead is not a
   missing finding, it is a manufactured one, and it propagates.
2. **A negative claim without its search space is not a finding.**
3. The **LATENT** class — echoed, structurally inert, but no conclusion leans
   on it — is distinct from FOUND-DEAD.

**Correction to the framing in the dispatch.** The dispatch offered "a knob
wired to nothing, a parameter the code reads and never uses, a gate whose
condition can never be false, a configuration option with no call site." That
is a superset of the repository's definition and it is the right superset —
Round 3 explicitly extended the term from solver options to **instruments and
rules that cannot fire** (*"a rule that cannot fire is a rule the lab believes
it has and does not"*). Both senses are used below and each finding says which.

---

## 1. Which round this is, and what the previous rounds concluded

| round | record | scope | found-dead |
|---|---|---|---|
| **R1** | `campaign/DEAD_LEVER_AUDIT_2026-08-08.md` (`946e4a26`) | Katie's AUDIT ORDER 1 — `campaign/`, `dafoam/`, 3 status files | **4** (FD-1 `transonicPCOption 2`; FD-2 SIMPLEC; FD-3 `decomposeParDict`; FD-4 `DAFOAM_SUBPC_TYPE` fallthrough) |
| **R2** | `campaign/DEAD_LEVER_AUDIT_BATCH_2026-08-10.md` | batch / mega-batch family | **0**, plus two named near-misses N-1, N-2 |
| **R3** | `campaign/INSTRUMENT_INTEGRITY_2026-08-11.md` §1 | fleet-wide C1 (A/B/C arms) | **6** — D1 (S6/S8), D2 (`check_wall_time`), D4 (`trapFpe` universal), FD-1 (DAFoam `printInfo`), **D3 and D5 never named** |
| **R4** | `docs/DEAD_LEVER_AUDIT.md` (`81b40251`, docket B7) | the hump, primal and adjoint | **0 on the hump**; 1 INACTIVE off it (I-1), 1 headline ACTIVE-UNPROVEN (U-1 `jacMatReOrdering` at `rcm`) |

**This is Round 5.** Its brief is the one thing the first four did not do:
R1–R4 each classified levers and then moved on, and a lever found dead once and
left alone leaves its downstream claims standing. Round 5 re-verifies every
prior found-dead and then enumerates what still leans on it.

R1's own summary is worth restating because it survived contact: *"no NEW
conclusion-reopening dead lever was found anywhere in the archive."* Round 5
did not overturn that. What Round 5 overturned is something else — a
found-dead-adjacent verdict that was itself wrong (§3).

---

## 2. FOUND-DEAD REOPENED — every prior verdict re-tested

| prior verdict | round | re-verified 2026-08-14 | downstream claims still standing |
|---|---|---|---|
| FD-1 `transonicPCOption: 2` dead for `DARhoSimpleCFoam` | R1 | **STILL DEAD** (confirmed in-container at R1's addendum; not re-openable from this host) | **NONE — the owed annotations were applied.** `R5_ADJOINT_CONDITIONING.md:257`, `ADJOINT_MEMORY_ENVELOPE.md:611` and `PROOF.md:2642` each carry the retroactive note R1 said was owed. **Closes clean.** |
| FD-2 SIMPLEC `consistent yes` | R1 | **REFUTED, and correctly** — R1's own addendum retracted it; A4's cause claim retracted at `7ca80f8d` | none; the retraction travelled |
| FD-3 `decomposeParDict` edits are a no-op | R1 | still a no-op; standing practice reads the `Decomposition method` line back | none — no conclusion was ever shipped on the dead edit |
| FD-4 `DAFOAM_SUBPC_TYPE` non-`lu` fallthrough | R1 | hazard class, unchanged | none — every conclusion-bearing sub-LU run carries the banner plus a negative control |
| **N-1 Ahmed refinement promotion never fired** | R2 | **STILL NEVER FIRED** — §4 | **YES — `F10_YPLUS_FIX.md` §4** |
| **D1 — S6 / S8 unreachable in production** | R3 | **SPLIT: S6 REPAIRED, S8 STILL DEAD** — §5, mutation-proven | **YES — one ladder row** |
| D2 `check_wall_time` has no production caller | R3 | **STILL DEAD** — only callers are `sdk/tests/test_head_engineer.py:189,200,215,224`; `git grep` over the tracked frame returns no other | **NONE.** `MONITOR_STANDARD.md:1028-1035` already records it UNREACHABLE and records S9 firing by the other route (`wall_time_record_field`). Correctly recorded; **closes clean** |
| D4 `trapFpe` universal is false | R3 | not re-measured this round (§7) | R3 named two; unchanged |
| FD-1(R3) DAFoam `printInfo` prints requested, not effective | R3 | stands | none — pre-registered around before the runs |
| **D3 and D5** | R3 | **CANNOT BE RE-VERIFIED — THEY WERE NEVER NAMED** | **unknown, and that is the finding** — §6 |
| U-1 `jacMatReOrdering` has no activity proof at `rcm` | R4 | **FALSIFIED IN ITS BROAD FORM** — §3 | **YES, and in the opposite direction from the one filed** |

---

## 3. THE HUMP-ADJOINT VERDICT — and a correction that runs the other way

Katie named the hump adjoint conclusions explicitly. R4 worked through 14
lever/conclusion pairs and returned **zero found-dead on the hump**. Round 5
did not re-run that census and does not dispute it. Round 5 went after the one
hump-adjoint lever R4 left unresolved, because that is the lever the hump's
load-bearing conclusion rests on.

### 3.1 What R4 and D40 claimed

R4's headline finding U-1: *"`jacMatReOrdering` has no activity proof anywhere
in this archive when set to `rcm`."* Frame L, 1,635 `*.log` files: **386** logs
print the requested `Mat ReOrdering:`, **257** request `rcm`, **8** carry a
`-ksp_view` `matrix ordering:` readback, and the intersection of the last two
is **0**.

Docket **D40** carried that into a specific charge against a published
root-cause document: `ROOTCAUSE_getRotationMatrix3d.md` §4.7 tests
pre-registered prediction **P6** — *"adjoint matrix reordering (`rcm` vs
`natural`) must not move the result at all"* — reports 207.04% vs 207.05% at
idx8, and concludes *"Reordering is not a factor."* D40's verdict:

> P6's null is therefore exactly what an inert `rcm` would produce and the
> check does not discriminate.

D40's prescribed remedy: *"strike P6's verdict in place … and do not carry it
into any upstream draft."*

### 3.2 D40's evidence, independently re-verified — it holds

Re-measured 2026-08-14 with `/usr/bin/grep`, filesystem frame:

| log | `matrix ordering` | `KSP Object` | `Mat ReOrdering` |
|---|---|---|---|
| `W5-rotation-branch/D5a_pl_real_rotON_RCM.log` | **0** | 0 | 1 |
| `W5-rotation-branch/D5b_pl_real_rotOFF_RCM.log` | **0** | 0 | 1 |
| `W5-rotation-branch/D1a_pl_real_rot_ON.log` | **0** | 0 | 1 |
| positive control `W4-adjoint-pc-unblock/control_rcm.log` | **1**, at `:12` `matrix ordering: rcm` | — | — |

Every number D40 published is reproduced exactly. The readback is genuinely
absent and the instrument genuinely finds one when it exists.

### 3.3 …and the conclusion drawn from it is nevertheless FALSE

D40 counted the readback and stopped. Six lines below the line it read, the
same four logs carry the answer.

**The P6 arms, read out of their own logs:**

| arm | line 417 echo | iteration-0 KSP residual | converged in | final residual |
|---|---|---|---|---|
| `D1a_pl_real_rot_ON.log` | `jacMatReOrdering natural;` | `1.243721539281e+01` | **86** | `1.084852511275e-04` |
| `D1b_pl_real_rot_OFF.log` | `jacMatReOrdering natural;` | `1.243721539281e+01` | **86** | `1.084852511275e-04` |
| `D5a_pl_real_rotON_RCM.log` | `jacMatReOrdering rcm;` | `1.243721539281e+01` | **79** | `1.242231735482e-04` |
| `D5b_pl_real_rotOFF_RCM.log` | `jacMatReOrdering rcm;` | `1.243721539281e+01` | **79** | `1.242231735482e-04` |

All four reach `PetscConvergedReason: 2`.

**An inert lever cannot do this.** Flipping the key moved the adjoint GMRES
from 86 iterations to 79 — an 8.1% change in the Krylov count — while the
iteration-0 residual stayed **bit-identical to 13 significant figures**. Since
the iteration-0 residual is `‖b‖` and `b = dF/dW` depends on the primal state
and not on the preconditioner, that bit-identity proves the four runs share a
primal state and an RHS. The only thing left that can change the iteration
count is the preconditioner, and the only configuration difference is the
ordering.

**Single-change, verified rather than assumed** (the R-1 discipline: R4 caught
S1 rung 4 published as a one-change arm having moved three levers). A full diff
of `D1a` against `D5a` over lines 1–830 — the entire pre-solve region — returns
**86 differing lines, of which exactly one is substantive**:

```
417c417
<         jacMatReOrdering natural;
---
>         jacMatReOrdering rcm;
```

Every other difference is the container hostname (`7c570e4eed1b` vs
`3483f3dcf5c7`), the wall clock, and MPI buffer-attach message ordering.

**Run-to-run nondeterminism is excluded by the design of the set.** The two
`natural` runs agree with each other to all 13 digits; the two `rcm` runs agree
with each other to all 13 digits; the two groups differ. Ordering determines
the iteration count and the rotation setting does not touch it. Four logs, two
orderings, exact replication within each.

### 3.4 What this means, stated at exactly its real strength

- **`jacMatReOrdering` is ACTIVE — proven by behaviour, in a matched
  single-change pair.** This is L-50's standard, the one the lab adopted after
  the SIMPLEC refutation: a correction must not travel on the evidence class of
  the thing it corrects. D40 reasoned from a source-and-grep absence; this
  refutation is a measurement.
- **U-1's broad form is falsified.** "No activity proof anywhere in this
  archive when set to `rcm`" is not true. The proof was inside R4's own frame L
  the whole time.
- **U-1's narrow form survives, and Round 5 does not touch it.** The
  behavioural discrimination proves the key reaches the preconditioner and
  changes it. It does **not** prove the permutation produced is specifically
  reverse-Cuthill-McKee. Only the `-ksp_view` `matrix ordering:` readback
  settles that, and it is still absent from all 257 archived `rcm` runs.
- **P6 HELD, and now for a better reason than it was originally given.** The
  lever was live, it demonstrably moved the linear solve, and the `warpDeriv`
  error did not follow it — 207.04% vs 207.05%. That is a *discriminating*
  null, not a vacuous one. D40 had it exactly backwards.
- **D40's prescribed remedy must not be executed.** Striking P6 would have
  written a false correction onto a published root-cause document and into an
  upstream-headed draft. This is L-43's second corollary arriving a third time:
  a false found-dead is a manufactured finding, and this one was three days
  from propagating into an upstream filing.
- **The priced compute request M-A is now half-superseded for free.** R4 priced
  ~8 core-min to answer *"is the printInfo ordering line faithful, and does the
  lever act."* The archive already answers the second half at zero cost. Only
  the first half — does `rcm` produce RCM specifically — still needs the
  readback. **No compute is requested by this round.**

### 3.5 Why the instrument missed it — L-84, precisely

R4 and D40 both ran a positive control and both passed it: the grep for
`matrix ordering:` fires on `control_rcm.log`. That control proved the
instrument **can** fire. It did not prove that the thing it looked for was the
only evidence available, and it was not. The readback was absent; the *effect*
was present, printed, and archived, in the same files.

*A positive control proves an instrument can fire — not that it reaches, not
where it looked, and not that what it looked for was the only evidence there
was.*

---

## 4. N-1 REOPENED — the Ahmed refinement promotion, still never fired

R2 named this *"the closest thing in the family to a set-but-never-ran lever,
and the one to watch."* Re-measured 2026-08-14 against
`demo-output/website/mega-batch/ledger.jsonl` (**208,194 rows**):

| measurement | 2026-08-10 | 2026-08-14 |
|---|---|---|
| `simplefoam-ahmed-3d-viscous` ledger rows | 52 | **52** |
| distinct `cells` on those rows | {45760, 45813} | **{45760, 45813}** — 25 and 10 respectively on the rows carrying the key |
| rows carrying `metrics.mesh_refinement` | 0 of 52 | **0 of 52** |
| last ahmed row timestamp | 2026-07-29T11:16:13Z | **2026-07-29T11:16:13Z** |

**Positive control for that zero (L-84).** `mesh_refinement` is not a token the
instrument cannot see: it appears **69,288** times in the same file, e.g. row
index 3, `"solver": "openfoam-cylinder"`, `"design": {… "mesh_refinement":
1.511 …}`. The reader finds the key when it is present; its absence on all 52
ahmed rows is a fact about those rows.

**Verdict: NOT DEAD, NEVER FIRED.** `_ahmed_refinement_for_reynolds` at
`sdk/workflows/mega_batch.py:544` is live wired code, called at `:594` and
consumed at `:601-602`, and its condition `reynolds >= 2.8e6` is reachable
inside the declared design space `[1.5e6, 4.0e6]`. Round 5 declines to
manufacture a found-dead here, exactly as R2 did.

**Downstream claim, and it is load-bearing.** `mega-batch/F10_YPLUS_FIX.md`
publishes an **AFTER** table of four measurements presented as the deployed
fix's results, of which the two "promoted" rows are the only evidence the
promotion lever ever produced anything:

| row | index | refinement | cells | y+ avg |
|---|---|---|---|---|
| threshold | 3215 | 3 (promoted) | 79,439 | 334.43 |
| high | 239 | 3 (promoted) | 79,439 | **463.89** |

The document names the second of these *"the load-bearing measurement."*
Neither index has a surviving ledger row, a surviving case directory, or a
surviving log. Struck in §8.

---

## 5. D1 REOPENED — S6 was repaired, S8 was left, and S8 is MUTATION-PROVEN DEAD

R3's D1 found both S6 (residual stall) and S8 (Courant excursion) unreachable
in production: `HeadEngineer` built `LogMonitor(novel=novel, on_anomaly=...)`
and there was no parameter by which either gate could be supplied.

**S6 was repaired.** `head_engineer.py:1129` `arm_residual_gate()` reads the
staged case's own `system/fvSolution`, excludes the sentinel class by
construction, and sets `self.monitor.residual_target = target` at `:1193`. It
is called from staging at `:1127`, so every case passes through it. The reach
table at `MONITOR_STANDARD.md:1028` was updated to match. That half of D1 is
genuinely closed.

**S8 was not.** `courant_limit` is accepted at `head_engineer.py:221`, stored at
`:230`, and gates the rule at `:619` (`if self.courant_limit is None: return`).
`git grep` over the tracked frame returns it in exactly three places: the
definition, the gate, and `sdk/tests/test_head_engineer.py:148,163`. **There is
no arming method, and no production construction site supplies it.** The only
production site is `head_engineer.py:1030`, which passes `novel` and
`on_anomaly` and nothing else.

### 5.1 Mutation proof — not a code read

`__pycache__` cleared first (the stale-bytecode trap inverts mutation tests).
Two arms, identical input, one lever:

```
peak Courant fed: 49.48 against a case limit of 1.5

ARM A  production shape   LogMonitor(novel=True, on_anomaly=...)
   anomalies: 0  []
   courant-excursion: 0

ARM B  positive control   ... courant_limit=1.5
   anomalies: 2  ['courant-excursion']
   FIRED: flag | maximum Courant number reached 1.59 against a case limit
          of 1.5 (reported maximum above the case limit); reduc...
```

A Courant number **33 times the case limit**, climbing monotonically over 60
fixed time steps, raises **zero** anomalies in the shape production actually
builds. The identical input fires twice the moment the gate is supplied — so
the rule works, and nothing can reach it. **S8 is DEAD in production, in the
sense Round 3 extended the term to: a rule the lab believes it has and does
not.**

### 5.2 The downstream claim

`MONITOR_STANDARD.md`'s reach table (`:1028`) is honest and current — it reads
`**S8** Courant excursion | **UNREACHABLE** (needs courant_limit)`. The defect
is one row in a *different* table in the same document. The validation ladder
at `:694` grades S8:

> | S8 Courant excursion | **4 archived transient logs, 13308 time steps, 417
> ledger rows** | 0 healthy runs | **validated.** Tolerance measured, not
> assumed…

Two things are wrong with that cell, and they are separate:

1. **It is the only row in a 12-row table with no date.** Every sibling carries
   one — S2 *"replayed 2026-08-01"*, S3 *"validated 2026-08-01"*, S12
   *"validated 2026-08-02"*, S10d *"validated 2026-08-08"*. S8 reads bare
   `validated`.
2. **The same document contradicts it at `:1169`:** *"**S8.** No replay exists
   at all. The archive holds 21 transient logs with residual series, which is
   the corpus a Courant replay would run over."* And `:1168` — *"S8 is
   unchanged: still no replay, still needs one."*

One of those two sentences is false and Round 5 does not adjudicate which; the
document's owner does. What Round 5 establishes independently is the part that
does not depend on the adjudication: **whichever is true, a reader scanning the
ladder sees S8 graded `validated` alongside S9, S10 and S12, with no reach
qualifier, for a rule that has never fired on a production run in the lab's
history.** That is L-55's exact shape — the per-rule status lines are
scrupulously honest and the summary assembled from them is not.

`sdk/scripts/replay_monitor_rules.py` covers **S1 to S6 only** (its own
docstring, `:2`; the rule map at `:123-128`), which is consistent with `:1169`
and not with `:694`.

**Not repaired here, and deliberately.** `docs/standards/MONITOR_STANDARD.md`
is a standing record and outside this round's write scope (H6). Filed as D60.

---

## 6. R3's D3 and D5 were never named — a found-dead pair that cannot be reopened

R3 §1.4 reports **"6 FOUND-DEAD across the fleet-wide remainder"** and ranks
them. Ranks 1–4 are D1, D4, D2 and FD-1, each named, quoted and evidenced.
Ranks 5–6 are listed as **"D3 and D5"** with the note *"detail pending
consolidation; see 1.3"*, and §1.3 records its own detail as **pending**. R3's
own §5 item 10 carries this forward: *"C1-C's consolidated detail for FOUND-DEAD
D3 and D5 is pending; only the count of 6 and the D1/D4/D2 ranking are
established."*

Three days later the consolidation had not landed. `git grep` over the tracked
frame finds no record naming a fleet-wide found-dead D3 or D5.

**This is the worst shape in the audit, and it is worth naming as its own
class.** Two levers were judged dead by an executed sweep; the judgement was
published as a count; the identities were not. Nothing downstream can be
checked, because there is nothing to check *against*. The headline number
**6** has been quoted since 2026-08-11 and one third of it is unfalsifiable.

Round 5 cannot re-verify what was never written down, and says so rather than
quietly reporting 4. Filed as part of D60.

**Sharpened 2026-08-14, same round, before the finding shipped.** A closer read
distinguishes the two, and the distinction makes this worse rather than better.
`D3` is referenced once more, at `:226`, inside the dated amendment: *"**D1, D2
and D3** below were therefore found independently, twice, on the same night, and
are already actioned."* So **D3 was known, actioned, and its identity still
never written down** — the information existed and was lost, rather than never
having been determined. `D5` carries no such reference and is undescribed
anywhere.

**Positive control for both absences (L-84).** In the same file and by the same
reader, `D1` occurs **7** times and `D4` **6**, each fully described, quoted and
evidenced. The reader finds a described found-dead when one is present. The
only other occurrences of the tokens `D3` and `D5` in that file are at `:142`,
where they name `rotation_branch` diagnostic runs — a different numbering
entirely, and not to be confused with them.

---

## 7. What this round could not reach

Ranked by what a reader would most want covered next.

1. **`PROOF.md` §1–24 interior, ~2,400 lines.** Open since R1, carried by R3
   and R4, still open. Untouched here.
2. **R3's D4** (`trapFpe` false universal) — not re-measured this round. R3
   called it *"the live one"*; it stays live and unreopened.
3. **The in-container DAFoam build.** `DAResidualSimpleFoam.C` is not on this
   host. No claim that a `daOptions` key is dead *code* was made by this round,
   and none could be settled from here.
4. **The SDK-wide mechanical census** — unconsumed parameters, config keys with
   no reader, env vars set-but-never-read, argparse dests never referenced, and
   always-true gate conditions across `sdk/` and `scripts/` — was dispatched and
   had not returned when this record was committed. §5's S8 result came from a
   targeted reopen, not from that census. **The census is the largest unswept
   surface this round leaves.**
5. **Frame L's edges**, inherited from R4: gzipped logs, `log.run`-named logs,
   and logs not matching `*.log` sit outside the 1,635. §3's finding is
   unaffected — it rests on four named files read directly, not on a population
   count.
6. **The two 906 MB tarballs at `/home/ubuntu`**, unopened since R3 named them.

---

## 8. Strikes filed by this round (L-76 — struck and kept, dated)

Applied on the record's own face, quoting rather than deleting:

1. **`demo-output/website/dafoam/A1_A5_A6_DIAGNOSIS.md` §1.4** — the finding
   *"One stated check is confounded, and it is stated as passed"* is falsified
   by §3.3. Struck and kept with the counter-evidence quoted.
2. **`demo-output/website/dafoam/ROOTCAUSE_getRotationMatrix3d.md` §4.7** —
   **not** struck. A dated note records that P6's null was independently
   re-tested and is discriminating, and that D40's prescribed strike must not
   be applied.
3. **`demo-output/website/mega-batch/F10_YPLUS_FIX.md`** — the AFTER table's
   two promoted rows carry a dated note that the promotion lever has never
   fired in any archived run and that neither index survives in the ledger.

`docs/DOCKET.md` **D40** is falsified by §3 and is **not edited here** — the
docket rule is that an agent edits only its own row. D60 carries the
correction and names D40 explicitly, in the same shape D56 used.

---

## 9. Docket filing

One row at the next free id, **D60**, covering the class (D57–D59 were taken by concurrent agents while this round was being written; the row was renumbered rather than renumbering theirs — W-4, renumbering IS the defect): *a lever found dead
is a finding with a half-life, and this lab has been filing the finding without
filing the sweep of what leaned on it.* Four instances in one round — D40's
remedy unexecuted for three days and pointing the wrong way, S8 left behind
when its twin was repaired, N-1's downstream table unannotated, and two
found-dead levers whose names were never published at all.
