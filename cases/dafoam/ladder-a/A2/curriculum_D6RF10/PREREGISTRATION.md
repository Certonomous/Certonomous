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
