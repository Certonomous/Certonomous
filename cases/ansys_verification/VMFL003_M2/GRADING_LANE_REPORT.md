# VMFL003-M2 — GRADING LANE REPORT (arms A and B)

**Lane:** `ansys-lane-opus48` (Opus 4.8). **For:** `ansys-verification-supervisor`.
**Date:** 2026-08-25 (UTC). **NOT FILED ANYWHERE** — nothing here leaves the box
(CLAUDE.md rules 7, 8). **Zero new compute:** these are already-finished runs; no
solver was started, and nothing was written into any run directory.

This report is my only channel to the supervisor (lane→supervisor messaging is
one-way). It is committed alongside the register and calibration appends it drafts.

---

## 1. WHAT I DID

- Read the manual page (VMFL003, VM2026R1 p. 19–20) and the frozen pre-registration
  from the **HEAD blob** (`git show HEAD:…/PREREGISTRATION.md`), not the worktree.
- Ran the launch-safety sweep: the only live ansys solver at start was `simpleFoam`
  pid 2396481 on arm D's `L3_1000x5`; arms A and B were quiescent. Mid-task the
  supervisor confirmed pid 2396481 **exited ~19:05Z** — I re-checked and it is dead;
  the only live `*simpleFoam` now are heat-transfer `buoyantBoussinesqSimpleFoam`,
  none of them mine. I touched nothing under arms C or D.
- **Rule 2 (comparator freeze):** `grade_vmfl003_m2.py` on disk hashes
  `6dcc99940154ea204a598ba2118042bf972a786d`, byte-equal to
  `HEAD:…/grade_vmfl003_m2.py`; its own `--verify-frozen HEAD` returns rc 0. The
  launcher log records the freeze-check taken at launch (`PREREGISTRATION.md == HEAD
  (cdbf2659…)`; freeze commit `c5fdcad4` is an ancestor of launch_head `117d8adc`).
  The grading path is bound to the freeze.
- **Rule 3 (self-blindness):** `scripts/check_grader_self_blindness.py
  …/grade_vmfl003_m2.py` → clean on both probes, exit 0. And the comparator's own
  three planted-zero controls FIRED on the real artifacts of both arms (below).
- Graded arms A and B by running the frozen comparator against each arm's run root,
  writing JSON to scratch (never into the run tree). Independent regrade reproduced
  the already-present committed `GRADING_*.json` **byte-for-byte** for both arms.
- Completion evidence taken from **`log.simpleFoam` explicitly**, never a `log*`
  glob (which matches `log.blockMesh` first and would report the mesher's `End`).

## 2. WHAT I MEASURED — arms A and B (gate triple = the freeze's NAMED triple `L1_250x5`/`L2_500x5`/`L3_1000x5`, prereg §9)

| quantity | arm A `kEpsilon` | arm B `realizableKE` |
|---|---|---|
| **VERDICT (rule 1)** | **`NOT A RESULT`** | **`NOT A RESULT`** |
| gate verdict before rule 5 | `GATE FAIL` | `GATE FAIL` |
| Δp at L3_1000x5 (Pa) | 20 800.824488339003 | 20 278.128649236500 |
| dev vs manual target 21 744 | **−4.337635723 %** | **−6.741498118 %** |
| dev vs Colebrook 21 792.88 | −4.552199385 % | −6.950670093 % |
| f_dev at L3 | 0.027147309 | 0.026462670 |
| Roache triple state | CONVERGING, monotone | CONVERGING, monotone |
| triple (coarse/med/fine, Pa) | 20 802.99 / 20 800.99 / 20 800.82 | 20 280.51 / 20 278.47 / 20 278.13 |
| R | 0.0804 | 0.1657 |
| observed order p | 3.6364 **NOT TRUSTED** | 2.5930 **NOT TRUSTED** |
| GCI at Fs=1.25 | **not quoted** (`null`) | **not quoted** (`null`) |
| y⁺ L3 mean / min | 37.600 / 23.812 | 37.491 / 23.784 |
| ladder spread | 1.7356 % (< 5 %) | 0.6746 % (< 5 %) |
| cost (core-min, ExecutionTime) | 29.962 | 31.152 |

**Why NOT A RESULT — the machinery, in order (rule 5).** For both arms the comparator
refused at **step 1: every Roache level failed the frozen iterative-convergence
residual leg** (final initial residuals of p, Ux, k, ε each < 1.0e−8). Arm A L3 misses
on **ε alone** (2.49442e−08, 2.5× the floor); L1/L2 miss on all four. Arm B L3 misses
on **k = 1.377e−07 and ε = 7.490e−08**; L1/L2 broadly. The gate would independently
have been `GATE FAIL` (both outside the frozen ±2.5 % band); rule 5 turned it to
`NOT A RESULT` — the only permitted direction. No GCI is quoted on a `NOT A RESULT`
row, and the observed order is separately flagged untrusted (differences are
7.8 ppm-scale, below the noise floor).

**No triple was selected after seeing numbers.** The freeze (§9) named the triple; I
graded exactly it. The six levels do not admit a "better-grading" alternative triple —
the three Roache levels are the only ratio-2 axial family, and the `D_500x*` levels are
the wall-treatment ladder, not a Roache triple. There is nothing to choose.

**KEY SUBSTANTIVE FINDING (arm A, the control).** Arm A existed to discharge run-1
"Defect B" (iterative convergence) by bumping endTimes to 15000/18000/22000. **It did
not.** L3's ε residual is still above 1e−8 (run 1 2.523e−08, arm A 2.494e−08 — barely
moved), and L1/L2 sit at ~1e−6. Δp is fully plateaued at every level while the
normalised initial residual never reaches 1e−8. So the frozen 1e−8 residual floor is
not reachable on this wedge-pipe k-ε configuration within these counts; a converged
`kEpsilon` baseline was **not** obtained, and run-1's model-level deficit (−4.6 % vs
Colebrook) is unchanged and reconfirmed.

