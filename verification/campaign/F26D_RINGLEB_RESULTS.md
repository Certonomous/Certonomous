# F26D — RINGLEB DISCRIMINATING ARM: which of zero viscosity, wall curvature or high subsonic Mach carries the F26 failure (`rhoSimpleFoam`, three arms × four levels, 1 rank) — GRADED RECORD

Team cfd. Pre-registration `cases/F26_RINGLEB/PREREGISTRATION_F26D_2026-08-27.md`
frozen at **`ed09c9ef5f9ca20571105185e5210a1d60f8a231`**. Amendment 1
(2026-08-27T19:47:58Z, **BEFORE FIRST COMPUTE**, condition checked three ways: run
root `verification/runs/F26D_runs` ABSENT, `verification/runs/F26_RINGLEB_runs`
ABSENT, `find cases/F26_RINGLEB` for `RC.txt`/`log.*` returning **0 files**, spend
**0 core-minutes**) repaired a comparator defect found by the supervisor's §3
check 1 — the grader had classified a **never-run** level directory as **FAILED**,
so a budget halt would have been read as a physics failure. It moved no gate,
threshold, cap or label.

**THIS IS A DIAGNOSTIC, NOT A LADDER, AND IT DOES NOT RESCOPE F26.** The
registration says so in its opening lines and the grader repeats it in its closing
line: **F26_RINGLEB REMAINS BLOCKED**
(`cases/F26_RINGLEB/SOLVER_ADMISSION_ARM_2026-08-27.md`). Nothing here unblocks it,
rescopes it, or establishes a rescope cost. **The rescope cost is NOT established
and stays not established.** No result here may be promoted into F26's registration.

Graded at **zero new compute**, plain `python3`:
`python3 /home/ubuntu/Certonomous/cases/F26_RINGLEB/grade_f26d.py --prereg-commit=ed09c9ef5f9ca20571105185e5210a1d60f8a231`
— **rc 0**. **This grader writes no artefact: its output is stdout only unless
`--json` is passed, and `--json` was not passed.** This record therefore cites the
pre-registration, the grader source by line, and the run-tree artefacts, and it was
written after re-running the grader in this lane's own invocation and reading the
output directly.

---

## 1. VERDICT — fixed vocabulary

> **GATE REACHED — reading: AMBIGUOUS.**

**Both words matter and neither may be softened.** `GATE REACHED` is the verdict:
the arm ran, the registered observable was measured at every level of every arm,
the registration's own refusal condition was tested and did not fire, and the
result maps onto one of the four rows fixed before compute. `AMBIGUOUS` is the
**reading**, and it is one of those four registered rows — not a shortfall, not a
partial success, and not a failure.

**The registered reading, quoted exactly from prereg `:137`:**

> **AMBIGUOUS, and reported as such.** Both are sufficient repairs; neither is
> shown necessary. No candidate is eliminated.

The grader printed it in the same words:

> Both probes are sufficient repairs and neither is shown necessary. NO CANDIDATE
> IS ELIMINATED. Reported as ambiguous, not resolved.

This is not progress dressed up and it is not a failure dressed down. Three
candidate causes were named before compute — **C_mu** (zero viscosity), **C_kappa**
(strong wall curvature, max |κ| = 0.4544 measured), **C_M** (high subsonic Mach,
max M = 0.8567 measured) — and the arm's outcome is that **each of the two knobs
independently repairs the failure**, so neither candidate is shown *necessary* and
none is eliminated.

---

## 2. THE OBSERVABLE IS ORDINAL — no triple, no order, no GCI, and the absence is DEMONSTRATED

`N*` is **the coarsest registered level at which an arm FAILS** (prereg `:93-95`).
It is a **completion property**: it needs no exact solution, no error norm and no
Richardson extrapolation. `N* = NONE` iff all four levels complete.

**A level COMPLETES iff all of** (prereg `:97-100`): `rc = 0`; an `End` line in the
solver log; last time == `endTime` (4000); `ExecutionTime` count == 4000. Anything
else — SIGFPE (`rc=136`), FOAM abort (`rc=134`), negative temperature, or a short
log — **is a FAILURE**.

