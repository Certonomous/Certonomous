# JF1E RUNG E2b — GRADING RECORD

**Rung:** E2b — `nNonOrthogonalCorrectors 1 -> 2`, the ONE change from E2a.
Continuation seeding, `fvSchemes`, `k` and `omega` relaxation 0.5, `U` relaxation 0.7
and `p` field relaxation 0.3 are all inherited from E2a unchanged.

**Registration:** `verification/campaign/JF1E_TURBULENCE_STALL_ESCALATION_PREREGISTRATION.md`,
frozen `6e83157c112cdf606094f88ff0592bf1b02bc4b3`, blob
`800944bcfeb591973ca8830ae6c8ec6787ce730c`. Verified twice — before the first solver
started and again at grading — that the working-tree copy, `HEAD`'s blob and the blob
at the freeze commit all hash to `800944bc…`. **The frozen file is the file that ran**
(CLAUDE.md rule 2). Each row's own `RUN_STATUS` carries the same assertion, made by the
wrapper's own fail-closed guard *before* that row's solve.

**Grading path:** `verification/runs/JF1_jet_flap/analyse_jf1_ladders.py`, landed
`74c4f5fb`, blob `ef4c0b0c72c4bd23b9afea9d4c7a17181cbbec53`, **byte-identical to `HEAD`
and to the blob at that commit at grading time — the comparator has not drifted.**
Invoked as `gateE --rung E2b`. Its self-test ran first and **passed**, including the §4
planted control: the `bounding k` reader returned **494** on `JF1_L1_BLOWN_CMU010_A0`
(required 494 exactly) and **0** on the same log with every `bounding k` line deleted.
The CL reader returned its plant of `1.234e-03` to `1e-9` and the control's recorded
`0.54884644`.

**LABEL: `numerics-diagnostic`.** No physics verdict, no lift claim, no observed order,
no GCI and no band comes off this rung (registration §0).

**CAVEAT D-1, carried:** no run in this chain was seeded from a converged field. This
lab has no converged JF1 solution at any `C_mu`. Every seed is the final field of a
**stationary-but-clipping-held** run. **Nothing in this record calls the seed
converged.**

---

## 1. RUNG VERDICT

**RUNG E2b: `GATE FAIL` — escalate to the next rung in the frozen order.**

All four rows satisfy the strict completion rule in full, so **clause E-6 is satisfied
on all four** and the rung is `GATE FAIL`, not `NOT A RESULT`.

Chain launched `2026-09-02T20:57:42Z`, closed `2026-09-02T22:39:15Z`, driver rc = 0
(`verification/runs/JF1_jet_flap/JF1E_E2b_LAUNCH_RC.txt`).

## 2. PER-ROW, AS THE COMPARATOR GRADED IT

Windows: `bounding k` / `bounding omega` counted over the **final 500 iterations**
(7501–8000); residuals at `endTime` = 8000.

| row | verdict | `bounding k` /500 | `bounding omega` /500 | res k | res omega | res p | CL |
|---|---|---|---|---|---|---|---|
| CMU005 | **`GATE FAIL`** | 14 | 100 | 1.732e-06 | 6.999e-09 | 1.652e-08 | 0.40591319 |
| CMU010 | **`GATE FAIL`** | 65 | 100 | 5.954e-06 | 8.250e-09 | 1.721e-08 | 0.55011873 |
| CMU020 | **`GATE FAIL`** | 84 | 83 | 8.932e-06 | 1.174e-08 | 4.032e-08 | 0.74416062 |
| CMU040 | **`GATE FAIL`** | 204 | 83 | 2.477e-05 | 3.966e-08 | 3.570e-07 | 1.01000031 |

**Clause by clause:** E-1 (`bounding k` == 0) **FAILS on all four**. E-2 (`bounding
omega` == 0) **FAILS on all four**. E-3 (res k < 1e-6) **FAILS on all four**. E-4 (res
omega < 1e-6) passes on all four. E-6 passes on all four. E-5 as the comparator
evaluates it passes on all four — **see §6, where that reading does not survive
inspection, exactly as it did not for E2a.**

### 2.1 E-6, the strict completion rule, clause by clause

Measured on every row: `solver_rc 0`; exactly **one** `End` line; last `Time = 8000 ==
endTime`; `ExecutionTime` count **8000 == endTime**; fields `U p k omega nut` all
present at `8000/`; and the **age guard** holds with margin — the youngest field at
`endTime` is newer than that case's own `0/U` by **1457.6 s to 1610.2 s**, i.e. by the
whole length of the solve that was allowed to produce it. Every row: `rc = 0`,
`stage_at_exit done`.

## 3. THE ONE CHANGE, PROVED RATHER THAN ASSERTED

One change per rung is this ladder's entire evidentiary content, so the claim is
measured in three places and the run refuses if any of them fails.

