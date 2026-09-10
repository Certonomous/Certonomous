# RC4 PRE-FLIGHT — APPARATUS DEMONSTRATION: WHICH CHANNEL IS MEASURING CONTINUITY ON THE CBFS MESH

**Item:** `RC4-PREFLIGHT` — an **apparatus demonstration**. It is **not** RC4, it
is **not** a rung, and **it asserts no RC4 gate verdict**.
**Team:** closure. **Drafted:** 2026-09-10 by a closure lane on the
closure-supervisor's dispatch.
**Status:** **DRAFT / UNFROZEN.** `prereg_commit:` = `PREFLIGHT_FREEZE_PENDING`.
**Instrument:** `preflight_two_channel.py`, beside this file, frozen with it.
**Compute:** **ZERO SOLVER COMPUTE.** No solver is launched by §1–§6 of this
document. §7 registers a single deferred solve which is **not authorised by this
document** and does not run without the supervisor's separate word.

---

## 1. WHAT THIS IS, AND WHAT IT IS NOT

**It is:** a two-channel reading of continuity on **preserved** predecessor rows
that already sit on disk, taken with **RC4's own reader** and with **the solver's
own continuity channel** beside it, plus a **floor reading** for that reader on
the CBFS mesh.

**It is NOT compute against RC4's gates**, and every limb of that is executable
rather than asserted:

| claim | how it is enforced |
|---|---|
| launches no solver | the instrument contains no solver invocation; `--selftest` `ast`-parses itself and requires **zero** calls to `run_solve`, `run_campaign` or `build` |
| closes no RC4 gate | the same `ast` sweep requires **zero** calls to `score_all`, `verdict`, `gate_arithmetic`, `cut` or `ceiling_for`; the sweep is shown finding a **planted** violation, so it is not blind |
| writes nothing under RC4's run root | its scratch root is `/home/ubuntu/closure-data/preflight_cbfs_continuity`, which **shares no prefix** with `/home/ubuntu/closure-data/rc4` — checked in code, so no glob written against one can reach the other |
| RC4 has had zero compute | `/home/ubuntu/closure-data/rc4` is checked **ABSENT before and after every measuring pass**, and the prober is required in the same call to see `/home/ubuntu/closure-data/r4`, which **does** exist. A "not found" from a prober never shown able to find anything is not evidence |
| cannot ride RC4's freeze | this document carries its **own** DRAFT token — the one on the Status line above, which is neither a substring nor a superstring of RC4's. Clearing one cannot clear the other; checked in `--selftest`. **The token string is written in this file exactly ONCE, on the Status line**, so the supervisor's single substitution at the freeze clears the instrument in one edit and no prose about the token can be mistaken for the status field |

**It moves no bar.** RC4's binding 1e-3 continuity bar, its 1e-4 second reading,
its screen at `rc4_score.py:429-437`, its case set and its denominator are
**untouched**. The instrument **reads** both bars out of `rc4_score` rather than
retyping them, so it cannot drift from the thresholds it compares against and
cannot be read as declaring bars of its own.

---

## 2. WHY THE PRE-FLIGHT AS FIRST BRIEFED CANNOT BE MADE GATE-SAFE — recorded because it is the finding

The dispatch asked for a cheap solve of **`CBFS13700` in configuration `N`** under
RC4's own build path, in a separate root, to see whether RC4's own row lands
inside the binding bar. **This lane's finding is that no such solve can be
gate-safe**, and the reason is not the directory:

1. **`CBFS13700` is a registered case tag and `N` is a registered configuration**
   (`build_rc4_cases.py:86-94`), and the `N` row's `u_rms` is the **denominator of
   the headline gate P0** — `gate_arithmetic` takes `u0 = null["u_rms"]` and every
   `cut()` divides by it. Solving it is compute **of the thing the gates score**,
   not of a control.
2. **`VERIFICATION_CHARTER.md` §2d.2 (v1.32) has ruled on exactly this boundary:**
   *"RULING: `CLAUDE.md` RULE 2 GOVERNS. Gates close at the FIRST COMPUTE under the
   registration — feasibility compute included"*, and *"§2m is about the absence of
   a gate, not the character of the run."* RC4 has gates.
3. **The `r5d_fo_demo` precedent does not reach it, and its own status is an OPEN
   ESCALATION.** `docs/LAB_STATE.md:1545` records the closure-supervisor declining
   to take that ruling — *"that is precisely the argument an interested party would
   find persuasive … So it is not mine to take. ESCALATED to the chief for
   verification's ruling"* — and proceeding on the conservative branch meanwhile.
   Its distinguishing fact was that the demo computed **the driver's controls**;
   this would compute **a graded row**. That is R4b-I's shape, not R5D's.
