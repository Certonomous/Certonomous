# CURRICULUM D12R — PHASE 1 — RESULTS

**Dated 2026-08-27.** Lane: dafoam `lab-lane` (B). Supervisor: `dafoam-supervisor` (`[lab-attributed]`).
Pre-registration frozen at **`f9c8b9c8`**, amended to **v1.1** at **`9517a39f`** (§10).
Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D12R-cylinder-unsteady`, **preserved**.
**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).

---

## 0. THE LIMITATION THIS RECORD LEADS WITH, BECAUSE A READER MUST MEET IT FIRST

> **`G12R-0` GRADES 32 OF THE LEDGER'S 33 STAGES, AND THE ONE IT DOES NOT GRADE IS `S0`, THE
> MESH STAGE EVERY OTHER STAGE RESTS ON.**

`S0` is recorded in `ledger.txt` (`TASK=mesh`, `rc=0`, `wall_s=4`, 0.0667 core-min) and **is not in
`manifest.jsonl` at all**, so the completion gate never sees it. The comparator carries a live
`elif kind == "mesh": pass` branch, so a reader of the code would reasonably conclude mesh stages
are graded; **on this run no row ever presents one, and the branch is dead code.** Found by
reconciling the ledger's own cost arithmetic against the manifest (`PHASE1_GRADE_REFUSAL.md` §8).

**This is NOT repaired here and was deliberately not repaired.** The successor comparator solves it
with a separate ledger cross-read gate (`g0b` in `curriculum_D12R2/d12y_grade_w3.py`). Back-porting
it would be a second instrument change on a closed-gate item whose entire authority is L-342/R-RC
compliance **at one named site**, and **compliance is not a licence to improve the gate**
(`dafoam-supervisor`, 2026-08-27). Any future repair is its own registration.

**A second limitation, stated here rather than in a footnote.** For a `shell` stage there is no
per-stage JSON, so the `obj` versus `obj_from_log` cross-check is silently skipped on `S1a` — the
same family as the S0 gap: **an instrument whose coverage reads wider than what it is handed.**
Measured and not repaired.

---

## 1. THE VERDICT

> ## **D12R PHASE 1 = `NOT A RESULT`**
>
> **`G12R-4` step sizing: `h_min = 1.742838e-01` EXCEEDS the registered `h_max = 5.000e-02` by
> 3.49×. NO ADMISSIBLE FD STEP EXISTS at `W = 300`. `admissible: false`, `steps: []`.**

**This is the pre-registration's own §2.2 branch, registered in advance:**

> *"D12 MAY BE A CASE WHERE THE FD BRIGHT LINE CANNOT BE CROSSED AT ALL. That would be a GENUINE
> FINDING ABOUT THE METHOD–CASE PAIR, NOT A FAILURE OF EITHER."*

It was registered before any number was produced precisely so it could never be read as a
consequence of an instrument defect. **The `G12R-4` no-admissible-step branch is a RESULT.**

### 1.1 IT IS NOT THE SAME VERDICT AS BEFORE, AND THE WORD BEING IDENTICAL IS THE TRAP

`PHASE1_GRADE_REFUSAL.md` (`9d26801e`) recorded D12R phase 1 as `NOT A RESULT` on 2026-08-26. **That
verdict is STRUCK, not rewritten, and that document stands on the record unedited.** The two are
not the same finding and must never be collapsed:

| | 2026-08-26 | 2026-08-27 |
|---|---|---|
| what happened | the comparator **REFUSED (exit 2) at stage 1 of 32** | every gate ran |
| numbers produced | **zero** | **nine gate readings** |
| what it was about | **the instrument pair** | **the method–case pair** |
| `step_plan.json` | did not exist | exists, `admissible: false` |

### 1.2 WHAT THIS RESULT MAY NEVER BE QUOTED AS

> **IT IS NOT AN INDEPENDENT MEASUREMENT OF THE FD BRIGHT LINE FOR THIS CASE.**

The successor item **D12R2 published these gates first** (`curriculum_D12R2/RESULTS.md` @
`65882eb3`; `C-115`), **bit-exactly** — same `h_min`, same `δ_eff`, same mean `CD`, same window
count. This amendment and re-grade were therefore authored in knowledge of the answer, and
`PREREGISTRATION.md` §10.2 says so in those words. **What this re-grade may be claimed to buy is
narrow: the recovery of 63.95 core-min from WASTE, and a corroboration reading. Nothing wider.**

---

## 2. THE GATES

Comparator `d12x_grade.py` at **`f2e6cd48af3890a2c0a9e427d09c416a`** (blob `3659e32f`), verified
byte-identical to its committed HEAD blob before grading — rule 2's grading-path clause, executed.
Machine record: **`PHASE1_REGRADE_GATES.json`** (5,253 bytes), reproduced byte-identically on three
separate invocations.

| gate | verdict | numbers |
|---|---|---|
| **G12R-0** completion | **PASS** | 32 stages; **1 infrastructure note** (§3) |
| **G12R-W** where-control | **PASS** | 31 stages witnessed |
| **G12R-1** limit cycle | **PASS** | mean `CD = 0.6563231414421499`; 2400 samples; 253 sign changes; p2p `0.13162450`, **p2p_rel 20.05 %**; period **18.964427** steps |
| **G12R-2** `δ_repeat` | **PASS** | `0.0` over 3 identical runs. **Registered as the EXPECTED np=1 reading on a deterministic solver from a byte-identical field, and explicitly NOT a clearance for the FD step** |
| **G12R-3** `δ_window` | **PASS** | `1.7958478e-03`, rel `2.7359805e-03`; 2101 windows; `W/P = 15.8191`, **not degenerate** |
| **G12R-3b** `δ_pert` | **PASS** | `2.2796668e-06`, max over 4 components; one component reports 0.0, meaning **no floor was detectable at these steps — not the same claim as no floor** |
| **G12R-4** `δ_eff` | **PASS** | `1.7958478e-03`; dominant term **`δ_window`**; nothing excluded by name |
| **G12R-4** step sizing | **NOT A RESULT** | `h_min = 1.742838e-01` vs `h_max = 5.000e-02`; `\|g\| = 1.0304159`; `admissible: false`, `steps: []` |

**A PRE-COMPUTE PREDICTION OF THIS ITEM'S OWN FAILED, AND IS REPORTED AS FAILED.**
`PREREGISTRATION.md` §5 predicted `δ_window` **DEGENERATE** — a ~50-timestep shedding period would
make `W = 300` exactly 6.0 periods. The **measured** period is **18.9644** steps, giving
`W/P = 15.8191`, and `δ_window` is **live, not cancelled**. The gate tested the prediction rather
than confirming it, which is what registering it in advance was for.

---

## 3. THE INFRASTRUCTURE NOTE, QUOTED IN FULL

`G12R-0` returns `n_infrastructure_notes: 1`:

> `S1a: JSON status NOT MEASURED (INFRASTRUCTURE, L-342/R-RC) -- task='shell' invokes no run
> script and writes no per-stage JSON, so no status record exists to read. This is NOT a waiver of
> completion: the evidence is carried instead, and in full, by the rule-4 limbs rc, oomkilled,
> end_line_present, last_time_equals_endTime, coldstart_ok, age_guard, each of which refuses on its
> own below.`

**The six rule-4 limbs, re-derived from the artefacts by the lane and not taken from the manifest's
own summary fields** — `rc` cross-read against `ledger.txt`, the log limbs re-parsed from each
stage's own log, the age guard re-driven against each case's own `0/U`/`0/U.gz`:

| limb | result |
|---|---|
| `rc = 0` | **32 / 32** (two independent sources; `docker_exit` 0 and `oomkilled` false 32/32) |
| `End` line | **32 / 32** |
| last time == `endTime` | **32 / 32** |
| fields present at `endTime` | **32 / 32** (S1a 8; the other 31 carry 11 + `uniform`) |
| `ExecutionTime` count | **32 / 32** (`Time =` == registered steps on all 31 unsteady rows) |
| **age guard** | **32 / 32**, on a datum **6–100 s STRICTER** than the launcher's own recorded `AGE_DATUM` |

Exactly one row of 32 carries `status != "COMPLETE"`, and exactly one row of 32 carries
`task == "shell"`. **They are the same row.**

---

## 4. TWO FILES THIS RE-GRADE WROTE INTO THE PRESERVED RUN ROOT

Named so no later reader takes either for an original artefact of the 2026-08-25 solve:

| file | bytes | written | by |
|---|---|---|---|
| `step_plan.json` | 400 | 2026-08-27T18:51Z | the comparator's `--plan` mode |
| `PHASE1_REGRADE_GATES.json` | 5,253 | 2026-08-27T19:0xZ | the comparator's stdout on the same path |

**No existing artefact was modified** — verified by `find -newermt`. `step_plan.json` **cannot fire
anything**: `admissible: false, steps: []` means phase 2 takes its registered no-sweep branch.

---

## 5. A REPRODUCIBILITY DATUM, WITH ITS SCOPE AS LIMITS AND NOT AS A HEADLINE

D12R and D12R2 produced a **byte-equal 2400-sample `CD` series, 0 differing samples**. That is
equally consistent with two bit-deterministic solves and with copied output, so the copy hypothesis
was **refuted on positive evidence** rather than left unsupported
(`D12R_D12R2_REPRODUCIBILITY_EVIDENCE.txt`): **all 2400 `ExecutionTime`/`ClockTime` pairs differ**
(4,800 of 4,806 differing log lines; S2b 510.84 s vs 417.68 s); **32 of 33 stages differ in
`wall_s`** in their own ledgers (3,837 s vs 3,331 s); output field mtimes differ by ~4 h 40 m. The
single nanosecond-identical artefact across both roots is `S1a/0_orig/U` — **the staged INPUT**,
which is the condition of the test, not a confound.

> **SCOPE: n = 2, one case (2,450-cell 2D URANS cylinder), one host, one container image, `np = 1`.
> NOTHING IS ESTABLISHED AT `np > 1`, where MPI reduction order can vary — which is exactly where
> such a claim would matter most. It is not a claim about parallel runs, about other cases, or
> about this box's successors.**

Consequence for this item: `G12R-2`'s `δ_repeat = 0.0` is corroborated as a real property rather
than an artefact of the three repeats sharing state — and it does **not** weaken §2's registered
caution, because the noise that actually threatens a time-averaged objective on a limit cycle is
**phase noise**, measured by `G12R-3` at `1.7958e-03`, not zero.

---

## 6. STANDING CAVEATS — CARRIED IN FULL, NOT SUMMARISED

**A record that quotes this item and drops these is the failure they were registered to prevent.**

1. **`St` IS NEVER TO BE QUOTED AS A STROUHAL MEASUREMENT.** The measured period of **18.9644**
   timesteps gives `f ≈ 5.27 Hz` and **`St ≈ 0.527`, roughly 2.6× the accepted ≈0.2**. On a
   **2,450-cell 2D URANS mesh with wall functions** that is **far more likely a RESOLUTION ARTIFACT
   than a discovery**. The estimator is **mean-crossing**, which underestimates the fundamental on a
   harmonic signal, so the period is a **LOWER** bound and `St` an **UPPER** bound. It is a
   **window-sizing diagnostic and nothing else.** **No mesh-convergence study is bought here, so the
   artifact hypothesis is neither tested nor refuted** (`PREREGISTRATION.md` §2.1).
2. **Nothing about the physical accuracy of `CD`** at `Re_D = 1.0e6` on 2,450 cells.
3. **No grid family, so `CLAUDE.md` rule 5 has no row to gate and NO GCI IS QUOTED.**
4. **Nothing at `np > 1`**, nothing about `reduceIO: False`, nothing about forward-AD or
   complex-step as a reference, nothing about the endpoint gradient as a gate.
5. **The PATCHED row is UNBOUGHT** — `--image patched` was not run.
6. **Phase 2, 3 and 4 are not run and are not claimed.**

---

## 7. COST

**Phase 1 solve: predicted ~70 core-min (`PREREGISTRATION.md` §8); actual 63.95 core-min; ratio
0.914** (`ledger.txt`, `PHASE1_COMPLETE spent=63.95 core-min`), against `CAP_CORE_MIN = 600.0` —
**no overrun, no cap moved.**

**The re-grade itself: 0.00497 core-min** — 0.298 wall s at 1 rank, measured. The amendment, the
planted-failure proof and this record cost **no solver compute**; nothing was re-run.

**`C-107`'s `WASTE = 63.95 core-min` is STRUCK** by the calibration row for this record, because the
compute did not produce nothing — it produced the measurement, and a grader defect hid it for
30 hours. **The defect's real price is a different number: the lab bought this one measurement
TWICE, and the second purchase is D12R2's 55.5167 core-min.** That duplicate is **not** re-booked as
waste: it was correctly bought under the then-standing *"RE-REGISTER. NOT REPAIR, NOT PATCH."*
ruling, and a spend legitimately incurred under a then-correct ruling is not retroactively waste.

**cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED**
(`COMPUTE_BUDGET_CHARTER.md` §5 — the box cannot read its own billing). Dollar figures derived on
that basis are **DERIVED, NOT MEASURED**.

---

## 8. THE RECORD TRAIL

| what | where |
|---|---|
| pre-registration v1.1, amendment §10 | `PREREGISTRATION.md` @ `9517a39f` |
| the struck 2026-08-26 refusal, unedited | `PHASE1_GRADE_REFUSAL.md` @ `9d26801e`, `60e838aa` |
| comparator + 545-line delta | `d12x_grade.py`, `d12x_grade_DELTAS_amendment1.diff` @ `9517a39f` |
| planted-failure proof, both flags | `d12x_grade_amendment1_proof_evidence.txt` @ `9517a39f`, `76846c1e` |
| the machine gate record | `PHASE1_REGRADE_GATES.json` @ `76846c1e` |
| the re-solve evidence | `D12R_D12R2_REPRODUCIBILITY_EVIDENCE.txt` @ `76846c1e` |
| the outbound-connection incident | `INCIDENT_OUTBOUND_GIT_FETCH_2026-08-27.md` |
| authority | `L-342`; `R-RC` (`etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md` §0); `docs/L342_GRADER_AUDIT.md` Addendum 2 @ `7547e8f8` |

---

## 9. CLOSURE OF THE PHASE-2 BRANCH — 2026-09-04. THE REGISTERED `G12R-4` CONTINGENCY WAS EXECUTED AND WITNESSED, PHASES 3 AND 4 ARE DEMONSTRATED UNREACHABLE ON `W = 300`, AND NO FOURTH WINDOW WAS PROBED HERE

**This section closes bookkeeping, not physics.** It adds no new physical measurement about the
cylinder, the adjoint or the gradient. What it adds is that the `G12R-4` no-admissible-step branch
— registered in advance at `PREREGISTRATION.md` §2.2 as *"a GENUINE FINDING ABOUT THE METHOD–CASE
PAIR, NOT A FAILURE OF EITHER"* — has now actually been **fired through the frozen launcher and the
frozen comparator, on disk, and witnessed**, rather than merely inferred from phase 1's gate record.
**A successor skimming the D12 family must not count a fourth window probe here. There was none.**

### 9.1 THE VERDICT

> **`NOT A RESULT` on the registered `G12R-4` branch.** The verdict is the dafoam supervisor's.
> It is the same branch `W3` landed on, reached here **without a fourth window being probed**.

The frozen comparator's own words, from `PHASE1_REGRADE_GATES.json` and reproduced by this run's
`step_plan.json` (md5 `f24aeda37e9fe7f802ea105d086dfc04`, pinned into `ledger.txt` by the launcher
before it refused):

`h_min 1.742838e-01 EXCEEDS h_max 5.000e-02` — **over by a factor of 3.4856758**, which is exactly
`h_min / h_max`.

Stated as the condition on the gradient rather than on the step, because that is the form a reader
can act on: with `EPS_NOISE_TARGET = 0.01` and `H_MAX = 0.05`, admissibility requires

`|g| >= delta_eff / (0.01 * h_max) = 0.0017958478225974517 / 0.0005 = 3.5916956451949034`

against a **measured `|g| = 1.0304158599180422`**. The shortfall is 3.4856758×.

### 9.2 WHAT WAS RUN, AND THE THREE PREDICTIONS SCORED AGAINST IT

Both commands were registered in writing by the supervisor **before** this lane ran them, together
with three falsifiable predictions. Nothing else was run. **`--plan3` was NOT fired**: it was
established unreachable, and firing an unreachable step to watch it fail is the re-firing habit this
closure exists to end.

| # | prediction, registered before the run | measured outcome | scored |
|---|---|---|---|
| 1 | phase 2 → `rc = 0` | `rc = 0` | **HIT** |
| 2 | phase 2 → two `NO ADMISSIBLE FD STEP` lines | **one line, written to two sinks** — `d12x_stage_and_run.sh:732` is a single `tee -a`, so the string appears once on stdout and once in `ledger.txt`, two occurrences in total. The refusal *block* is two lines (`:732` + `:733`, the second being `Phase 2 is NOT LAUNCHED. That is a RESULT, not a failure`), and both appeared. | **HIT under the two-sink and two-line-block readings; MISS under a two-distinct-stdout-lines reading, which is impossible by construction of the frozen launcher.** Recorded as an ambiguity in the prediction's wording, not as a discrepancy in the artefact. |
| 3 | phase 2 → zero `S6*` directories created | **zero `S6*` directories — and in fact zero new top-level entries of any kind** under the run root, `before`/`after` listings differenced | **HIT** |
| 4 | `--plan2` → `rc = 2` and `REFUSAL: G12R-5: only 0 usable sweep steps on disk` | `rc = 2`; stderr carries `REFUSAL: G12R-5: only 0 usable sweep steps on disk; a plateau needs at least 3 and one step is never a plateau` | **HIT** |

`step_plan2.json` was **not written** — checked under the planted control of §9.3.

### 9.3 THE PLANTED CONTROLS, BECAUSE EVERY ZERO HERE IS LOAD-BEARING

Three zeros are claimed above. None is reported from a reader that was not first shown finding a
non-zero (`CLAUDE.md` rule 3).

| claimed zero | reader | known-positive the SAME reader found | result |
|---|---|---|---|
| 0 `S6*` directories | `find <root> -maxdepth 1 -mindepth 1 -type d -name '<pat>'` | **16 `S3b*` directories**, and 3 `S3_r*` | reader proved non-blind |
| 0 `step_plan2.json`, 0 `step_plan3.json` | `find /home/ubuntu/certonomous-runs -maxdepth 3 -name '<pat>'` | **6 `step_plan.json`**, in six sibling run roots | reader proved non-blind |
| `W_CONTINGENCY` never executed | `grep -nw '<name>' d12x_grade.py` | **`W_PRIMARY` at 4 sites** incl. two live call sites (`:1777`, `:2307`); **`H_MAX` at 7** | reader proved non-blind |

**A MISCOUNT IN THE BRIEF, CORRECTED HERE RATHER THAN INHERITED.** The control was specified to this
lane as *"the 48 `S3b*` directories that do exist"*. **There are 16 `S3b*` directories.** 48 is the
count of `S3b*`-prefixed **top-level entries** — 16 directories plus 16 `.log` files plus 16 `.ok`
markers. The frozen pre-registration settles it independently: §3's stage table registers **`S3b` as
`16 × 300`** — 2 probe steps a decade apart × 4 components × 2 signs. **This is exactly the class of
error the control exists to catch, and it was in the control's own constant.**

### 9.4 THE `W` CLAIM IS CORRECTED. A WIDER WINDOW *DOES* HELP — MEASURED — AND IT HAS NOT HELPED ENOUGH

This lane was asked to confirm that *"`W` is absent from this item's condition and no window could
help it."* **The first half is true only in a trivial sense and the second half is refuted by
measurement on this box.** The correction is recorded because a successor acting on the uncorrected
sentence would wrongly believe the window axis is closed.

**Why `W` is in the condition.** `delta_eff := max(delta_repeat, delta_window, delta_pert)`
(`d12x_grade.py:633`). Here `delta_repeat = 0.0`, `delta_pert = 2.279666841643725e-06`, and
`delta_window = 0.0017958478225974517` — **`delta_eff` IS `delta_window`, to every printed digit**,
and `delta_window` is by construction a function of `W` (`g3_delta_window`, `:579`). The registered
window is `W = 300` timesteps = **15.8191 shedding periods**, 2101 sliding blocks over the 2400-sample
retained series, `degenerate: false`.

**What the sibling probes measured.** Five `step_plan.json` files exist across the D12 family's run
roots, all `admissible: false`, all with `dominant_term: delta_window`:

| run root | `W` | `delta_window` | `\|g\|` | `h_min` | over `h_max` |
|---|---|---|---|---|---|
| `CURRICULUM-D12R-cylinder-unsteady` (this item) | 300 | 1.7958478e-03 | 1.0304159 | 0.17428379 | **3.4856758×** |
| `CURRICULUM-D12R2-cylinder-unsteady` | 300 | 1.7958478e-03 | 1.0304159 | 0.17428379 | 3.4856758× |
| `CURRICULUM-D12RLX-armC-repro` | 300 | 1.7958478e-03 | 1.0304159 | 0.17428379 | 3.4856758× |
| `CURRICULUM-D12R2W2R-cylinder-unsteady` | 300 | 1.7958478e-03 | 1.1398353 | 0.15755328 | 3.1510656× |
| `CURRICULUM-D12R2W3-cylinder-unsteady` | **2000** | **4.4535e-04** | **0.4883598** | **0.09119302** | **1.8238604×** |
| `CURRICULUM-D12RLX-armR-repaired` | — | 7.8522913e-04 | 0.8531404 | 0.09203984 | 1.8407969× |

**THE MECHANISM, AND IT IS THE REASON THE HONEST ANSWER IS NOT "NO WINDOW COULD HELP".** Going from
`W = 300` to `W = 2000` — a 6.6667× wider window, 105.46 shedding periods against 15.82 —
**cut `delta_window` by 4.0325×**. It also **cut `|g|` by 2.1100×**, because widening the averaging
window changes the objective and damps the mean's own sensitivity to the shape DV. `h_min` is their
ratio, so the two movements partially cancel and the net gain is **1.9112×** (4.0325 / 2.1100 =
1.9111). **The window axis is real, it moves `h_min` in the right direction, and after the widest
probe on this box it is still 1.8239× short of `h_max`.**

**What that does NOT license.** Fitting `h_min ∝ W^-p` to the single measured pair gives
`p = 0.3414`, and closing the residual 1.8239× would need a further **5.81× in `W`, i.e. `W ≈ 11,600`
timesteps**. **That extrapolation is ONE PAIR AND IS NOT A MEASUREMENT** — the exponent is
contaminated by the `|sin(pi * frac(W/P))|` term the sliding-block spread carries, which differs
between the two probes (0.1809 vs 0.4574 fractional offset), and no third `W` exists to test it. It is
recorded as an unmeasured estimate so a successor does not re-derive it, and it is quoted for one
purpose only: **`W ≈ 11,600` is roughly 4.8× the entire 2,400-sample retained series that exists**, so
the window that might close this gap cannot be evaluated on the data on disk at all. It would need a
new `S2b` series and a re-run of the whole `S3` / `S3b` / `S5` chain at the new `W`. **That is a new
item, not a repair of this one, and this lane did not buy it.**

**Also recorded: these six roots are NOT a controlled single-variable `W` study.** `D12R2W2R` carries
the *same* `delta_window` at a *different* `|g|`, so more than the window differs between siblings.
Only `D12R2W3`'s manifest names `W` (`W: 2000`) explicitly. The table above is a family comparison,
not a sweep, and must not be quoted as one.

### 9.5 A REGISTERED CONTINGENCY THAT IS DECLARED AND NEVER EXECUTED — REPORTED, NOT REPAIRED

`PREREGISTRATION.md` §7 registers **`W2 = 900` contingency** among this item's frozen constants, and
Amendment 1 §10.3 lists **`W_CONTINGENCY = 900`** among the values it explicitly leaves unmoved. The
frozen comparator declares it at `d12x_grade.py:37` with its own comment:

`W_CONTINGENCY      = 900        # timesteps, fires only on the G12R-4 branch`

