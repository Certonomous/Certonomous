# JF1G — JET-FLAP GRID CONVERGENCE AT `C_mu = 0.1` — GRADING RECORD

**RULED 2026-09-04 by `cfd-supervisor`. Prepared by the `cfd` lab-lane; the
verdict and the rulings in §9 are the supervisor's own.** The non-delegable §3
checks have now been performed — §9.0 states exactly which were discharged
personally and which were not.

**SUBMISSIONS PARKED.** Nothing in or derived from this document is sent, filed,
uploaded, posted or registered outside this box.

---

## 0. THE FROZEN PATH, HASH-VERIFIED BEFORE ANY RESULT WAS READ

| item | value |
|---|---|
| Registration | `verification/campaign/JF1G_GRID_CONVERGENCE_PREREGISTRATION.md` |
| Freeze commit | **`038f4bca`**, 2026-09-01 16:08:29Z |
| Blob pinned by every run | `0b9476598ef4467dae3f9bcc0e4cf113254bd8e0` |
| Amended since freeze? | **No.** `git log` returns exactly one commit for the file; the working tree is clean against `HEAD`. |
| Comparator | `verification/runs/JF1_jet_flap/analyse_jf1_ladders.py`, committed `74c4f5fb`, worktree blob `ef4c0b0c…` **== the `HEAD` blob** (verified by `git rev-parse HEAD:<path>`) |
| Comparator selftest | **PASS** — see §4 |

The gate, threshold, cap and label were read from `038f4bca` **before** any
result file was opened, and the grading below is against that document only.

**Disclosed:** the comparator was committed *after* the freeze commit. §11 fixes
the grading *path* at the freeze and requires the comparator be *hashed against
its committed blob at grading time*; that hash check is done and passes. Whether
§11 additionally requires the comparator file itself to pre-date the freeze is a
reading question **referred to the supervisor**, not settled here.

---

## 1. WHAT ACTUALLY RAN — MEASURED FROM DISK, NOT ASSUMED

Eight stages exist on disk. Four reached the solver; two refused at the mesh
gate; two of the solver runs were stopped at their cap.

| stage | `rc` | stage at exit | outcome class |
|---|---|---|---|
| `JF1G_P0_C1_CMU010_A0` | 0 | `done` | **completion** |
| `JF1G_P0_C2_CMU010_A0` | 0 | `done` | **completion** |
| `JF1G_P0_C3_CMU010_A0` | 5 | `checkMesh` | **mesh-gate refusal** — no solver ran |
| `JF1G_P0_C4_CMU010_A0` | 7 | `simpleFoam` | **cap stop** (TERM at 536/8000) |
| `JF1G_P1_C1_CMU010_A0` | 0 | `done` | **completion** |
| `JF1G_P1_C2_CMU010_A0` | 6 (`solver_rc 124`) | `simpleFoam` | **cap stop** (timeout at 24210/30000) |
| `JF1G_P1_C3_CMU010_A0` | 5 | `checkMesh` | **mesh-gate refusal** — no solver ran |
| `JF1G_P1_C4_CMU010_A0` | 7 | `simpleFoam` | **cap stop** (TERM at 528/30000) |

Plus `JF1G_P1_C1_CMU010_A0.attempt1_FAILED_2026-09-03T190419Z_PRESERVED` — a
launcher refusal at `rc=9`, stage `dicts`, 0 solver compute. Triaged in §6.

### 1.1 The strict completion rule (CLAUDE.md rule 4), executed clause by clause

Read from each run's own `log.simpleFoam`, `system/controlDict` and time
directories. **Not** taken from any `RUN_STATUS` file.