1. **The staged dictionary against E2a's own.** The wrapper rebuilds E2a's
   configuration from the case template, then asserts that reconstruction is
   **byte-identical to the `system/fvSolution` E2a actually ran** — `cmp` against
   `verification/runs/JF1_jet_flap/JF1E_E2a_<TAG>_A0/system/fvSolution`, per row. It
   refuses (exit 13) if E2a's run root is absent, so "inherited from E2a unchanged" is
   never asserted on trust.
2. **The change itself.** `diff` of the finished dictionary against that baseline must
   be **exactly two lines (one `<`, one `>`)** and the changed line must name
   `nNonOrthogonalCorrectors`. Measured content of that diff, verbatim in words: the
   single line `nNonOrthogonalCorrectors    1;` inside the `SIMPLE` block becomes
   `nNonOrthogonalCorrectors    2;`. **Nothing else differs.**
3. **Against the case template**, for the record, the diff is **six lines (three
   changed)**: `k 0.7 -> 0.5`, `omega 0.7 -> 0.5` (both inherited from E2a) and
   `nNonOrthogonalCorrectors 1 -> 2` (this rung). `U 0.7`, `p 0.3` and both
   `div(phi,k)` / `div(phi,omega)` `limitedLinear 1` entries are asserted **unchanged**,
   so E2c has not leaked into this rung.

Every other staged file was checked byte-identical to its template on all four rows:
`system/fvSchemes`, `constant/transportProperties` and `constant/turbulenceProperties`
against `cases/JF1_JET_FLAP/case/`, and `system/controlDict` against
`cases/JF1_JET_FLAP/case_blown/`. `endTime` is 8000 on every row, as registered.

**The change is live in the solver, not merely in the dictionary:** `p` is solved
**three** times per iteration on every E2b row where E2a solved it twice.

The full assertion is recorded in each row's own `RUN_STATUS.JF1E_E2b_<TAG>_A0.txt`
under `one_change`.

## 4. WHAT THE SECOND CORRECTOR ACTUALLY DID — AND THE MEASUREMENT IS STRIKING

**On `omega` it did nothing whatsoever, and "nothing" here is exact rather than
approximate.**

The set of iterations at which `bounding omega` fires is **bit-identical between E2a and
E2b on all four rows** — same count, same first iteration, same last iteration,
symmetric difference **zero**:

| row | E2a `bounding omega` iterations | E2b | identical? | symmetric difference |
|---|---|---|---|---|
| CMU005 | 1598 | 1598 | **yes** | **0** |
| CMU010 | 1600 | 1600 | **yes** | **0** |
| CMU020 | 1333 | 1333 | **yes** | **0** |
| CMU040 | 1333 | 1333 | **yes** | **0** |

And the pattern is **strictly periodic**. The gap between consecutive
`bounding omega` iterations takes one value for essentially the whole run:

| row | E1 stride | E2a stride | E2b stride |
|---|---|---|---|
| CMU005 | 3 (100.0 % of 2664 gaps) | 5 (99.9 % of 1597) | **5 (99.9 % of 1597)** |
| CMU010 | 3 (100.0 % of 2666) | 5 (100.0 % of 1599) | **5 (100.0 % of 1599)** |
| CMU020 | 4 (100.0 % of 1999) | 6 (100.0 % of 1332) | **6 (100.0 % of 1332)** |
| CMU040 | 4 (99.9 % of 1998) | 6 (99.9 % of 1332) | **6 (99.9 % of 1332)** |

So `omega` clipping in this case is a **limit cycle of fixed period**, and the two
rungs move it differently: the turbulence-relaxation change (E2a) lengthened the period
from 3 to 5 and from 4 to 6, while **the pressure-equation change (E2b) did not perturb
it by a single iteration.**

**On `k` it moved things, and not in one direction.** Final-500 `bounding k` went
20 → 14 on CMU005 and 104 → 84 on CMU020, but 57 → 65 on CMU010 and **139 → 204 on
CMU040**. Whole-run counts barely move at all: 275 → 302, 819 → 884, 1353 → 1357,
2377 → 2341. The `k`-bounding iteration sets, unlike `omega`'s, are **nearly disjoint**
between the two rungs — on CMU005 the two sets of 275 and 302 iterations share only
**6** members — so the second corrector redistributes `k` clipping in time without
reducing its amount.

**This is a measurement, not a diagnosis.** The label is `numerics-diagnostic` and §0 of
the registration forbids a physics verdict here. What is recorded is that the one
control this rung moved is **demonstrably not the control that governs `omega`
clipping**, and governs `k` clipping only in the sense of reshuffling it.

**Mesh context, read from the run's own `log.checkMesh` and identical on E2a and E2b:**
`Mesh non-orthogonality Max: 57.5270425 average: 10.03080802`, `Mesh OK`. A mean
non-orthogonality of 10° is the regime in which one corrector is already sufficient, so
a second one having no measurable effect is **consistent with** the mesh. That is
context offered for a successor, not a claim this rung is entitled to prove.

