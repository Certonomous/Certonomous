# K0d. Turbulent mixed convection, Blay–Mergui–Niculae ventilated cavity: RESULTS

# VERDICT: `BLOCKED`

**Written 2026-09-03. THIS FILE RESOLVES NOTHING.** It is a **transcription of an
existing verdict into the file where a reader looks for it**, and it is **NOT a
re-grade**. No comparator was run to produce it, no number in it is new, and
every figure below cites the record that established it.

**Why it exists.** K0d is a **registered rung with 105.10 core-minutes of real
compute on disk**, and until today its verdict lived only inside a ruling
document. A reader who went to `K0d_RESULTS.md` — where this campaign puts every
other rung's verdict — **found nothing**, while two arms' fields sat in
`verification/runs/F14-cooling-ladder/K0d_runs/` with no closure record on the
tree's face. That gap is what this file closes, and it closes **only** that gap.

**Sanaa's 2026-09-03 17:30Z wording stands: no re-grading of past results unless
a specific comparator is shown to have moved. None has been shown to have moved,
and none is claimed to have moved here.**

---

## 1. THE VERDICT, AND WHERE IT WAS ISSUED

**`BLOCKED`.** Issued by the heat-transfer supervisor on 2026-08-25 in
**`docs/campaigns/F14-cooling-ladder/K0d_FIRE_RULING_2026-08-25.md`**:

| citation | text |
| --- | --- |
| **line 4** | *"**Verdict: `BLOCKED`.**"* |
| **line 58** | *"**K0d DOES NOT FIRE.** Not tonight, not on a sixth amendment."* |

The rung's own forensics record independently **recommended** the same verdict:

| citation | text |
| --- | --- |
| **`K0d_FORENSICS_2026-08-25.md` line 1052** | *"**Rung verdict recommended: `BLOCKED`. Every graded row `NOT A RESULT`.**"* — on three independent grounds: `P` (Blay `NOT OBTAINED`), `G` (the L2 parity contradiction), `V` (the reader disagreement) |
| **same, line 1054** | *"**Never `GATE REACHED` — that asserts a gate was reached, and none was.**"* |

**Every graded row is `NOT A RESULT`.** No row of K0d is a measurement of
anything the rung set out to measure.

---

## 2. WHAT BLOCKS IT, AND WHY THAT IS NOT THIS FILE'S TO SETTLE

**The defining Rayleigh number is over-determined, and TWO FROZEN AMENDMENTS
RECONCILE IT DIFFERENTLY.** `K0d_FIRE_RULING_2026-08-25.md` §1, lines 15–32,
states it and prints the arithmetic:

> **lines 27–29:** *"`AMENDMENT 1` §A1.2 reconciled this by moving `ν` to
> 1.569e-5. `AMENDMENT 5` §A5.7 reconciled the SAME contradiction by moving `β`
> to 3.26577e-3. Both are frozen, both are in the document, **and they
> disagree.**"*

> **lines 30–32:** *"A pre-registration whose own amendments settle its defining
> dimensionless parameter two different ways does not determine what physics is
> being simulated. **That is not a gap another amendment fills; it is a
> contradiction.**"*

**THAT CONTRADICTION IS NOT SETTLED BY THIS FILE. It is not this lane's to
settle and it is not the supervisor's to settle.** Standing rule 6 puts both
amendments beyond editing, and the ruling itself escalated rather than took the
call:

> **lines 61–66:** *"**RECOMMENDED, AND ESCALATED RATHER THAN TAKEN** ... **Retiring
> a frozen pre-registration is not a call this team takes alone.**"*

**Writing this record must not appear to settle it, and does not.** If a reader
takes anything from §2 it should be that the contradiction is still open and
still unruled.

**A second, independent blocker is untouched by everything above.** The primary
reference is not held:

> **lines 103–104:** *"it would not change that **G6 stays `PENDING` on Blay
> 1992, which is `NOT OBTAINED`.**"* — the sentence sits inside §6, "WHAT IS NOT
> CLAIMED", where the ruling lists what a re-registration would *still* not fix.

