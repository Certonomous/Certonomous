# T3f — the `R_fy` continuation (`R_fz`): drive `|U|` to `tol` on a **falsifiable decay prediction**, and score **every** prediction the registration declares

> **STATUS AT THIS COMMIT: DRAFT. NOT FROZEN. NOT ENQUEUED. NOT LAUNCHED. AUTHORISES NO SOLVE.**
>
> **The freeze is WITHHELD until §7's rehearsal is driven**, per `VERIFICATION_CHARTER` §2ap —
> **and §7 adds a leg §2ap does not require**, because T3e passed all four of its legs and still
> shipped a grader that did not score one of its own registered predictions (§1, D-4).

**Authored personally by `heat-transfer-supervisor`.** The `Agent` tool remains **DENIED** by the
permission classifier for this team; the denial is **not routed around** and is disclosed here as
it was in T3e. **If execution needs lanes and the denial persists, it is a named capability gap for
Sanaa, not something to work around.**

---

## 1. WHAT T3e ESTABLISHED, AND THE ONE DEFECT IT SHIPPED

T3e graded **`GATE REACHED`** (`T3e_RESULTS.md`, `646ed113`). It answered the question T3d could
not: **`|U|`'s non-convergence is DECAYING, not stalled.**

| pair | `\|U\|` `relative` | ratio to previous |
|---|---:|---:|
| (2000, 4000) | 2.45109e-06 | — |
| (4000, 6000) | 2.08526e-06 | **0.8507** |
| (6000, 8000) | 1.77017e-06 | **0.8489** |

**Mean factor 0.8498 per 2,000 iterations; the two independent intervals agree to 0.2 %.**

**D-4 — THE DEFECT T3f REPAIRS.** T3e's registration declared **P-1, P-2 and P-3**; its grader
scored **P-1 and P-2 only**. P-3 was measured **out-of-band, by hand**, and **was FALSIFIED** —
`p_rgh`'s residual maximum reached 2.0× its seed value against an F-3 written over the maximum.
**T3e's §2ap rehearsal passed all four legs and this still got through, because §2ap rehearses
BUILDER → GRADER and no leg asked whether the grader scores every REGISTERED prediction.**
*Repair: §7.1 leg 5, and §5's completeness clause.*

---

## 2. THE CASE

Continuation of `R_fy`, seeded from `R_fy/8000`. **Mesh IDENTICAL to `R_ff`, `R_fx` and `R_fy` —
602,128 cells. Not a new ladder level; no refinement is introduced.** Case `R_fz`,
`buoyantBoussinesqSimpleFoam`, **8 ranks**, `kOmegaSST`, wall-resolved. All physical constants are
inherited and copied **by key** from `R_ff/CASE.txt` (§7.2), never retyped.

`endTime` **8,000** additional iterations · `writeInterval` **2000** · **`purgeWrite` 0** —
four checkpoints, **three consecutive pairs**, as T3e.

---

## 3. THE PREDICTIONS — AND THE HEADLINE ONE IS DELIBERATELY AT RISK

**P-1 — PRIMARY. `|U|` REACHES `relative ≤ 1e-06` BY `endTime` 8,000.**
Derivation, stated so the arithmetic is checkable rather than asserted: from T3e's last measured
`1.77017e-06` at the mean factor `0.8498` per 2,000 iterations, four intervals give
`1.77017e-06 × 0.8498⁴ = 9.2318e-07`.
**FALSIFIER F-1: `relative > 1e-06` at the last pair.**

> ### ⚠ **THIS PREDICTION IS TIGHT ON PURPOSE AND ITS FAILURE MODE IS NAMED IN ADVANCE.**
> The predicted margin below tolerance is **7.7 %**. **P-1 FAILS IF THE DECAY FACTOR IS ≥ 0.868** —
> a drift of just **0.018** from the measured 0.8498. That is well inside plausible drift for a
> factor measured over three pairs on one run. **A prediction with comfortable margin would not be
> a prediction; this one can genuinely lose, and if it loses that is a finding about the decay
> law, not a disappointment.**

**P-2 — THE MECHANISM. The decay factor STAYS IN `[0.830, 0.870]` on all three of T3f's pairs.**
That is T3e's measured `0.8498` ± `0.020`. **FALSIFIER F-2: any pair-to-pair ratio outside that
band falsifies the geometric-decay model — EVEN IF P-1 SUCCEEDS.**
**P-1 and P-2 can disagree, and that is the point:** convergence could arrive while the law drifts,
or the law could hold while convergence does not. **Two independent falsifiers over one run.**

**P-3 — `T` STAYS CONVERGED**, below `1e-06` on all three pairs. It finished T3e at `4.42715e-07`
and was itself decaying. **F-3: any pair above `1e-06`.**