## 5. L-235 IS BINDING ON THIS READING — THE CL COLUMN IS NOT EVIDENCE OF CONVERGENCE

**`k` is still clipping through the final iterations on all four rows**, at 14 / 65 / 84
/ 204 of the last 500. CL agrees with E2a's to within `4e-06` on every row
(CMU040 1.01000031 against E2a's 1.00999182) and CL peak-to-peak over the final 2000
iterations is **1.594e-06 / 3.760e-06 / 4.293e-07 / 6.643e-06**. **A settle test on CL
alone would call all four converged, and the reason CL stopped moving is not that the
solve converged.** That is L-235, it is why E-1 and E-2 are the load-bearing clauses,
and registration §4 says so in advance: *"a rung that clears E-3 to E-5 but not E-1/E-2
is `GATE FAIL`, and no report of it may use the word converged."*

**A reduction is not a clearance, and the frozen threshold is zero.** On this rung there
is not even a consistent reduction: two rows improved on E-1 and two got worse.

## 6. THE TWO GRADING-PATH DEFECTS FOUND AT E2a ARE CARRIED, NOT REPAIRED — AND ONE IS WORSE HERE

Reported, not repaired: the grading path is fixed at the pre-registration commit
(rule 2) and a lane does not amend it. **Both are conservative in the wrong direction —
they make the solve look MORE converged than it is — and neither changes E2b's
`GATE FAIL`,** because E-1, E-2 and E-3 fail on all four rows under any reading.

**D-E2a-1, carried — clause E-5 is evaluated on `p` alone; `Ux` and `Uy` are never
read.** The frozen clause names *"initial residual of `Ux`, `Uy` and `p` at `endTime`
< 1e-6"*; the comparator's gate expression tests `bk`, `bo`, `rk`, `ro` and `rp` only.
Measured from the E2b logs at `endTime`: **`Uy` misses 1e-6 on three of four rows**
(1.112e-06 / 1.763e-06 / 4.327e-06 for CMU010/020/040) and **`Ux` misses on CMU040**
(1.415e-06).

**D-E2a-2, carried and AMPLIFIED BY THIS RUNG'S OWN CHANGE.** The comparator takes the
LAST `Solving for p` match. `simpleControl::criteriaSatisfied()` tests
`maxResidual(entry).first()` — the **maximum** initial residual over all solves of that
field in the iteration — so the correct read is the maximum over the correctors, which
is the first. **E2b makes this worse by construction: `nNonOrthogonalCorrectors 2` means
`p` is solved three times per iteration where E2a solved it twice, so the comparator's
last-match read is now the third corrector.** Measured at `endTime`:

| row | comparator's read (last corrector) | **maximum over the three correctors** | factor |
|---|---|---|---|
| CMU005 | 1.652e-08 | **1.972e-06** | 119× |
| CMU010 | 1.721e-08 | **3.616e-06** | 210× |
| CMU020 | 4.032e-08 | **6.913e-06** | 171× |
| CMU040 | 3.570e-07 | **1.653e-05** | 46× |

Against E2a's factor of 20 to 29, the discrepancy is now **46× to 210×**. **Under the
corrected reading `p` misses its 1e-6 criterion on all four E2b rows** — and note the
trap this sets for a careless successor: the comparator's `res p` column *fell by an
order of magnitude* from E2a to E2b (1.003e-07 → 1.652e-08 on CMU005), which looks like
the second corrector converging the pressure equation, when the maximum residual the
solver's own `residualControl` actually reads **rose** (2.056e-06 → 1.972e-06 is flat on
CMU005, and 1.297e-05 → 1.653e-05 is a rise on CMU040). **Adding correctors makes the
comparator's `p` column look better while the graded quantity does not improve.**
Recorded so it is falsifiable rather than inherited.

**No script was changed to produce this record.** These are proposed findings about the
grading path; reading a measurement-script diff is the supervisor's personal check under
`SUPERVISION_CHARTER.md` §3 and is not a lane's to make.

## 7. COST — CLAUDE.md RULE 12

Serial (`ranks = 1`) throughout, so core-min == wall-min. Each figure read from that
row's own `RUN_STATUS.JF1E_E2b_<TAG>_A0.txt`, written by the wrapper's `EXIT` trap.

| row | wall s | **core-min MEASURED** | per-link cap | **$ DERIVED, NOT MEASURED** |
|---|---|---|---|---|
| CMU005 | 1521 | **25.3500** | 55.0 (46 %) | $0.021674 |
| CMU010 | 1500 | **25.0000** | 55.0 (45 %) | $0.021375 |
| CMU020 | 1612 | **26.8667** | 55.0 (49 %) | $0.022971 |
| CMU040 | 1460 | **24.3333** | 55.0 (44 %) | $0.020805 |
| **rung** | **6093** | **101.5500** | **220 registered** | **$0.086825** |