**The `G12R-4` branch is the branch that just fired.** `W_CONTINGENCY` appears at exactly **two** sites
in the comparator — its definition (`:37`) and an echo into `out["registered"]` (`:2296`). It is never
passed to `g3_delta_window` and never sizes anything. The frozen launcher has **no `W2` stage at all**:
`W_STEPS=300` is hard-coded at `d12x_stage_and_run.sh:110`, and the only `900` in that file is a
`timeout 900` on the mesh stage. **The registered contingency is declared, echoed, and dead.**

**This is disclosed, not fixed.** Both instruments are frozen by md5 at the pre-registration commit
and standing rule 6 forbids editing them; the `INSTRUMENT_VERIFIED` lines this run printed
(`d12x_grade.py` md5 `f2e6cd48af3890a2c0a9e427d09c416a`, `d12x_run_script.py` md5
`2790c39a09cd458d5a3263d7f1811da5`) are the proof the files that ran are the files that were frozen.
**The consequence for a successor is the point: this item's terminus is `NOT A RESULT` at `W = 300`,
and the registered escape hatch at `W = 900` was never available on these instruments. §9.4's measured
family evidence is what stands in its place, and it points the same way — a wider window helps and
does not close the gap.**

### 9.6 WHAT THIS CLOSES, AND THE ONE HOLD IT DOES NOT RELEASE

