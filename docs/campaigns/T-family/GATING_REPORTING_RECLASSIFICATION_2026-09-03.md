# Gating / reporting reclassification — heat-transfer territory (2026-09-03)

**ONE-PASS AUDIT, NOT A NEW CYCLE.** Ordered by Sanaa 2026-09-03 ~20:00Z
(`etc/sessions/2026-09-03T2000Z_sanaa_governance_reform.md`). Her rule, verbatim:

> Every standard, lesson, and grader check is classified as gating or reporting.
> Gating requires a stated reason of the form "without this, the verdict on result X
> cannot be trusted." Anything without that reason is reporting. Reporting checks run,
> log, and attach to the certificate; they never block a solve from starting, a mesh
> from being used, or a hand-off from happening. Existing rules are re-classified once,
> by their owning team, with the reason recorded. Anything that can't produce the reason
> drops to reporting. This is a one-pass audit, not a new cycle.

**ZERO COMPUTE. 0 core-min. $0.00.** **No grader was edited by this pass.** This is a
classification, not a repair: every path below was read read-only. Where a check is
mis-implemented that fact is recorded and referred, never fixed here
(`SUPERVISION_CHARTER` §3 — a measurement-script change requires the supervisor's
personal diff read).

**Population.** Checks implemented in `verification/runs/T-family/` and
`verification/runs/F14-cooling-ladder/` graders, `mark_done_*` and `build_*` scripts,
and the gates registered in `docs/campaigns/T-family/` and
`docs/campaigns/F14-cooling-ladder/`. Classified by **check family**, not by file: a
family is one predicate recurring across rungs, and one representative `path:line` is
cited for each with siblings named. Per-rung gate rows in pre-registrations are
instances of these families and are classified by their family.

