# Curriculum D6RF10 — A2-wing convergence probe `P_conv`, the CONFOUND-REMOVAL successor to D6RF9 (`NOT A RESULT | CONFOUNDED`)

Supersedes: **D6RF9** — A2-wing convergence probe `P_conv`, item verdict **`NOT A RESULT | CONFOUNDED`**
(autograder-confirmed, check-3, chief-endorsed; LAB_STATE S-142, commit `e3d9cd8f`). D6RF9 did NOT produce a
clean capability finding: **two mechanical confounds** stood between the ladder and a measured answer, and
**D6RF10 exists ONLY to remove them and re-measure the identical science.** No gate, threshold, floor, field,
scoring or rung lever is moved (T25). The D6RF9 run root (ledger + logs) is at
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF9-a2-wing-convergence-probe/`.

**THE TWO CONFOUNDS D6RF10 REMOVES (each traced to a MEASURED artefact, not inferred):**

1. **Confound (i) — R2 timed out incomplete.** R2 (`nNonOrthogonalCorrectors 12`) was killed at its frozen
   `855 s` deadline near outer-iteration ~250 of `endTime 2000`, `rc=124`, `wall_s=862`, `57.467 core-min`
   (ledger `ARM=P_conv rung=R2 phase=candidate ... rc=124`). Rule-4 fails (last time != endTime): the run is
   **incomplete**, so its `GATE FAIL` is not a measured floor-miss. The deadline was too small because it was
   sized from an arbitrary per-rung cap, not from R2's own measured per-step cost — **and R2's per-step cost
   ESCALATES** (§5). D6RF10 sizes the deadline to the measured escalating rate (launcher `rung_cap`, fix (i)).
2. **Confound (ii) — R3/R4 crashed on a stale-decomposition collision.** R3 and R4 (SIMPLEC,
   `DARhoSimpleCFoam`) crashed at `rc=59` in `wall ~10–11 s` (ledger), on `decomposePar: Case is already
   decomposed` → PETSc `SEGV`. **Root cause CONFIRMED 2026-09-09:** the D6RF7 source arms carry stale
   `processor*` dirs — `$SRC/P_conv/mp04`, `mp05`, `mp06` **each hold `processor0..processor3`**; the `P_conv`
   root itself holds none. `cp -a` staged them in; the SIMPLEC path re-decomposes into that collision (the
   `DARhoSimpleFoam` rungs R1/R2 tolerated the stale dirs, which is why it read as a solver-arm crash, not a
   staging bug). D6RF10 strips `processor*` dirs both at staging AND at the start of **every** leg (launcher
   fix (ii)), because by R3 the dirs also exist from the R1/R2 legs that ran before it in the same `$WORK`.

**Neither confound is an N-D43 capability finding.** D6RF9's `NOT A RESULT | CONFOUNDED` says the question was
never cleanly measured, not that the primal cannot reach the floor. D6RF10 re-runs the identical ladder with
both confounds removed so the P2–P5 predictions (§2) can be MEASURED.

> **SUPERSEDED BY THE FROZEN BLOCK AT THE FOOT (2026-09-09).** The `PERMISSION = NOT_FROZEN` / DRAFT / STATUS lines throughout this file are superseded by the dated FROZEN block appended at the foot; they are retained unaltered per CLAUDE.md rule 6.

**PERMISSION = NOT_FROZEN.** This is a lane's prediction-first proposal. Nothing here is a registration until
the dafoam-supervisor freezes this file by sha (CLAUDE.md rule 2), after the supervisor's non-delegable
**check-1** (the grader is a name-only adaptation of the D6RF9 FROZEN grader — §4) **and** the chief's cost
sign-off on the **Option A / Option B decision (§5, §5b)**. The freeze, the per-instrument pin fixpoints and
the enqueue belong to the supervisor and are **not** taken here. **Zero compute has run for this item.**
Because D6RF10 is a NEW item, its gates are OPEN pre-compute; before first compute this file is amendable, and
any amendment must state the condition and how it was checked (name the run directory that does not exist:
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF10-a2-wing-convergence-probe/`, confirmed absent). After first
compute the gate, threshold, cap and label are closed (rule 2).

**Single-point by design.** As D6RF3→D6RF7→D6RF9, this A2 **convergence probe** is single-arm `P_conv`: it
exists to measure whether the primal reaches its own accept floor, not to optimise. The FD/CD/off-design/price
gates are dropped; the multipoint SHIPPED row is NAMED-UNBOUGHT and priced (§6), not bought here.

**DOWNSTREAM DEPENDENCY — unchanged from D6RF9. This item unblocks the mandatory D6R2 transonic multipoint.**
The mandatory **D6R2 transonic-multipoint chain stays BLOCKED** on the A2 accept-floor question. V-128 (commit
`a2978688`, 2026-09-08) ruled `p_first_uncorrected` STANDS as the binding field, the `GATE FAIL` is UPHELD, the
gate is NOT changed (T25). **D6R2 stays BLOCKED until D6RF10 either (a) drives `p_first_uncorrected < 1.0e-05`
at some rung (`STOPPED_AT_FIRST_PASS`), unblocking the A2 primal the transonic multipoint sits on, or (b)
measure-exhausts to a CAPABILITY FINDING (§2 P5) that re-opens the escalated N-D43 acceptance-rule question for
Sanaa.** The D6R2 blocker is not lifted here and not by the lab (§7). D6RF9 could NOT deliver either outcome
cleanly (the confounds); D6RF10 is the run that can.

---

## 0. WHY A SUCCESSOR AT ALL — the measured plateau, and the ruling that redirects it (carried from D6RF9 §0)

D6RF7's finding is a **measured** demonstration that scheme-side aids are insufficient. The binding residual is
`p`'s uncorrected first solve, established as a **monotone-asymptotic steady-state plateau** — the magnitude of
the explicit (lagged / deferred-correction) non-orthogonal correction term carried into each outer iteration's
first pressure assembly — *not* a linear-solver failure and *not* oscillatory
(`docs/dafoam/D6RF4_CONVERGENCE_RESEARCH.md:45-66`).

**Two facts MEASURED from the D6RF7 log** (a non-solver read, zero compute):

1. **The first-uncorrected p `initRes` is FLAT by outer-iteration ~300** and does not decay to `endTime 1000`.
   Sampled first-p-solve trajectory (F5/original-scheme leg): iter 100 `2.17e-04`, 200 `1.87e-05`, 300
   `1.662e-05`, 400 `1.659e-05`, 500–1000 all `1.6583e-05` to four figures. The LIMITED leg is the same shape
   at `1.6256e-05`. **The outer loop reaches a fixed floor; more iterations at the D6RF7 config do not move it.**
2. **The run ended at `Time = 1000 = endTime`, NOT at the accept floor.** Since `1.6256e-05 > 1.0e-05`, the
   primal never met its convergence criterion, so `endTime` is the binding outer-iteration cap.

**The OUTER-LOOP lever (not a mesh or scheme lever):** the deferred non-orthogonal correction is iterated by
`nNonOrthogonalCorrectors`, and D6RF7 only ever ran 3 correctors. Iterating the correction to convergence
(R2), changing the pressure–velocity coupling SIMPLE→SIMPLEC (R3), the outer horizon (R1) and the
under-relaxation (R4) are the outer-loop levers this item measures, IN ORDER. **V-128 rules the lever is
outer-loop convergence and that ruling binds this draft.** The genuine scientific risk is recorded plainly
(§2, §8): SIMPLE/SIMPLEC/relaxation converge to the same discrete fixed point, so the ladder may
**measure-exhaust** to a capability finding — registered to be MEASURED, never inferred.

---

## 1. THE GATE — INHERITED VERBATIM FROM D6RF7 → D6RF9 (T25)

**Gate id: `G-CONV`** — per field, per graded leg, the **final-iteration `initRes`** against the accept floor.

- **Threshold / accept floor = `CONV_BAR = 1.0e-05`** = `primalMinResTol 1e-08 × primalMinResTolDiff 1000`
  (**N-D43**: the floor is the **PRODUCT**, never the tolerance alone; `primalMinResTolDiff` is `1000` on this
  case, read from the run, never carried from memory).
- **Binding field = `p_first_uncorrected`** (the FIRST/uncorrected p-solve of the final outer iteration); the
  tighter `p_corrected` is reported, never gated as the convergence measure.
- **Verdict rule: `PASS` iff `v < CONV_BAR` else `GATE FAIL`**, per field; a leg is `PASS` only if every field
  is; a non-finite or absent field makes the leg `NOT A RESULT` (strictly restrictive, rule 5).

