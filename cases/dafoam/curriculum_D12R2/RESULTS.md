# D12R2 PHASE 1 — GRADED. EVERY GATE PRODUCED A NUMBER, AND THE ANSWER IS THAT THE FD BRIGHT LINE CANNOT BE CROSSED HERE

**Dated 2026-08-26.** Lane: dafoam `lab-lane`. Pre-registration and instruments frozen at **`e6580910`**.
Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady`, stamp
**`20260826T033053Z_3069758`**, started **03:30:54Z**, phase 1 complete **04:26:40Z**.
**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).

---

## 1. THE HEADLINE

> **`G12R-4` STEP SIZING = `NOT A RESULT`. `h_min = 1.742838e-01` EXCEEDS the registered
> `h_max = 5.000e-02` by 3.49×. NO ADMISSIBLE FD STEP EXISTS AT THIS WINDOW.**

**AND THIS OUTCOME WAS REGISTERED IN ADVANCE, TWICE, BEFORE ANY COMPUTE.** `PREREGISTRATION.md`
§8.2 of this item, and §2.2 of the superseded D12R before it (`f9c8b9c8`):

> **D12 MAY BE A CASE WHERE THE FD BRIGHT LINE CANNOT BE CROSSED AT ALL. That would be a GENUINE
> FINDING ABOUT THE METHOD–CASE PAIR, NOT A FAILURE OF EITHER**, and it is registered here as an
> anticipated outcome **so it cannot later be read as a consequence of an instrument defect.**

**That sentence is why this result is worth anything.** It was written into a frozen document
before the solver started, on an item whose entire history is instrument defects. **The
no-admissible-step branch is a RESULT.** The optimisation does not proceed on a gradient that
cannot be verified, and nothing is published as verified that was not.

**This is also the first time in this case's history that the comparator ran to completion.**
`curriculum_D12` phase 1: zero graded output. `curriculum_D12R` phase 1: zero graded output
(`NOT A RESULT`, refused at stage 1 of 32). **D12R2 phase 1: all nine gates returned.**

---

## 2. EVERY GATE, WITH ITS NUMBER AND ITS ARTIFACT

Graded by the **frozen** `d12y_grade.py`, blob `3a76c828`, **verified identical to `e6580910`
immediately before grading** (rule 2's grading-path clause). Selftest run immediately before:
**`rc=0`, 82 registered / 82 listed / 82 RETURNED A RESULT / 0 failures, all 15 emitted gates
exercised, 0 unexercised.** All values below cite `step_plan.json` / `manifest.jsonl` /
`ledger.txt` in the run root.

| gate | verdict | value |
|---|---|---|
| **G12R-0b** binding | **PASS** | 33 manifest rows, 33 ledger `STAGE=` lines, registered 33 |
| **G12R-0** completion | **PASS** | 33 stages |
| **G12R-W** where-control | **PASS** | 31 stages witnessed |
| **G12R-1** limit cycle | **PASS** | mean `CD = 0.6563231414421499`, 2400 samples, 253 sign changes, p2p 0.13162, **p2p_rel 20.05 %**, period **18.9644 steps** |
| **G12R-3** `δ_window` | **PASS** | **`1.7958478e-03`** (rel 0.27359 %), 2101 windows, `W/P = 15.8191`, **not degenerate** |
| **G12R-2** `δ_repeat` | **PASS** | **`0.0`** over 3 identical runs |
| **G12R-3b** `δ_pert` | **PASS** | **`2.2796668e-06`**, max over 4 components |
| **G12R-4** `δ_eff` | **PASS** | **`1.7958478e-03`**, dominant term **`δ_window`**, none excluded by name |
| **G12R-4** step sizing | **`NOT A RESULT`** | **`h_min = 1.742838e-01` vs `h_max = 5.000e-02`; `steps: []`, `admissible: false`** |

`δ_eff := max(δ_repeat, δ_window, δ_pert) = 1.7958478e-03`, and
`h_min = 100·δ_eff/|g| = 100 × 1.7958478e-03 / 1.0304158599180422 = 0.1742838`.

### 2.1 TWO ZEROS THAT ARE NOT WHAT A ZERO USUALLY MEANS, AND THE COMPARATOR SAYS SO ITSELF

**`δ_repeat = 0.0` IS NOT A CLEARANCE.** The comparator's own registered note, carried verbatim
into this record rather than paraphrased:

> *"`delta_repeat == 0` is the EXPECTED reading at np=1 on a deterministic solver from a
> byte-identical field. **IT IS NOT A CLEARANCE FOR THE FD STEP**: the noise that threatens a
> time-averaged objective on a limit cycle is phase noise, measured by `G12R-3`."*

And it is `G12R-3`'s phase noise that dominates `δ_eff` and sets `h_min`. **A reader who took
`δ_repeat = 0` as "no noise" would have concluded the opposite of the truth.**

**TWO OF FOUR `δ_pert` COMPONENTS REPORT `0.0` WITH `detectable: false`** (components 0 and 3),
and again the comparator distinguishes the claims: *"a component reporting 0.0 means **NO FLOOR
WAS DETECTABLE AT THESE STEPS, which is not the same claim as no floor**."* `δ_pert` is taken as
the **max** over components because `h*` must be admissible for all of them.

### 2.2 THE `g_implied` FIGURES — WHAT THEY ARE NOT, AND WHY THEY APPEAR IN NO TABLE

**PLACEMENT IS PART OF THE CLAIM, so this subsection carries no table, no row and no heading that
could be lifted as a result.** The lab's standing hazard is that a printed discrepancy labelled
*"diagnostic only"* is **worse than one never computed**: the label lives in prose, the number
lives in a table, and the next reader quotes the number. **A label is not positional protection.**
Accordingly every figure below sits inside the sentence that says what it is not.

`G12R-3b` emits a per-component `g_implied_DIAGNOSTIC_ONLY`, and **not one of those four values is
a gradient**: the `1.2529` on component 0 is not a 21.6 % disagreement with the adjoint's
`1.0304`, the `−0.1883` on component 1 is not a sign flip against it, and the `0.4341` and
`1.4388` on components 2 and 3 are not agreement or disagreement of any kind — **all four are
noise, and the noise is measurable rather than asserted.** Those probes sit at `h = 1e-06` and
`h = 1e-05`, where the measured signals are `S_a ≈ 1.1e-06 … 4.2e-06` against a floor of
`δ_eff = 1.80e-03`: **the noise is two to three orders of magnitude ABOVE the signal**, so a
finite difference there divides one noise sample by another.

> **THESE FIGURES ARE A SYMPTOM OF THE `G12R-4` HEADLINE, AND ANY USE OF THEM AS AN
> ADJOINT-VERSUS-FD COMPARISON IS A MISREADING.** They are exactly what "no admissible FD step
> exists" looks like from inside: at a step small enough to be linear, the objective difference is
> beneath the noise floor. **They are not evidence about the adjoint, they are not an FD table,
> and they must never be quoted as either.** The one adjoint-versus-FD comparison this item could
> have made is `G12R-6`, and **`G12R-6` DID NOT RUN.**

---

## 3. CORROBORATION AND DEPARTURE AGAINST THE **NOT IMPORTED** PRIORS

`PREREGISTRATION.md` §3.4 fixed the rule before compute: **a repeat is corroboration, a departure
is a FINDING.** Priors are from the superseded items and were **not imported**.

| quantity | prior (NOT IMPORTED) | D12R2 measured | departure | reading |
|---|---|---|---|---|
| mean `CD` | `0.6563506540` | **`0.6563231414`** | **−0.004 %** | **CORROBORATION**, to four significant figures |
| period | `18.9955` steps | **`18.9644`** steps | **−0.16 %** | **CORROBORATION** |
| `p2p_rel` | 19.40 % | **20.05 %** | +3.38 % | corroboration, loose |
| sign changes | 221 | **253** | **+14.5 %** | **DEPARTURE** |
| `δ_window` | `1.274958e-03` | **`1.7958478e-03`** | **+40.9 %** | **DEPARTURE, and the consequential one** |

> **THE OBJECTIVE CORROBORATES AND THE NOISE DOES NOT.** Mean `CD` and the shedding period repeat
> to well under a percent; the **noise** terms are materially larger. That is the honest shape of
> it, and it is stated rather than smoothed.

**A CANDIDATE EXPLANATION, AND IT IS LABELLED AS UNTESTED.** The priors came from
`curriculum_D12`, whose **defect 1 was that `FIELD_B` was a per-step write carrying a diagnostic
subset that could not start a solve**. D12R2's `S2b` series starts from a **final-time write,
11 of 11 fields, with its planted control firing** (§4). A different initial condition producing
a different phase-noise measurement is unsurprising. **This lane did not test that mechanism and
does not claim it** — the departure is reported as measured, with a hypothesis named as a
hypothesis.

### 3.1 THE ANTICIPATED OUTCOME HELD; THE ANTICIPATED MAGNITUDE DID NOT

`PREREGISTRATION.md` §8.2 predicted `h_min ≈ 1.10`, **~22× over `h_max`**, by direction-only
arithmetic. **Measured: `h_min = 0.1743`, 3.49× over.**

> **THE CONCLUSION IS UNCHANGED AND THE MARGIN IS SIX TIMES SMALLER.** The registered branch fires
> either way, but a record that quoted "~22× over" would be quoting a number this item did not
> measure. **The measured figure is 3.49×, and the prediction is a DEPARTURE of that size,
> reported as one.**

---

## 4. THE COMPLETION RULE, AND THE THREE REPAIRS UNDER LIVE FIRE

**All 33 rows:** `rc=0`, `docker_exit=0`, `oomkilled=false`, `end_line_present=true`,
`coldstart_ok=true`, `age_guard_ok=true`. **`last_time == endTime` on all 32 non-mesh rows.
`time_line_count == expected_steps` on all 31 unsteady rows.** Tasks present:
`mesh`, `shell`, `run_model`, `compute_totals` — **all four branches of the repaired taxonomy
exercised by real stages.**

**`FIELD_B` and its planted control, live:** `FIELD_B_CREATED from S2a/3 (a FINAL-time write, not
a per-step write)`; `FIELD_B_COMPLETENESS required=11 present=11 reference=FIELD_A`; and the
control fired — `COMPLETENESS_PLANT_OK the check found U_0 betaFINuTilda fvSource meshPhi
nuTilda_0 nut p_0 missing from the intermediate write 0.01 — **it can say NO**`. **Seven fields,
including `nut`, seen missing under the plant.** The registered discard is **0 by construction**.

**THE THREE REPAIRS, CONFIRMED ON THE LIVE RUN:**

| defect | confirmation |
|---|---|
| `D12R2-DEF-3` | `S0_MANIFEST_ROW cells=2450 check_ok=True polyMesh=8 age_guard=True`, then `S0_ROW_WRITTEN`. The launcher **aborts** if the row is absent, so it cannot silently fail to fire. |
| `D12R2-DEF-1` | `S1a` (`task=shell`, `status=null`) and `S0` (`task=mesh`, `status=null`) **both PASS**, while all 31 JSON-task rows were still required to carry `status="COMPLETE"`. **The exact row that killed D12R now grades, and the protection that refused it is intact.** |
| `D12R2-DEF-2` | `G12R-0b` **PASS at 33/33/33.** |

> **AND THE ARITHMETIC THAT EXPOSED `DEF-2` NOW CLOSES EXACTLY.** In D12R the manifest rows summed
> to 63.8833 against a ledger total of 63.95 — a 0.0667 residue that **was** the vanished S0. In
> D12R2 the 33 rows sum to **55.5167**, and `ledger.txt` reads `PHASE1_COMPLETE spent=55.5167
> core-min`. **The same check that found the defect is the one that now certifies its repair.**

---

## 5. PHASE 2 WAS NOT LAUNCHED, BY THE REGISTERED BRANCH — AND THAT IS THE RESULT

`--phase 2` was **run**, so the decision is on the record rather than merely inferred. The frozen
launcher read the comparator's `step_plan.json` (`STEP_PLAN_MD5=f24aeda37e9fe7f802ea105d086dfc04`,
*"written by the comparator, not by this launcher"*), found `admissible: false`, and wrote:

    NO ADMISSIBLE FD STEP AT THIS WINDOW -- the comparator's registered G12R-4 branch fired.
    Phase 2 is NOT LAUNCHED.  That is a RESULT, not a failure (see the pre-registration).

**`rc=0`. Zero containers created. Zero core-minutes spent.** Phases 3 and 4 depend on
`step_plan2.json`, which depends on the sweep phase 2 did not run, so **the FD line terminates
here** at `W = 300`.

### 5.1 A FINDING ABOUT THE INSTRUMENTS, DISCLOSED: **THE `W2` CONTINGENCY HAS NO EXECUTION PATH**

`PREREGISTRATION.md` §6 registers `W2 = 900` as the contingency window, and `G12R-4`'s own
refusal text says *"the contingency window fires"*. **It does not fire, because there is nothing
to fire.** Measured: `W_CONTINGENCY` appears in `d12y_grade.py` at exactly **two** lines — its own
definition (`:38`) and a reporting dictionary (`:2470`) — **no gate consumes it**, and
`grep W2` over `d12y_stage_and_run.sh` returns **no phase that runs it**.

> **A REGISTERED CONTINGENCY WITH NO PATH TO IT IS THE SAME FAMILY AS `elif kind == "mesh": pass`
> ON A RUN THAT NEVER PRESENTS A MESH ROW** — a reader of the document believes a fallback exists,
> and the code cannot reach it. **It is disclosed here rather than quietly relied upon.** It does
> **not** change this result: `W = 300` is the registered primary window, it was not degenerate
> (`W/P = 15.8191`), and the gate at that window returned. **Whether to buy a `W2` run is the
> supervisor's call and is NOT taken by this lane** — it would be new compute against a path no
> frozen instrument currently implements.

---

## 6. STANDING CAVEATS — CARRIED IN FULL

1. **`St` IS NEVER TO BE QUOTED AS A STROUHAL MEASUREMENT.** This item **re-measured** the period
   at **18.9644 steps**, giving `f ≈ 5.27 Hz` and **`St ≈ 0.5273`** — again roughly **2.6× the
   accepted ≈0.2**. **On a 2,450-cell 2D URANS mesh with wall functions that is a RESOLUTION
   ARTIFACT, not a discovery.** The estimator is **mean-crossing**, which underestimates the
   fundamental on a harmonic signal, so **18.9644 is a LOWER bound on the period and 0.5273 an
   UPPER bound on `St`**. It is a **window-sizing diagnostic and nothing else.** No
   mesh-convergence study was bought, so the artifact hypothesis is **neither tested nor refuted**.
   **That the re-measurement corroborates the prior does NOT make it a Strouhal number** — it
   makes it a reproducible artifact.
2. **THE `G12R-4` NO-ADMISSIBLE-STEP OUTCOME IS NOW THIS ITEM'S OWN**, because the gate **ran**.
   D12R was never entitled to state it; **D12R2 is**, at `W = 300`, on this mesh, for this
   objective, with `h_max = 0.05` and `EPS_NOISE_TARGET = 0.01` as registered. **It is a finding
   about the METHOD–CASE PAIR and not a failure of either.**
3. **No grid family was run, so rule 5 has no row to gate and NO GCI IS QUOTED.** Nothing here
   speaks to the physical accuracy of `CD` at `Re_D = 1.0e6` on 2,450 cells.
4. **The PATCHED row is UNBOUGHT** — `--image patched` was not run, and this record quotes only
   shipped-image numbers.

---

## 7. COST

**Phase 1: predicted 70.0 core-min, actual 55.5167, ratio 0.793.** Measured from `ledger.txt`
(`PHASE1_COMPLETE spent=55.5167 core-min`) and independently reproduced by summing the 33
manifest rows' own `core_min`. Longest row **S5 at 654 wall s**, so **no row matches the
3600-s stall rule and gross = cleaned**. Guard `CAP_CORE_MIN = 600.0`, **no overrun, no cap
moved**. Phase 2 spent **0.0**. **$0.0475 DERIVED, NOT MEASURED** at $0.0513/core-h,
c7a.4xlarge, reported-by-owner (`COMPUTE_BUDGET_CHARTER.md` §5 — the box cannot read its own
billing). Calibration row **`C-115`** in `docs/COST_CALIBRATION.md` (see §8).

---

## 8. CORRECTION, 2026-08-26 — A CALIBRATION-ROW ID I PREDICTED INSTEAD OF DERIVING

**Same day, same lane. Sections 1–7 are otherwise byte-unchanged; lines whose number changed
above this section: 0.** One cell in §7 was corrected, and this section says exactly what and why.

§7 as first committed (`37779471`) read **"Calibration row `C-108`"**. **The row actually landed
as `C-115`.** Between writing that sentence and committing the row, peers landed six further
rows, so the maximum id moved from 107 to 114.

**The id itself was never at risk**: it is re-derived by hand from the HEAD blob **inside the
committing shell invocation**, with an explicit collision assert, exactly as `CLAUDE.md` rule 11
requires — which is why `C-115` is correct and unique. **What was wrong was the CITATION**, which
I wrote in advance by adding one to a number I had read earlier.

> **THE LESSON, AND IT IS A SMALL ONE THAT GENERALISES: RULE 11 BINDS THE CITATION AS WELL AS THE
> ASSIGNMENT.** A record that names a row id it has not yet created is predicting, and this file
> is written by six teams committing constantly. The same trap took `C-100` → the next dafoam row
> was `C-107`, not `C-101`. **Cite the id the commit actually produced, not the one you expect.**

**Nothing else in this record depends on that cell**, and no gate verdict, number or artifact
path is affected.