**Not in scope, and deliberately not reached into:** `scripts/check_comparator_freeze.py`
itself (verification's instrument, verification's programme — her clause 7: *"coverage
ratios forward-only, unreported"*); the mesh-quality standard `docs/standards/MESH_STANDARD.md`
(cfd's); `docs/LESSONS.md` (concurrent lane). `T3_runs/` and the T5c/T25R6b registrations
carry live lanes and were read only where already-committed line citations were needed.

**Counts: 8 GATING, 13 REPORTING.**

---

## 1. GATING

Each row states the reason in Sanaa's exact form. Rows 1–3 are the three standing
instruments this team originated and is custodian of; the supervisor's ruling of
2026-09-03 fixes them as gating and the wording below was checked against the
instruments before it was written.

| # | check | where it lives (`path:line`) | class | reason — "without this, the verdict on result X cannot be trusted, because …" |
|---|---|---|---|---|
| **G1** | **The planted-zero control** (`CLAUDE.md` rule 3). Plants a known perturbation, reads it back from disk, and **refuses** (exit 2) if the reader cannot see it. | `verification/runs/T-family/T25R_MODULE_runs/analyse_t25R.py:595` (all nine clauses; refusals `:652`, `:654`, `:884`); `T25R6a_C5_OUTER_runs/grade_t25R6a.py:348`; `T10a_runs/analyse_t10a.py:846`; `T8_runs/analyse_t8.py:197`; `T18_runs/analyse_t18.py:213`; `T19b_runs/analyse_t19b.py:328`; `T13_runs/analyse_t13.py:378`; `T14_runs/analyse_t14.py:185`; `E4_runs/analyse_e4a.py:63` | **GATING** | **Without this, the verdict on any quantity read from disk cannot be trusted, because a zero from a reader not shown able to see a non-zero is not evidence of a zero — it is equally evidence of a blind reader.** Proven this day: `VERIFICATION_CHARTER` §2d.11.1 (v1.45, `ad9eda53`) rules that the T3 control's predicate could return `True` on a 2.47 K change while the planted cell was **never the argmax**, clearing a 1.234e-03 K plant by ~2000× **without seeing it**. A control that passed while blind certified nothing. |
| **G2** | **The strict completion rule with its age guard** (`CLAUDE.md` rule 4). All conjuncts: `rc=0` from inside the detached wrapper, an `End` line, last time == `endTime`, fields present at `endTime`, `ExecutionTime` count, and **every field at `endTime` newer than the case's own `0/T`**. | `verification/runs/T-family/T14_runs/mark_done_t14.py:110` and `:194` (age guard); `T8_runs/analyse_t8.py:484-490`; `T13_runs/mark_done_t13.py:136`,`:212`; `T15_runs/mark_done_t15.py:137`,`:238`; `T25R6a_C5_OUTER_runs/grade_t25R6a.py:290`; launch guard `T25R6a_C5_OUTER_runs/stage_t25R6a.py:122` | **GATING** | **Without this, the verdict on any rung cannot be trusted, because a field written by an earlier run, or a solve that stopped before `endTime`, produces numbers that are not the numbers the registered case was supposed to produce.** |
| **G3** | **Roache triple gating** (`CLAUDE.md` rule 5). Non-`CONVERGING` triple → `NOT A RESULT` whatever the value; GCI at Fs = 1.25 and never quoted over a non-monotone triple. | `verification/runs/T-family/T8_runs/analyse_t8.py:1009-1089` (`gci_triple` `:800`, `FS` `:146`); `T13_runs/analyse_t13.py:398-408`; `T4_runs/analyse_t4.py:356-359`; `T1_runs/analyse_t1b_L4.py`; guard note `docs/campaigns/F14-cooling-ladder/K0b_GCI_DIVERGENT_TRIPLE_GUARD_2026-08-25.md` | **GATING** | **Without this, the verdict on any grid-convergence claim cannot be trusted, because an observed order computed from a non-monotone or non-converged triple is noise, and a GCI quoted over it is a false uncertainty.** |
| **G4** | **Rule 5 step (a) — iterative convergence, `C_CONV`.** Initial residuals of the **gated** channels ≤ the registered floor at every iteration of the final 10 % of `endTime`. | `verification/runs/T-family/T13_runs/analyse_t13.py:462` (registered `build_t13.py:334`, floor 1.0e-06); registered at `docs/campaigns/T-family/T13_PREREGISTRATION.md:120` and `T16_PREREGISTRATION.md:266` | **GATING, and gating *only* because it feeds G3.** | **Without this, the verdict on any grid-convergence claim cannot be trusted, because rule 5 step (1) makes a level that is not iteratively converged `NOT A RESULT` before any triple is consulted, so an unenforced convergence floor lets a non-converged level enter the triple that produces the observed order.** *Scope is exactly the channels the triple is built from; see R8 for the residual thresholds that are merely reported alongside — they are not this check and do not inherit its class.* |
| **G5** | **Rule 5 step (a) — plateau / stationarity.** Every level must have plateaued across the registered window; not plateaued → `NOT A RESULT`. | `verification/runs/T-family/T8_runs/analyse_t8.py:1012` (`grade_row` `:1009`); `T4_runs/analyse_t4.py:356-359`; `T13_runs/analyse_t13.py:397`; `T1_runs/analyse_t1b_cmf_gated.py:17`; `T23G_runs/analyse_t23g.py:617` | **GATING, and gating *only* because it feeds G3.** | **Without this, the verdict on any grid-convergence claim cannot be trusted, because a level still drifting has no settled value to place in the triple, and an observed order computed across drifting levels measures the drift rather than the discretisation error.** |
| **G6** | **`DONE.<case>` existence as the precondition to grading.** No `DONE` → the comparator refuses; the whole rung is graded or none of it is. | `verification/runs/T-family/T13_runs/analyse_t13.py:425`; `T14_runs/analyse_t14.py:239`; `T15_runs/analyse_t15.py:549`; `T18_runs/analyse_t18.py:268`; `T19b_runs/analyse_t19b.py:454` | **GATING, as the carrier of G2.** | **Without this, the verdict on any rung cannot be trusted, because `DONE.<case>` is the completion rule's certificate, and a comparator that grades without it grades a run never shown to satisfy rule 4 at all.** Class fixed by this team's own L-342 audit, which puts `DONE.<case>` **existence** in PHYSICS-CRITICAL (`docs/campaigns/T-family/L342_FIELD_CLASS_AUDIT_2026-08-26.md`, classification table). *The `DONE` marker's **mtime/timestamp** is INFRASTRUCTURE and is reporting — see R7.* |
| **G7** | **The y+ SUBLAYER BOUND on the point maximum** — `max(y+) ≤ YPLUS_MAX = 5.0` on every registered wall, and y+ **not measured at all** → `NOT A RESULT`. | `verification/runs/T-family/T5b_runs/analyse_t5b.py:382-387` (bound) and `:371-377` (unmeasured); field class `analyse_t5b.py:68`, `:855` — `yPlus.dat` is a **GATE INPUT and never infrastructure** | **GATING — PROPOSED to the supervisor for ruling, not in his listed tier.** | **Without this, the verdict on any wall-resolved heat-transfer rung cannot be trusted, because a near-wall cell outside the viscous sublayer makes the resolved-wall assumption under the Nusselt reading false, and an unmeasured precondition is not a satisfied one.** **This is the limb the verification ruling deliberately KEPT on the point maximum**: `VERIFICATION_CHARTER` §2d.11.2 — *"A point maximum is the CORRECT statistic for 'was the sublayer ever violated' and the WRONG one for 'how does resolution scale.'"* See R1: the **other** limb drops. |
| **G8** | **Registered mesh identity** — `checkMesh` cell count must equal the count registered for that level; a mismatch refuses at build. | `verification/runs/T-family/T13_runs/build_t13.py:275`; `T16_runs/build_t16.py:333` | **GATING — PROPOSED to the supervisor for ruling, not in his listed tier.** | **Without this, the verdict on any rung cannot be trusted, because a solve on a mesh that is not the registered mesh produces a number for a different case than the one the pre-registered gate was frozen against, and the refinement ratio `r` that G3 divides by is then not the ratio the triple assumes.** *Distinct from mesh QUALITY, which drops — see R2.* |

---

## 2. REPORTING

These run, log, and attach to the certificate. **They never block a solve from starting,
a mesh from being used, or a hand-off from happening.**

| # | check | where it lives (`path:line`) | class | why it cannot produce the reason |
|---|---|---|---|---|
| **R1** | **The y+ LADDER-CONSISTENCY clause** — `max(y+) ≤ TOL × the level target`, used to assert that resolution scales as the ladder designed. | `verification/runs/T-family/T5b_runs/analyse_t5b.py:388-396` (the `drift` test) | **REPORTING** | **Ruled this day.** `VERIFICATION_CHARTER` §2d.11.2 (v1.45, `ad9eda53`, Item B GRANTED): the point maximum's observed order is **0.52–0.54** against the ladder's design 0.99–1.04, and on `roof` the maximum is **NON-MONOTONE under refinement (p = −0.074)** — the MAX margin *climbs* 0.7316 → 0.9253 → 1.1550 while the area average is flat. *"A ladder-consistency clause is a claim about how resolution scales under refinement, and a statistic that increases under refinement cannot estimate it."* A check that cannot support the inference it is used for cannot produce the reason. The maximum is still **reported beside the average either way**. |
| **R2** | **Mesh quality — `checkMesh` "Mesh OK", non-orthogonality, skewness.** | `verification/runs/T-family/T14_runs/build_t14.py:148`; `T18_runs/build_t18.py:150`; `T19b_runs/build_t19b.py:291`; `T25R_MODULE_runs/analyse_t25R.py:792`,`:802` | **REPORTING** | Sanaa's clause 7 directly: *"skewness quarantine reclassified to reporting"*, and *"reported, not gated" adopted as the standard's default mode*. A quality metric outside a band does not by itself make a verdict untrustworthy; it makes it **caveated**. A mesh defect that actually prevents a trustworthy result (wrong patch identity, a boundary condition set wrong) is a **BLOCKING PHYSICS FIX** under her clause 7 taxonomy — it jumps every queue and needs no gate to authorise it. The owning standard is cfd's `docs/standards/MESH_STANDARD.md`, not ours. |
| **R3** | **Pre-run compute-cap refusal** — total ladder CAP must not exceed the registered ceiling; refuses before launch. | `verification/runs/T-family/T25R4_MODULE_runs/ladder_gate_t25R4.py:90`,`:14`; build-cap refusal `T23G_runs/mesh_ladder_t23g.py:72`,`:95` | **REPORTING** *(as a verdict check)* | It protects a **budget, not a verdict**. A run that costs more than predicted produces exactly the same number. **Explicit carve-out: `CLAUDE.md` rule 12 — "an overrun stops the run; it does not get a new budget" — is a constitutional compute control owned by Sanaa and is NOT retired, weakened or reclassified by this pass.** Cost control survives here as compute discipline; what is reclassified is only its standing as a *verdict* gate. A team cannot retire a constitutional clause (`FIRST-ACTION` rule, reserved powers). |
| **R4** | **Registered cost gates on a graded rung** (e.g. `G-T6a`: core-min over cap → `GATE FAIL`). | `verification/runs/T-family/T25R6a_C5_OUTER_runs/grade_t25R6a.py:527` | **REPORTING — FORWARD-ONLY** | Same reason as R3: a budget, not a verdict. **Adopted forward-only under Sanaa's clause 2.** Cost gates already **frozen into committed pre-registrations stand as registered** — `CLAUDE.md` rule 2 closes gates after first compute and forbids a change to a gate, threshold, cap or label; reclassifying them retroactively would be exactly the post-hoc gate change rule 2 exists to prevent. **No backfill and no re-registration is scheduled.** New registrations from this date carry cost as reporting. |
| **R5** | **Estimate-versus-actual cost calibration** at process completion; ratio actual/predicted into the calibration ledger. | `CLAUDE.md` rule 12 final bullet; ledger `docs/COST_CALIBRATION.md`; per-rung `COST.txt` | **REPORTING** | Protects the lab's **estimates**, not any verdict. The obligation to *record* the comparison is unchanged (rule 12 makes a completion report without it incomplete); what it may not do is block a hand-off. |
| **R6** | **Cap census / cap-transcription audits.** | `verification/runs/T-family/cap_census_audit.py`; `T20_runs/check_t20_transcription.py:179`; `docs/campaigns/T-family/CAP_CENSUS_2026-08-27.md` | **REPORTING** | Budget bookkeeping. Its own planted control (`check_t20_transcription.py:179`) remains armed — a reporting check still has to be honest about what it can see — but it moves no verdict. |
| **R7** | **INFRASTRUCTURE run fields** — `wall`/`wall_s`, `timeout_s`, `ranks`, `core_min`, `capped`, `checkMesh_rc`, `solver_path`, `note`, launch logs, `log.checkMesh`, `COST.txt`, DONE-marker mtimes/timestamps, freeze-checker stamps, anything a poller writes. Absent → NOT MEASURED, disclosed, grade proceeds. | `docs/campaigns/T-family/L342_FIELD_CLASS_AUDIT_2026-08-26.md` (classification table, 56 rows); implemented `T25R_MODULE_runs/mark_done_t25R.py:168`; `T23_runs/mark_done_t23.py:145`; `T24_runs/mark_done_t24.py:163`; `T25R2_MODULE_runs/mark_done_t25R2.py:181`; `T13_runs/build_t13.py:358` | **REPORTING — already so classified** | **This team had already made Sanaa's split, under L-342**, from her own earlier words: *"a bookkeeping failure invalidates the bookkeeping, never the physics artifacts."* No row moves. Recorded here so the reform's table is complete and the two classifications are visibly the same classification. |
| **R8** | **Absolute residual floors that are NOT the rung's gate**, and **degenerate-channel residuals** (`Ux` on a channel where `Ux ≈ 0`, L-338). | `verification/runs/T-family/T19b_runs/analyse_t19b.py:365-377` (*"REPORTED, NEVER GATED … an absolute residual floor is NOT the gate-(1) criterion"*, gate (1) there is the plateau test); `T13_runs/analyse_t13.py:20-22`,`:462`; registered `docs/campaigns/T-family/T13_PREREGISTRATION.md:120`, `T16_PREREGISTRATION.md:266` | **REPORTING — already so classified** | **This is the distinction G4 turns on and it was already drawn in code.** A residual threshold is gating **only** where it is the criterion rule 5 step (1) consults; a floor printed beside the gate, or a floor on a channel whose residual is noise because the channel is degenerate, feeds no verdict and drops. |
| **R9** | **Freeze-marker / `UNFROZEN` reporting in our graders** — our comparators' own self-reports of frozen-literal status. | `verification/runs/T-family/T25R6a_C5_OUTER_runs/grade_t25R6a.py:149`,`:328`,`:626`; `T3_runs/analyse_t3c.py:39-40` | **REPORTING — FORWARD-ONLY, and NOT OURS TO GRADE** | Freeze enforcement is **verification's programme and verification's instrument** (`scripts/check_comparator_freeze.py`, `CLAUDE.md` rule 2). We classify only our graders' own self-reports, and we do not reach into their instrument. Per Sanaa's clause 7, *coverage ratios forward-only, unreported*: **no backfill of freeze markers across existing T-family comparators is scheduled** and none is owed by this pass. (Rule 2's own requirement that the grading path be frozen before compute is untouched — it is constitutional, not a grader check of ours.) |
| **R10** | **Filing and naming conformance** — `<RUNG>_<PURPOSE>.md`, run outputs never beside the prose, paper sidecars. | `scripts/check_filing.py`; `docs/charters/FILING_CHARTER.md` | **REPORTING** | A misfiled artifact is hard to find; it is not a wrong number. No filing violation makes a verdict untrustworthy. |
| **R11** | **Absent optional controls reported as absent** — e.g. the `C-T` temporal-bias control when its case did not run. | `verification/runs/T-family/T14_runs/analyse_t14.py:317`; `T18_runs/analyse_t18.py:346` (*"REPORTED as absent, never gated"*) | **REPORTING — already so classified** | An absent supplementary control is a **disclosed gap**, and disclosure is what makes the grade honest. It cannot produce the reason because the primary controls G1–G3 carry the trust. |
| **R12** | **Preflight / executability smoke tests** before a rung launches. | `verification/runs/T-family/T23G2_runs/preflight_gate_t23g2.py:12`; `docs/campaigns/F14-cooling-ladder/K0d_PREFLIGHT_SMOKE_TEST.md`, `K0d_PREFLIGHT_EXECUTABILITY_FINDING.md` | **REPORTING** | It saves core-minutes by finding a broken case early; it grades nothing. A preflight failure that means the case genuinely cannot run is a **blocking physics fix** under Sanaa's clause 7 and needs no gate to authorise the repair. |
| **R13** | **Documentation-shape checks** — provenance tagging, assert-under-`-O` inventory, checkpoint-gate and saturation audits, standards-intake conformance. | `docs/campaigns/T-family/PROVENANCE_TAGGING_PROPOSAL_2026-08-31.md`, `ASSERT_UNDER_O_INVENTORY_2026-08-26.md`, `CHECKPOINT_GATE_AUDIT_2026-08-25.md`, `SATURATION_AUDIT_2026-08-25.md`, `STANDARDS_INTAKE_RULING_2026-08-25.md` | **REPORTING** | Audits of how records are written. They improve legibility and none of them is a predicate any verdict rests on. *(The `-O` inventory names a real hazard — an `assert` stripped under `python -O` — but the graders that carry verdicts refuse via explicit `refuse()`/`SystemExit`, not via `assert`, so no gating predicate depends on it.)* |

---

## 3. Forward-only adoptions (Sanaa's clause 2)

*"If the protected result isn't on any team's current line, the rule is adopted as
'forward-only' (applies to new entries) and the backfill is not scheduled."*

| item | forward-only because | backfill |
|---|---|---|
| **R4** — cost gates reclassified to reporting | Committed pre-registrations froze cost gates before first compute; `CLAUDE.md` rule 2 forbids altering a frozen gate, threshold, cap or label after compute. Registered rows stand as registered. | **NOT SCHEDULED.** No rung is re-graded and no verdict is withdrawn by this pass. |
| **R9** — freeze-marker self-reports | Verification's programme; adding markers across existing T-family comparators would require re-touching files that are **frozen** under rule 6 and would create work in another team's instrument. | **NOT SCHEDULED**, per her clause 7 (*coverage ratios forward-only, unreported*). |
| **G7 / G8** — the y+ sublayer bound and mesh-identity rows, if the supervisor rules them gating | Both are already implemented and already enforced where they exist; nothing is added to any other team. | **NO BACKFILL REQUESTED.** Rungs already graded are not re-graded. |

**No check in this table requires another team to backfill, migrate or re-register.**
This pass creates zero work outside heat-transfer territory.

## 4. Referred, not fixed

- **The T3 rule-3 control predicate** (`T3_runs/analyse_t3.py:326-327`) reads back the
  **maximum change over all cells** rather than the change **at the planted cell**, and
  demands recovery to `1e-15` absolute on a difference of two ~300 K doubles where one
  ulp is 6.661e-14. Already ruled a rule-3 violation inside a rule-3 control
  (`VERIFICATION_CHARTER` §2d.11.1) and already under repair on a separate lane. **Not
  touched here.** It is recorded because it is the proof of G1's reason, not because
  this pass discovered it.
- **No other mis-implemented check was found in this pass.** The one classification
  consequence that looks like a defect — the y+ split at G7/R1 — is a consequence of the
  verification ruling, not a newly found implementation error.

---

*Classified by heat-transfer, once, per Sanaa's 2026-09-03 order. G7 and G8 are proposals
awaiting the supervisor's ruling; every other row is final for this pass. This audit
opens no follow-up question, proposes no new check, and builds no instrument to measure
another instrument's reach (her clause 2).*