**T25 ASSERTION — NO WIDENING.** No gate, no threshold, no floor, and no field selection is moved. `CONV_BAR`
stays `1.0e-05`; `primalMinResTol` stays `1e-08`; `primalMinResTolDiff` stays `1000`; the binding field stays
`p_first_uncorrected`. The imported accept-floor control **refuses the grading (exit 2) in BOTH directions** —
a tightened floor refuses too — so this item cannot silently earn a PASS against a bar D6RF7/D6RF9 did not
fail. The accept-floor control `d6rf10_accept_floor_control.py` is a **BYTE-IDENTICAL** copy of D6RF9's
(md5 `c6e63098e7afd542ea379a03eccfaf12`, verified equal on disk — §4).

---

## 2. THE REGISTERED PREDICTION — HONEST, and TO-BE-MEASURED (`PENDING`) — carried from D6RF9 §2

Registered **before compute**; every clause is a prediction to be MEASURED, never inferred. **D6RF10 adds
nothing to the science; it removes the two confounds so these predictions can finally be measured.**

- **P1 (R1, extended horizon `endTime 2500`): predicted INSUFFICIENT** (flat by outer-iter ~300). **D6RF9
  MEASURED R1 clean and complete: `GATE FAIL`, `p_first_uncorrected ≈ 1.6255e-05` (~1.626×), `rc=0`,
  16.067 core-min** — R1 was NOT confounded, and D6RF10 re-runs it as the ladder baseline unchanged. `PENDING`.
- **P2 (R2, deep corrector loop 3→12): the load-bearing rung, outcome GENUINELY UNCERTAIN.** In D6RF9 R2 was
  **confounded (i) — killed incomplete before reaching `endTime`, so it measured nothing about the floor.**
  D6RF10's fix (i) is the whole reason this rung can now be measured. `PENDING`.
- **P3 (R3, SIMPLEC): may accelerate/deepen convergence; CD/CL shift predicted ~0.** In D6RF9 R3 was
  **confounded (ii) — crashed at step 0, measured nothing.** D6RF10's fix (ii) lets it run. `PENDING`.
- **P4 (R4, heavy under-relaxation): fallback, predicted low-probability.** In D6RF9 R4 was **confounded (ii) —
  crashed at step 0.** Fixed. `PENDING`.
- **P5 (ladder-level): the ladder MAY measure-exhaust.** If all four rungs are MEASURED (now confound-free) and
  none drives `p_first_uncorrected < 1.0e-05`, the item records a **CAPABILITY FINDING** — *measured*, not
  inferred — that **re-opens the escalated N-D43 acceptance-rule question for Sanaa** and is **not decided by
  the lab**. The `1.0e-05` floor is not widened under any outcome (T25). **This is the outcome D6RF9 could not
  legitimately reach, because a confounded ladder cannot exhaust anything.**

---

## 3. THE LADDER — ordered outer-loop-convergence rungs, IDENTICAL to D6RF9 (only the launcher's operational bugs fixed)