**P-4 — NO RESTART SPIKE, and this time IT IS SCORED BY THE GRADER.** No solved field's initial
residual exceeds its own first value by more than **2.5×**. **F-4: any field above that.**
**The threshold is registered at 2.5× BECAUSE T3e MEASURED 2.0× on `p_rgh` and was falsified by a
clause written over the bare maximum.** ⚠ **This is a WIDER threshold than T3e's, and it is
declared as such rather than slipped in: T3e's F-3 tripped on any excursion at all, which made it
unfalsifiable-in-the-useful-direction — a seeded restart perturbs `p_rgh` by construction. The band
is set from a MEASURED value on the identical case and is registered BEFORE this run.** It is
**not** a widening applied to rescue a failed row: **T3e's P-3 stays FALSIFIED and is not re-graded.**

---

## 4. THE GATE

**Graded quantity: the composed `convergence_state` at each of the three pairs**, `tol = 1e-06`,
**inherited unchanged from T3d and T3e and NOT moved.**

**Outcomes, all gradeable — the T19 lesson:**
- `|U| ≤ tol` at the last pair **and** P-2 holds → **`PASS`**.
- `|U| ≤ tol` but P-2 falsified → **`GATE REACHED`**, converged but the decay law is not what was registered.
- `|U| > tol` with P-2 holding → **`GATE FAIL`** on P-1: a measurement that missed a threshold frozen before compute.
- `|U| > tol` and P-2 falsified → **`NOT A RESULT`** on rule 5 clause (1), routing under §2an to numerical rule-out.

**RULE 5.** **NO ROACHE TRIPLE IS FORMED** — one mesh, one refinement. **No observed order, no GCI,
no Richardson extrapolate is computed, quoted or derivable, and EVERY NUMBER THIS RUNG PRODUCES
CARRIES NO DISCRETISATION BOUND AT ALL.** Clause (1) **is** reached and applied: while `|U|` is not
iteratively converged **no T3 ladder row is graded from this level**, whatever P-1 says.

---

## 5. THE GRADER'S COMPLETENESS CLAUSE — D-4's REPAIR

**`analyse_t3f.py` MUST score P-1, P-2, P-3 and P-4, and MUST REFUSE at exit 2 if any registered
prediction is unscored.** The grader carries the prediction list as data, checks at run time that
every entry produced a verdict, and refuses naming the unscored one. **A registration that declares
a prediction its grader silently ignores is the same class of defect as a builder that writes what
its grader cannot read — the pair is REGISTRATION → GRADER instead of BUILDER → GRADER.**

**D-J1 discipline, carried forward:** every `convergence_state` is emitted with its `field_range`
beside it; a zero denominator returns `NOT A RESULT`, **never `0.0`**.

---

## 6. THE COMPLETION-MARKER PRODUCER — REGISTERED BEFORE COMPUTE

**`verification/runs/T-family/T3_runs/mark_done_t3.py`, git blob
`5da28c733e47a4a6c8046dfdf8674c2af27ab81a`**, frozen 2026-08-21, invoked as
`python3 mark_done_t3.py --root T3_runs R_fz`. **Its invocation and full output are recorded beside
the case** (§2ao condition 1). **If it refuses, the refusal is the finding** and is not worked
around. **`reconstructpar_rc = 0` is additionally required** from `STATUS.R_fz` — `R_fz` runs
decomposed on 8 ranks — and is registered here rather than assumed.

---

## 7. THE §2ap REHEARSAL — FIVE LEGS, AND THE FIFTH IS NEW

Before this document freezes, `build_t3f.py` and `analyse_t3f.py` are driven end to end and the
transcript committed:

1. **SUCCESS** — the grader reads every key from the builder's **real** output and names each.
2. **VERDICT** — the grader runs to a verdict on synthetic fields.
3. **CORRUPTION** — one key removed → the grader **REFUSES at exit 2**.
4. **LAUNCHER** — wrong ranks, wrong timeout and wrong case each refuse, naming the registered values.
5. ⚡ **COMPLETENESS (NEW, D-4's repair, beyond §2ap's requirement)** — a prediction is removed from
   the grader's scoring path and the grader **MUST REFUSE**, naming the unscored prediction.
   **Legs 3 and 5 are the load-bearing ones: a rehearsal that only shows success does not show the
   check is live.**

**§7.2 — the builder's contract.** `R_fz/CASE.txt` carries the **full structured key-value block**,
inherited constants copied **by key** from `R_ff/CASE.txt`. It seeds **`0.orig/`, NOT `0/`** — the
registered launcher creates `0` from `0.orig` and touches `0/T` **last**, so that mtime dates the
run. **A builder writing `0/` directly hands the age guard a COPIED mtime and defeats it; T3e's
rehearsal caught exactly that before it cost a run.**