**MECHANISM DIAGNOSTIC (secondary, not a credential).** f_dev: A 0.027147, B 0.026463 —
realizableKE is **2.52 % below** arm A, i.e. it under-predicts wall friction *more* than
standard k-ε (both below Colebrook 0.028464). This **exceeds** the prereg Arm-2 >1 %
"materially moved friction" threshold and **falsifies** Arm-4's prediction that ε-family
variants sharing the log-law wall function stay within ~1 % of A on f_dev. Caveat: both
arms are `NOT A RESULT` on the residual leg, so this rests on plateaued-but-not-
residual-converged Δp. **Arm-5's four-model falsification is NOT evaluable** — only two of
four arms are gradeable and both others are `NOT A RESULT` on incompleteness (C at
`aba61e53`; D a budget stop, below).

**Planted-zero controls (rule 3) — all three FIRED on both arms' real artifacts:**
Δp+ρ plant seen 1.51165 Pa = expected (the ρ=1.225-live test; a ρ-blind reader is
refused); y⁺ plant seen 7.77; f_dev plant seen 9.38e−6. The reader is demonstrably not
self-blind.

## 3. THE rc CLAUSE — a correction to the brief's premise (measured)

The brief stated there is **no** `RC.txt`/`record.json` under `VMFL003_M2`, so the
`rc = 0` leg of rule 4 could not be evaluated from disk, and told me to report it as
unevaluable or a disclosed substitution. **That premise does not hold for arms A and B.**
Every one of their twelve level directories carries a **`RUN_RC.txt`** reading `rc=0`
(plus `wall_s`, `ranks`, `core_min`), and the frozen comparator's completion clause **C1
reads exactly `RUN_RC.txt`** (`re.search(r"rc\s*=\s*(-?\d+)")`) and **passed at all six
levels of each arm** — the grader returned exit 0 with a full JSON, which it does only if
`check_completion` did not refuse. So the `rc = 0` clause is **satisfied — not
unevaluable, not substituted** — for both graded arms, and the full rule-4 set holds:
C1 rc=0, C2 an `End` line, C3 last `Time` == `endTime`, C4 fields `U p k epsilon nut`,
C5 `ExecutionTime` count == `endTime`, C6 age guard, at all six levels of A and B.
The charter-grade concern the brief raised — "a launcher that cannot evidence its own
exit code cannot satisfy rule 4" — **does not apply to this launcher**: `run_vmfl003_m2.sh`
does evidence rc, via `RUN_RC.txt`, and the comparator consumes it. Recorded so the
premise is not carried into a future grading as fact.

## 4. ARM STATES (for the record; only A and B are mine to grade)

- **A `kEpsilon`** — `NOT A RESULT` (residual leg). Complete; 29.96/40 core-min.
- **B `realizableKE`** — `NOT A RESULT` (residual leg). Complete; 31.15/40 core-min.
- **C `RNGkEpsilon`** — `NOT A RESULT` on ladder incompleteness, ruled `aba61e53`
  (not reopened). 39.93/40 core-min.
- **D `kOmegaSST`** — `NOT A RESULT`, ruled by the supervisor 2026-08-25 (SUPERVISION
  §3 crash triage, personal). A **budget stop**, not a crash: `simpleFoam` reached
  `Time = 5949` of `endTime 22000` = **27.0 %**, `ExecutionTime = 1662.74 s` under
  `timeout 1663`, no `End` line, `ExecutionTime`/`ClockTime` = 1662.74/1662 = 1.0004
  (real CPU, not contention). **No fresh cap** (rule 12). Recorded as a stop, never
  `PENDING`. 39.99/40 core-min. I confirmed the dead pid and these figures read-only;
  I did not restart, grade, or write into arm D.