The chain runs rungs **in order** and **STOPS at the first rung whose graded leg drives
`p_first_uncorrected < 1.0e-05`** (`STOPPED_AT_FIRST_PASS`). Each rung changes **outer-loop numerics ONLY** —
never the mesh, geometry, objective/constraint, `fvSchemes` (held at D6RF7's `Gauss linear limited corrected
0.333`, md5 `8374443e7a374e9d353cffccdb654aaf`), or the accept floor. Every rung runs **beside the D6RF7 frozen
config as a known-fail control** (D4): a PASS on the control withdraws the rung's verdict.

| rung | lever | EXACT key changes vs D6RF7 config | endTime (Option A) | why |
|---|---|---|---|---|
| **R1** | extended outer horizon | `endTime 1000 → 2500` (nothing else) | 2500 | cheapest; the MEASURED control on the "run longer" lever; D6RF9-measured `GATE FAIL` |
| **R2** | deep corrector loop | `nNonOrthogonalCorrectors 3 → 12` | 2000 | iterate the LAGGED deferred-correction to within-iteration convergence — un-tried above 3 |
| **R3** | SIMPLEC coupling | `DARhoSimpleFoam → DARhoSimpleCFoam`; `relax (p\|p_rgh) 0.30 → 0.70`; keep `nNonOrth 12` | 2000 | consistent SIMPLE removes the pressure under-relaxation limit; same fixed point (CD/CL ~0, reported) |
| **R4** | heavy under-relaxation | `relax (p\|p_rgh) 0.30 → 0.15`, `equations 0.70 → 0.50`; keep SIMPLEC + `nNonOrth 12` | 4000 | damp the outer loop onto a lower plateau if the floor is a weak limit cycle (low-probability) |

**The two OPERATIONAL FIXES are in `d6rf10_run_arm.sh`, NOT in the science:**
- **Fix (i) — deadlines sized to the measured escalating rate (§5).** `rung_cap` is enlarged so
  `deadline_s = cap·60/RANKS − FRAME` can reach `endTime`, replacing D6RF9's undersized fixed deadlines.
- **Fix (ii) — `processor*` strip.** `rm -rf processor* mp0*/processor*` runs at staging AND at the start of
  every leg, so each leg (SIMPLEC included) decomposes fresh.

Notes bounding scope (unchanged): R3's SIMPLEC *activity* is read back from the run by `G-CONFIG` and a leg
that did not run the registered coupling is `NOT A RESULT`, never a PASS; no rung touches `fvSchemes`; no rung
raises `primalMinResTol` or `primalMinResTolDiff` (N-D43, the bright line).

---

## 4. GRADING PATH — the frozen instrument (name-only adaptation), controls, and check-1

- **Grader: `d6rf10_grade.py`** — a **NAME-ONLY adaptation** of the D6RF9 FROZEN grader `d6rf9_grade.py`
  (md5 `6e76ed57ac6890b0a7fa260c46dc517b`, frozen `ed181847`). The ONLY changes are the substitutions
  `D6RF9→D6RF10` / `d6rf9→d6rf10` (item name, leg-marker tokens, and the accept-floor import). **PROOF the gate,
  scoring, floor and field selection are byte-identical: reverse-substituting `D6RF10→D6RF9` in `d6rf10_grade.py`
  and diffing against `d6rf9_grade.py` is EMPTY.** The D6RF9 four DELTAS (D1 leg discriminator on
  `fvSolution`/`solverName`; D2 `G-CONFIG` reads back solver/nNonOrth/relax/endTime; D3 `CONV_MEASURED_D6RF7`
  baseline; D4 D6RF7-frozen control leg) are inherited unchanged. Leg tokens are renamed in BOTH the grader
  (reader) and `d6rf10_run_leg.py` (producer), so the static reader↔producer contract holds.
- **Accept-floor instrument: `d6rf10_accept_floor_control.py`** — a **byte-identical copy** of
  `d6rf9_accept_floor_control.py` (md5 `c6e63098e7afd542ea379a03eccfaf12`, VERIFIED equal on disk), which is
  itself byte-identical to D6RF7's. Imported, not re-implemented, so this file and the floor cannot disagree;
  it refuses (exit 2) if either floor term moves in EITHER direction (T25 made executable). **The floor is NOT
  widened (T25).**
- **Planted-zero control (CLAUDE.md rule 3):** `run_residual_plant_control` plants `PLANT_INITRES = 1.234e-03`
  into a COPY of a log, reads it back through the SAME `read_legs` the gate calls, refuses if the reader cannot
  see it, and asserts the original is byte-unchanged.
- **Driver: `d6rf10_run_leg.py`** — name-only adaptation of the frozen `d6rf9_run_leg.py`
  (md5 `ae6ee60ce40239e6579b0ba59ae311a9`); reverse-substitution diff EMPTY. Overrides only `solverName`;
  touches neither `primalMinResTol` nor `primalMinResTolDiff` (the bright line).
- **Drivable NOW at zero compute:** `python d6rf10_grade.py --drive` ran here: **RESULT `ALL AS REGISTERED`**
  (`rc=0`) — `accept_floor_inherited_verbatim=True`, `t25_floor_unmoved=True`, planted `1.234e-03` read back
  (`EXERCISED-PASS`, original unchanged), `1.62e-05 → GATE FAIL` / `8.0e-06 → PASS` scoring correct, a
  wrong-corrector leg ⇒ `NOT A RESULT`.
- **check-1 (supervisor, non-delegable):** confirm the reverse-substitution diffs are empty (grader + driver),
  confirm the accept-floor md5 `c6e63098`, then set the D6RF10 grader/driver md5 pins at freeze
  (`MD5_GRADE` / `MD5_RUN_LEG` are `PLACEHOLDER_AT_FREEZE` in the launcher, and `GRADER_MD5` in the autograder;
  each refuses to run while a placeholder stands).

---

## 5. COST — costed estimate / cap (CLAUDE.md rule 12), grounded in the MEASURED R2 escalation

**The load-bearing measured fact: R2's per-step cost ESCALATES.** From the D6RF9 R2 candidate log —
`Time 1 → ExecutionTime 3.83 s`; `Time 100 → 143.56 s` (≈`1.41 s/step` over 1–100); `Time 200 → 557.35 s`
(≈`4.14 s/step` over 100–200, **and still rising**); killed at the `855 s` deadline near `Time ~250`, `rc=124`.
A quadratic fit `E(N) = 3.79 + 0.0276·N + 0.01370·N²` seconds reproduces all four anchors (it predicts the kill
at `N≈249` for `855 s` — matching the ledger `wall_s=862`). `core_min = E·RANKS/60 = E/15`; `RANKS=4`. Dollars
are **DERIVED** at **c7a.4xlarge `$0.0513/core-h`** (`$0.000855/core-min`), **reported-by-owner, NOT measured**
(the box cannot read its own billing; `COMPUTE_BUDGET_CHARTER.md` §5).

**Two extrapolation models bracket every non-R1 rung, because the escalation was still rising at the kill so a
single number is not honest:**
- **QUADRATIC (upper):** the per-step cost keeps rising as fit — `E(N)` above. This is **not a true ceiling**:
  we have no data beyond `N≈250`, so the real cost could be even higher, or lower if it plateaus.
- **PLATEAU (lower):** the per-step cost freezes at the last measured rate `4.14 s/step` from step 200:
  `E(N) = 557.35 + 4.138·(N−200)` for `N>200`. Optimistic; the measured trend argues against it.

R1 is **MEASURED complete** (`endTime 2500`, `rc=0`, candidate `16.067` + control `7.4` = `23.5 core-min`,
`GATE FAIL`) and needs no re-estimate. Control legs are measured at `~7.4 core-min` each. R3/R4 (SIMPLEC) ran
ZERO steps in D6RF9 (confound ii), so **their candidate cost is UNMEASURED and uses R2's escalation as a
PROXY** — flagged, not measured.

### 5a. OPTION A — keep endTimes 2500/2000/2000/4000, size deadlines so each rung completes (chief's literal framing)

| rung | endTime | candidate core-min (plateau → quadratic) | +control | rung est range (core-min) | rung cap (draft) |
|---|---|---|---|---|---|
| R1 | 2500 | **16.1 (MEASURED, `rc=0`, complete)** | 7.4 | **23.5 (measured)** | 48 |
| R2 | 2000 | 533.7 → 3657.3 | 7.4 | **541.1 → 3664.7** | 700 |
| R3 | 2000 | 533.7 → 3657.3 *(SIMPLEC proxy)* | 7.4 | **541.1 → 3664.7** | 700 |
| R4 | 4000 | 1085.5 → 14620.9 *(SIMPLEC proxy)* | 7.4 | **1092.9 → 14628.3** | 1420 |

- **Ladder total estimate (all four rungs run to completion): `2198.6` (plateau) → `21981.2` (quadratic) core-min**
  ⇒ **`$1.88` → `$18.79` DERIVED.**
- **Ladder cap (draft, sum of per-rung caps): `2870 core-min` ⇒ `$2.45` DERIVED.** Set from the plateau
  estimate × ~1.3 margin. Both totals sit under the $25 CPU pre-authorisation, but the ladder cap is
  **~10× the D6RF9 `291` hard stop.**
- **HONEST WARNING — Option A may NOT remove confound (i).** The `2870`-core-min cap reaches `endTime` **only if
  the escalation plateaus.** If it continues quadratically, R2 needs `~3665` core-min (and R4 `~14628`), the
  cap is hit, the run stops (rule 12) and R2/R3/R4 are **again incomplete** — reproducing confound (i) at 10×
  the cost. And every Option A leg runs `2.5–6 wall-hours`, each of which is a **"stall" (>3600 wall s)** under
  `COMPUTE_BUDGET_CHARTER.md`. The quadratic upper bound is **not measurable** from the data we have.

### 5b. OPTION B — shorten R2/R3/R4 endTime to the plateau horizon (a DESIGN CHANGE, for chief/Sanaa to rule; NOT baked in)

R1 measured `p_first_uncorrected` **flat by outer-iter ~300** (§0), essentially converged to four figures by
~400–500. A shorter `endTime` reaches the plateau and satisfies rule-4 completion at far lower cost — it pays
for the plateau reading (the entire scientific question) and not for thousands of post-plateau iterations §0
measured do not move the residual. **This changes a rung lever (`endTime`) versus D6RF9, so it is a DECISION,
not a mechanical confound fix**; the corrector-depth science (R2's nNonOrth 12) is unchanged.

| B variant | R2/R3/R4 endTime | R2 (or R3/R4) rung est, core-min (plateau → quad) | ladder total (plateau → quad) | $ DERIVED | vs D6RF9 `291` cap |
|---|---|---|---|---|---|
| B-1000 | 1000 (D6RF7 baseline) | 265.3 → 922.8 | **819.4 → 2791.9** | $0.70 → $2.39 | 2.8× – 9.6× over |
| B-500 | 500 | 127.3 → 236.9 | **405.4 → 734.2** | $0.35 → $0.63 | 1.4× – 2.5× over |
| **B-300** | 300 (bare plateau onset + margin) | 72.1 → 90.4 | **239.8 → 294.7** | $0.21 → $0.25 | **FITS (0.82× – 1.01×)** |

(R1 stays `endTime 2500`, `23.5 core-min` measured, in every B variant. R3/R4 use R2's escalation as a proxy.)

- **Only B-300 fits the existing `291`-core-min envelope**; even B-1000 blows it. This is a direct consequence
  of the steep measured escalation: the plateau horizon (~300 outer-iters) is affordable at `nNonOrth 12` only
  near its onset.
- **Scientific caveat on B:** R1's plateau horizon (~300 iters) is measured at `nNonOrth 3`. R2's `nNonOrth 12`
  may plateau at a **different** horizon; a too-short `endTime` risks reading a not-yet-plateaued value.
  A defensible B choice keeps margin (B-500 over B-300) OR reads back the per-iter trajectory to confirm the
  plateau before grading. This is exactly the lever-change judgement reserved to the chief/Sanaa.

### 5c. Recommendation (lane, non-binding) and calibration

The lane's honest read: **Option A cannot be guaranteed to remove confound (i)** (the escalation may just
re-time-out at 10× cost), and its legs are all stalls. **Option B at a plateau-horizon `endTime` (B-500 with a
trajectory check, or B-300 if the `291` envelope must hold) removes confound (i) by construction** — the run
completes to a short `endTime` well within any sane deadline — at `<$1` derived. But B changes a rung lever, so
**the choice is the chief's / Sanaa's, recorded at freeze (§PERMISSION).** The launcher currently encodes
Option A (chief's framing); the supervisor sets the final `rung_endtime`/`rung_cap`/hard-stop at freeze (the
launcher is OUTSIDE the freeze hash-lock, D19T parent posture).

**Estimate-vs-actual calibration (rule 12):** at each rung's completion the pre-registered per-rung estimate is
compared to the actual `core_min` from the log; the ratio and its attribution (contention / waste / escalation
misprediction — waste named separately, never absorbed) land as a row in `docs/COST_CALIBRATION.md` under that
file's append rules and the rule-10 private-index protocol. **The escalation model above is the first thing to
recalibrate:** D6RF9 measured only `N≤250`; the first D6RF10 rung that completes to a real `endTime` is the
first measurement of whether the per-step cost plateaus or keeps rising.

---

## 5ba. LAUNCH PLAN — §2ba: live monitor AND committed detached autograder (charter v1.72)

Every rung launches under BOTH:
1. **A live monitor** the launching lane watches (per-leg `Time`/`ExecutionTime` progress and the ledger), so a
   stall or a re-decomposition collision is caught in real time — not discovered only at the deadline.
2. **A committed detached autograder — `d6rf10_autograde.sh`** — run under `setsid` (PPID=1, own session) so
   the authoritative grade lands even after the agent fleet dies. It polls the ledger for `D6RF10_LADDER_DONE`,
   verifies the frozen grader md5 (REFUSES exit 2 on drift), grades every real-solver rung, and writes
   `D6RF10_AUTOGRADE_DONE.txt`. It **declares no verdict and files no row** — those are the supervisor's calls.
   **It inherits the already-fixed `any_pass` logic byte-identically: `any_pass` keys ONLY on
   `"binding_verdict":"PASS"`** (the D6RF9 autograder fix committed `c37a8206` today — the prior regex
   false-matched per-field verdicts and the control's `EXERCISED-PASS`, giving a cosmetic `any_pass=1` on an
   all-`GATE FAIL`/`NOT A RESULT` ladder; real binding verdicts always read direct). The `GRADER_MD5` is
   `PLACEHOLDER_AT_FREEZE` in the draft and set at freeze.

---

## 6. TWO-ROW RULE (DAFOAM_CHARTER.md §6)

- Row **BOUGHT**: `PATCHED` (patched IDWarp image; digest `sha256:2927768a…30f6d35`, the same D6RF7/D6RF9 bought).
- Row **NOT BOUGHT**: `SHIPPED`, **priced anyway at `155.70 core-min`** (a multipoint F_mp on stock IDWarp at
  the same cap). An unbought row that is priced can be bought by a successor; an unbought row that is unpriced
  quietly becomes never.

---

## 7. WHAT THIS ITEM DOES NOT DECIDE

- It does **not** re-open the acceptance rule. Whether a successor may register a different acceptance rule is
  **escalated to Sanaa and unruled** (N-D43); D6RF10 either reaches the *unchanged* floor or records a MEASURED
  capability finding that puts the question on Sanaa's desk.
- It does **not** choose Option A vs Option B — that lever-change decision is the chief's / Sanaa's, recorded
  at freeze (§5b).
- It does **not** freeze, launch or enqueue anything (`PERMISSION = NOT_FROZEN`). SUBMISSIONS PARKED.

---

## 8. WHAT I COULD NOT VERIFY (honest gaps)

- **Whether any rung actually reaches the floor is UNMEASURED and is the whole point of running the item** — and
  in D6RF9 it was never measured at all for R2/R3/R4 (the confounds). The registered risk (§2) that the floor is
  the deferred-correction residual at the shared fixed point stands; not inferred either way.
- **The escalation model is fit to `N≤250` only.** Whether R2's per-step cost plateaus or keeps rising past
  `~step 250` is UNKNOWN; it is the single largest cost uncertainty and drives the Option A/B gap. The quadratic
  "upper" is not a proven ceiling.
- **R3/R4 (SIMPLEC) candidate cost is a PROXY from R2** — SIMPLEC never ran a step in D6RF9. SIMPLEC's per-step
  cost and convergence rate on this case are unmeasured; the proxy may over- or under-state.
- **Confound (ii)'s fix is verified structurally, not dynamically.** The `processor*` strip is confirmed to
  leave no stale dirs at staging (launcher asserts it), and the per-leg strip is emitted into every cmd file;
  but that `DARhoSimpleCFoam` then decomposes and runs cleanly is UNMEASURED until R3 runs (no compute here).
- **R3's SIMPLEC *activity*** on the A2 `P_conv` setup is not confirmed at freeze; `G-CONFIG` reads it back and
  refuses (`NOT A RESULT`) if the registered coupling did not run. A supervisor/liaison activity confirmation
  before R3 (as done for A1) is a follow-up, not established here.
- **The grader/driver md5 pins are `PLACEHOLDER_AT_FREEZE`.** The byte-identity of the grading LOGIC to D6RF9's
  frozen instruments IS verified now (empty reverse-substitution diff; accept-floor md5 `c6e63098` equal);
  the supervisor sets the D6RF10 file md5 pins at freeze.

---

## (DRAFT — NOT FROZEN)

**STATUS: DRAFT, `PERMISSION = NOT_FROZEN`.** This file is a lane's prediction-first proposal. It is not a
registration and no gate/threshold/cap/label is committed until the dafoam-supervisor appends a dated FROZEN
block here (as D6RF9 did at its foot) after check-1 and the chief's §5/§5b cost sign-off. No compute has run.
SUBMISSIONS PARKED (CLAUDE.md rule 7).

---

## AMENDMENT A1 — 2026-09-09 (S-144) — pre-compute confound-removal: complete the SIMPLEC divSchemes

*lines whose number changed above this section: 0*

**Legality (CLAUDE.md rule 2 — pre-first-compute).** The GRADED D6RF10 run root does **not** exist
(`/home/ubuntu/certonomous-runs/` carries only the SEPARATE `D6RF10-PREFLIGHT-EXERCISE` measurement root, never
a graded row). `PERMISSION = NOT_FROZEN`; grader/driver md5 pins are still `PLACEHOLDER_AT_FREEZE`. This is a
pre-first-compute amendment; it alters **no gate, threshold, cap, label or floor** (the `1.0e-05`
p_first_uncorrected accept floor and T25 are UNCHANGED). It is a confound removal, not a lever change.

**Condition, and how it was checked.** The §2bb pre-flight MEASUREMENT exercise (ran ~2026-09-09T06:00Z; root
above) drove R3/R4 (`DARhoSimpleCFoam`, compressible SIMPLEC) to `rc=59` at ~11 s each, before any solve:
`FOAM FATAL IO ERROR: Entry 'div(phid,p)' not found in dictionary ".../mp04/system/fvSchemes/divSchemes"`
(R3 smoke log lines ~2132-2196). The D6RF9 decompose collision is separately FIXED (this exercise's
`decomposePar` ran clean). R2 (`DARhoSimpleFoam`, non-SIMPLEC) reached endTime 300 `rc=0` on the SAME staged
fvSchemes — so `div(phid,p)` is referenced only on the compressible-SIMPLEC pressure-flux path, which is why
the registered R3/R4 solver could not start at all.

**Change (verbatim from the solver's own canonical tutorials — NOT a discretisation lever).** Two divScheme
entries are added to `curriculum_D6RF7/d6rf7_fvSchemes_LIMITED` (the single source `cp -a`'d into
`{,mp04/,mp05/,mp06/}system` by both the exercise and `d6rf10_run_arm.sh`):

| entry | value | source (all four `DARhoSimpleCFoam` tutorials byte-identical, divSchemes block md5 `744b37fe3d8b`) |
|---|---|---|
| `div((nuEff*dev2(T(grad(U)))))` | `Gauss linear` | `/home/ubuntu/dafoam-tutorials/{NACA0012_Airfoil/transonic,Onera_M6_Wing,DPW4_Aircraft,CRM_Wing}/system/fvSchemes` |
| `div(phid,p)` | `Gauss limitedLinear 1.0` | same four files |

Values are taken verbatim from the tutorials of the exact registered solver (`DARhoSimpleCFoam`); neither was
chosen to aid convergence (upstream `rhoSimpleFoam`'s `Gauss upwind` for `div(phid,p)` was deliberately NOT
used — that would be a robustness lever). The **working** entries (the `bounded` D6RF7 forms R1/R2 already ran)
are untouched. Under `divSchemes { default none; }` an unreferenced entry is inert — `div(phid,p)` is inert for
R2 (proven: R2 ran clean without it), and the addition covers the compressible-SIMPLEC term set completely
(both the rho and non-rho viscous forms are now present), closing the missing-entry surface in one pass.

**md5 supersession.** The body of this file (and both launchers) pinned `d6rf7_fvSchemes_LIMITED` at
`8374443e7a374e9d353cffccdb654aaf`; that reference is **struck** and superseded by
**`fbca617a0808c56113a34d156c5890b9`**. Pins updated in lockstep: `d6rf10_preflight_exercise.sh:110`,
`d6rf10_run_arm.sh:205`. No gate/floor/grader pin changed.

**What still gates the FREEZE (unchanged three-gate discipline).** (1) a re-exercise MEASURING each SIMPLEC rung
(R3/R4) to first solve + its per-step cost + p_first_uncorrected plateau (the current exercise never measured
them — the crash); (2) verification's verdict-preservation / T25 audit of this amendment returning SOUND;
(3) `scripts/check_ladder_preflight.py` (§2bb) PASS on the combined manifest. R2@300 stays SOUND (S-143/T25).
Nothing here freezes, launches or enqueues a graded run. SUBMISSIONS PARKED.

---

## AMENDMENT A2 — 2026-09-09 (S-144) — plateau criterion for a would-be-PASS rung (operationalizes rule 5); R3 runs to its REGISTERED endTime 2000

*lines whose number changed above this section: 0.* Appended at the foot under rule 6. Pre-first-compute
(the GRADED D6RF10 run root does NOT exist; `PERMISSION = NOT_FROZEN`). **This addendum is STRICTLY MORE
RESTRICTIVE and touches NO gate / floor / cap / field / label** — the 1.0e-05 accept floor on
`p_first_uncorrected` is UNCHANGED. It adds a plateau requirement that a `PASS` must clear, per CLAUDE.md
rule 5 (a convergence verdict is a claim about the plateau, not one sub-floor sample taken while the value
is still descending). Authority: verification's cross-team gate-audit ruling on the R3 re-exercise
(chief-relayed, 2026-09-09), which found the S-143 "B-300" horizon does NOT apply to a would-be-PASS rung.

**Why (measured).** The D6RF10 re-exercise measured R3 (SIMPLEC `DARhoSimpleCFoam`, relax_p=0.70) at
`p_first_uncorrected@300 = 6.306e-6` — BELOW the 1.0e-05 floor — but with a **9.16% late-window relative
spread, still monotone-DECREASING**. The campaign's own measured plateau signature is R1's **0.307% drift
over outer-iterations 300→2500**. A 9.16%-moving sub-floor sample is not a plateau; and reading R3 at
iter 300 *because* it dipped below floor is selection-by-horizon (forbidden). The "below-floor + decreasing
→ conservative" argument is valid ONLY for a GATE-FAIL rung (R1), never a would-be-PASS rung — local
monotonicity over a 9.16% window is not the global asymptotic flatness a PASS needs, and the campaign names
a weak-limit-cycle possibility near the floor.

**The criterion (I set the numbers; frozen pre-compute).** For ANY D6RF10 rung to be graded `PASS`, BOTH must
hold at its REGISTERED endTime (NOT a shortened horizon):
1. **Below floor:** `p_first_uncorrected(endTime) < 1.0e-05` (the existing accept floor, verbatim, unchanged).
2. **Plateaued:** over the **late window = outer-iterations [1500, 2000]** (R3's registered endTime 2000; ≥5
   `p initRes:` first-uncorrected samples read from the solver log over that window), the **relative spread
   `(max − min) / mean` ≤ 0.31%** (bounding by R1's measured 0.307% plateau signature — the campaign's own
   bar; catches BOTH residual drift AND a weak limit cycle).
   - Below floor AND plateaued → **PASS**.
   - Below floor but spread > 0.31% (still moving / oscillating) → **NOT A RESULT** (not converged, rule 5).
   - Plateaued but ≥ floor → **GATE FAIL**.

**R3 horizon (correcting the S-143 draft).** R3 is graded at its **REGISTERED endTime 2000**, NOT 300 and NOT
an ad-hoc 600–1000 — no authority shortens the horizon of a rung whose plateau is unmeasured; shortening is
what produced the R3@300 ambiguity. Cost ≈ 450 core-min (R3's measured 4.15 s/step × 2000 × 4 ÷ 60, np=4),
under budget; the §2bb deadline is sized from that measured per-step rate ×1.25. R1 (complete, endTime 2500)
and R2 (endTime per registration) are unaffected — R2 stays a GATE-FAIL rung (1.68e-5 > floor), for which the
B-300/early-stop-conservative logic still holds.

**R4 (NOT dropped).** R4 stays registered; under STOPPED_AT_FIRST_PASS a clean R3 PASS never reaches it.
R4's re-exercise `rc=1` GAMG `SolverPerformance`-readback confound (primal solved; a post-solve config/
instrument defect, triaged) is recorded; striking R4 from the ladder would require its OWN dated amendment
stating that condition + how checked, and is NOT done here.

Nothing here freezes, launches or enqueues a graded run. SUBMISSIONS PARKED.

---

## AMENDMENT A3 -- 2026-09-09 -- R2 registered endTime 2000 -> 300 (removes a MEASURED rising-cost timeout confound; conforms to verification's b88c8926 R2-SOUND-at-300 ruling)

*lines whose number changed above this section: 0.* Appended at the foot under rule 6.

**Legality (CLAUDE.md rule 2 -- PRE-FIRST-COMPUTE, condition AND how checked).** This is a pre-first-compute
amendment. **How checked:** the GRADED D6RF10 run root does **not** exist --
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF10-a2-wing-convergence-probe/` is confirmed ABSENT on disk (only
the SEPARATE `D6RF10-PREFLIGHT-EXERCISE` measurement root is present, never a graded row). `PERMISSION =
NOT_FROZEN`; the grader/driver md5 pins are still `PLACEHOLDER_AT_FREEZE`. Because zero graded compute has run,
the gate, threshold, cap and label are still OPEN and this amendment is legal.

**Condition (all MEASURED, not inferred).** R2 (`nNonOrthogonalCorrectors 12`, `DARhoSimpleFoam`) is a
**GATE-FAIL rung**: the D6RF10 pre-flight exercise measured its `p_first_uncorrected@300 = 1.68e-5`, which is
`> 1.0e-05` (the accept floor, unchanged). The exercise ALSO measured R2's **per-step wall cost RISING**:
`4.330 s/step over [100,200] -> 5.059 s/step over [200,300]` (the late window `5.0585 s/step` is recorded in
`D6RF10-PREFLIGHT-EXERCISE/d6rf10_preflight_MEASUREMENTS.json`). Extrapolated, `endTime 2000` is a **predictable
TIMEOUT**: a flat-rate deadline is exhausted at `~iteration 1447`, well short of `2000` -- which would
RE-INTRODUCE the very "incomplete-run" confound (i) that D6RF10 exists to remove (rule 4: last time != endTime
-> the run is incomplete and its `GATE FAIL` is not a measured floor-miss). Two facts remove the confound at a
short horizon: (a) verification's standing **T25 ruling `b88c8926` found R2 SOUND at endTime 300** (the binding
residual is monotone-DECREASING, so an early stop reports a HIGHER value -- conservative, it cannot manufacture
a PASS); and (b) the exercise ran R2 **COMPLETE to endTime 300, `rc=0`** (`stopped=no`, cumulative wall
`~1052.48 s`). A complete run to 300 measures the floor cleanly; a timed-out run to 2000 does not.

