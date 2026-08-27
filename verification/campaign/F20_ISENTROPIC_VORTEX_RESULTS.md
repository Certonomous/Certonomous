# F20-ISENTROPIC_VORTEX — 2-D isentropic vortex, `rhoCentralFoam` — GRADED RECORD

Team cfd. Pre-registration `verification/campaign/F20_ISENTROPIC_VORTEX_PREREGISTRATION.md`
frozen at **`548fc02e2ac8d1c27868af67a343f3a5495e8ecb`**. **Instrument-check**
(`CASE_SELECTION_CHARTER.md` §3). Graded 2026-08-26T20:47Z by a cfd lab-lane at
**zero new compute**; the three levels were launched by the queue runner at
17:51:23Z with no agent attached and completed 19:01:23Z.

**Filed 2026-08-27 by cfd lane R2 to close a filing gap, not to grade anything.**
F20 was graded `PASS` × 2 on 2026-08-26 and its calibration row **C-136** is in
`docs/COST_CALIBRATION.md`, but **no record stood in `verification/campaign/`**,
where every sibling rung's verdict lives (F17, F17b, F18, F18b, F19, F21, F22,
F24). §7 records exactly what was and was not on disk. **Every number below is
the frozen grader's own, read by this lane from
`verification/runs/F20_ISENTROPIC_VORTEX_runs/F20_GRADED.json` and
`GRADE_F20.out`. Nothing here re-grades, re-derives, re-runs or amends
anything.**

Grader: the frozen `cases/F20_ISENTROPIC_VORTEX/grade_f20.py` (blob
`68057e2e`), **rc 0**, `GRADE_F20.err` **empty (0 bytes)**. Stdout
`verification/runs/F20_ISENTROPIC_VORTEX_runs/GRADE_F20.out`; machine record
`F20_GRADED.json` (`rung` = `F20-ISENTROPIC_VORTEX`, `prereg_commit` =
`548fc02e…`). Gated by `scripts/roache_triple.py::grade_ladder`, **one call
node** (`ast_call_nodes [551]`); AST census **4 files, 0 `assert` nodes,
planted assert seen**.

## 1. VERDICTS — fixed vocabulary, the grader's tally verbatim

    G-F20-1_E2_density_L2_at_T               PASS
        finest triple ('coarse', 'medium', 'fine') CONVERGING at dim = 2,
        observed order 2.7786, GCI 5.1038 % = 5.91977e-05 absolute at Fs = 1.25
    G-F20-2_mean_kinetic_energy_at_T         PASS
        finest triple ('coarse', 'medium', 'fine') CONVERGING at dim = 2,
        observed order 1.2762, GCI 0.0020 % = 2.04339e-05 absolute at Fs = 1.25

| gate | fine value | reference | registered band | triple (c, m, f) | observed p | GCI (Fs = 1.25) | Richardson | **verdict** |
|---|---|---|---|---|---|---|---|---|
| **G-F20-1** `E2_density_L2_at_T` | **1.1598741628142594e−03** | 0.0 | [1.3910166315426575e−04, 1.2519149683883918e−03] | **CONVERGING**, dim 2, monotone | **2.778625815979563** | 5.1038 % = 5.91977e−05 abs | 1.1125159710836914e−03 | **PASS** |
| **G-F20-2** `mean_kinetic_energy_at_T` | **1.0055387971424934** | 1.005633548659453 | [1.0049158929516355, 1.0063512043672704] | **CONVERGING**, dim 2, monotone | **1.2761825604037556** | 0.0020 % = 2.04339e−05 abs | 1.0055224500053284 | **PASS** |

`band_verdict` reads `PASS` on both rows independently of the gate, and the gate
left both as PASS — the one-way property is visible in the record rather than
asserted.

Level values, from the grader's own `levels` arrays:

| level | cells | G-F20-1 E2(ρ) at T = 10 | G-F20-2 box-mean KE at T = 10 |
|---|---|---|---|
| coarse 128² | 16,384 | 3.342462996686085e−03 | 1.0056183415176365 |
| medium 256² | 65,536 | 1.4374871371699892e−03 | 1.0055620423240867 |
| fine 512² | 262,144 | **1.1598741628142594e−03** | **1.0055387971424934** |

