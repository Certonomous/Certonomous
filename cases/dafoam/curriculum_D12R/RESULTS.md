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