4. **RC4's own instrument agrees.** `rc4_run.solver_command`'s registered docstring
   says its injectable `program` exists so a real process can be driven *"without
   launching a solve against an unfrozen registration."*

**So the solve is not bought.** What replaces it is §3, which answers the same
question at zero solver compute — and, on the evidence that prompted the
supervisor's second correction, answers a **better** one.

---

## 3. WHAT IS MEASURED, ON WHICH ROWS, BY WHICH CODE PATH

Four **preserved** rows, every artifact **named** — no glob, no `log.*`, no
discovery (a multi-file `grep … | tail -1` is a coin flip):

| row | case directory | named log artifact | role |
|---|---|---|---|
| `CBFS13700__NULL` | `/home/ubuntu/closure-data/aposteriori/kaandorp/CBFS13700__NULL` | `log.run` | **the floor reading** — uncorrected baseline, correction fields identically zero |
| `CBFS13700__TRUTHR` | `…/CBFS13700__TRUTHR` | `log.run` | the row whose reader continuity **0.3219275282624856** is hardcoded at `rc4_score.py:683` |
| `AR_1_Ret_360__NULL` | `…/AR_1_Ret_360__NULL` | `log.run` | **cross-geometry control** — the duct, where the two channels are expected to AGREE in order of magnitude |
| `AR_1_Ret_360__TRUTHR` | `…/AR_1_Ret_360__TRUTHR` | `log.run` | cross-geometry control, repaired row |

**CHANNEL R — the reader RC4's screen actually consults.**
`rc4_score.score_row(tag, case, bench)`, called **UNMODIFIED**, and the number
reported is the dict key `divU_rms_over_gradscale` set at `rc4_score.py:303`,
together with `continuity_ok` — **the very key `rc4_score.py:430` reads.** L-512
is satisfied in the strict direction: the committed tool's **input** is scoped (a
read-only scratch assembly of the preserved row's own bytes, `copy2`, real mtimes
preserved); its **transform is not reimplemented anywhere in this item.** This is
why the number is the same quantity the screen reads: it *is* the screen's number,
produced by the screen's own function.

**CHANNEL P — the producer's own continuity channel, the INDEPENDENT WITNESS.**
OpenFOAM's `time step continuity errors : sum local = …`, which is
`fvc::div(phi)` from `continuityErrs.H`, parsed from the one named log per row.
The **final** line is taken, with its line count and its first value reported
beside it. Channel P is the solver's own arithmetic on its own flux field;
channel R is a structured-gradient reconstruction from cell centres, documented
in `_common/sst_baseline_metrics.py:114-116` as validated to **0.5–1.0 % interior
rel-L2**.

**Neither channel replaces the other.** Channel R is what RC4 grades on. Channel
P is what the solver believes. The measurement is the **comparison**, per row,
with the ratio R/P printed.

---

## 4. THE REGISTERED OUTCOME — THREE WAYS PLUS A REFUSAL, FIXED IN ADVANCE

Fixed here, before the instrument is run, so no reading of the answer can be
chosen to suit anybody. The classes are a closed set of four, checked in code
(`CLASSES`), and **none of them is an RC4 verdict.** The deciding row is
`CBFS13700__NULL`; `R` is its channel-R value, `P` its channel-P `sum local`.
`SOLVER_TOLERANCE` is registered here as **1e-9**.