**No Roache triple, no observed order and no GCI is reported, and the grader proves
by AST census that it structurally cannot produce one.** Control **G7** reads
**10 imports and 177 identifiers** out of the comparator's own syntax tree and
finds **none naming `roache`, `gci` or `richardson`** — and the census reader was
itself shown able to see those names when planted in a synthetic source. The
absence is therefore **demonstrated, not asserted**. This matters beyond
bookkeeping: the registration records (prereg `:111-121`) that
`scripts/roache_triple.py` accepts `r21 = 1.125` as CONVERGING **with no minimum-`r`
guard** — an instrument gap that is verification's to close and is not touched
here. This arm is immune to it by construction, because it performs no
extrapolation at all. `r = 2` here sets only how tightly the threshold is
bracketed; **no claim in this record depends on any `r`.**

---

## 3. MEASURED — N*(A0) = L3, N*(AV) = NONE, N*(AM) = NONE

**The crashes ARE the measurement, not a failure of the run.** Prereg `:97-99`
registers SIGFPE `rc=136` **in advance** as a FAILURE *reading* of the observable.
A reader who opens this run tree and finds two arms that died with `rc=136` is
looking at the instrument working, not at a broken run. This is said first,
deliberately, because it is the easiest thing in this record to misread.

| arm | knob | L1 (96) | L2 (384) | L3 (1,536) | L4 (6,144) | **N\*** |
|---|---|---|---|---|---|---|
| **A0** | baseline, as F26 was posed | COMPLETED | COMPLETED | **FAILED** | **FAILED** | **L3** |
| **AV** | `mu` raised | COMPLETED | COMPLETED | COMPLETED | COMPLETED | **NONE** |
| **AM** | `k`-band lowered (Mach **and** curvature together) | COMPLETED | COMPLETED | COMPLETED | COMPLETED | **NONE** |

The two A0 failures, with the grader's own reasons:

| level | rc | `End` line | last time vs `endTime` | `ExecutionTime` count vs 4000 |
|---|---|---|---|---|
| A0 L3 | **136 (SIGFPE)** | none | **103.0** != 4000 | **102** != 4000 |
| A0 L4 | **136 (SIGFPE)** | none | **166.0** != 4000 | **165** != 4000 |

Every clause of the completion rule fails on both, independently — the verdict does
not rest on any single reading. The ten completing runs each show `rc=0`, one `End`
line, last time 4000 and 4000 `ExecutionTime` lines, re-read from
`verification/runs/F26D_runs/<arm>/<level>/log.solve` and `RC.txt` by this lane.

**Mapped onto §4.2's table (prereg `:133-138`), the row is: AV completes all 4, AM
completes all 4 → AMBIGUOUS.** Under §4.1's predictions, C_mu predicted AV would
complete and AM would not; C_kappa and C_M each predicted the reverse. **Both
completed.** Each knob is a sufficient repair; the arm cannot say which cause is
necessary, and it does not pretend to.

---

## 4. §4.3's REFUSAL CONDITION WAS CHECKED, AND IT DID NOT FIRE

The registration made A0's own behaviour the arm's validity check (prereg
`:140-147`): **A0 completes L1 (96) and L2 (384) and FAILS at L3 (1,536)**, on the
basis that a prior arm bracketed the threshold between **600 and 864 cells**.

> **If A0 completes L3, this arm is `NOT A RESULT`** — the reference the two probe
> arms are read against would have moved, and AV/AM would be compared to nothing.

**This was a real risk that landed correctly, and it was tested by executable code,
not by prose.** The grader holds the condition as two frozen constants at
`grade_f26d.py:60-61` — `A0_MUST_COMPLETE = ("L1","L2")` and
`A0_MUST_FAIL_AT = "L3"` — and tests them at `:463` and `:494`, each guarding a
`return 2` NOT A RESULT branch. **Neither branch was taken.** A0 completed exactly
L1 and L2 and failed exactly at L3, so the reference held and AV/AM are read
against something.

Note how narrow that was: the bracket said 600–864 cells, L2 = 384 sits below it
and L3 = 1,536 above it, and **384 completed while 1,536 failed** — the prediction
landed inside a factor-4 window that the ladder could not have adjusted after the
fact.

The third registered refusal branch — Amendment 1's — also did not fire: no arm
read `UNDETERMINED`, no level directory was absent, and `cap_halt()` found no
marker in the run root, so no arm's threshold rests on an infrastructure gap.

---