Registered estimate **141.0 core-min**, registered cap **220**. Actual **101.5500** —
**0.720× the estimate, 46 % of the cap.** No cap struck; the dearest row reached 49 % of
its own per-link cap.

**Waste, named separately per `COMPUTE_BUDGET_CHARTER` §6 and NOT absorbed into the
ratio: 0.0167 core-min (1 wall s).** A first launch attempt at `2026-09-02T20:55:25Z`
was refused at the staging stage by an assert in the launcher — a `grep -q` inside a
pipeline under `set -o pipefail`, which SIGPIPEs its upstream `grep` on the first match
and so returns non-zero on **success**. The staged dictionary was provably correct; the
instrument was not. It died before `build_jf1.py`, before `checkMesh` and before the
solver, so it consumed one wall second and produced no time directory and no solver log.
The stub is preserved at
`verification/runs/JF1_jet_flap/JF1E_E2b_CMU005_A0.stage_refused_2026-09-02T2055Z_PRESERVED`
and its chain log at `JF1E_E2b_CHAIN.attempt1_stage_refused.log`, neither deleted. The
assert was rewritten to capture the diff before matching it, and the reason is recorded
in the script at the site.

Gross = cleaned: four links, four completed solves, no re-run of a solve, and the
longest row at 1612 wall s is well below the `COMPUTE_BUDGET_CHARTER` §2 3600-s stall
rule.

**Every dollar figure above is DERIVED at the recorded `c7a.4xlarge` rate of
$0.0513/core-h and is NOT MEASURED — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).** 101.5500 core-min = 1.6925 core-h.

**Estimate versus actual is filed as a row in `docs/COST_CALIBRATION.md`** per rule 12's
calibration bullet, and the attribution is not repeated here.

## 8. THE STANDING PREDICTION, SCORED

The `k_min` forecast recorded before E2a ran had two limbs: **(1) E2a would not clear
the stall — HELD, scored at E2a.** **(2) E2c (`limitedLinear 1 -> 0.5`) is the likelier
fix — still not scored.**

E2b does not score limb 2 either, and it is worth being precise about why the temptation
exists. E2b failing is *consistent* with limb 2 and is **not evidence for it**: this
rung tested the pressure-equation treatment, which the `k_min` reasoning never
implicated. What E2b does add is a **negative** result that narrows the field — §4
measures that the non-orthogonal corrector count does not govern the `omega` limit cycle
at all and does not reduce `k` clipping. **The prediction stands as half-scored: limb 1
correct, limb 2 open, and E2c is the next opportunity to score it.**

## 9. THE E4 TRIGGER, READ AND REPORTED

Registration §5 fires E4 on a row whose CL peak-to-peak over its final 2000 iterations
exceeds **1.0e-03**. Measured on E2b: **1.5936e-06 / 3.7601e-06 / 4.2929e-07 /
6.6431e-06**. **The trigger does not fire on any row** — as it did not on E0, E1 or E2a,
and it remains between two and three orders of magnitude clear. Read with §5, this is
the stationary-and-clipping-held signature, not evidence of a settled solve.

## 10. WHAT COMES NEXT — REGISTERED, NOT CHOSEN

The frozen order of registration §3 puts **E2c** next: **`div(phi,k)` and
`div(phi,omega)`: `limitedLinear 1 -> limitedLinear 0.5`**, applied to the same four
rows at `endTime` 8000, inheriting E2b's configuration as its new baseline per §3 —
that is, continuation seeding, `k`/`omega` relaxation 0.5 **and**
`nNonOrthogonalCorrectors 2`. Registration §6 prices E2c at **94.0 core-min** against a
**registered cap of 150**, `$0.0804` derived at $0.0513/core-h, derived and not measured.

**A note a successor will need, and it is a cost note, not a licence to change
anything.** That 94.0 was registered on the assumption that each rung costs about what
E0 did. E2b's measured per-iteration cost is **1.13× to 1.60× E2a's** because it carries
the extra corrector, and E2c inherits that corrector. On E2b's own outturn a four-row
E2c rung is nearer **102 core-min** than 94 — still inside the registered 150, so
nothing is at risk, but the margin is 32 % rather than the 60 % the registration implies.
**No cap, threshold, gate or label is altered by this observation**; it is recorded here
so it is not rediscovered.

**This record states the frozen order; it does not choose it, and it does not reorder
it.** Reordering after first compute is a registered refusal (§7 item 6).

**E2c is NOT launched by this record.**

---

**SUBMISSIONS PARKED.** Nothing in or derived from this record is sent, filed, uploaded,
registered, posted or commented outside this box.