| # | condition | registered class | **what it means for RC4's freeze** |
|---|---|---|---|
| i | `R < 1e-3` | `R-INSIDE-BAR` | **The finding-C prior is REFUTED on RC4's own reader.** The CBFS exposure is not what it was thought to be. **RC4 is freezable and launchable as it stands**, and the 140 core-minutes are justified. |
| ii | `R ≥ 1e-3` **and** `P ≥ 1e-9` | `PHYSICS-NONCONVERGENCE` | **The screen is doing its job.** The continuity error is the solver's, the prior stands on physics, and RC4 as registered would honestly read `NOT A RESULT` on `CBFS13700` — which, through the global screen, is `NOT A RESULT` for the whole item. **Spending 140 core-minutes to buy that is waste under `COMPUTE_BUDGET_CHARTER.md` §6.** The choice — disclose and launch, or re-scope the item — is **the supervisor's**, and this document takes it for nobody. |
| iii | `R ≥ 1e-3` **and** `P < 1e-9` **and** the duct control shows the two channels agreeing in order of magnitude | `READER-FLOOR-DOMINATED` | **An INSTRUMENT finding about the reader, not a physics finding about the case.** `R` on an uncorrected row where the true signal is at solver tolerance **is that reader's noise floor on that mesh**, so a registered bar of 1e-3 (0.1 %) — and *a fortiori* 1e-4 — sits **below its own instrument's demonstrated resolution** on this geometry. A screen like that is not strict; it is blind, and it would take RC4 to `NOT A RESULT` on a reader artifact. **THIS DOCUMENT DOES NOT MOVE THE BAR AND DOES NOT AUTHORISE MOVING IT.** It files the referral at §9. |
| iv | any control fails, any named artifact is absent, or the class is outside the closed set | **`NOT A RESULT`** | The pre-flight failed. **No inference is drawn in either direction**, the spend decision stays un-informed, and nothing about RC4 is concluded. |

**The duct rows are a control on the comparison itself, not decoration.** If the
CBFS gap were a parsing error or a units error in channel P, the duct would show
the same gap. It is registered here that **class iii requires the duct control to
show agreement**; without it, the reading is `NOT A RESULT` under iv.

---

## 5. CONTROLS — standing rule 3, every one a refusal, every one shown firing

1. **Channel R, direction A (plant).** A known divergence — each cell's velocity
   scaled by `1 + 1.234e-02 · i/n` — is written into a scratch copy of `U` with
   `rc4_score.swap_internal_vector` **unmodified**, and the reader is re-run.
   **REFUSES unless the metric moves by more than 1e-9.** A value from a reader
   not shown able to return a different one is not evidence.
2. **Channel R, direction B (determinism).** The same row read twice must agree
   **exactly**, or the move under the plant proves nothing.
3. **Channel P, presence.** A named log carrying no continuity line **REFUSES** —
   a missing channel is not a zero. A named log that is absent **REFUSES**.
4. **Channel P, not blind.** The line counter is shown returning **0** on a
   synthetic log with no such line and **non-zero** on a real one, and channel P
   is shown returning **different** values and **different** line counts on two
   different named logs — so it is not returning a constant.
5. **RC4's run root.** Checked **ABSENT** before and after every measuring pass,
   with the prober required to see `/home/ubuntu/closure-data/r4` in the same
   call.
6. **No gate, no launch.** `ast` parse of the instrument by itself: zero calls to
   RC4's grading or launching entry points, and **the sweep is shown finding a
   planted violation**.