## 5. WHAT THIS ARM CANNOT SEPARATE, carried forward from §5 of the registration

**It cannot separate C_kappa from C_M by any knob, and that is a property of
Ringleb flow, not a corner cut.** Measured at registration time over `k` in
[0.3, 0.9]: max Mach and max wall curvature are **both strictly monotone increasing
in `k`** and **both attain their maximum at `phi = 0`**, so no choice of `K_MIN`,
`K_MAX` or `PHI_END` lowers one while holding the other; cutting `PHI_END` to 0.8,
1.2, 1.6 or 2.0 changes **neither** maximum. Arm **AM therefore moves them together
by construction** and is registered as a **JOINT probe**.

**Honestly labelled: a PARTIAL discriminator.**

- It **separates C_mu from {C_kappa, C_M}** — cleanly, by a single knob.
- It **separates {C_kappa OR C_M} jointly from "none of the three"** — cleanly.
- It **does NOT separate C_kappa from C_M** by any knob.

The registration's §5.1 secondary reading (for `mu = 0` Euler flow there is no
intrinsic length scale, so curvature enters only through `κ·h`, which refinement
*reduces* — hence a curvature-carried failure should *ease* under refinement,
which is the opposite of what A0 does) is registered as **SECONDARY and weaker
than AV's knob**, *"may support a conclusion; it may not carry one alone"*. It is
recorded here on exactly those terms and carries no verdict.

---

## 6. A STRUCTURAL FINDING: the graded invocation ran ZERO planted-zero controls

**`grade_f26d.py:441-442` reads `if a.selftest: return selftest()` — the selftest
returns from `main()` before the graded path is entered.** The consequence is
precise and must be recorded: **all 13 controls (G1–G12 plus the freeze check) are
unreachable from a `--prereg-commit` run.** They are reachable only from a separate
`--selftest` invocation, which exits 0 and prints *"GRADER SELFTEST PASS: 13
controls fired, each shown able to fail."*

Those controls are strong. Among them:

- **G3 / G4 — the both-ways plant, through the real on-disk reader.** G3 drives a
  **COMPLETING** case to read `FAILED` (reasons `rc=136 (SIGFPE)`, `no End line`,
  `last time 794.0 != endTime 4000`, `ExecutionTime count 794 != 4000`); G4 drives a
  **FAILING** case to read `COMPLETED`. **Both directions shown**, so neither
  verdict is a stuck reading.
- **G5** — breaking each of `rc` / `End` line / last time / negative-T **alone**
  flips the verdict to FAILED, so **no clause of the completion rule is
  decorative**.
- **G8 / G10 / G11** — a cap halt reads `UNDETERMINED`, not a threshold; the
  pre-amendment defect reintroduced (`absent_is_failed=True`) reproduces the wrong
  answer **and is shown caught**; a level whose case never built reads
  `UNDETERMINED`.
- **G12** — `cap_halt()` returns None with no marker and reads arm/level/spent/cap
  off disk with one: **the halt is READ, never inferred from absence.**

**But they are evidence about the CODE, not about this graded run's own inputs.**
Rule 3 asks that the comparator plant a known perturbation, read it back **from
disk**, and refuse if the reader cannot see it — and on this invocation, against
these twelve run directories, **no plant was made and nothing could have refused.**
The grader's readers were shown able to see a non-zero *somewhere*, on synthetic
fixtures, in a different invocation; they were not shown able to see one *here*.

**This is a defect to repair in a successor, not here.** The pre-registration is
frozen and this case is post-compute: rule 2 closes the gates and rule 6 bars
editing the frozen comparator. Recording it is the whole of what this record may
do about it. A successor arm should route the controls through the **graded** path
so the two are not separable by a command-line flag.

**F26D alone among the three cfd graders closed this session performs a real freeze
check** (`grade_f26d.py:419-431`, `verify_freeze()`: it resolves
`<commit>:<prereg path>`, recomputes the git blob sha of the file on disk, and
**raises a Refusal** on any mismatch). It printed:

> `FREEZE VERIFIED: cases/F26_RINGLEB/PREREGISTRATION_F26D_2026-08-27.md on disk == committed blob 3e6a6a38c393 at ed09c9ef5f9ca20571105185e5210a1d60f8a231`