**Phases 3 and 4 are now demonstrated unreachable on `W = 300`, not merely un-fired.** Both stood at
`rc = 1` having aborted at zero compute (`STATUS.D12R_phase3` `rc=1 end=2026-08-26T16:10:17Z`,
`STATUS.D12R_phase4` `rc=1 end=2026-08-26T16:11:22Z`, and again
`STATUS.queue.D12R_phase3` `launcher_rc=1 end=2026-09-03T17:26:48Z`). Phase 3 aborts on a missing
`step_plan2.json`; `--plan2` has now **refused** on 0 usable sweep steps, and it refused because phase
2 correctly launched none. **`step_plan2.json` can therefore never exist on this window**, so phase 3
can never start and phase 4's precondition `step_plan3.json` can never be produced. That is a chain of
demonstrated unreachability, and it replaces three repeated `rc=1` aborts.

> **`verification/queue/dafoam/held/D12R_phase4.json` IS NOT RELEASED BY THIS SECTION AND MUST NOT BE
> RELEASED ON A GLANCE.** Its dependency **survives**: `step_plan3.json` does not exist anywhere under
> `/home/ubuntu/certonomous-runs` (searched to depth 3 under the §9.3 control). **But its stated
> `hold_reason` is now FALSE** — it reads *"Phase 3 is being launched now and PRODUCES that file.
> RELEASE CONDITION, checkable in one command: `step_plan3.json` present and phase 3 complete."*
> **Phase 3 will never complete on this window.** The hold is therefore **not stale — it is
> permanent on `W = 300`** — while the reason printed on its face is stale. A reader who checks only
> whether the reason still reads true will draw the wrong conclusion in the wrong direction.

