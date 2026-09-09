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