This lane extended that check by hand over **every path the freeze commit carries
for this case** — `git hash-object <disk>` against `git rev-parse ed09c9ef:<path>`
— **18 of 18 SAME**, including `grade_f26d.py` (`ee822d3f`), `build_f26d.py`
(`c99011b4`), `exact_f26.py` (`811b2dfe`), `foam_io_f26.py` (`ed69bce3`),
`knp_f26.py` (`30491646`), `run_f26d.sh` (`9620157b`), the five case dictionaries
and three `0/` templates, `SOLVER_ADMISSION_ARM_2026-08-27.md` (`1550320c`) and the
pre-registration (`3e6a6a38`). The single exception is
`cases/F26_RINGLEB/queue_entry_F26D.json`, an **INFRASTRUCTURE** record re-issued
against the amended sha and byte-identical to HEAD; no verdict reads it.

---

## 7. RULE 4 — strict completion, re-read from the run tree by this lane

Solver **`rhoSimpleFoam`**, **1 rank**, serial at every level; `decomposePar` is
never invoked (prereg `:181`).

| arm | level | cells | `RC.txt` | `End` | `ExecutionTime` lines | last time | ClockTime | ExecutionTime | state |
|---|---|---|---|---|---|---|---|---|---|
| A0 | L1 | 96 | 0 | 1 | 4000 | 4000 | 3 s | 2.23 s | COMPLETED |
| A0 | L2 | 384 | 0 | 1 | 4000 | 4000 | 4 s | 3.95 s | COMPLETED |
| A0 | L3 | 1,536 | **136** | **0** | **102** | **103** | 0 s | 0.48 s | **FAILED** |
| A0 | L4 | 6,144 | **136** | **0** | **165** | **166** | 2 s | 2.73 s | **FAILED** |
| AV | L1 | 96 | 0 | 1 | 4000 | 4000 | 3 s | 2.30 s | COMPLETED |
| AV | L2 | 384 | 0 | 1 | 4000 | 4000 | 5 s | 4.61 s | COMPLETED |
| AV | L3 | 1,536 | 0 | 1 | 4000 | 4000 | 16 s | 16.60 s | COMPLETED |
| AV | L4 | 6,144 | 0 | 1 | 4000 | 4000 | 70 s | 69.90 s | COMPLETED |
| AM | L1 | 96 | 0 | 1 | 4000 | 4000 | 2 s | 2.23 s | COMPLETED |
| AM | L2 | 384 | 0 | 1 | 4000 | 4000 | 3 s | 3.64 s | COMPLETED |
| AM | L3 | 1,536 | 0 | 1 | 4000 | 4000 | 11 s | 11.01 s | COMPLETED |
| AM | L4 | 6,144 | 0 | 1 | 4000 | 4000 | 76 s | 75.94 s | COMPLETED |

Ladder `r = 2` per direction, cells ×4 per step: L1 24×4, L2 48×8, L3 96×16,
L4 192×32. Run root records: `LAUNCH_UTC.txt` **2026-08-27T23:51:21Z**,
`PREREG_COMMIT.txt` **`ed09c9ef…`**, `PROGRESS.txt` (twelve rows, cumulative spend
per run), `SPENT_CORE_MIN.txt` **3.25**. **No cap-halt marker exists**, which is
what makes §4's UNDETERMINED branch inapplicable rather than merely unfired.

---

## 8. COST — rule 12 estimate-versus-actual