**Rule 5 limbs, in order, from the grader's own `levels_detail`.**
(1) `iterative_convergence` = **CONVERGED at every level** on the registered
basis (a Courant stability census; inviscid `rhoCentralFoam` has no iterative
residual). `plateau` = **`ABSENT: value at a fixed instant of a transient; no
plateau exists to test`** at every level — an absent measurement **reported as
absent, never as a pass** (`VERIFICATION_CHARTER.md` §9). (2) Both triples
CONVERGING and monotone. (3) Both fine values inside their registered bands →
**PASS**.

## 2. THE TWO REGISTERED PREDICTIONS THAT WERE MISSED

Both are recorded here because a verdict record that reports only the verdict is
not a verification record. **Neither miss changes a verdict, and no band,
threshold, order range or label was moved.**

- **G-F20-1 — the registered order range was MISSED.** §5 of the
  pre-registration predicted CONVERGING with observed order in **[1.0, 1.6]**;
  the grader read **2.7786**. The band is a **value** band (§5: *"does not
  depend on p"*), so the verdict stands on its own terms. What the numbers say,
  stated as a finding and not as a softening: the **Richardson extrapolate of
  the E2 triple is 1.1125e−03, not 0, against an exact reference of 0** — the
  triple is converging toward a **non-zero floor** rather than toward the exact
  solution, and a difference-based order reads high exactly when the increments
  shrink faster than the error does. The fine value is **92.6 % of the way to
  the band's upper edge**. **Raised to the cfd supervisor as a check-3 item.
  It is not a re-grade and nothing here re-computes it.**
- **G-F20-2 — the registered outcome was MISSED in the conservative
  direction.** The registration predicted a **non-monotone** KE triple and
  therefore **NOT A RESULT**. The triple came out **monotone** (all three below
  exact), CONVERGING at p = 1.2762 → **PASS**. A rung registered to fail and
  passing is still a miss of the prediction, and is recorded as one.

## 3. RULE 4 — strict completion, re-read from the run root by this lane

| level | `Time =` lines | `End` | last time == endTime | `RC.txt` | fields at `10/` | grader `completion.done` | ClockTime | ExecutionTime |
|---|---|---|---|---|---|---|---|---|
| coarse | **4,000** | yes | 10 == 10 | 0 | rho U p T | true (`n_times` 4000, `latest` 10.0, `rc` 0) | **44 s** | 44.36 s |
| medium | **8,000** | yes | 10 == 10 | 0 | rho U p T | true (`n_times` 8000, `latest` 10.0, `rc` 0) | **377 s** | 376.08 s |
| fine | **16,000** | yes | 10 == 10 | 0 | rho U p T | true (`n_times` 16000, `latest` 10.0, `rc` 0) | **3,699 s** | 3,697.95 s |

Read by this lane directly from
`verification/runs/F20_ISENTROPIC_VORTEX_runs/<level>/log.rhoCentralFoam` and
`RC.txt`, and agreeing with the grader's own `completion()` at every level. Age
guard satisfied at every level (`10/{rho,U,p,T}` newer than that case's own
`0/U`). All levels **serial on 1 rank**.

**Frozen files — disk == blob at `548fc02e`, re-verified by this lane
2026-08-27.** The freeze sha was obtained with
`git log --diff-filter=A -- verification/campaign/F20_ISENTROPIC_VORTEX_PREREGISTRATION.md`,
**never from a commit subject** (`VERIFICATION_CHARTER` v1.12), and returns
exactly one commit. Every path in `cases/F20_ISENTROPIC_VORTEX/` at that
commit, plus the pre-registration, hashed `git hash-object <disk>` against
`git rev-parse 548fc02e:<path>` — **15 of 15 SAME, 0 DIFFERENT**, including
`grade_f20.py` `68057e2e` and `run_f20.sh` `49523e10`.

## 4. COST — rule 12 estimate-versus-actual

| item | value |
|---|---|
| predicted (prereg §8 at `548fc02e`) | **60.0 core-min** (coarse 0.85, medium 6.6, fine 52.5); registered cap **240.0** |
| actual, MEASURED from the logs' `ClockTime × ranks ÷ 60` | coarse 44 s → 0.7333; medium 377 s → 6.2833; fine 3,699 s → 61.6500; **68.6667 core-min gross** |
| the grader's own `cost_claim` | `core_min_claim` **68.66666666666667**, `partial_sum_core_min` the same, `cap_core_min` 240.0, **`defects: []`** — the cost claim is not refused |
| actual cleaned | **68.6667** — cleaned == gross; see the stall note below |
| waste, named separately | **0.000 core-min** — no stall, kill, re-run or cap movement |
| quantisation | ClockTime is integer-second: ± 0.0083 core-min per level |
| share of cap | **28.6 %** |
| dollars | 68.6667 / 60 × $0.0513 = **$0.0587 — DERIVED, NOT MEASURED** ($0.0513/core-h, c7a.4xlarge, reported-by-owner; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5) |
| **ratio actual/predicted** | **1.144** |

**Gap attribution — misprediction of the per-cell-step rate at the fine level;
not contention and not waste.** Per-level ratios 0.86 / 0.95 / **1.17**: the
two smaller levels came in **under** and only the fine level over.
`ClockTime − ExecutionTime` = 0 / 1 / 1 s, so **no contention on any level**.
Per-cell-step rate rose with cell count against a flat registered basis.
**Stall rule:** the fine level's 3,699 wall s exceeds the 3,600-s figure **by
the letter**; it is that level's registered 16,000 steps run to `End`, not a
stall, and the spend is carried **gross** (the disposition C-133 recorded for
F15).

**Calibration row: ALREADY LANDED — `docs/COST_CALIBRATION.md` row `C-136`,
dated 2026-08-26**, carrying the 60.0 predicted / 68.667 measured / **1.144**
ratio, the attribution and the dollars marked derived. **This record adds no
second row**; a duplicate calibration entry for one completion would be a
worse defect than the missing verdict record it was filed to fix.

## 5. THE CAP OVERRUN NOTICE — an infrastructure record, and NOT a cap breach

`cases/F20_ISENTROPIC_VORTEX/CAP_OVERRUN.txt`, verbatim:

    2026-08-26T18:57:38Z CAP OVERRUN REPORTED, NOT ENFORCED: case
    F20_ISENTROPIC_VORTEX elapsed 3975 s > 1.10 x registered 3600 s
    (60.0 core-min / 1 ranks). The run was NOT killed (caps report;
    COMPUTE_BUDGET_CHARTER).

**This record must and does carry it, and must not carry it as a cap breach.**
The notice fired against **1.10 × the ESTIMATE (60.0 core-min = 3,600 wall s at
1 rank)**, not against the **registered CAP of 240.0 core-min**. Final spend was
**68.667 core-min = 28.6 % of the cap**; the cap was never approached, never
crossed and never raised, and the grader's own `cost_claim` records **no
defects**. The run was **not killed** and the ladder completed to `End` at every
level. It is an **INFRASTRUCTURE record under L-342** — a bookkeeping event that
cannot and does not touch the physics or either verdict — and the queue-runner
defect it exposes (comparing elapsed wall time against the *estimate* while
calling it a *cap*) was fixed under the cfd supervisor's 17:46Z order
(`scripts/queue_runner.py`, `QUEUE_RUNNER.md` §5). Recorded here so no later
reader meets the file cold and reads `CAP OVERRUN` as a rule-12 breach.

## 6. PLANTED-ZERO CONTROL (rule 3) AND THE INSTRUMENT, from `F20_GRADED.json`

Both planted into the **real artefact** `…/F20_ISENTROPIC_VORTEX_runs/fine/10/rho`
and read back **through the real reader**:

| gate | reader | planted | read back | **result** |
|---|---|---|---|---|
| G-F20-1 | `e2_from_files` | 5.336618047888707e−04 | 5.336618047888707e−04 | **passed** |
| G-F20-2 | `ke_from_files` | 1.2672241529050332e−03 | 1.2672241529050332e−03 | **passed** |

**All 9 registered controls `passed: true`:** symbolic substitution into the
co-moving steady Euler equations; `PZ-F20-BETA` (planted 1.1 β in T must go
non-zero); field at T equals field at 0 and moves at T/2; constant-ratio
refinement in h **and** Δt; the model forced, mass-conserving, ordered, KE
decomposed; `PZ-F20-GRADE_LADDER_CALLSITE` (AST census plus a grep matcher
driven both ways); solver dictionaries agree with the registration; the reader
parses real solver-written `rho` and `U` already on this box;
`PZ-F20-L342` infrastructure-vs-physics driven both ways.

**Both gate quantities shown able to take a passing AND a failing value**
(the grader's `gate_demonstration`, four rows, every `inside` matching its
`intended`): G-F20-1 inside **4.17304989e−04** / outside **1.66921996e−02**;
G-F20-2 inside **1.00562618** / outside **1.00763843**.

## 7. THE FILING GAP THIS RECORD CLOSES — what was and was not on disk

Stated plainly, because the alternative to stating it is a reader wondering why
a 2026-08-26 verdict carries a 2026-08-27 record.

**On disk before this record:** the grader's own outputs `F20_GRADED.json`
(21,890 B), `GRADE_F20.out` (814 B) and `GRADE_F20.err` (0 B), **and a full
verdict record at `verification/runs/F20_ISENTROPIC_VORTEX_runs/RESULTS.md`**
(8,572 B, blob `e0edeefc`, written 2026-08-26T20:49:49Z by the grading lane,
tracked in git). **The verdict was never unrecorded — it was recorded at the
wrong address.** `CLAUDE.md`'s WHERE THINGS LIVE table puts grading records in
`verification/campaign/` and run outputs in `verification/runs/<CAMPAIGN>/`
*"never beside the prose describing it"*; a verdict filed in the run root is
invisible to anyone reading the campaign directory, and its filename
`RESULTS.md` carries no rung id, unlike every sibling
(`F17_KV40_RESULTS.md`, `F18b_…_RESULTS.md`, …).

**This lane checked every number in that run-root record against the frozen
grader's own JSON and log files and found no discrepancy** — both verdicts,
both values, both bands, both orders, both GCIs, both Richardson extrapolates,
all six level values, all three ClockTimes, the 68.667 core-min claim, the
9 controls and the 4 gate demonstrations. This record is therefore a
**re-filing at the correct address, not a second grading.**

**Two open items left for the cfd supervisor, not decided by this lane:**
1. **The run-root `RESULTS.md` is left exactly where it is.** It is another
   lane's committed work; deleting or moving it is a repository change this
   lane does not make on its own authority. Until the supervisor rules, **two
   files carry one verdict** — this is named here so neither is later mistaken
   for an independent confirmation of the other.
2. **`scripts/check_filing.py` does not detect this class of defect.** Run in
   this lane's invocation it reports 34 violations across 7 rules and **not one
   of them is F20**: there is no rule for *a verdict record filed under
   `verification/runs/` instead of `verification/campaign/`*. The gap was found
   by a human reading the campaign directory, which is exactly what a filing
   checker exists to make unnecessary.

## 8. NOT REGISTERED, NOT SENT

No re-grade, no re-run, no re-derivation and no amendment to the frozen
pre-registration (post-compute). No claim about the E2 floor's cause — whether
it is the solver, the exact-field construction at the periodic seam, or the
cell-centre sampling: **not tested by anyone, and a successor registration
would have to say which.** The seam figure the run-root record cites is real
but was attributed to the wrong control there: it is
`seam_mismatch.velocity` = **4.889408860664357e−05** inside the control named
`field_at_T_equals_field_at_0_and_moves_at_T_over_2` (the third), **not**
control 2 (`PZ-F20-BETA…`). Corrected here from the grader's own JSON; the
control itself reads `passed: true` and the correction touches no verdict. **Nothing is sent, filed, uploaded, registered,
posted or submitted** (rule 7). Field data stays on disk under
`verification/runs/F20_ISENTROPIC_VORTEX_runs/` and is not committed.