**What A3 changes -- STRICTLY cost-reducing, verdict-PRESERVING, and ONLY R2's endTime.** R2's registered
`endTime` moves `2000 -> 300`. It moves **NO gate, NO floor, NO cap, NO field, NO label** -- the `1.0e-05`
accept floor on `p_first_uncorrected` and T25 are UNCHANGED; only R2's outer-iteration horizon changes, and it
changes DOWNWARD to conform to verification's standing ruling. For a **GATE-FAIL** rung this is direction-safe
by rule 5: the binding field is monotone-DECREASING over the outer loop, so a SHORTER horizon reports a **HIGHER**
`p_first_uncorrected` than a longer one -- the shortened R2 can therefore only stay `GATE FAIL`, and can **never**
manufacture a `PASS` against the unchanged floor. (This B-300/early-stop-conservative argument is valid ONLY for
a gate-fail rung; it is NOT applied to any would-be-PASS rung -- R3 stays at its registered endTime 2000 under
AMENDMENT A2, unchanged here.)

**Ambiguity resolved, honestly, subject to verification's binding call.** AMENDMENT A2 said "R2 (endTime per
registration)" -- and the grader's REGISTERED CONFIG dict carried R2 at `endTime 2000` -- while verification's
`b88c8926` ruled R2 **SOUND at endTime 300**. A2's wording and the grader config were therefore in tension with
the standing ruling. **A3 resolves that tension to `300`**, on the NEW measured rising-cost evidence above (which
was not before A2 when it was written), and does so **subject to verification's binding confirmation** that
`endTime 300` is the correct registered R2 horizon. If verification rules otherwise, this amendment is struck
and re-drafted; nothing here is frozen. The dafoam-supervisor's decision to move R2 `2000 -> 300` is pending
verification's binding confirmation and is the reason this file, the grader R2 config, and the §2bb manifest are
brought into agreement at `300` in one pass.

