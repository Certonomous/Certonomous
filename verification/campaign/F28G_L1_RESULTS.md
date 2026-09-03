# F28G L1 (`dp1000`, `U_inf 20`) — GRADING RESULTS

**Date:** 2026-09-03 (box clock)
**Team:** cfd
**Rung:** `F28G_L1_dp1000_U20` — level 1 of the F28G three-level grid-convergence ladder
**Run root:** `verification/runs/F28_runs/F28G_L1_dp1000_U20`
**Pre-registration:** `verification/campaign/F28G_GRID_CONVERGENCE_PREREGISTRATION.md`,
frozen at commit **`95974b79`** (full `95974b792dd0b0110db079dadae0804add57ee52`, Amendment 5).
Disk sha256 re-verified for this record: **`670bb8ae0ac887792cb21470051f2d824f53896df99f7bd44aa23f8d2cbbbea6`**,
and `git show 95974b79:<path> | sha256sum` returns the **same** digest — the frozen file **is**
the file on disk.
**Queue row:** `verification/queue/cfd/launched/F28G_L1_dp1000_U20.json`
**Grading transcript (in-tree):** `verification/runs/F28_runs/F28G_L1_dp1000_U20/GRADING_OUTPUT.txt`
**Grading spec (in-tree):** `verification/runs/F28_runs/F28G_L1_dp1000_U20/grade_spec_L1.json`

---

## VERDICT

| gate | verdict | held by |
|---|---|---|
| **This L1 row** (parent §8 convergence criteria) | **`NOT A RESULT`** | two independent registered grounds, below |
| **F28G §7 Roache triple on `T_total`** | **`PENDING`** — L2 and L3 not run | a single level is not a triple; the frozen grader refuses on a spec that is not three levels |
| **F28G §6 mesh-admission gate (M1–M6), `mesh_A4/L1`** | `GATE REACHED` — **closed earlier at `2bb79d3e`**, not re-litigated here | unchanged by this run |

**No graded value of `T_total` exists for this rung and none is asserted here.** The frozen
grading path refused before producing one, and computing one outside that path is exactly the
degradation the comparator exists to prevent (standing rule 4: comparators **refuse (exit 2)
rather than degrade**).

---

## 0. What this document is not

It is **not** an amendment to the registration and it alters no gate, threshold, cap or label.
The frozen document was read, hashed and obeyed; it was not edited (standing rule 6). It does
not re-open F28G §6, whose mesh verdict was issued before this run and is unaffected by it.

---

## 1. The grading path — hashed against its committed blob before it was run

Standing rule 2 fixes the grading path at the pre-registration commit and requires the frozen
file be verified **by hashing it against the committed blob**. Done, for both files the
registration's Amendment 4 §A4.2 names:

| file | blob | worktree | `@95974b79` | `@HEAD` | `@7f032d84` (A4) |
|---|---|---|---|---|---|
| `cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28g.py` | `8c17fdd5…` | ✔ | ✔ | ✔ | ✔ |
| `cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py` | `5aff1614…` | ✔ | ✔ | ✔ | ✔ |

All four readings return the **same** blob for each file. sha256, for citation by a reader who
does not have this repository's object store: `analyse_f28g.py`
`3c88c2033ec5de3d0c07279500dbda6948a96c84d57f4fecd7859023a0718292`; `analyse_f28.py`
`31238c108b527e78a7f8537a1b81b91c302f25e5a15885c68c49ce3f489f4a7a`.

**The weaker guarantee is restated, not quietly dropped.** `analyse_f28g.py` did **not exist** at
the original freeze `00188f82` — the grading path is fixed at Amendment 4's commit `7f032d84`,
which §A4.3 labels a weaker guarantee than a grader frozen with its registration. This record
carries that label forward unchanged. `analyse_f28.py` *is* byte-identical at `00188f82`.