## 5. COST CALIBRATION (rule 12) — arms A and B

Estimate: **28.1 core-min per model** (per-arm cap 40, slate cap 160), frozen at
`c5fdcad4`; basis run-1's measured 5.806e−6 s/(cell·iter). Actuals ExecutionTime-derived,
serial RANKS=1 (they match the supervisor's independent readings exactly):

| arm | actual core-min | ratio actual/predicted | % of 40 cap | $ derived |
|---|---|---|---|---|
| A | 29.962 | 1.066× | 74.9 % | $0.025617 |
| B | 31.152 | 1.109× | 77.9 % | $0.026635 |

**Attribution: misprediction only; contention measured-false; waste 0.**
`ExecutionTime`/`ClockTime` ≈ 1.000 on every level, so the spend is real CPU — no
contention component is charged despite co-resident peers. The ~7–11 % gap is the
endTime-bump residual risk the prereg §12 named; the corrected basis landed within ~7 %
(vs run-1's 1.406× miss). **Not pooled with arms C/D's cap-hitting overruns** — those are
a distinct per-iteration cost anomaly (§6), not arms A/B's story. Rows drafted for
`docs/COST_CALIBRATION.md` as the next two C-ids (derived from HEAD at commit).

## 6. CHARTER / DOC UPDATE LINE

**Two doc items; neither is a charter change I make as a lane — both are drafted for the
supervisor's read.**

1. **RC-instrument concern: VOID for this launcher (do not charter it).** The brief's
   worry that the M2 launcher cannot evidence its exit code is factually wrong here —
   `RUN_RC.txt` (rc=0) is present at every level and the comparator C1 reads it (§3).
   No charter clause is warranted on that ground.

2. **Candidate `N-AV*` numerics entry — a per-iteration cost anomaly (NOT run, drafted
   only).** On identical mesh `L2_500x5` / `endTime 18000`: A 333.93 s, B 322.91 s,
   D 353.01 s — but **C (RNGkEpsilon) 1413.1 s, 4.23× baseline**; and C's `L3` (633.58 s)
   is *cheaper* than its L2 despite 2× cells; arm D's L3 ran 0.2795 s/iter vs the
   ~0.04 s/iter its mesh scaling predicts (~7×). This reads as a **linear-solver regime
   problem** (a badly-converging inner solve burning multiples of predicted CPU), not a
   model-cost problem — a hypothesis, labelled one, from the supervisor's triage and my
   ExecutionTime reads. It bears on Sanaa's 2026-08-25 instruction *"When a grid doesnt
   converge, try different pre conditioners, see if that's a raised issue online/in the
   litterature, check for bugs."* **Available instrument, noted not invoked:** this team's
   VMFL007_R2 preconditioner sweep harness (`A1_GAMG_GaussSeidel` … `A6_smoothSolver_
   symGaussSeidel`) — running it is a separate registered experiment with its own cap, not
   part of this grading pass. Recommend the supervisor open the `N-AV*` entry (and, if
   Sanaa directs, a registered preconditioner experiment) at slate close-out, when arm D's
   stop and arm C's ruling are both on the register.

## 7. VERDICTS (fixed vocabulary, with numbers and cost)

- **Arm A `kEpsilon`: `NOT A RESULT`** — Δp 20 800.82 Pa, −4.338 % vs target (outside the
  frozen 2.5 % band → `GATE FAIL` before rule 5), residual leg unmet at all three Roache
  levels (L3 on ε, 2.494e−8); triple CONVERGING/monotone, order 3.636 untrusted, **no
  GCI quotable**. Tier **`NOT HELD`** (V present via a category-2 correlation, G actively
  negative). Cost **29.962 core-min** (measured), $0.025617 derived.
- **Arm B `realizableKE`: `NOT A RESULT`** — Δp 20 278.13 Pa, −6.741 % vs target
  (`GATE FAIL` before rule 5), residual leg unmet at all three levels (L3 on k and ε);
  triple CONVERGING/monotone, order 2.593 untrusted, **no GCI quotable**. Tier
  **`NOT HELD`**. Cost **31.152 core-min** (measured), $0.026635 derived.

Neither is a credential (only `PASS` rows are). Both are recorded as they are; nothing
softened.

## 8. WHAT I COULD NOT VERIFY

- I did not grade arms C or D and do not reopen their rulings; D's numbers are the
  supervisor's triage, cross-checked read-only against the log.
- The mechanism comparison (§2) rests on runs that are `NOT A RESULT` on the residual
  leg; it is a diagnostic, not a certified result, and Arm-5 cannot fire on two arms.
- Dollars are **derived** at $0.0513/core-h (owner-stated); the box cannot read its own
  billing, so no dollar figure here is measured.
- The `GRADING_*.json` files exist on disk but are **untracked** in git; committing the
  run evidence by explicit path (as done for VMFL045-R2) is the supervisor's call.