**What still gates the FREEZE (unchanged discipline).** (1) verification's binding confirmation of R2@300 and
its verdict-preservation / T25 audit of this amendment returning SOUND; (2) the supervisor's non-delegable
check-1 (the R2 endTime `2000 -> 300` grader diff read as a diff, grader/driver reverse-substitution diffs empty,
accept-floor md5 `c6e63098` unmoved); (3) `scripts/check_ladder_preflight.py` (§2bb) PASS on the rebuilt manifest
(R2 at endTime 300, deadline 1350 s from the proven ~1052.48 s complete run; R3 at endTime 2000, Basis-B deadline
16900 s). Nothing here freezes, launches or enqueues a graded run. SUBMISSIONS PARKED.

---

## FROZEN 2026-09-09 by dafoam-supervisor

**This block supersedes every DRAFT / `NOT_FROZEN` / STATUS line above (CLAUDE.md rule 6: originals are struck-by-supersession, never rewritten).**

**Design.** R1 endTime 2500, R2 endTime 300 (AMENDMENT A3, verification-SOUND `52c3f947`), R3 endTime 2000 (AMENDMENT A2). §2bb deadlines R1 600 s / R2 1350 s / R3 16900 s (R3 Basis-B, disclosed effective-average per-step). Accept floor `1.0e-05` on `p_first_uncorrected` UNCHANGED; the A2 plateau gate (spread <= 0.31% over [1500,2000]) binds a would-be-PASS. Frozen grader md5 `0cb9d89a11347bc943acf3b38e1766d2`, run_leg md5 `4136c1e45ba641b74ce09117e7009ff8`. PERMISSION is set in `d6rf10_run_arm.sh` to THIS freeze commit's sha in the immediately-following commit. Ladder STOPPED_AT_FIRST_PASS. Cost cap ~1257 core-min (~$1.07 DERIVED). SUBMISSIONS PARKED.

---

## ADDENDUM — 2026-09-09 — launcher runtime params brought into compliance with the already-frozen registration (moves NO gate/threshold/cap/label/endTime)

*lines whose number changed above this section: 0.* Appended at the foot under rule 6. This is a **post-first-compute** dated addendum (rule 2): it records a CORRECTION to a file OUTSIDE the freeze hash-lock (`d6rf10_run_arm.sh`, D19T parent posture) and **cannot and does not alter any gate, threshold, cap, label, field or endTime of the frozen REGISTRATION** — the registration was always R1@2500 / R2@300 / R3@2000, §2bb deadlines 600 / 1350 / 16900 s, accept floor `1.0e-05`. None of those move.