**The check-1 no-upgrade clause binds this record.** `analyse_f28g.py` is STRONG (read personally
and executed); `analyse_f28.py` is **QUALIFIED, source-read only, not executed** — it has no
`--selftest` entry point, so its `PLANT_PA/FO/SU/DX` are **declared, not executed**, and `T_total`
flows through that file. Nothing in this document upgrades that scope. A successful run does not
upgrade it; byte-identity to a freeze blob does not upgrade it.

---

## 2. Positive control block — standing rule 3, run **before** any zero was believed

`analyse_f28g.py --selftest`, with `__pycache__` cleared first (stale bytecode is known on this
box to invert mutation tests): **rc = 0, 83 limbs run, 0 limbs failed**, across nine suites —
`richardson_N_T8` (15), `roache_triple` (22), `checkMesh_M1_M2_M3` (11), `grading_readback_M4_M6`
(6), `ladder_M4_M5_M6` (9), `precondition_clause_4` (4), `verdict_ordering_rule_5` (8),
`crash_filter` (3), `completion_rule_4` (5).

**The zeros this record relies on are each backed by a limb that saw a non-zero:**

- **Crash filter — 0 stack frames on this run.** The same reader was shown, in the same
  invocation, reading **12** stack frames off a real FPE crash log
  (`verification/runs/FPE_DIAG_runs/HP1/log.simpleFoam`) on which `FOAM FATAL` occurs **0** times,
  and **0** frames off a real healthy F28 log. A third limb proves an `End` line does not clear a
  stack trace. **The zero on this run is therefore evidence.**
- **Completion rule.** The selftest drove the completion reader into refusal on clause 1
  (`rc = 1`), clause 3 + 5 (last time 100 ≠ endTime 200), and clause 6 (age guard: a field
  **older** than `0/U`). A reader shown able to refuse is a reader whose non-refusal means
  something.
- **Severe-face count and census.** Planted and read back through the same reader; a
  severe-face zero read off an *absent* line is a named limb.
- **Refusal control, run on the real spec.** With `L1` removed from the spec the same reader
  refuses `no 'L1' … A Roache triple has three levels`. The triple requirement is live code, not
  a comment.

---

## 3. The strict completion rule — re-derived, all clauses, through the frozen reader

Standing rule 4, all-or-nothing. Re-derived here independently of the supervisor's personal check,
including the two clauses he did not personally re-check.

| clause | required | measured | |
|---|---|---|---|
| 1 | `rc = 0` | `solver_rc=0` in `RUN_STATUS.F28.F28G_L1_dp1000_U20.txt`, captured **inside** the process on the solver line | ✔ |
| 2 | an `End` line | exactly **1** in `log.simpleFoam` | ✔ |
| 3 | last time == `endTime` | last `Time = 15000`; `system/controlDict:38` `endTime 15000` | ✔ |
| 4 | fields present at `endTime` | `15000/` holds `U k nut omega p phi` (+ `uniform/`) | ✔ |
| 5 | `ExecutionTime` count == `endTime` | **15000** `ExecutionTime` lines, endTime 15000 | ✔ |
| 6 | **age guard** — every field at `endTime` newer than the case's own `0/` anchor | newest `0/` file is `0/U` at `21:58:01.252019`; **earliest** `15000/` field is `k` at `22:12:04.095064` — **+842.84 s** | ✔ |
| 7 | `postProcessing` age guard | held (reported by the frozen reader) | ✔ |

Run through the frozen path rather than by hand: `analyse_f28.completion(...)` returns
`clauses = 1-6 all hold, plus clause 7 (postProcessing age guard)`, `age_ref = .../0/U`, without
refusing. **The run is complete. Completion is not the verdict.**

---

## 4. Why the verdict is `NOT A RESULT` — two independent registered grounds

### 4.1 Ground one — the run hit its registered iteration cap. This is the refusal the frozen path raised.

`analyse_f28g.py --grade`, exit **2**:

> `NOT A RESULT -- comparator refuses (exit 2): L1 ran to the registered iteration cap of 15000.`
> `Parent section 8: HIT CAP -> NOT A RESULT, NEVER "CLOSE ENOUGH", and F28G section 8's stop`
> `order stops the ladder there.`

`ITER_CAP = 15000` (`analyse_f28g.py:245`, cited to parent §8); the run's `endTime` is 15000.
`log.simpleFoam` carries **zero** occurrences of `SIMPLE solution converged` — the solver did not
meet `residualControl { p 1e-6; U 1e-6; k 1e-6; omega 1e-6; }` and exhausted its iterations
instead. At iteration 15,000 the gating **initial** residual for `p` is **0.1578798513** — five
orders of magnitude above its 1e-6 criterion, and flat. This is the same non-convergence the
registration's own §10 names as **untouched** by anything F28G changed.

**A clean `rc = 0` and a clean `End` line are exactly what a cap-stopped run looks like.** The
registration anticipated that in those words and this record does not soften it.

### 4.2 Ground two — the run is not plateaued. Rule 5 clause (1), and it fires independently of the cap.

Read through the frozen `analyse_f28.thrust_stationarity`, in the registration's own frame:

| quantity | value |
|---|---|
| window | 2,000 iterations, `Time` 13,001 → 15,000, 2,000 samples |
| `ptp` (peak-to-peak, 5° sector N) | **0.0295546 N** |
| criterion | `ptp <= max(0.001·\|T_mean\|, T_floor)` — Addendum 3 §3, the struck relative-only form not evaluated |
| relative limb | 0.000318607 N |
| floor limb | 0.000593412 N — **the FLOOR governs** (floor/relative = 1.86) |
| limit | 0.000593412 N |
| **`ptp_over_limit`** | **49.80×** |
| **`pass`** | **`False`** |

**Rule 5 clause (1): any level not iteratively converged or not plateaued → `NOT A RESULT`.** The
level fails by a factor of **49.8** against the governing limb. Had the cap check not fired first,
this one would have. Two independent grounds, both registered before the run.

### 4.3 What was *not* wrong

Stated because a finding is only as useful as its boundary.

- **No crash.** 0 stack frames, from a filter shown able to see 12 on a real crash (§2).
- **No mesh-quality failure.** `mesh_A4/L1` was certified `GATE REACHED` against F28G's own §6.1
  at `2bb79d3e` and this run does not disturb that.
- **No decomposition imbalance.** Per-rank cells 8801 / 8967 / 8890 / 8886 — max/min **1.019**.
- **The disk source is internally consistent.** `T_disk` from the source term vs its analytic
  value: relative difference **0.00127** against a registered tolerance of **0.005**.
- **The mesh is better conditioned than its predecessor**, measured: **14.617** GAMG `p` linear
  iterations per outer iteration on `mesh_A4/L1` against **18.136** on the feasibility mesh.