7. **`ast.Assert` count 0**, so no guard here evaporates under `python3 -O`
   (§6.1's discipline, L-332).

---

## 6. COST — standing rule 12

**Unit: core-minutes = wall seconds × ranks ÷ 60. RANKS = 1**, and it is stated
rather than inherited: the instrument runs one Python process, invokes no
`mpirun`, no `decomposePar` and no `-parallel`, and launches no solver.

| block | derivation | wall s |
|---|---|---|
| `SB.load_case` ×4 (benchmark field reads) | measured field reads of this size on this box run seconds, budgeted generously | 40 |
| channel R ×4 rows, ×3 reads each (clean, clean-again, planted) | `structured_gradient` on ~13k–20k cells; 12 reader passes | 60 |
| channel P ×4 named logs (one is 28 MB) | regex over ≤ 28 MB | 10 |
| `--selftest` ×2 (`python3`, `python3 -O`) | | 10 |
| | **total** | **120 s** |

**REGISTERED ESTIMATE: 2.0 core-minutes** (120 wall s × 1 rank ÷ 60).
**REGISTERED CAP: 10.0 core-minutes.** Derived: 10 ÷ 60 = 0.167 core-h ×
**$0.0513/core-h** = **$0.0086 — DERIVED at the owner-stated rate, NOT
MEASURED.** This box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 pre-authorisation. **An overrun
STOPS the pre-flight; it does not get a new budget.** The 5× cap ratio covers the
28 MB log and the four benchmark loads, neither of which this lane has timed.

**Rule-12 calibration.** At completion the estimate is compared with the actual
core-minutes, the ratio stated, the gap attributed, and a row lands in
`docs/COST_CALIBRATION.md` under that file's append rules and the rule-10
private-index protocol.

---

## 7. THE DEFERRED ARM — the one link that still needs a real process, and it is NOT authorised here

`RC4_kaandorp_propagation_repair/PREREGISTRATION.md` A2.6 item 1 records one open
inference: **`rc4_run.py` has never driven `simpleFoam`**, so it is inferred
rather than measured that `simpleFoam` under **this** wrapper writes the
`log.solve` and `rc` channels that `r4_lib.solve_complete` opens.

**A gate-safe closure exists and is prepared, not run.** It is the same class of
act as the real-process arms A2 already ran and the supervisor already accepted at
check-1: `run_solve(case, tag=None, cfg=None, root=<tempdir>, check_freeze=False)`
driving the **real `simpleFoam` binary** on
`$FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily` — **not** a registered case
tag, **not** a registered configuration, in a `mkdtemp` root, on a mesh RC4's
gates cannot score under any reading. `verify_record` then reads both channels
back from disk and `rc4_score.completion` grades clauses 1–6 on them.

**Registered figures for that arm, if the supervisor authorises it:** ranks
**1**; estimate **≤ 1.0 core-minute** (pitzDaily is 12,225 cells and converges in
a few hundred iterations); **cap 5.0 core-minutes**, enforced by the runner's own
`timeout` through `budget_or_refuse`. **Both ways, in advance:** if the two
channels appear and clauses 1–6 pass, A2.6 item 1 is **CLOSED by measurement** and
the runner is complete. **If they do not appear, that is a FINDING and it is worth
more than a passing pre-flight** — it would mean §8's clauses 1–3 are unsatisfiable
by the producer RC4 registered, which is finding B's exact shape a second time, and
RC4 must not be frozen until it is repaired.

**This document does not authorise that solve.** It registers it so that when the
word is given, the outcome is already fixed both ways.

---

## 8. WHAT THIS LANE COULD NOT ESTABLISH, STATED PLAINLY

1. **This pre-flight does not measure RC4's own solve of `CBFS13700`/`N`, and no
   substitute is claimed to be one.** What it measures is a **converged**
   uncorrected baseline solve of the same case, on the same mesh, with the same
   solver, under the **same registered model** — `kOmegaSSTCorrected`, read from
   `CBFS13700__NULL/constant/turbulenceProperties`, identical to
   `build_rc4_cases.MODEL`. The bounding argument, and it is an argument rather
   than a measurement: that row's `residualControl` is **p 1e-6, U 1e-6**, where
   RC4 registers **p, U, k, omega all at 1e-6** — strictly stricter — and it
   required **30,884 iterations** to converge, where RC4's `ITER_CAP` is
   **30,000** — strictly fewer. RC4's own row therefore has no route to a
   *better-converged* state than this one on iteration count or tolerance. It
   could still differ, because RC4 builds fresh from the benchmark `t0` while
   this row resumed from 30,000 with `purgeWrite 0`. **That residual is not
   closed by this pre-flight and is not pretended to be.**
2. **The 0.5–1.0 % resolution figure is the reconstruction's own documentation**
   (`sst_baseline_metrics.py:114-116`), read by this lane at source. It is a
   documented figure, not a figure this pre-flight measures.
3. **No RC4 verdict is asserted, and none of §4's classes is one.** The pre-flight
   cannot produce `PASS`, `GATE REACHED` or `GATE FAIL` about RC4, and its own
   refusal label is the shared `NOT A RESULT`.
4. **Zero solver compute produced this document.**

---

## 9. THE REFERRAL — filed, not decided

**If §4 returns class iii, a registered threshold in RC4 sits below its own
instrument's demonstrated resolution on one of its three cases.** What follows
from that is **not this lane's to decide and not this document's to enact**:

- moving, narrowing or re-scoping RC4's continuity bar is a **gate change**, and
  `CLAUDE.md` rule 2 forbids it after first compute and the supervisor has already
  refused it once before compute;
- **retiring or replacing a gate threshold is reserved to Sanaa**
  (`CLAUDE.md` FIRST-ACTION, *Reserved to Sanaa*);
- **SUBMISSIONS ARE PARKED** (rule 7). Nothing here is sent, filed, uploaded,
  registered, posted or commented anywhere outside this box.

The referral is therefore: **the closure-supervisor rules on RC4's freeze, and on
the branch that changes a threshold, it goes to Sanaa's desk.** This lane records
the measurement and the classes, and takes neither decision.

---

*Drafted 2026-09-10 by a closure lane. **THIS IS NOT THE FREEZE.** The document is
DRAFT / UNFROZEN, its instrument refuses every measuring entry point while the
token stands, and nothing may be measured against it. No frozen file was edited.
No RC4 gate, bar, screen, case set or denominator was altered. Nothing sent.*