**Finding.** After first compute, the launcher's runtime params were found **STALE** versus this frozen registration: `rung_endtime()` returned R2 = 2000 (registered **300** per AMENDMENT A3) and `rung_cap()` returned R3 = 700 → deadline `10410 s` (registered Basis-B manifest deadline **16900 s**). Additional Option-A leftovers: R1 cap 48 → deadline 630 s (registered 600 s), R2 cap 700 → deadline 10410 s (registered 1350 s), and the cumulative hard stop was 2870 core-min (the four-rung Option-A sum). The run executing these stale params was **STOPPED** and stands as **NOT A RESULT | CONFOUNDED**, archived at `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF10-a2-wing-convergence-probe.CONFOUNDED-ARCHIVE.20260909T232614Z` (untouched, rule 6).

**Correction (launcher only).** `rung_endtime()` R2 → 300 (R1/R3/R4 already matched the grader: 2500 / 2000 / 4000). `rung_cap()` R1 → 46 (deadline 600), R2 → 96 (deadline 1350), R3 → 1133 (deadline 16905 ≥ the 16900 floor; 1133 is the smallest INTEGER cap that meets it, since exact 16900 needs cap 1132.67). `CUMULATIVE_HARD_STOP_CORE_MIN` → 1275 = the sum of the three frozen-registration per-rung caps (46 + 96 + 1133), which equals the frozen ~1257 core-min DEADLINE-basis budget plus the 3×90 s per-rung FRAME_ALLOWANCE (18 core-min) — the same 3-rung budget in the two bases. Every corrected runtime param now MATCHES the frozen registration; a runtime-param-vs-registration table is the check-1 artifact.

**R4 — flagged, NOT resolved by this lane.** The launcher ladder loop still iterates `R1 R2 R3 R4` (STOPPED_AT_FIRST_PASS). R4 (endTime 4000, cap 1420) MATCHES the grader RUNG_CONFIG but is **NOT** in the frozen 3-rung §2bb manifest and is NOT covered by the ~1257 / 1275 core-min budget, and R4 carried the S-144 GAMG-readback confound. This lane changed **neither** R4's endTime nor its cap. Whether R4 is registered (manifest + budget) or removed from the loop is a dafoam-supervisor decision, owed BEFORE any re-launch.

**Lesson owed.** The lesson from this correction — a launcher's runtime params must be re-verified against the frozen registration (endTime, per-rung deadline, cumulative budget) after any amendment, because a file outside the freeze hash-lock can drift and silently confound the run — is owed to `docs/LESSONS.md`; its number is assigned from the tail at that commit (rule 11) and is not fabricated here.

---

## R4-STRIKE AMENDMENT — 2026-09-09 — R4 struck from the RUNNABLE ladder loop (chief ruling; AMENDMENT A2's strike-condition met)

*lines whose number changed above this section: 0.* Appended at the foot under rule 6.

**Authority.** AMENDMENT A2 required that striking R4 from the ladder "would require its OWN dated amendment stating that condition + how checked." The chief ruled STRIKE R4 from the D6RF10 runnable ladder (LAB_STATE, 2026-09-09). This amendment is that dated amendment. It moves **NO gate, threshold, floor, cap, label or field** of R1/R2/R3, and does **NOT** change R4's grader `RUNG_CONFIG` — R4 stays **registered-but-not-run**. It only removes R4 from the launcher's ladder LOOP (`d6rf10_run_arm.sh`, a file OUTSIDE the freeze hash-lock, D19T parent posture): the loop `for RUNG in R1 R2 R3 R4` becomes `for RUNG in R1 R2 R3`.

**CONDITION — R4 is struck from the RUNNABLE ladder for three independent reasons, each traced to a measured/recorded artefact:**

- **(a) R4 is ABSENT from the frozen 3-rung §2bb manifest `LADDER_PREFLIGHT.json`.** Launching R4 would run an UNREGISTERED rung — the freeze-integrity failure class of **L-517** (a launcher runtime param that has no counterpart in the frozen registration silently confounds the run).
- **(b) R4 was never cleanly pre-flight-exercised, and its S-144 GAMG-readback confound is unresolved.** The D6RF10 re-exercise measured R4 (`DARhoSimpleCFoam`, relax_p=0.15) at `rc=1` at ~44 steps — a DAFoam `SolverPerformance` readback parse error on `system/data/solver/p` (`Expected '(' … found 'GAMG'`); the primal solved (CD 0.0237 / CL 0.298) but the post-solve config/instrument defect stands untriaged-to-resolution. Running R4 now risks another confounded **NOT A RESULT** — a repeat of a known mistake (**L-516**).
- **(c) R4's cap 1420 core-min EXCEEDS the frozen 3-rung hard-stop 1275 core-min.** A rung pre-registered to blow the budget must not launch (**rule 12** — an overrun stops the run; it does not get a new budget).

**HOW CHECKED (all verifiable):**

- **(a)** `LADDER_PREFLIGHT.json` lists exactly R1/R2/R3 — its `rungs` array has three entries and no `"rung": "R4"` (grep it). R4 is absent by inspection.
- **(b)** The S-144 GAMG-readback confound is recorded in this file (AMENDMENT A2, R4 paragraph; the ADDENDUM R4 paragraph) and in the dafoam board (LAB_STATE S-144: R4 `rc=1` at ~44 steps, `SolverPerformance` `Expected '(' … found 'GAMG'`, primal solved, post-solve defect — a separate follow-up).
- **(c)** Arithmetic: launcher `rung_cap R4` = 1420 core-min > `CUMULATIVE_HARD_STOP_CORE_MIN` = 1275 core-min (= R1 46 + R2 96 + R3 1133).

**Scope.** `rung_endtime()`/`rung_cap()`/`rung_solver()` etc. still carry harmless R4 entries in their `case` statements; the loop no longer calls them, so R4 is unreachable in the runnable ladder. R4's grader `RUNG_CONFIG` is untouched: R4 remains a registered rung whose verdict path exists, but it is not run.

**If R4 is ever wanted later** it must FIRST get its own pre-flight EXERCISE resolving the S-144 GAMG-readback confound (**L-516** — no repeat of a known mistake) AND a runtime-param registration in the §2bb manifest `LADDER_PREFLIGHT.json` (**L-517** — no unregistered rung in the loop), before being returned to the loop. This amendment does not authorise that return.

Nothing here freezes, launches or enqueues a graded run. SUBMISSIONS PARKED.

---

## DATED ADDENDUM 2 — 2026-09-12, R2 RE-FIRE: THE CAP IS **REMOVED AS A STOP AND RETAINED AS A REPORTED FIGURE**, AND THE PREDICTION IS REGISTERED BEFORE THE RUN

> 🔴 **THIS HEADING REPLACES AN EARLIER DRAFT OF THIS SAME ADDENDUM THAT READ "THE CLOCK
> KILL IS REMOVED, THE CAP IS RAISED".** That draft was written, was never committed, and
> is struck here in place rather than silently overwritten. **Under Sanaa's 2026-09-12
> directive #17 a cap RAISE is not a smaller change than a cap REMOVAL — it is the wrong
> change**, because it leaves a kill in the file and merely moves it further out. The
> ruling applied below is REMOVAL. **`rung_cap R2` is restored to its frozen `96`** and
> `CUMULATIVE_HARD_STOP_CORE_MIN` to its frozen `1275`; neither number kills anything any
> more, and both are still printed into the ledger.

**Version 1.3. Lines whose number changed above this section: 0.** This addendum is APPENDED. It strikes nothing above by rewriting it; every superseded statement is superseded in place by this block (CLAUDE.md rule 6). It **alters no gate, no threshold, no band, no floor, no label and no grading path**, and the frozen instruments are unmoved on disk at this writing: grader `d6rf10_grade.py` md5 `0cb9d89a11347bc943acf3b38e1766d2`, driver `d6rf10_run_leg.py` md5 `4136c1e45ba641b74ce09117e7009ff8`, accept-floor control `d6rf10_accept_floor_control.py` md5 `c6e63098e7afd542ea379a03eccfaf12`. Ruled by the dafoam-supervisor, **[lab-attributed]**; drafted and applied by a dafoam lane.

### 1. What died, and what it was

The graded R2 candidate leg (`ledger.txt`: `rung=R2 leg=R2 rc=124 wall_s=1357`, log `R2_20260910T024650Z_953457.log`) was **SIGKILLed by `timeout` against the §2bb deadline `1350 s`**, at `Time` ≈ 292–299 of its registered `endTime` 300 (`D6RF10_GRADE_RECORD.md` §4). The frozen grader correctly returned `NOT A RESULT`, `reason: CONFIG_NOT_AS_REGISTERED`, `final_time: 0` — the registered config **was** installed (`config_install_marker`: `endTime 300, nNonOrth 12, relax_p 0.30, sites 4`); what was absent was a completed final outer iteration for the corrector count to be read back from. **The cause was the clock, not the physics and not either D6RF9 confound.**