`THERMAL_CAPABILITY_STATE.md` §4 lists **Blay, Mergui & Niculae 1992** under
**NOT OBTAINED**, blocking *"all of K0d — the entire mixed-convection class"*.
**Even if the Rayleigh contradiction were ruled tomorrow, K0d would still have
nothing to grade against.**

---

## 3. SUPERSESSION — K0f IS THE SUCCESSOR

**`K0f` supersedes `K0d`.** The chain, as recorded:

1. **`K0d_PREREGISTRATION.md` is superseded by `K0d_REREGISTRATION.md`**, which
   governs (`K0d_FORENSICS_2026-08-25.md` line 37: *"`K0d_PREREGISTRATION.md` IS
   SUPERSEDED. `K0d_REREGISTRATION.md` GOVERNS."*). Neither file is edited; all
   five amendments stay on disk byte-unchanged.
2. **`K0f_PREREGISTRATION.md` is the successor rung**, adopting
   `K0d_REREGISTRATION.md` §§1, 1.1, 1.2, 1.3 **by citation, byte-unchanged**
   (`K0f_PREREGISTRATION.md` line 68), and explicitly **not editing** the K0d
   documents (line 84).
3. **The successor's id is `K0f`, not `K0e`.** `K0f_PREREGISTRATION.md` §−1
   records why: `K0e` was already in use in this campaign for a different physics
   problem — the forced-convection flat plate — so an id that collided with a
   live rung would have defeated the very ruling that demanded the successor be
   distinguishable.
4. **K0f has run and been graded.** Its verdict is **`GATE REACHED`, tally 0 of
   10, every graded row `NOT A RESULT`** (`K0f_RESULTS.md`; `COST_CALIBRATION.md`
   row `C-137`). **That is K0f's verdict and it is not K0d's.**

---

## 4. WHAT IS ON DISK, MEASURED

`verification/runs/F14-cooling-ladder/K0d_runs/` holds **ten arm directories**.
**Two carry a solver log; eight do not.**

| arm | `log.blockMesh` | `log.solve` | time directories |
| --- | --- | --- | --- |
| **`M1_c`** (`kOmegaSST`, L1) | yes | **yes** | `0`, `36000`, `40000` |
| **`M2_c`** (`RNGkEpsilon`, L1) | yes | **yes** | `0`, `36000`, `40000` |
| `B_hi` | yes | **no** | `0` only |
| `C_lam` | yes | **no** | `0` only |
| `I_hi` | yes | **no** | `0` only |
| `M1_f` | yes | **no** | `0` only |
| `M1_m` | yes | **no** | `0` only |
| `M1_m_seed` | yes | **no** | `0` only |
| `M2_f` | yes | **no** | `0` only |
| `M2_m` | yes | **no** | `0` only |

**The two solves that ran, ran cleanly and reached `endTime`.**
`K0d_FORENSICS_2026-08-25.md` ADDENDUM 4 §D1 records both at `Time = 40000`, one
`End` line, `ExecutionTime` count 40000, and every registered field present *for
that case's own closure* — `M1_c` all 8 including `omega`, `M2_c` all 8 including
`epsilon`. The final lines of the two logs read `ClockTime = 3215 s` (`M1_c`) and
`ClockTime = 3091 s` (`M2_c`).

### 4.1 CLAUSE 1 IS UNVERIFIABLE, AND THAT IS A LAUNCH-PROTOCOL GAP, NOT A SOLVE FAILURE

**`K0d` had no launcher.** The L1 pair was started with an ad-hoc `setsid` +
`timeout` invocation that **never captured the solver's return code**, so **no
`STATUS.<case>` file was ever written**, so **clause 1 of the strict completion
rule cannot be checked for either arm** (`K0f_PREREGISTRATION.md` line 504:
*"**K0d HAD NO LAUNCHER AT ALL.**"*).

`K0d_FORENSICS_2026-08-25.md` ADDENDUM 4 §D2, lines 952–991, prints the
clause-by-clause result:

| clause | `M1_c` | `M2_c` |
| --- | --- | --- |
| **1 `STATUS.<case>` reports `rc=0`** | **ABSENT** | **ABSENT** |
| 2 `End` line | PASS | PASS |
| 3 last time == `endTime` | PASS | PASS |
| 4 registered fields, per closure | PASS (8/8) | PASS (8/8) |
| 5 `ExecutionTime` count == `endTime` | PASS | PASS |
| 6 age guard, fields newer than `0/T` | PASS | PASS |

**Both arms are `NOT DONE` under the strict completion rule**, on that one
clause, and the record is explicit that the `rc` **was never captured and is
unrecoverable** — writing `rc=0` afterwards would be back-dating a measurement
nobody took (lines 975–981). **Standing rule 4 is all-or-nothing precisely so
that it cannot be satisfied by a plausible reconstruction.**

**Nothing in §4.1 changes the verdict.** K0d is `BLOCKED` on the §2 grounds
whether or not those two arms are `DONE`.

---

## 5. COST — ALREADY ACCOUNTED, AND NOT RE-COUNTED HERE

**The 105.10 core-minutes are already reconciled in the calibration ledger at
`docs/COST_CALIBRATION.md` row `C-99` (line 175). This file adds no ledger row
and re-counts nothing.**

| | |
| --- | ---: |
| predicted (2 × the registered POINT of 43.50) | **87.00 core-min** |
| actual gross | **105.10 core-min** = (3 215 + 3 091) wall s × 1 rank ÷ 60 |
| actual cleaned | **105.10 core-min** — gross == cleaned, **no stall** (both walls under the 3 600 s threshold) |
| **ratio actual/predicted** | **1.208** |
| derived cost | **$0.0899** at $0.0513/core-h — **DERIVED, NOT MEASURED**, `cost_basis` reported-by-owner |
| share of the rung's 2 748.64 core-min ceiling | **3.82 %** |

**Attribution, as `C-99` records it: CONTENTION, measured rather than guessed.**
The measured solve rates were 3.140e-06 (`M1_c`) and 3.019e-06 (`M2_c`)
s/cell-iteration against the registered POINT rate of 2.549e-06 — ratios 1.232
and 1.184, reproducing the 1.208 overall. **The gap is RATE, not iteration count:
cell count and iteration count were exactly as registered.** The box carried 5–9
foreign solvers throughout, with measured occupancy at launch 8.10 of 16 cores.

**Waste, named separately per `COMPUTE_BUDGET_CHARTER.md` §6 and NOT folded into
the ratio: ~0.17 core-min** of meshing across two failed builds. **Zero solver
iterations were wasted — both failures died before any solve.**

**THE RUNG EARNS NOTHING FROM THIS SPEND.** 105.10 core-minutes bought two arms
whose every graded row is `NOT A RESULT` and which are `NOT DONE`.

---

## 6. ONE DATING NOTE, RECORDED SO A COLD READER IS NOT MISLED

`K0d_FIRE_RULING_2026-08-25.md` lines 4–6 read *"Zero core-minutes spent against
a registered POINT of 829.36. K0d remains **FROZEN, ARMED, UNFIRED**; `K0d_runs/`
does not exist."*

**That was true when the ruling was written and is not true now.** The L1 pair
was fired later the same day under `K0d_REREGISTRATION.md`, and `C-99` accounts
for it. **The ruling is not edited and is not corrected** (standing rule 6): its
verdict is unaffected, and this paragraph exists only so that a reader who
compares the two records does not read the discrepancy as an error in either.

---

## 7. WHAT THIS FILE DOES NOT DO

- **It does not settle the Rayleigh contradiction.** Two frozen amendments still
  reconcile the defining parameter differently, and that call is not this team's
  (§2).
- **It does not re-grade anything.** No comparator was run; no comparator is
  claimed to have moved.
- **It does not unblock K0d.** Blay 1992 is still `NOT OBTAINED`.
- **It does not retire, widen or amend any standard, gate threshold or charter
  clause.** Those are reserved to Sanaa.
- **It does not revive K0d as a live rung.** K0f is the successor (§3).
- **Nothing here was sent, emailed, filed, uploaded, registered, posted or
  commented. Submissions are PARKED.**

---

*Transcribed by a heat-transfer lane on the supervisor's decision, 2026-09-03.
This lane assigned no verdict: the `BLOCKED` above is the supervisor's of
2026-08-25, quoted by line.*