**None of these rescue the verdict, and rule 5 forbids them from doing so** — the ordering is
one-way: the gate may turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT` and never the reverse.

### 4.4 The diagnostic `T_total`, and why it is not the row's value

The frozen `t_total` reader returns **`T_total = 67.823 N`** (full annulus; `T_duct` 23.287,
`T_hub` 1.865, `T_disk` 42.671). **This is a diagnostic, not a graded value, and it is not
gradeable**: it comes from a level the registered path refused to measure, whose thrust window is
49.8× off plateau. It is printed rather than withheld because a number computed and hidden is
worse than one never computed — and it is labelled here so that no later reader can lift it into
a gate. **Rule 5's one-way ordering means no reading in this section can raise the verdict.**

---

## 5. What L1 alone can and cannot close

**Read from the registration, not inferred from the run.**

**It can close** — and did: the parent §8 convergence criteria for this level. F28G §8's
**registered stop order** makes exactly this the L1 question: *"L1 first; L2 only if L1 satisfies
every §8-of-parent convergence criterion."* L1 does not satisfy them. The stop order continues:
*"A level that hits the 15,000 cap is `NOT A RESULT` (parent §8) and the ladder stops there — the
remaining budget is not spent proving the same thing twice."*

**It cannot close, and no reading of one level can:**

- **§7's Roache triple on `T_total`** — `PENDING`. Observed order `p ∈ [1.3, 2.5]`, `GCI_fine < 3 %`
  and `Fs = 1.25` all require three levels. The frozen grader states it in code: *"A Roache triple
  has three levels; two is not a triple and no order exists."* **No `p`, no GCI and no
  extrapolate is quoted anywhere in this record**, and none may be inferred from L1.
- **§7 clause 4's iterative-vs-discretisation precondition** — `PENDING`. It compares the
  iterative change on every level against the difference between **consecutive mesh levels**;
  with one level there is no consecutive difference. (What *can* be said now: L1's iterative
  `ptp` alone already fails its own plateau criterion by 49.8×, so the precondition has no
  prospect of being met on this level as it stands.)
- **§7 clause 6's `y+` requirement** across the ladder — `PENDING` on L2/L3.

**Successor decision is not this lane's.** The registered stop order stops the ladder; whether
F28G proceeds — and on what basis, given that the `p` residual has now failed to move in 15,000
iterations on three separate configurations — is a supervisor referral, and a cap raise is
Sanaa's alone.

---

## 6. Cost — standing rule 12, and the calibration comparison it owes

**Every figure below was re-derived for this record.**

| | value | basis |
|---|---|---|
| **Predicted** | **144.0 core-min** | registration §8, table row L1 (35,544 cells × 4.05e-6 s anchored `t_cell` × 15,000 iters = 2,159 wall s × 4 ranks) |
| Wall | **843.21 s** | `_launch.started_epoch` 1788472680.7950 (2026-09-03T21:58:00.795Z) → `RUN_STATUS` `end=2026-09-03T22:12:04Z` |
| **Actual (gross)** | **56.21 core-min** | 843.21 s × 4 ranks ÷ 60 |
| Solver-only cross-check | 55.46 core-min | `ExecutionTime = 831.9 s` × 4 ÷ 60 |
| Solver-only cross-check | 56.07 core-min | `ClockTime = 841 s` × 4 ÷ 60 |
| **Actual (cleaned)** | **= gross, 56.21 core-min** | the single run row is 843 s, well under the 3,600 s stall rule, which therefore matches nothing |
| **Ratio (cleaned/predicted)** | **0.390×** | under the estimate |
| **Waste** | **0.000 core-min** | no discarded or re-launched arm; the moved preflight artifact consumed zero compute |
| Dollars, **DERIVED NOT MEASURED** | **$0.0481** actual against **$0.1231** predicted | 0.9369 core-h × $0.0513/core-h, c7a.4xlarge, owner-stated; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5) |

**No cap was breached.** The row's registered share is 144 core-min and the triple cap is 900
core-min; 56.21 core-min is 39 % of the row's share. The fleet safety ceiling that would have
applied (3 × 144 = 432 core-min) was never approached — and, per §7 below, was never actually
armed.

### 6.1 Gap attribution — the prior reading is **confirmed in its direction and overturned in its conclusion**

The prior reading called the gap **misprediction, not contention**, reasoning that a busy box
slows a run and cannot produce an under-run. **The direction is right. The conclusion that
contention is absent is wrong, and the measurement that overturns it is a rate comparison against
this case's own record.**

Two terms, in **opposite** directions:

**(a) Misprediction, over-predicting — the dominant term.** Registration §8 anchored `t_cell` at
**4.05e-6 s** per cell per iteration from the *jet-flap lane's* super-linear `N^0.55` model. The
run's actual is **1.5815e-6 s** — the anchor is **2.56× high**. And the lab already held a better
anchor: this case's **own** completed feasibility arm `FEAS_L1_dp1000_U20_A2` (31,752 cells,
15,000 iters, 4 ranks, same box, 2026-08-31) measured **1.3123e-6 s** per cell per iteration.
Against that, the registration's anchor is **3.09× high**. That measurement was already a row in
this very ledger — **`C-20260833`**, landed 2026-08-31, three days before this launch, stating in
its own words *"an L1 arm costs ~41 core-min, not 10."*

> **The calibration finding, and it is the useful one:** the registration priced this rung from a
> **foreign lane's fitted model** while a **direct measurement of the same case, same solver, same
> rank count, same box** stood in the lab's own cost ledger. The next F28G row should anchor on
> `C-20260833`, not on the jet-flap fit.

**(b) Contention, slowing — present, measured, and masked by (a).** Per cell per **outer**
iteration, F28G L1 ran at 1.5815e-6 s against the feasibility arm's 1.3123e-6 s — **1.205×
slower**. Cell count explains only 1.1195× of the 1.349× wall ratio, and is already divided out of
the per-cell figures. The slowdown is **not** more work: F28G's mesh needed **fewer** GAMG `p`
linear iterations per outer iteration (**14.617** vs **18.136**). Normalised to actual linear
work, F28G is **1.49× slower per unit of solver work** (0.1082e-6 vs 0.0724e-6 s per cell per `p`
linear iteration). Decomposition imbalance is excluded (max/min 1.019 vs 1.008).

**Net:** the ratio 0.390 is the product of an over-prediction and a slowdown pulling against each
other. **Net of the measured 1.205× slowdown, the misprediction alone is 0.32×.** Reporting 0.390
as pure misprediction would *understate* the misprediction — which is why (b) is named separately
and not absorbed into the ratio (`COMPUTE_BUDGET_CHARTER` §6, applied here to contention as it is
to waste).

**What this lane could not verify, stated plainly.** No contemporaneous box-load record covering
21:58–22:12Z exists in any artifact found on disk, so the prior reading's "56–58 % busy" figure is
**neither confirmed nor refuted here**. The contention term above rests on the **rate comparison**,
not on a load log. Corroborating but not contemporaneous: at 23:06Z the box read load average
34.68 on 16 cores — oversubscribed by 2.2× — so contention is a standing condition on this box,
not a hypothesis. **The 1.205× is measured; its attribution to contention specifically (rather
than to some other machine-state effect) is an inference and is labelled one.**

**Ledger row:** landed in `docs/COST_CALIBRATION.md` with this record, id tool-allocated by
`scripts/append_record.py --allocate-id`.

---

## 7. A gap in this rung's RECORD that is **not** a defect in the run

**Stated in those words because that is what it is.**

The queue daemon (pid 1664) started at **15:35:14** on 2026-09-03. **Four commits** subsequently
landed on `scripts/queue_runner.py` — `0ac4eb42` (16:13:39), `d2005e7c` (17:29:27), `1c81275b`
(17:37:18), `26361970` (19:02:01) — and those four are where the grading-freeze recorder and the
report-only fleet safety ceiling were introduced. **The running module predates all four.**

**Consequence, measured rather than assumed:** the launched row
`verification/queue/cfd/launched/F28G_L1_dp1000_U20.json` carries the underscore-prefixed keys
`_schema_note`, `_field_classes`, `_launch` and **no `_grading_freeze` stamp and no fleet-ceiling
reading**. Peer rows launched by a current module do carry them (heat-transfer's `P_Ts_f`,
`P_Ts_m`, `P_q_f`, `P_q_m` carry `_fleet_ceiling`; verification's `VR1`–`VR6` carry `_ceiling`).
The recorder was **not in the running module**, so it recorded nothing.

**This is a gap in the record, not a defect in the run.** The run's own artifacts are complete and
its verdict does not rest on the missing stamp. The two facts the stamp would have carried are
independently established in this document:

- **The grading path**: both graders hash to the same blob at worktree, `95974b79`, `HEAD` and
  `7f032d84` — §1 above, verified by this lane, not relayed.
- **The launcher of record**: `cases/F28_DUCTED_ACTUATOR_DISK/run_f28.sh` hashes to
  **`51c5643a4f1ef0d29340772d596f106aafdfdebd`** identically in the worktree, at the frozen prereg
  commit `95974b79`, and at `HEAD` (sha256
  `d99b5bbe48e16e92bb71f2fd41ca14d1bdb6e185c31731c59ee880aa9d72b253`). **The code of record is not
  in doubt.**

**It is not papered over and it is not disqualifying.** The honest statement is that for this row
the freeze property is carried by *this document's* verification rather than by the launcher's own
contemporaneous stamp — which is a **weaker** form of the same guarantee, in the same way §A4.3's
grading-path pin is weaker, and it is labelled weaker rather than presented as equivalent. The
queue row's own `grading_freeze_note` anticipated exactly this: *"IF THE FREEZE RECORDER READS
THIS ROW AS UNPINNED … THAT READING IS CORRECT AND IS NOT TO BE SUPPRESSED."*

**Forward-only referral (not actioned by this lane):** rows launched by a daemon instance older
than its source carry no stamp, and nothing on the row says so. A daemon that recorded its own
module's commit at launch would make this self-evident instead of requiring a reader to compare
process start time against `git log`. Referred to `cfd-supervisor`; **the daemon was not touched,
restarted, or reconfigured by this lane, and no queue row was edited.**

---

## 8. Artifact inventory

**Committed with this record**

| path | what |
|---|---|
| `verification/campaign/F28G_L1_RESULTS.md` | this document |
| `verification/runs/F28_runs/F28G_L1_dp1000_U20/GRADING_OUTPUT.txt` | the grading transcript — selftest summary, the `--grade` refusal, and the live refusal control |
| `verification/runs/F28_runs/F28G_L1_dp1000_U20/grade_spec_L1.json` | the spec handed to the frozen grader |
| `docs/COST_CALIBRATION.md` | the §6 calibration row |

**On disk, deliberately not committed** — bulk solver output:
`log.simpleFoam` (34.4 MB), `log.decomposePar`, `log.reconstructPar`, `processor0..3/`, `15000/`,
`postProcessing/`. Every figure in §3, §4 and §6 cites one of these by path and they remain on
disk at the run root.

**Unchanged by this record:** the frozen registration, both graders, `run_f28.sh`, and the queue
row. Nothing frozen was edited (standing rule 6); no submission was made (standing rule 7).

---

## ADDENDUM 1 — 2026-09-03 — §4.1's "and flat" is refined, and the refinement STRENGTHENS the finding

**Version:** v1.0 → **v1.1**. This document carried no version line before this addendum; **v1.0**
denotes its state at commit `23eeff7e`.

**Rule-6 assertion: lines whose number changed above this section: 0.** Nothing above was edited.
Both addenda are appended at the foot. §4.1's original sentence is struck by this addendum, not
rewritten, and remains readable at its original line numbers.

**The struck words.** §4.1 reads *"At iteration 15,000 the gating **initial** residual for `p` is
**0.1578798513** — five orders of magnitude above its 1e-6 criterion, **and flat**."*

**The value and the five-order gap are unchanged and are re-verified.** `0.1578798513` occurs
**exactly once** in the 656,692-line `log.simpleFoam`, at line **656652**, inside the `Time = 15000`
block that opens at line 656647, and it is the **first** of the two `p` solves in that block.

**"And flat" is wrong, and the correct description is worse for the run, not better.** Measured over
the last 4,000 iterations, the gating `p` residual has **min 0.1171, max 0.5132, mean 0.1855,
stdev 0.0375**; across the whole run it **never falls below 0.0642**. It does not descend and it
does not settle: it **wanders across a factor of 4.4 with no downward trend**.

**This is stronger evidence of non-convergence than "flat" was, not weaker.** A flat residual is at
least stationary — it is consistent with a solution that has stopped moving and is merely stuck
above its criterion. A residual wandering across a factor of 4.4 with no trend is **further** from
convergence than a flat one: the iterate is still changing substantially every outer iteration and
is not approaching a fixed point at all. **The verdict `NOT A RESULT` is undisturbed and this
addendum does not touch either registered ground.**

**Neither ground rests on this figure.** The HIT-CAP ground is structural (`ITER_CAP = 15000`
against the run's `endTime`, `analyse_f28g.py:245`) and reads no residual value; the not-plateaued
ground reads `postProcessing/forcesDuct/0/force.dat`. **The 0.1579 figure is corroborative, not
load-bearing** — and it is correct.

**Provenance of this addendum:** the figure was challenged and the challenge was withdrawn in full
after re-measurement. The full reconciliation, including how the challenge arose, is
`verification/campaign/F28G_L1_RESIDUAL_RECONCILIATION.md`.

---

## ADDENDUM 2 — 2026-09-03 — §5's "three separate configurations" is corrected to FOUR, and the fourth is the informative one

**Rule-6 assertion: lines whose number changed above this section: 0.**

**The struck words.** §5 reads *"…given that the `p` residual has now failed to move in 15,000
iterations on **three separate configurations**…"*. **The count is four.** It was asserted, not
counted; this addendum counts it from the run tree.

Every run root under `verification/runs/F28_runs/` holding a `log.simpleFoam` was read. **Four**
reached the 15,000-iteration cap, and **`SIMPLE solution converged` occurs 0 times in every one**:

| run root | cells | disk source (`constant/fvOptions`) | `farfield` BC | gating `p`, last-500 band | last |
|---|---|---|---|---|---|
| `FEAS_L1_dp0_U20_A2` | 31,752 | **`U ((0.0 0 0) 0)` — SOURCE OFF** | `totalPressure` | 0.3317 – 0.6885 | 0.5145 |
| `FEAS_L1_dp1000_U20_A2` | 31,752 | `U ((166666.66666666666 0 0) 0)` | `totalPressure` | 0.3110 – 0.5269 | 0.3669 |
| `FEAS_L1_dp1000_U20_A2_BCPROBE` | 31,752 | `U ((166666.66666666666 0 0) 0)` | **`slip`** | 0.0579 – 0.3465 | 0.1416 |
| **`F28G_L1_dp1000_U20`** (this row) | 35,544 (`mesh_A4/L1`) | `U ((166666.66666666666 0 0) 0)` | `totalPressure` | 0.1478 – 0.4014 | **0.1579** |

The four configurations span **two meshes**, **two disk loadings including OFF**, and **two
farfield boundary conditions**. The remaining four logs in that tree are short aborts (19–32
iterations) or hold no `p` solves at all, and are evidence of nothing either way.

**`FEAS_L1_dp0_U20_A2` is the single most informative row and it had not been used against this
question.** It carries `U ((0.0 0 0) 0)` — the actuator-disk source is **exactly zero** — and it
plateaus **highest of the four**. **That exonerates the actuator disk as the mechanism by
measurement rather than by argument.** Corroborating, from the same dictionaries: even when on, the
source is `((166666.66666666666 0 0) 0)` — constant `Su`, **`Sp = 0`**, purely explicit with no
velocity dependence — so no source feedback loop exists to sustain a limit cycle in the first place.

**No mechanism is asserted here.** What is established is negative and specific: the plateau is
**not** caused by the actuator-disk source, and it survives a change of mesh and a change of
farfield boundary condition. Candidate mechanisms and the measurement that separates each are in
the reconciliation document named in Addendum 1; **the successor decision remains a supervisor
referral and a cap raise remains Sanaa's alone**, exactly as §5 states.

**Nothing in either addendum alters a gate, threshold, cap or label, and the verdict is
`NOT A RESULT` as issued.**