### 2. The change, named for what it is: **EVERY STOP ACTION IS DELETED; EVERY FIGURE IS KEPT**

The §2bb deadline is not an independent constant. `d6rf10_run_arm.sh` computes `DEADLINE = round(CAP*60/RANKS) - FRAME_ALLOWANCE_S` (RANKS 4, FRAME 90). R2's `1350 s` **is** its registered 96 core-min cap expressed in wall seconds, less the frame allowance.

| | before | after |
|---|---|---|
| R2 `rung_cap` | 96 core-min | **96 core-min — UNCHANGED, and now REPORTED ONLY** |
| `CUMULATIVE_HARD_STOP_CORE_MIN` | 1275 | **1275 — UNCHANGED, and now REPORTED ONLY** |
| in-container `timeout -k 60 $DEADLINE` | SIGKILLs the solve | **DELETED. The container runs to its own completion.** |
| `D6RF10_CUMULATIVE_HARD_STOP … action=STOP_LADDER` + `break 2` | stops the ladder | **DELETED. Replaced by `D6RF10_CUMULATIVE_REPORT … action=REPORT_ONLY_NOT_A_STOP`, with no `break`, no `exit` and no verdict assignment.** |
| `$DEADLINE` | killed the run | **still computed, still printed in `D6RF10_RUNG_BEGIN`, binds nothing** |

🔴 **AND THE RAISE WAS NEVER NEEDED. THIS IS THE MEASUREMENT THAT SETTLES IT, AND IT WAS NOT KNOWN WHEN THE EARLIER DRAFT PROPOSED 300:**

| quantity | value |
|---|---|
| R2 registered cap | 96 core-min = **1440 wall s** at RANKS 4 |
| minus `FRAME_ALLOWANCE_S` 90 | **1350 s** ← the deadline that SIGKILLed it |
| R2 at the kill | wall 1357 s = **90.467 core-min** |
| R2's clean need (~1400 s) | **93.333 core-min** |

**93.333 < 96. The run fits inside its own registered cap and was killed anyway.** The 90-second frame allowance was *subtracted out of the solver's budget* instead of being reserved beside it — 6 core-min of a 96 core-min cap, and R2 needed 3.3 of them. **The defect was never the size of the cap; it was that a wall deadline derived from a core-minute cap killed a run that was still under that cap.** Raising 96 to 300 would have masked that defect behind a bigger number and left it in the file for the next rung to hit.

**Authority.** Sanaa's **2026-09-12 directive #17** (no run stopped by a time or budget cap, any team; strip the guards), her 2026-09-11 NO-CAP ruling (`6f3abf8a3`), and her 2026-09-10 16:50Z words for 3D cases — *"i dont want to see any budget gates ( time or money)"* — all **postdate** the 2026-09-09 freeze. Under CLAUDE.md rule 2 this lands as a **dated addendum**, not a rewrite, and it is recorded here rather than asserted in a commit message.

### 3. §2bb MANIFEST DISAGREEMENT — DISCLOSED, NOT EDITED

`LADDER_PREFLIGHT.json` pins R2 `deadline_s: 1350.0`. **That figure is NOT edited, and this paragraph is the disclosure.**

The nature of the disagreement is narrower than the earlier draft's, and better: the launcher's `rung_cap R2` still returns `96` and `DEADLINE` is still computed as `1350`, so **the manifest's number is still arithmetically correct**. What changed is that **`deadline_s` no longer has an enforcing limb anywhere in the launcher** — nothing consumes it as a kill. A reader auditing the manifest against the launcher will find the numbers agree and the *action* absent, and this addendum is the authority for that absence. R1 `600 s` and R3 `16900 s` are likewise unchanged and likewise no longer enforced.

### 4. RUNG-SCOPED RE-FIRE — THE GUARD WIDENING, STATED PLAINLY

The launcher could not re-fire one rung: `G-ROOT.1` pinned `BASE` to the single registered root, `G-ROOT.3` refuses a root that exists, and the loop was `for RUNG in R1 R2 R3`. An opt-in `D6RF10_RERUN_RUNG` now scopes `REGISTERED_BASE` to a fresh `…​.RERUN-<RUNG>-<UTC timestamp>` sibling and the loop to that one whitelisted rung. **Unset, the launcher is byte-identical in behaviour to the frozen fire.**

**What this widens, admitted rather than minimised:** `G-ROOT.1`'s *predicate* is untouched (`BASE` must still equal `REGISTERED_BASE`) but its *intent* moves from "exactly one root for this item, ever" to "**one fresh timestamped root per explicit rung-scoped re-fire, never the graded root**". The protective purpose — never re-run into graded evidence — is preserved intact. `G-ROOT.2`/`.2b`/`.3`/`.4` keep their predicates and their force; no `rm` is added and nothing is deleted; the md5 fixpoint, the age datum, the cap-identity assert and **both planted controls** survive unchanged. *(The earlier draft of this sentence also listed "the `timeout`" among the survivors. It does not survive — §2 deletes it — and the list is corrected here rather than left standing.)*

**THE GRADED ROOT `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF10-a2-wing-convergence-probe/` REMAINS THE AUTHORITY FOR R1 AND R3**, is not moved, renamed or written to, and every path cited by `D6RF10_GRADE_RECORD.md` stays valid. **The re-fire root carries R2 and only R2.** The rejected alternative was to raise the cap and re-fire the whole ladder from an archived root: it was refused because it re-spends 628 core-min re-running an R3 that already landed **and** strands the artifacts behind two committed verdicts by moving a root a committed record cites by path.

`d6rf10_autograde.sh` takes a matching `D6RF10_RUN_ROOT` env default (one line) so the **frozen** grading invocation — `--log <log> --rung R2`, no `--skip-freeze` — runs itself against the re-fire root. Its `GRADER_MD5` refusal limb (exit 2 on drift) is untouched.

### 5. REGISTERED PREDICTION — WRITTEN BEFORE THE SOLVER STARTS

**R2 will land `GATE FAIL`, at roughly 1.7x the `1.0e-05` accept floor on `p_first_uncorrected`. It will not PASS.**

The evidence this prediction is staked on, all already on disk:
- R2's last printed block (`Time = 200`) reads `p_first_uncorrected initRes = 1.781574265e-05` — **1.78x the floor, WORSE than R1's failing 1.681x**.
- R2's own control leg (`nNonOrth 3`, `endTime 1000`) plateaued at `1.681172924e-05`, **byte-identical** to the R1 control leg measured 2.5 h earlier.
- R3 (SIMPLEC, `relax_p 0.70`) is the arm that moved the binding field, to `6.3233727e-06`. R2's lever is `nNonOrth` alone.