| item | value |
|---|---|
| predicted | **6.8 core-min** (prereg `:182`); registered cap **10.2** = 1.5 × the estimate (prereg `:183`) |
| `cost_basis` as registered | **derived, NOT MEASURED** — 97.92 M cell-iterations at 3.55 µs/cell-iteration, *"a rate read from ONE lab record of a DIFFERENT case"* (`verification/runs/FPE_DIAG_runs/BL1/log.simpleFoam`), plus ~1.0 core-min for 12 mesh builds. The registration also declared it *"an upper estimate for the completing case: an arm that aborts costs less"* |
| actual, MEASURED from the logs' `ClockTime × ranks ÷ 60` (**1 rank**) | A0 **0.1500**; AV **1.5667**; AM **1.5333**; **3.2500 core-min gross** |
| corroboration | `verification/runs/F26D_runs/SPENT_CORE_MIN.txt` reads **3.25** and `PROGRESS.txt`'s twelve cumulative rows close at **3.25** — **agree to every digit** with this lane's own re-read of the twelve `log.solve` files |
| ExecutionTime basis, stated beside it | 195.62 s ÷ 60 = **3.2603 core-min** |
| actual cleaned | **3.2500 — cleaned == gross.** No row approaches the 3,600-s stall rule (longest run 76 wall s) |
| waste, named separately | **0.000 core-min** (`COMPUTE_BUDGET_CHARTER.md` §6). **The two SIGFPE aborts are NOT waste**: they are the registered measurement of the observable, bought deliberately |
| quantisation | `ClockTime` is integer-second: ± 0.0167 core-min per run at 1 rank. At A0 L3 it rounds a 0.48-s ExecutionTime run to **0 s** |
| share of cap | **31.9 %** (3.2500 / 10.2); no overrun, cap never raised, no halt marker written |
| dollars | 3.2500 / 60 = 0.05417 core-h × $0.0513/core-h = **$0.00278 — DERIVED, NOT MEASURED** (c7a.4xlarge, reported-by-owner; `COMPUTE_BUDGET_CHARTER.md` §5). Registered: $0.0058 at the estimate, $0.0087 at the cap |
| arithmetic ratio | 3.2500 / 6.8 = **0.478** |

**The ratio 0.478 is NOT a like-for-like estimate-versus-actual, and this record
will not report it as a calibration figure.** The estimate priced **twelve complete
runs**; the actual is **ten complete runs plus two that died at 103 and 166
iterations of 4,000** — A0 L3 and A0 L4 between them consumed **2 s of ClockTime**
(3.21 s of ExecutionTime, rounded to 0 s and 2 s by integer-second resolution),
where the completing runs at those two mesh sizes cost **11–16 s** and **70–76 s**. The registration anticipated exactly
this asymmetry in its own words (*"an arm that aborts costs less"*), which is why
the honest label for this row is **NOT COMPARABLE**, not "0.478× — over-estimate".

A like-for-like figure could be constructed by pricing A0 L3 and L4 at the AV/AM
rates, but that would be arithmetic on an assumption rather than a measurement, and
this record does not manufacture one. **What *is* measurable and is worth carrying
forward** is the imported-rate error the registration itself flagged: the estimate
used **3.55 µs/cell-iteration** borrowed from a turbulent RANS `simpleFoam` case,
while the **ten completing `rhoSimpleFoam` runs measured 1.79 to 3.26
µs/cell-iteration at L2, L3 and L4** (L2 1.95 / 2.60 / 3.26, L3 1.79 / 2.60,
L4 2.85 / 3.09), with **L1 reading 5.21–7.81 µs** where fixed startup on a
96-cell mesh and integer-second quantisation dominate. The registered 3.55 µs
therefore sits **above every measured L2–L4 rate** — an over-estimate of the
per-cell-iteration cost as well, on top of the two aborts. The lab has now priced this
same import-a-rate-from-another-case failure at F21, F22, F18b, F17 and F25.

**Estimate-versus-actual calibration lands as a row in `docs/COST_CALIBRATION.md`,
appended at the file's foot at commit time under its own append rules and the
rule-10 private-index protocol, labelled NOT COMPARABLE with the reason.**

---

## 9. WHAT THIS ARM DID NOT ESTABLISH — carried verbatim from the grader's own closing lines

> F26_RINGLEB REMAINS BLOCKED. This arm is a diagnostic, not a ladder; it does not
> rescope F26 and the rescope cost is NOT established.

Also not established: which of C_kappa and C_M carries the failure (§5 — not
separable by any knob of this arm); whether a fourth cause outside the three
registered ones contributes (the registration's fourth row, *"NONE of the three"*,
was the outcome that would have addressed it, and it did not occur); and any
statement about F26's exact solution, error norms or grid convergence, none of
which this arm computes.

## 10. NOT REGISTERED, NOT SENT

No re-grade; no amendment to the frozen pre-registration (this arm is
**post-compute** — its gate, thresholds, cap and labels are **closed**); no
promotion of any figure here into F26's registration; no repair to the frozen
comparator (§6 records the defect for a successor instead). **Nothing is sent,
filed, uploaded, registered, posted or submitted** (rule 7). Run data stays on disk
under `verification/runs/F26D_runs/` and is not committed.