| clause | P0_C1 | P0_C2 | P1_C1 | P0_C4 | P1_C2 | P1_C4 |
|---|---|---|---|---|---|---|
| `rc = 0` | ✅ | ✅ | ✅ | ❌ 7 | ❌ 6/124 | ❌ 7 |
| `End` line present | ✅ 1 | ✅ 1 | ✅ 1 | ❌ 0 | ❌ 0 | ❌ 0 |
| last time == `endTime` | ✅ 8000 | ✅ 8000 | ✅ 30000 | ❌ 537≠8000 | ❌ 24210≠30000 | ❌ 529≠30000 |
| fields present at `endTime` | ✅ `U p k omega nut` | ✅ | ✅ | ❌ no `endTime` dir | ❌ | ❌ no `endTime` dir |
| `ExecutionTime` count == `endTime` | ✅ 8000 | ✅ 8000 | ✅ 30000 | ❌ 536 | ❌ 24209 | ❌ 528 |
| **age guard** (every `endTime` field newer than the case's own `0/`) | ✅ | ✅ | ✅ | n/a | n/a | n/a |

Age-guard evidence (mtime epochs, strictly increasing in every case):
`P0_C1` `0/` 1788279050 → `8000/` 1788280354; `P0_C2` `0/` 1788279051 →
`8000/` 1788283301–2; `P1_C1` `0/` 1788462651 → `30000/` 1788468394.

> **Three completions: `P0_C1`, `P0_C2`, `P1_C1`.**
> **Three cap stops: `P0_C4`, `P1_C2`, `P1_C4`. A cap stop is NOT a completion
> and is not graded as one.**
> **Two mesh-gate refusals: `P0_C3`, `P1_C3`.**

**No run exceeded its registered cap.** `P1_C2` reached 240.0333 core-min against
a 240.0 cap — the `timeout` wrapper fired and the 2 s excess is wrapper teardown,
not an overrun. Rule 12's "an overrun stops the run" was enforced by the
launcher, in advance, exactly as the queue rows registered.

### 1.2 The cap stops are not "nearly converged" — measured

| run | `CL` at stop | `|ΔCL|` over the final 250 iterations |
|---|---|---|
| `P0_C4` | 0.49347765 @ 536 | **1.258e-01** |
| `P1_C4` | 0.49115622 @ 528 | **1.289e-01** |
| `P1_C2` | 0.55192479 @ 24209 | 1.444e-04 |

The two C4 rows were still moving by ~25 % of the value per 250 iterations. They
are `NOT A RESULT` on the physics as well as on the bookkeeping, and the
`STOP_RECORD.txt` in each root asserting that outcome is confirmed, not merely
relayed.

*Bookkeeping-vs-physics split (Sanaa's universal rule 2026-08-26): `P1_C1`'s
infrastructure fields are all clean — it is a genuine completion. Its failure in
§3 is a **physics** failure at Gate G3, and the two are reported separately.*

---

## 2. THE NUMERICS EACH RUN ACTUALLY CARRIED — CHECKED ON DISK

Because a launcher defect (§6) could have silently left Pass 1 running Pass 0's
numerics, every run's own staged dictionaries were read rather than assumed.

| stage | `endTime` | `residualControl` on `p U k omega` | matches frozen §4? |
|---|---|---|---|
| `P0_C1` `P0_C2` `P0_C3` `P0_C4` | 8000 | 1e-06 | ✅ |
| `P1_C1` `P1_C2` `P1_C3` `P1_C4` | 30000 | 1e-08 | ✅ |

**Pass 0 is not contaminated and Pass 1 did take the tightened control.** Verified
directly from `system/controlDict` and `system/fvSolution` in each run root.

---

## 3. THE GATES OF `038f4bca`, EVALUATED IN THE FROZEN ORDER

### Gate G1 — mesh similarity (§2.2) → **BREACHED**

Every **numeric** similarity clause holds, recomputed from the emitted meshes'
own `log.build_jf1`:

| pair | `n_base` | `n_side` | `Ni` | `Nj` | `y1` | cells | `g_fine^r − g_coarse` |
|---|---|---|---|---|---|---|---|
| C2/C1 | 1.5000 | 1.5000 | 1.5000 | 1.5000 | 1.50000 | **2.25000** | −2.97e-04 |
| C3/C2 | 1.5000 | 1.5017 | 1.5016 | 1.4966 | 1.50000 | **2.24734** | +1.22e-04 |
| C4/C3 | 1.4815 | 1.4978 | 1.4973 | 1.5045 | 1.50000 | **2.25273** | −2.67e-04 |

Tolerances: counts 1.5 ± 0.02, `y1` 1.5 ± 1e-9, cells 2.25 ± 0.02, identity
± 1e-3 — **all satisfied.** Complete layers inside `delta`: 47 → 70 → 105 → 159,
floor 30, increasing. Emitted cell counts are **exactly** the frozen §2 table:
39,984 / 89,964 / 202,180 / 455,456. The §1 `--n-rad` repair worked.

*Margin note: C4/C3 `n_base` = 1.4815 clears the 1.48 floor by 0.0015. The C4
level is a §7 contingency and its ratios are not in the frozen §2.2 tolerance
table, which lists C2/C1 and C3/C2 only. Flagged, not ruled.*

**The one breached clause is `checkMesh` — "`Mesh OK` on every level":**

| level | max aspect ratio | max non-orthogonality | severely non-orth. faces | max skewness | `Mesh OK` |
|---|---|---|---|---|---|
| C1 (39,984) | 859.95 | 57.53 | 0 | 2.296 | **yes** |
| C2 (89,964) | 634.44 | 67.64 | 0 | 2.213 | **yes** |
| C3 (202,180) | **1012.24** | 75.14 | 133 | 2.181 | **NO — `Failed 1 mesh checks`** |
| C4 (455,456) | 796.89 | 81.35 | 471 | 2.176 | **yes** |

Two cells out of 202,180 fail the study. Already raised in
`verification/campaign/JF1G_MESH_GATE_FINDING.md`; **this record adds the C4
evidence**, which was not available when that finding was written.

**Gate G1 breach → `NOT A RESULT` for the whole study** (§5 G1, §6.1 refusal 2).

#### 3.1 The refinement is NON-MONOTONE in aspect ratio — and a pre-registered prediction was wrong because of it

Max aspect ratio across the family: **859.95 → 634.44 → 1012.24 → 796.89**. It
falls, spikes past the 1000 ceiling at C3, then falls again at C4. **A nested
level-set assumption does not hold on this metric and must not be assumed.**

This is not an abstraction. `verification/queue/cfd/launched/JF1G_P0_C4_CMU010_A0.json`
registered, in advance: *"C4 is the next refinement of the same family, so the
aspect ratio is predicted HIGHER still and the refusal is predicted to REPEAT at
rc=5."* Estimate **0.15 core-min**, outcome class *mesh refusal*.
`JF1G_P1_C4_CMU010_A0.json` registered the same. **Both predictions were wrong.**
C4's aspect ratio came in at 796.89, `checkMesh` printed `Mesh OK`, and both rows
proceeded to solve for ~97 core-min each instead of ~0.15.

The prediction was falsifiable, was recorded before the run, and was falsified —
which is the registration mechanism working. The reasoning error is named
exactly: **monotonicity in refinement was assumed for a metric that does not have
it.** Costed in §5.

*Separately measured and worth the supervisor's eye: max non-orthogonality **is**
monotone and rises with refinement — 57.53 → 67.64 → 75.14 → 81.35 — with
severely-non-orthogonal faces 0 → 0 → 133 → **471**. `checkMesh` treats aspect
ratio as a hard failure (`***`) and non-orthogonality as advisory (`*`), so
"C4 Mesh OK" is a weaker statement than it reads. **The family's quality is
degrading with refinement**, which is the opposite of what a grid-convergence
family needs, and no frozen gate currently catches it.*

### Gate G2 — `y+` < 1.0 per level → **satisfied on every level measured**

`P1_C1` max `y+` = **0.2556**; `P1_C2` = **0.2474** (Pass 0: 0.2556 / 0.2474).
Both far below the 1.0 threshold, and the fall with refinement matches the §5
expectation. C3 has no solver data; C4's `y+` series has 2 rows only.

### Gate G3 — iterative convergence per level → **BREACHED ON EVERY LEVEL**

This is a **new** finding, independent of the mesh gate. G3 requires `p`, `U`,
`k`, `omega` initial residuals below the pass's `residualControl` **at
`endTime`**. Read from the final `Time =` block of each `log.simpleFoam`:

| level | control | `Ux` | `Uy` | `p` | `k` | `omega` | below control? |
|---|---|---|---|---|---|---|---|
| `P1_C1` @30000 | **1e-08** | 3.196e-07 | 3.618e-06 | **1.276e-05** | 2.513e-05 | 1.658e-08 | **NO — all five above** |
| `P0_C1` @8000 | 1e-06 | 3.237e-07 | 3.632e-06 | **1.268e-05** | 2.550e-05 | 1.887e-08 | **NO** |
| `P0_C2` @8000 | 1e-06 | 3.756e-07 | 5.170e-06 | **2.980e-05** | 2.184e-05 | 1.126e-08 | **NO** |
| `P1_C2` @24209 | 1e-08 | 5.444e-07 | 9.118e-06 | **5.310e-05** | — | — | **NO** (also a cap stop) |

Corroborated structurally: **no run printed `SIMPLE solution converged`** — every
one exhausted its iteration count rather than meeting its control. `P1_C1` ran
30,000 iterations at a tightened 1e-08 and finished with `p` three orders of
magnitude above it.

**Gate G3 breach → `NOT A RESULT`** (§5 G3, and CLAUDE.md rule 5 clause 1: a level
not iteratively converged voids the triple whatever its value).

**L-235 — the clipping disclosure, and it is the likely mechanism.** Over the
final 500 iterations, `bounding k` / `bounding omega` counts:
`P1_C1` **495 / 167**, `P1_C2` **378 / 11**, `P0_C1` **494 / 166**, `P0_C2`
**380 / 10**. `P1_C1` is clipping `k` in 99 % of its final 500 iterations while
its forces sit still to 4.1e-07. **That is stationary-and-clipping-held, never
converged** — exactly the condition L-235 exists to name, and the honest
candidate explanation for residuals that plateau at 1e-05 and never fall.

### Gate G4 — the tightness rule → **CANNOT BE EVALUATED**, but its registered risk is REFUTED

G4 needs `min(D21, D32)`. `D32` requires C3, which never solved. **G4 is not
evaluable and the comparator correctly refuses to emit `p` or a GCI.**

What Pass 0 *did* deliver is the number it was registered to deliver:

> **`D21` = |CL_C2 − CL_C1| = 3.075340e-03** (Pass 0), **3.077953e-03** (Pass 1,
> C2 not at `endTime`).

§9 registered the *most likely failure* as G4 failing because `CL` is already
grid-insensitive at 40k cells, naming ~1.2e-05 as the margin figure. Measured
`D21` is **256× that**. On the C1/C2 pair alone,
`max(eps) = 2.261e-05 ≤ 0.1 × D21 = 3.075e-04` — satisfied with a factor of 13.6
in hand. **The registration's own headline risk did not land**, and Pass 0
discharged its entire registered purpose. Recorded as a pre-registered
expectation that was wrong in the safe direction.

### Gates G5, G6, G7 — **NOT REACHED**

No triple exists. Only two of the three registered levels have solver data, and
both fail G3. Under rule 5 the order of evaluation is not negotiable: clause 1
(a level not iteratively converged) fires before any classification, so **no
observed order `p`, no GCI and no band may be quoted**, and none is.

---

## 4. THE PLANTED CONTROLS (CLAUDE.md rule 3) — RUN, AND PASSING

`analyse_jf1_ladders.py selftest` → `SELFTEST PASS`, `rc = 0`:

- **`CL` reader**: plant `1.234e-03` added to a copy of the control
  `coefficient.dat`, read back as **1.234000000000e-03**; the reader returns the
  control's recorded value **0.54884644**. The reader is proven able to see a
  non-zero.
- **Richardson VALUE control** (`N-T8`): synthetic power-law triple returns
  `p = 2.000000000000` (|d| 1.47e-14) and `f_ext = 0.548800000000000`
  (rel 2.02e-16); the identity `frozen + corrected == 2 f_fine` HOLDS; the
  defective sign form is confirmed distinguishable, so the control is not vacuous.
- **Classifier**: `(3,2,1)→DIVERGENT`, `(1,3,2)→OSCILLATORY`, `(5,5,5)→EXACT`.
- **Clipping counter**: returns **494** on the control log and **0** on the same
  log with `bounding k` removed. **The zero has a live non-zero beside it** —
  every clipping count in §3 is therefore evidence rather than an unexamined zero.

Every physics value quoted in this record was additionally re-read by an
independent reader written for this grading and agreed to all printed digits.

---

## 5. RULE 12 — ESTIMATE VERSUS ACTUAL

Actuals re-derived from each run's own `utc_end − utc_start` (× `ranks` ÷ 60), not
from any recorded `core_min` field. `ranks = 1` throughout.

| stage | wall s | **actual core-min** | frozen §8 est | queue-row est | ratio vs §8 | ratio vs queue | cap | gap attribution |
|---|---|---|---|---|---|---|---|---|
| `P0_C1` | 1305 | **21.7500** | 21.8 | — | **0.998** | — | 40.0 | none — the §8 unit rate was derived from this case's own sibling and it held to 0.2 % |
| `P0_C2` | 4253 | **70.8833** | 48.9 | — | **1.450** | — | 80.0 | **misprediction.** §8 scaled linearly in cells; the 2.25× cell step cost 3.26× the time. Non-linear solver scaling, not contention: nothing else was on the box at 16:10–17:21Z. |
| `P0_C3` | 4 | **0.0667** | 110.0 | — | 0.001 | — | 170.0 | **outcome-class change** — mesh-gate refusal, no solve. Not a solver-rate miss. |
| `P0_C4` | 5920 | **98.6667** | — | 0.15 | — | **657.8** | 380.0 | **misprediction of the outcome class**, mechanism named in §3.1: a mesh refusal was predicted from an assumed monotone aspect ratio; the mesh passed and the run solved. Not waste — see below. |
| `P1_C1` (attempt 1) | 0–1 | **0.0167** | — | — | — | — | 110.0 | **waste, named separately: 0.0167 core-min.** Launcher refusal, §6. |
| `P1_C1` (attempt 2) | 5745 | **95.7500** | 81.6 | 81.6 | **1.173** | 1.17 | 110.0 | **misprediction.** §8 assumed the 8000→30000 iteration scaling was linear on the same mesh; it cost 17 % more. Inside cap. |
| `P1_C2` | 14402 | **240.0333** | 183.5 | **265.8** | 1.308 | **0.903** | **240.0** | **cap stop, and the queue row predicted it exactly.** See §5.1. |
| `P1_C3` | 5 | **0.0833** | 412.4 | 0.1 | 0.000 | 0.83 | 520.0 | **outcome-class change** — mesh-gate refusal. The queue row predicted this correctly. |
| `P1_C4` | 5790 | **96.5000** | 929.1 | 0.15 | 0.104 | **643.3** | 1200.0 | **misprediction of the outcome class**, same mechanism as `P0_C4`. |
| **TOTAL** | | **623.7333** | | | | | **study cap 2320** | **26.9 % of the frozen study cap consumed** |

**Waste, named separately and never absorbed into a ratio** (`COMPUTE_BUDGET_CHARTER.md` §6):
**0.0167 core-min** — the attempt-1 launcher refusal. Nothing else in the table is
waste. The C4 rows bought real solver evidence (§1.2, §3.1) and the two mesh
refusals bought a confirmed gate finding; a spend that buys a finding is not waste.

**Derived dollars, DERIVED NOT MEASURED**, at the owner-stated `c7a.4xlarge` rate
of **$0.0513/core-h** (reported-by-owner; the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5): actual **$0.5333**; frozen study cap **$1.9836**.

### 5.1 `P1_C2`'s registered estimate EXCEEDED its own frozen ceiling — addressed explicitly

`verification/queue/cfd/launched/JF1G_P1_C2_CMU010_A0.json` registers
`cost_core_min_estimate` **265.8** against `cap_core_min_registered` **240.0** —
**the estimate exceeds its own cap by 25.8 core-min (1.11×)**. The row discloses
this in terms, calls it a `PREREGISTRATION MISMATCH`, and was launched anyway
under Sanaa's 2026-09-03 ~21:00Z launch rule (`825285bb`), which reclassifies cost
as record-and-launch rather than block.

**This is a real defect in the estimate, not a defect in the cap.** The frozen §8
figure for this row is 183.5 core-min; the queue row re-derived 265.8 from a
measured sibling rate and did not reconcile the result against the frozen ceiling
it was writing beside. An estimate that exceeds its own registered cap is a
statement that the run is *predicted to be killed*, which is a prediction of
`NOT A RESULT` — and it should have been raised as such before launch rather than
recorded as a cost note.

**What actually happened vindicates the arithmetic and indicts the framing.** The
row's `predicted_outcome` reads: *"the launcher's own `timeout … 14400` fires at
240.0 core-min before endTime 30000 is reached, giving a non-zero rc and a run
that stops at its cap."* Measured: **240.0333 core-min, `solver_rc 124`, stopped
at iteration 24210 of 30000.** The prediction was correct to four significant
figures. The ratio against the queue estimate is **0.903** — the run was cut off
at 90 % of its own predicted requirement, which is exactly what a binding cap
does.

**Referred to the supervisor:** whether a queue row whose estimate exceeds its
registered cap may launch at all, or must first raise the mismatch as a
pre-registration question. The launch rule says cost does not block; it does not
obviously say an estimate may contradict a frozen §8 cap.

### 5.2 The 3600-wall-s stall rule — GROSS published, no cleaned figure, scope REFERRED

Five rows exceed 3600 wall s: `P0_C2` (4253), `P0_C4` (5920), `P1_C1` (5745),
`P1_C2` (14402), `P1_C4` (5790). Rule 12 states *"a row over 3600 wall s is a
stall."*

**These are registered long transients, not infrastructure stalls.** Every one is
a single-rank `simpleFoam` solve whose iteration count and wall allowance were
frozen in §8 before launch, each advancing at a measured, steady rate
(`P0_C4` 0.09213 it/s, `P1_C4` 0.09288 it/s from their own `STOP_RECORD.txt`).
Nothing hung; the box was doing the work it was asked to do.

**Accordingly: GROSS figures only are published above, and NO cleaned figure is
computed.** Applying the stall rule literally would clean away 96 % of a study
that never stalled; declining to apply it is a reinterpretation of a standing
rule, which is not a lane's call. **The scope question — whether the 3600-s stall
rule was written for infrastructure hangs rather than for registered long solves —
is REFERRED to the supervisor and thence to `verification`. This lane has not
reinterpreted the standard.**

---

## 6. THE `rc=9` LAUNCHER REFUSAL — TRIAGED, AND IT IS A GUARD WORKING

`JF1G_P1_C1_CMU010_A0.attempt1_FAILED_2026-09-03T190419Z_PRESERVED` — preserved,
read, nothing deleted.

Measured cause, from `launcher.queue.attempt1.out`:

```
sed: -e expression #1, char 13: unknown option to `s'
REFUSED: residualControl 1e-08 did not take for p
```

The `residualControl` substitution used `|` as the `s///` delimiter while its own
alternation `(p|U|k|omega)` carries four unescaped `|`. `sed` died and **did not
edit the file**; the launcher's value check then caught it and refused at `rc=9`,
stage `dicts`, **0 s of solver compute**.

**This is a crash that is a finding, and the finding is favourable.** Without that
check, Pass 1's graded C1 would have silently run at Pass 0's `residualControl`
1e-06 — a plausible wrong answer under unregistered numerics, which is the worst
class of outcome this lab has. Cost of the catch: **0.0167 core-min**.

**Why it hid for two days**, and this is the part that matters: on Pass 0 the
target value `1e-06` *equals* the shipped template default, so a value-check
cannot distinguish "the substitution ran" from "the substitution never ran and
the default was already right". The guard was blindest exactly where the desired
value equals the default. That is `docs/FAIL_OPEN_GATE_AUDIT.md` §28's caller-side
defect arriving in a **launcher** rather than in a grader.

**Consequence for this grading, checked rather than assumed:** §2 above reads each
run's own staged dictionaries from disk. Pass 0 is uncontaminated; Pass 1 carries
1e-08 and 30000. The defect was inert on Pass 0, not wrong.

**Code of record.** `cases/JF1_JET_FLAP/run_jf1g.sh` has since been changed (class
fix, committed `388859b8`, adding a `subst_or_refuse` helper that checks `sed`'s
exit status and counts matched lines before writing). **The four live runs did not
execute that version.** They executed
`cases/JF1_JET_FLAP/run_jf1g.sh.AS_EXECUTED_BY_THE_FOUR_LIVE_RUNS_2026-09-03T1906Z_PRESERVED`,
which carries only the one-line delimiter repair. The distinction is preserved on
disk and is stated here so no reader grades these runs against a launcher they
never saw.

---

## 7. VERDICTS — AGAINST THE FROZEN GATE, NOT AGAINST WHAT THE NUMBERS SUGGEST

### Study-level

> ## `NOT A RESULT`
>
> **Overdetermined, on two independent frozen gates:**
>
> 1. **Gate G1** — `checkMesh` does not print `Mesh OK` on C3 (max aspect ratio
>    1012.24 on 2 of 202,180 cells). §5 G1: breach → `NOT A RESULT` for the whole
>    study. §6.1 refusal 2 repeats it.
> 2. **Gate G3** — no level, in either pass, meets its own `residualControl` at
>    `endTime`; `p` finishes three orders of magnitude above the Pass 1 control.
>    CLAUDE.md rule 5 clause 1: a level not iteratively converged voids the triple
>    whatever its value.
>
> **No observed order `p`, no GCI and no band on `CL` may be quoted from this
> study, and none is quoted anywhere in this record.**

### Per stage

| stage | verdict | basis |
|---|---|---|
| `JF1G_P0_C1` | **NOT A RESULT** | Pass 0 is `LABEL: diagnostic` and scores nothing by §4 of the registration. Completion clean; G3 unmet. |
| `JF1G_P0_C2` | **NOT A RESULT** | as above |
| `JF1G_P0_C3` | **NOT A RESULT** | Gate G1 breach; no solver ran |
| `JF1G_P0_C4` | **NOT A RESULT** | cap stop; rule 4 fails on five clauses; `CL` still moving 1.26e-01/250 it |
| `JF1G_P1_C1` | **GATE FAIL** *(G3)* | the only genuine completion in the study — all six rule-4 clauses pass — but its residuals do not meet the frozen 1e-08 control at `endTime`. Bookkeeping clean, physics gate failed. |
| `JF1G_P1_C2` | **NOT A RESULT** | cap stop at 24210/30000, `solver_rc 124` |
| `JF1G_P1_C3` | **NOT A RESULT** | Gate G1 breach; no solver ran |
| `JF1G_P1_C4` | **NOT A RESULT** | cap stop; `CL` still moving 1.29e-01/250 it |

**Total cost of the study to date: 623.7333 core-min = 10.3956 core-h, 26.9 % of
the frozen 2320 core-min study cap. Derived $0.5333 — DERIVED, NOT MEASURED.**

### 7.1 A discrepancy between the comparator and the frozen gate — REFERRED, NOT RESOLVED

`analyse_jf1_ladders.py gridG` prints **`VERDICT: PENDING — 2 of 3 levels
present`** for both passes. **This record reaches `NOT A RESULT`.**

They differ because the comparator treats a level with no `log.simpleFoam` as
*not yet run*. C3 is not "not yet run": it **ran and was refused at the mesh
gate**, `rc=5`, and its mesh is on disk failing `checkMesh` now. `PENDING` is
reserved for "not yet run" and may never soften a breached gate (CLAUDE.md
rule 1). Two frozen gates are breached on evidence already in hand, so the frozen
document's own answer is `NOT A RESULT`.

**This lane has NOT edited the comparator.** Changing a script that produces or
grades a measured number requires the supervisor's non-delegable diff read
(`SUPERVISION_CHARTER.md` §3). The proposed change is described in §8 and no
diff has been applied.

---

## 8. FOR THE SUPERVISOR — WHAT NEEDS A RULING

1. **The study verdict**: `NOT A RESULT` (§7) versus the comparator's `PENDING`.
2. **Comparator defect A — the verdict path.** `gridG` returns `PENDING` where the
   frozen gate returns `NOT A RESULT`, because it never evaluates the `checkMesh`
   clause of §2.2 for a level that has no solver log. §6.1 refusal 2 requires that
   evaluation. **Instrument change — diff not written, awaiting your read.**
3. **Comparator defect B — a display truncation that misleads.** The completion
   string is truncated at `[:60]` (`analyse_jf1_ladders.py:476`), so `P1_C2`'s row
   prints `last time 24210 != endTime 3000` — **"3000" is a truncated "30000"** and
   reads as a different `endTime`. The underlying comparison is correct (line 184
   uses the real value); only the printed diagnostic is wrong. Cosmetic, but it is
   a number a reader would quote. **Diff not written, awaiting your read.**
4. **The mesh gate itself** — `JF1G_MESH_GATE_FINDING.md` is open on your desk.
   This record adds C4: the aspect ratio is **non-monotone** (859.95 → 634.44 →
   1012.24 → 796.89), and **non-orthogonality is monotone and worsening**
   (0 → 0 → 133 → 471 severely non-orthogonal faces). Both bear on any repair.
5. **§5.1** — may a queue row whose estimate exceeds its own registered cap launch?
6. **§5.2** — the 3600-s stall-rule scope question, for referral to `verification`.
7. **§0** — whether §11's frozen grading path requires a comparator committed at or
   before the freeze.
8. **Gate G3 is the deeper finding.** The mesh gate is a threshold argument. G3 is
   physics: this case does not converge at any resolution tested, in either pass,
   and clips `k` in 99 % of `P1_C1`'s final 500 iterations while its forces sit
   still. **Repairing G1 would not produce a gradable study.** Any next JF1G step
   should address convergence before it addresses aspect ratio.

---

## 9. WHAT THIS LANE DID NOT VERIFY

- **C4's `y+`** — only 2 `yPlus` rows exist in each C4 root; Gate G2 is not
  evaluated for C4. Marked **VERIFY**.
- **Whether the C4 levels would pass G1's numeric clauses as a *registered*
  triple** — C4's ratios are computed in §3.1 but the frozen §2.2 tolerance table
  lists C2/C1 and C3/C2 only. Marked **VERIFY**.
- **The cause of the non-monotone aspect ratio** — measured and reported; the
  generator-side mechanism is not diagnosed here.
- **Whether `P1_C1` would ever meet 1e-08** — its residuals plateau, but no run
  was extended to test it. The clipping in §3 is the candidate mechanism, not a
  demonstrated one. Marked **VERIFY**.

---

## 9. THE SUPERVISOR'S RULING — `cfd-supervisor`, 2026-09-04

### 9.0 What I checked PERSONALLY, and what I did not

`SUPERVISION_CHARTER.md` §3 makes four checks non-delegable, and a relayed check
is a summary rather than a check. On this record:

- **Check 3 (big-claim verification before belief) — DISCHARGED PERSONALLY.**
  Gate G3's breach is the claim that kills this study independently of the mesh,
  so I re-derived it myself at the artifacts rather than believing §3. **I read
  the FIRST initial residual per field in the final `Time =` block**, never
  `grep … | tail -1` — this team convicted itself of exactly that hand-read in
  `F28G_L1_RESIDUAL_RECONCILIATION.md` §4, and the discipline is worth nothing if
  it is not re-entered on the next reading. My independent figures for `P1_C1` at
  `Time = 30000`: `Ux` **3.196239643e-07**, `Uy` **3.617877009e-06**, `p`
  **1.276407487e-05**, `omega` **1.658474263e-08**, `k` **2.512984572e-05**,
  against a `residualControl` of **1e-08** read from that run's own
  `system/fvSolution`. **All five are above control** — `p` by 1,276×, `k` by
  2,513×, and even the best, `omega`, by 1.66×. I separately counted
  `SIMPLE solution converged` across all six solver logs: **zero in every one.**
  §3's table agrees with mine to every printed digit.
- **Check 2 (crash triage) — DISCHARGED.** The `rc=9` launcher refusal is
  triaged in §6 at 0 s solver compute, and the preserved attempt-1 tree is intact
  rather than deleted. A guard that refused is a guard working.
- **Check 4 (pre-registration committed before compute) — DISCHARGED.** Freeze
  `038f4bca`, one commit ever for the file, never amended, blob
  `0b9476598ef4467dae3f9bcc0e4cf113254bd8e0` pinned by every run.
- **Check 1 (measurement-script diffs) — NOT DISCHARGED, AND THEREFORE NOTHING
  BELOW RESTS ON A COMPARATOR CHANGE.** No comparator was modified for this
  grading, so no diff was owed. The three comparator defects ruled in §9.3 are
  **repairs I am commissioning, not repairs I am accepting** — their diffs come
  to me before any output of the repaired instrument is believed.

⚠ **Stated as unchecked:** I did not re-derive the mesh-metric table, the cost
arithmetic, the clipping counts, or the `D21` figure. They are accepted **as
recorded**, from an instrument whose selftest I read the results of but whose
source I have not read line by line. That is a real limit on this record and it
is named rather than glossed.

### 9.1 THE VERDICT — `NOT A RESULT`

**The JF1G grid-convergence study at `C_mu = 0.1` is `NOT A RESULT`**, on **two
independent breached gates**, either of which is sufficient:

| gate | breach | the number |
|---|---|---|
| **G1** — mesh similarity, `Mesh OK` on every level | C3 fails `checkMesh` | max aspect ratio **1012.24**, `Failed 1 mesh checks`, 2 cells of 202,180 |
| **G3** — iterative convergence per level | **every** level, both passes | `P1_C1` at 30,000 iterations: `p` = **1.276e-05** against a **1e-08** control; no run ever printed `SIMPLE solution converged` |

**No observed order `p`, no GCI and no band is quoted, and none may be.**
CLAUDE.md rule 5's order is not negotiable: clause 1 — a level not iteratively
converged — fires before any classification, and the gate may only turn a `PASS`
or `GATE FAIL` **into** `NOT A RESULT`, never the reverse.

🔴 **The G3 finding is worth more than the G1 finding, and this is the sentence I
most want a successor to read: REPAIRING THE MESH GATE WOULD NOT PRODUCE A
GRADABLE STUDY.** The obvious reading of this campaign — "C3's mesh failed, fix
the mesh, re-run" — is **wrong**, and it would have cost the full ladder to learn.
Every level that *did* solve failed to converge, including the one that ran
30,000 iterations at a tightened control on a mesh that passed. The binding
defect is in the numerics, not the grid.

### 9.2 RULING — `NOT A RESULT`, **NOT** `PENDING`. The comparator is wrong here, and this is comparator defect C

The comparator reports `PENDING` because it treats C3 as *not yet run*. **C3 ran
and was refused** — `rc=5`, stage `checkMesh`, its failing mesh on disk, 0.0667
core-min of real compute spent producing that refusal.

**`PENDING` may never soften a breached gate.** Under CLAUDE.md rule 1, `PENDING`
is a **display/queue state** meaning "not yet run" (`VERIFICATION_CHARTER` §9;
`REPORTING` §2 rule 5 reserves the form `PENDING: <path>`). Using it for a level
that ran, was measured, and was refused would convert a measured failure into an
appearance of unfinished work — the difference between "we have not looked" and
"we looked and it failed." **A refused level is a measurement, not an absence.**

**I therefore record this as comparator defect C**, alongside A and B: *the
comparator does not distinguish "never ran" from "ran and was refused", and the
two carry opposite evidentiary weight.* It is the most consequential of the
three, because it is the one that changes a verdict word.

### 9.3 RULING on the three comparator defects — all three are real; all three are repaired before this instrument grades again

- **Defect A — `gridG` never evaluates §2.2's `checkMesh` clause for a level with
  no solver log, though §6.1 refusal 2 requires it.** **REAL.** Note what this
  means in combination with defect C: the instrument skips the mesh clause for
  precisely the levels whose *only* result is a mesh refusal. **The one thing C3
  and P1_C3 measured is the one thing the comparator does not read.**
- **Defect B — `analyse_jf1_ladders.py:476` truncates a diagnostic at `[:60]`,
  printing `endTime 3000` for a real `30000`.** **REAL, and I decline to
  down-rate it as cosmetic.** The underlying comparison at line 184 is correct, so
  no verdict is wrong today. But a diagnostic that misprints an `endTime` by a
  factor of ten is *exactly* the instrument that produces a wrong hand-read, and
  this team has already paid for one: the `res p` episode in
  `F28G_L1_RESIDUAL_RECONCILIATION.md` §4 was a supervisor reading a correct log
  through an incorrect habit. **A misleading printout is a defect in an
  instrument whose product is a number a human then quotes.**
- **Defect C — `PENDING` for a refused level.** As ruled in §9.2.

**None of the three is repaired by this record**, and **no diff has been written
for any of them** — check 1 is mine and non-delegable, and I will read each
change as a diff before any output of the repaired comparator is believed. A
lane's test of its own repair is evidence, not my read.

### 9.4 RULING on §5.1 — **NO.** A queue row whose estimate exceeds its own cap may not launch

`P1_C2` registered **estimate 265.8 against cap 240.0** — **1.11× its own
ceiling** — and then behaved exactly as that arithmetic said it would: killed by
`timeout` at **240.0333 core-min, `rc 124`, 24,210 of 30,000 iterations**. The
row's `predicted_outcome` was right to four significant figures.

**An estimate above its own cap is not a cost note. It is a pre-registered
prediction that the run will be killed — which is a pre-registered prediction of
`NOT A RESULT`.** Rule 12 says an overrun *stops the run* and does not get a new
budget; a row that predicts its own stop before it launches has answered the
question in advance, and launching it spends the cap to confirm arithmetic
already on the page. **This one spent 240 core-min to learn what its own two
numbers said.**

**Ruled for cfd's queue rows, effective now:** a row whose estimate exceeds its
own cap is **raised as a pre-registration question before launch**, never filed
as a cost note. Either the estimate is wrong, or the cap is wrong, or the run
should not be launched in that shape — and which of the three it is must be
settled *before* compute, not discovered after.

⚠ **The general form is NOT mine and is REFERRED, not taken.** Whether this
belongs in `COMPUTE_BUDGET_CHARTER.md` as a lab-wide launch precondition is a
charter question, and charters are not amended on a supervisor's ruling. **It
goes to the chief for routing.** I bind my own team's rows and nobody else's.

### 9.5 REFERRED, not ruled — two questions that are not cfd's

- **§5.2, the rule-12 stall-rule scope.** Five JF1G rows exceed the 3,600 wall-s
  threshold. All five are **registered long transients**, none is an
  infrastructure stall. The record publishes **gross with no cleaned figure** and
  names the reason. **That is the correct conservative handling and I affirm it.
  The scope question stays REFERRED** — it was referred by heat-transfer on
  2026-09-03 and by this team on board 55, and a third team reinterpreting a
  standard is how a standard quietly changes. **No agent reinterprets it.**
- **§0, whether §11 requires the comparator to be committed at or before the
  freeze.** The comparator was committed *after* `038f4bca`; its blob hash
  against the committed blob passes, which is what §11 explicitly requires.
  Whether §11 *additionally* requires the file to pre-date the freeze is a reading
  of `VERIFICATION_CHARTER` §11, and **that charter is the verification team's.
  REFERRED to verification-supervisor.** I note only that the conservative
  reading would invalidate this grading path, and that I am not entitled to pick
  the convenient one.

### 9.6 🔴 THE FINDING THAT LEAVES THIS CAMPAIGN — the `checkMesh` verdict-string gate is now DEMONSTRATED, not hypothesised

The chief's desk carries an item about **30 launchers across four teams gating on
`checkMesh`'s verdict STRING rather than on its NUMBERS.** Until tonight that was
a code-shape concern. **This study is a measured instance of it, and the
comparison is inside my own territory:**

| campaign | max non-orthogonality | what happened |
|---|---|---|
| **M6 `R1-M0`** | **88.88926674°** | **KILLED.** Branches (a1) and (a2) dead against a **70°** numeric gate |
| **JF1G C4** | **81.35°**, with **471** severely non-orthogonal faces | **`Mesh OK`.** Admitted into a grid-convergence study and solved for ~97 core-min |

**Same quantity, same lab, same week, opposite treatment — and the only
difference is that one gate reads a NUMBER and the other reads a VERDICT
STRING.** `checkMesh` classes aspect ratio as a hard failure (`***`) and
non-orthogonality as advisory (`*`), so a mesh at 81.35° prints `Mesh OK` and
passes a gate written as *"`Mesh OK` on every level."*

**And the family is degrading in exactly the direction a refinement family must
not:** non-orthogonality rises **monotonically** with refinement — 57.53 → 67.64
→ 75.14 → **81.35** — while severely-non-orthogonal faces go **0 → 0 → 133 →
471**. Meanwhile the metric the gate *does* read, aspect ratio, is
**non-monotone** — 859.95 → 634.44 → **1012.24** → 796.89. **The gate reads the
metric that wanders and ignores the metric that is monotonically getting worse.**
No frozen gate in this study catches it. That is not a JF1G defect; it is a
defect in how this lab writes mesh gates, and it goes up.

### 9.7 A CROSS-CASE FINDING I OWE MY OWN TERRITORY — the knowledge existed, in writing, in a sibling case, and did not travel

`JF1G_P1_C1_CMU010_A0/system/fvSolution` carries this comment, written by
whoever built the JF1 case, immediately below its `residualControl` block:

> `p is a FIELD relaxation in OpenFOAM (simpleFoam calls p.relax(), which reads`
> `relaxationFactors/fields); putting p under 'equations' would silently apply NO`
> `p relaxation at all.`

**`F28G_L1_dp1000_U20/system/fvSolution` has precisely that bug** — `p 0.3`
inside an `equations` sub-dictionary with no `fields` sub-dictionary, so `p` runs
unrelaxed at `alpha_p = 1.0`. It took a full source trace through four levels of
OpenFOAM v2606 to convict it in
`F28G_L1_RESIDUAL_RECONCILIATION.md` §5.

**Two cases in one team's territory: one carries the warning, the other carries
the defect, and the warning is sitting in a dictionary nobody diffs.** The lab's
knowledge was not missing and was not wrong — **it was unreachable from the place
it was needed**, because it lived in a comment in a sibling case's input file
rather than in `NUMERICS_KNOWLEDGE.md` or a lint. That is the durable lesson and
it is worth more than either case's verdict. A lesson is owed; the duplicate
check against L-478's family (*a name is not a control*) comes first, because
this may be a member of it rather than a new axis.

### 9.8 What is NOT concluded

**This is not a finding that the jet-flap physics is wrong**, and nobody may read
it as one. `D21` = **3.075340e-03** is **256×** the ~1.2e-05 margin the
registration named as its most likely failure mode, so `C_L` is **not**
grid-insensitive at 40k cells and **Pass 0 discharged its entire registered
purpose.** The registration's own headline risk was **refuted in the safe
direction.** What failed is iterative convergence and a mesh gate — both ours to
fix. Under Sanaa's 2026-09-04 order this case is **worked, fixed and solutioned
until at least a gate pass**; `NOT A RESULT` tonight is a **waypoint with its
causes measured**, not a resting place, and **not one gate, threshold, cap or
label is widened to get there.**

**Cost of this ruling: 0.000 core-minutes.** Artifact reads and arithmetic only.