**Falsifiable, and it costs something if it is wrong:** a measured R2 `p_first_uncorrected` below `1.0e-05` refutes this prediction outright, and a value below `1.681236312e-05` (R1's) refutes the narrower claim that deeper correctors do not move the floor on this case.

**Why the run is still bought.** Registered prediction **P2** — the load-bearing rung, outcome registered as GENUINELY UNCERTAIN — has been **UNMEASURED for three campaigns** (D6RF7 never tried it; D6RF9 confound (i); D6RF10 a short deadline). A measured negative on the deep-corrector lever **closes P2** and is a real result; a fourth campaign of silence is not. This addendum does not pre-judge the grade: the frozen grader, unchanged, declares it.

### 6. COST, PRE-REGISTERED BEFORE THE RUN (rule 12)

`RANKS = 4` is **not a free parameter** — the case is staged with a scotch/4 decomposition and `processor0..3`. Predicted from the 2026-09-10 measured legs scaled by a contention multiplier of **1.60x** (box load 39.92 at 2026-09-12T03:17Z vs 24.99 during the graded R3, `D6RF10_GRADE_RECORD.md` §9):

| quantity | predicted |
|---|---|
| candidate leg wall | 1400 x 1.60 = **2240 s** (pessimistic 3500 s) |
| control leg wall | 161 x 1.60 = **258 s** |
| **ledger-basis core-min** | (2240 + 258) x 4 / 60 = **166.5 core-min** |
| end-to-end wall | ~2520 s (~42 min), incl. ~50 MB staging + ~11 s setup container |
| **cost** | 2.775 core-h x $0.0513/core-h = **$0.142 — DERIVED, NOT MEASURED** (owner-stated rate; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5) |
| cap | **96 core-min, REPORTED, NOT ENFORCED.** No ceiling is authorised because no ceiling stops anything (directive #17). The 166.5 core-min prediction **exceeds the reported 96** at the ledger basis, and that is stated here in advance rather than discovered in the ledger: the excess is contention, the 1.60x multiplier is in the row above it, and **nothing kills the run when it crosses.** The crossing will print `D6RF10_CUMULATIVE_REPORT`. |

The rule-12 **estimate-versus-actual** comparison against these figures is owed at completion, as a row in `docs/COST_CALIBRATION.md`, with waste named separately and never absorbed into the ratio.

### 7. WHAT IS NOT AUTHORISED HERE

The grader, the `1.0e-05` accept floor and its `primalMinResTol x primalMinResTolDiff` provenance, the AMENDMENT A2 plateau criterion, the per-field leg rule, every band and every label. All frozen, all unchanged. R1 stays `GATE FAIL`; R3 stays binding-field `PASS` / rung `GATE FAIL`; `N-D43` stays escalated and unruled; no acceptance rule is widened under any outcome (T25). The two-row DAFoam bright line is unmoved: this is a primal-convergence measurement, **not** a DAFoam verdict.

### 8. 🔴 RESTART AND CHECKPOINTS (Sanaa items 1–3) — AND A DEFECT FOUND WHILE ANSWERING IT

**Asked directly: does R2 have any restartable write to resume from? NO, AND IT COULD NOT HAVE HAD ONE.** Measured on disk, not inferred:

- The staged `system/controlDict` carries **`writeControl timeStep`** with **`writeInterval 1000`**, against R2's **`endTime 300`**. 300 is not a multiple of 1000.
- **No numbered time directory exists anywhere under the R2 work root.** The only `1000` directories present belong to the *control* leg (`CTRL_ENDTIME 1000`), which completed `rc=0`.

**So the re-fire starts FROM SCRATCH, and no resume is invented.** That is the honest answer to her item 1.

**The defect this exposes is larger than the killed run and is recorded, not quietly patched:** with `writeInterval 1000` and `endTime 300`, **a fully successful R2 would also have written nothing.** The rung as frozen could not produce a field at its own `endTime`. It was gradeable only because the frozen grader reads the *log*, not the fields.

**The repair, registered here before the run:** `install_config` now also sets `writeInterval` and `purgeWrite 2`, each **read back from the file after writing** — the same discipline every other swap in that function already used. A new marker `D6RF10_CHECKPOINT_INSTALLED` carries them. **The grader-bound `D6RF10_CONFIG_INSTALLED` line is byte-untouched**, deliberately, so no frozen parser meets a new field.

| rung | endTime | `writeInterval` | divides exactly? | interval in wall time |
|---|---|---|---|---|
| R1 | 2500 | **125** | 20 writes, one AT endTime | rate UNMEASURED → her fallback "every 200 iterations", taken tighter |
| **R2** | **300** | **100** | **3 writes, one AT endTime** | **MEASURED: 1357 s / ~299 steps = 4.54 s/step → 100 steps ≈ 454 s = 7.6 min** |
| R3 | 2000 | **200** | 10 writes, one AT endTime | rate UNMEASURED → her fallback exactly |
| control | 1000 | **100** | 10 writes, one AT endTime | leg measured 161 s → ≈16 s |

**Every value divides its rung's `endTime` exactly, so a write now also lands AT `endTime`** — which the frozen configuration did not do. **`purgeWrite 2` keeps the last two and purges older**, her item 1 verbatim. R2's 7.6-minute cadence is far inside her 30-minute bound; **R2's entire clean run (~23 min) is shorter than one 30-minute interval**, so the bound could not have been violated in any case, and the cadence is chosen to give a real resume point rather than to satisfy a bound that was never at risk.

**Not done, and named:** her item 5 kill-and-resume proof is **one test per solver class before the fleet launches anything**. It is not this rung's to perform and **this addendum does not claim it**. If no such proof exists for the DAFoam-primal class when the runner reaches this entry, the resume path here is *configured but unproven*, and that is the honest state.

### 9. AS UBUNTU, NEVER ROOT (Sanaa launch item 6)

`run_container` ran `--user 0:0`. It now runs **`-u 1000:1000 --group-add 1002 -e MPLCONFIGDIR=/tmp`**, and `sudo -n docker` becomes plain `docker` (verified on this box: `ubuntu` is in group `docker`).

uid 1000 and gid 1000 are both `ubuntu`, so artifacts land `ubuntu:ubuntu`; **gid 1002 is the *image's* `dafoamuser` group, carried as a supplementary group for one purpose only** — traversing the `0750` `/home/dafoamuser` to source `loadDAFoam.sh`. **Measured on this box 2026-09-12 by a peer lane: `-u 1000:1000` alone dies `Permission denied` sourcing `loadDAFoam.sh`; with `--group-add 1002` it reaches `LOADED_OK`.** Corroborated by a live peer container on the same image (`User=1000:1000`, `GroupAdd=["1002"]`). **This spelling is taken from the peer lane's measurement, not invented here.**

`mpirun --allow-run-as-root` is left in the emitted cmd files: as a non-root user it is inert, and removing it would change a line the frozen driver path emits for no gain.

### 10. QUEUE POSITION AND DECLARED RESOURCES (directive item 19)

**The runner is the only launcher. Nothing in this addendum launches anything**, and no agent's message is Sanaa's consent. The entry is placed **behind `D6R2` and `MP_A5R`**; the runner's core gate sequences it.

| declared | value | basis |
|---|---|---|
| `ranks` | **4** | **NOT a free parameter.** `RANKS=4` is fixed in the launcher, the case is staged with a `scotch`/4 decomposition and `processor0..3`, and §3 registers it. |
| `memory_footprint_gb` | **20** | the launcher's own `MEM=20g` cgroup limit, the figure the container is actually given |
| `solver_class` | DAFoam primal (`DARhoSimpleFoam`), containerised | |
| re-fire scope | `D6RF10_RERUN_RUNG=R2` → a fresh `…​.RERUN-R2-<UTC>` sibling root | the graded root remains the authority for R1 and R3 and is never written to |

Nothing here is sent, filed, uploaded, registered or posted. **SUBMISSIONS PARKED.**

### 11. 🔴 CORRECTION, same day — **§10 SAYS "THE ENTRY IS PLACED". IT WAS NOT. IT WAS REFUSED.**

**§10 above was written before the entry met the runner, and it asserts an accomplished
fact that did not happen.** It is corrected here rather than left standing, because a
record that asserts something untrue is worse than one that says less.

**What actually happened:** the entry was written, `scripts/queue_entry_check.py` returned
`ACCEPTED`, and **`scripts/queue_runner.py` REFUSED it at GATE A** and moved it to
`verification/queue/dafoam/refused/D6RF10-R2-REFIRE.json`. Two causes, one mine:

1. **A lane error:** the entry declared `solver_class: dafoam-primal-containerised`, which
   is not one of the four the runner registers. The correct value is **`openfoam-steady`**.
2. **A structural blocker that survives fixing (1):** gate A's controlDict limb reads
   `<cwd>/system/controlDict` **before launch**, and this launcher has **no case directory
   at rest** — it creates its root at launch, stages into it, and installs the controlDict
   **inside the container**. The re-fire root does not exist yet (and `G-ROOT.3` refuses one
   that does); the repo has no `system/`; and the staging source is **D6RF7's graded root**,
   which measures `writeInterval 1000` / `purgeWrite 0` (refusing both limbs) and which
   `G-ROOT.2` forbids writing to.

**Full analysis, including the option that was refused on principle:**
`D6RF10_R2_QUEUE_BLOCKER.md`, beside this file.

**SUPERVISOR RULING, 2026-09-12 [lab-attributed]: OPTION (2). `G-ROOT.3`/`.4` ARE NOT
RESTRUCTURED AND R2 WAITS.** The stated reason is recorded because it outranks this rung:
`G-ROOT.3` exists to stop a launcher staging over graded evidence, and **that failure was
found live the same night in D8G's launcher, which was silently `rm -rf`-ing a completed
arm as root at every launch behind a `2>/dev/null`.** A fourth campaign unmeasured is a
cost; **a graded root staged over is unrecoverable.** The fix is gate A gaining a registered
limb for stage-then-install launchers — pinning the md5 of the `install_config` that does
the work, giving the gate **proof of what WILL be installed rather than a reading of what
IS installed** — and it is **escalated to verification as a shared cross-team gate
question**, since every stage-then-install launcher in `cases/dafoam/` meets the same wall.

**Recorded because it was refused deliberately and the refusal is the point:** pointing
`cwd` at a case-shaped directory the run does not use would have passed gate A by having it
read a controlDict **with no causal connection to the solve** — a green light with the
30-minute loss bound never verified. **That option was available, was not taken, and is
recorded as not taken.**

**STATE: R2 is `BLOCKED` pending verification's ruling on gate A. Nothing launches.** The
cap removal, the non-root spelling and the checkpoint repair in §§2, 8 and 9 above are
committed and stand on their own; they are not contingent on the queue entry.