### 9.7 COST — AND WHETHER THIS SPEND IS WASTE

**MEASURED: 0.016105 core-min gross**, at `np = 1`. Phase 2 wall **0.9194 s**; `--plan2` wall
**0.0469 s**; total **0.9663 s** × 1 rank ÷ 60. **Gross equals cleaned**: neither invocation reaches
0.03 % of the 3600-wall-s stall rule of `COMPUTE_BUDGET_CHARTER.md` §2, nothing was restarted and
nothing was discarded. Against the supervisor's written authorisation of **≤ 1.5 core-min**, this is
**1.074 % of the ceiling**; no overrun, no cap moved.

**Dollars: $0.0000138, DERIVED, NOT MEASURED**, at c7a.4xlarge $0.0513/core-h, reported-by-owner —
the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**Ratio against the registered phase-2 estimate: 0.00124.** The registered denominator is
**~13.0 core-min**, the same figure `verification/queue/dafoam/launched/D12R_phase3.json` carries and
derived the same way — 10 window-length stages at this item's own measured phase-1 mean of
**1.2984 core-min per 300-step stage** (`ledger.txt`). **The denominator is not adjusted to flatter the
ratio.** But the ratio must not be averaged into the lab's rate-estimation record: **the gap is not a
misprediction of a rate, it is a REGISTERED BRANCH.** The 13.0 prices the sweep that fires when
`admissible: true`; `admissible` was `false`, so the launcher's own guard refused before any
`docker run`. **Attribution: 100 % registered-branch selection, 0 % contention, 0 % rate error,
0 % waste.**