**§7.3 — the freeze.** At freeze, §8 pins by git blob sha: `build_t3f.py`, `launch_t3f.sh`,
`analyse_t3f.py`, and §6's marker producer. **Until those four pins exist this document authorises
nothing.**

---

## 8. ARTIFACTS AND PINS

**NOT YET CUT.** `T3f_runs/` does not exist. No case, builder, launcher, grader or queue entry.

---

## 9. COST — RULE 12

**Basis: T3e's OWN MEASURED rate on this identical mesh, `0.172867` core-min/iteration**
(1,382.933 ÷ 8,000, from `STATUS.R_fy`). **The calibration lesson applied twice over:** T3d's POINT
used `R_ff`'s saturated-box whole-run average and missed by 13.21 %; T3e used T3d's own measured
rate and missed by 12.2 %, **the residual being load, which is not in the basis.** T3f uses T3e's,
and the residual will be load again — **stated in advance rather than discovered.**

| | |
|---|---|
| **POINT** | **1,382.9 core-min** = `0.172867 × 8,000` |
| **HARD CAP** | **4,148.7 core-min** = `3 × POINT` |
| registered `timeout_s` | **31,115 s** = `4,148.7 × 60 ÷ 8` |
| dollars at POINT | **$1.1824** — **DERIVED at $0.0513/core-h, reported-by-owner, NEVER MEASURED** |

**An overrun stops the run; it does not get a new budget.** A predicted-versus-actual row is owed at
completion and at no earlier point.

---

## 10. WHAT THIS DOCUMENT DOES **NOT** DO

- It **does not freeze**; §7's five-leg rehearsal has not been driven.
- It **does not create** `T3f_runs/`, build, enqueue or launch anything.
- It **does not move** `tol`, any cap, or any label. **P-4's 2.5× is a NEW threshold on a NEW rung,
  registered before compute from a measured value — not a relaxation of T3e's F-3**, which stays
  falsified and is not re-graded.
- It **does not re-grade** T3d, T3e or any sibling.
- It **does not assert any verdict**; no term of rule 1's vocabulary is claimed for T3f.
- It **does not claim** `|U|` will converge. **P-1 can lose, and §3 names the exact factor at which it does.**

---

## AMENDMENT 1 — 2026-09-05 — **T3f IS FROZEN. THE FIVE-LEG REHEARSAL PASSED AND §8's PINS ARE CUT.**

**Appended by `heat-transfer-supervisor`. Lines whose number changed above this section: 0.**
**No gate, threshold, band, cap or label moves. `tol = 1e-06` is unchanged.**

**PRE-FREEZE CONDITION, CHECKED IN THE COMMITTING INVOCATION:** `R_fz` holds `0.orig/`,
`CASE.txt`, `constant/` and `system/` — **no `0/`, no numeric time directory, no
`STATUS.R_fz`, no `DONE.R_fz`, no solver has run, zero core-minutes.**

**§7's five legs all PASSED** (`T3f_runs/T3f_REHEARSAL_2ap.txt`). **Leg 5 — beyond §2ap's
requirement — dropped P-4 from the scoring path and the grader REFUSED at exit 2, naming it.
That is D-4's repair proven live, and it is the leg T3e did not have.** Builder and launcher are
T3e's by registered substitution only, each **delta-proved to 0 differing lines** on reversal.

### §8 — THE PINS

| artifact | git blob SHA-1 |
|---|---|
| `verification/runs/T-family/T3f_runs/build_t3f.py` | `53d562ecd053207278f86ca53fc04fa9092c8044` |
| `verification/runs/T-family/T3f_runs/analyse_t3f.py` | `d29c0eabe30e0e31fd2a52177dbab060d5c4308c` |
| `verification/runs/T-family/T3f_runs/launch_t3f.sh` | `ae9832707706e7ca1705ec826ab08160744fe469` |
| `verification/runs/T-family/T3_runs/mark_done_t3.py` (§6) | `5da28c733e47a4a6c8046dfdf8674c2af27ab81a` |

**§7.3's condition is met and this document is FROZEN.**

---

## AMENDMENT 2 — 2026-09-07 — §2ay LINEAGE ANNOTATION (recorded predecessor)

**Appended by a heat-transfer lab lane. Lines whose number changed above this section: 0.**

This dated addendum records, in the line-leading form the §2ay completion-enforcement
reader (`scripts/check_completion_enforcement.py`, recorded-lineage limb) reads from a
registration, the attempt this rung follows. It is a **pure lineage annotation**: it
alters no gate, threshold, band, cap, label or verdict — T3e's graded verdict stands
unchanged, nothing above is reopened, and no frozen sha moves.

**Predecessor: `T3e` (explicit, for §2ay linkage).**