**IS IT WASTE? ARGUED BOTH WAYS, THEN DECIDED.**

*For waste.* `COMPUTE_BUDGET_CHARTER.md` §6's test is an **outcome** test — solver cost that bought
nothing. This spend produced no field, no directory, no new number: §9.2 line 3 records literally zero
new top-level entries. On a strict reading, compute was consumed and no physics came back.

*Against waste.* Three things, and the first is decisive. **(i) No solver cost was incurred at all.**
§6's test names *solver* cost; the launcher refused at `:731` before reaching any `docker run`, so the
0.016 core-min is interpreter and shell time, not solve time. There is no solver row to call wasted.
**(ii) It bought a state transition the record needed.** Before, the item's terminus on `W = 300` was
an inference from phase 1's gate record; after, the registered `G12R-4` refusal is executed and
witnessed on disk, with the plan pinned by md5 into `ledger.txt`, and phases 3 and 4 move from
*un-fired* to *demonstrated unreachable* (§9.6). `PREREGISTRATION.md` §2.2 registered exactly this as
**a RESULT**. **(iii) The finding survives the contingency.** Even if a future item widens `W` and
finds an admissible step, this refusal at `W = 300` is the measurement that would trigger it, not a
purchase superseded by it.

> **DECIDED: NOT WASTE. `WASTE = 0.0000 core-min`**, on ground (i) — zero solver cost — with (ii) and
> (iii) as corroboration rather than as the argument. **The decision is recorded as this lane's, and
> the contrary reading is left standing above rather than deleted**, because a reader who applies §6's
> outcome test literally will reach "waste" and is entitled to see why this record does not.

### 9.8 WHAT THIS SECTION DOES NOT ESTABLISH

1. **No new physics.** Every §6 standing caveat carries forward unchanged and unsummarised.
   `St` is still never to be quoted as a Strouhal measurement; no grid family, so no GCI; nothing at
   `np > 1`; the **PATCHED row is still UNBOUGHT**, so no D12R number is a toolchain-independent
   statement (`DAFOAM_CHARTER.md` §6).
2. **`--plan3` was not run and is not claimed** in either direction.
3. **The `W ≈ 11,600` extrapolation of §9.4 is an unmeasured estimate from one pair**, not a result,
   and no successor may cite it as one.
4. **This lane discharged none of the four `SUPERVISION_CHARTER.md` §3 checks and claims none.**
   Check 4 — pre-registration committed before compute, `prereg_commit`
   `f9c8b9c840ea80f88c619e06801da96c7f42c266`, committed 2026-08-25T22:44:53Z with phase 1 starting
   12 s later — was discharged **personally by the dafoam supervisor** and is recorded here as theirs.
5. **Whether the `W2 = 900` dead constant of §9.5 is a defect worth a successor item is the
   supervisor's call, not this lane's.** It is reported, not repaired, and no instrument was edited.
