# D12R2-W3 — PHASE 1 COMPLETE AND GRADED AT `W = 2,000`: `NOT A RESULT`, AND THE FALSIFIER FIRED THROUGH THE **GRADIENT**, NOT THROUGH WINDOW NOISE. THE REGISTERED `W = 2,400` FALLBACK DOES NOT RESCUE THE ITEM, AND THE MEASURED RECORD SAYS LENGTHENING THE WINDOW MADE ADMISSIBILITY **WORSE**

**Written 2026-09-04 by a dafoam `lab-lane` for `dafoam-supervisor`, `[lab-attributed]`.**
Item `D12R2-W3`, case directory `cases/dafoam/curriculum_D12R2`, run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady`.
Pre-registration `W3_PREREGISTRATION.md` **v1.0 FROZEN 2026-08-26**, plus Amendment 1 (v1.1),
Amendment 2 (v1.2), Amendment 3 (v1.3) — all **PRE-COMPUTE** — and **Addendum 1 (v1.4,
POST-COMPUTE)**, which is the registration that governs the fire graded here.
Queue entry `verification/queue/dafoam/launched/W3_chain.json`, `prereg_commit`
**`5ce4566260f2048e445e4f368373d4bbd37c4f5d`**.

**Nothing in this item is filed, sent, uploaded, registered, posted or commented outside this
box** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS REMAIN PARKED.**

---

## 1. THE HEADLINE — the registered branch fired, and the mechanism is not the one that was registered

> **ITEM VERDICT: `NOT A RESULT`.** `G12R-4` step sizing returns
> **`h_min = 9.119302e-02` against the registered `h_max = 5.000e-02`** — no admissible FD step
> exists at `W = 2,000`. `step_plan.json` reads `admissible: false`, `steps: []`. Phase 2
> **LAUNCHED NOTHING** on the launcher's registered no-launch branch; the driver stopped at
> `--plan2`'s Refusal, which `W3_PREREGISTRATION.md:80` registers as **the registered terminus**,
> never a driver failure. Verdict mapping `:101`: *"P3 MISS (`admissible: false` at 2,000) |
> **`NOT A RESULT`** — the registered no-launch branch; phases 2–4 never fire"*.

**And this is the part that matters.** The registration predicted the falsifier would be a
**window-noise** problem — that `δ_window` would not fall fast enough with `W`. **It did fall
exactly as predicted.** `P1` is a **HIT** to every printed digit and the `1/W` envelope law held.
The item was falsified on the **other** factor: the adjoint gradient `|g(2000)| = 0.48836`
collapsed to **2.33× below** the value the freeze carried forward from `W = 900`, and
`h_min = 100·δ_eff/|g|` is inversely proportional to it. §3 and §4 below.

**The grid cell does not move** (`:101`): 2D · unsteady · incompressible stays
`gradients: CAN DO, CAVEATS — no admissible FD step` / `optimisation: CAN NOT DO`.

---

## 2. THE GRADING PATH — THE HASH FIRST (rule 2), AND THE `f3c1252c` / `3950d30f` QUESTION RESOLVED

**The two md5 strings in circulation are the SAME FILE AT TWO DIFFERENT VERSIONS OF THE
REGISTRATION, and the one that governs is `3950d30f…`.** Stated plainly because a grading-path
question is load-bearing and the supervisor asked for it to be resolved rather than assumed:

| where the string appears | md5 | status |
|---|---|---|
| `W3_PREREGISTRATION.md:109` (§8, **Version 1.0**) and `:131` (Amendment 1, asserting *"the comparator is UNTOUCHED … md5 `f3c1252c…` on disk and at HEAD"*) | `f3c1252c11fb94a3d4c580fdcbe7a62d` | **SUPERSEDED.** True of v1.0 and v1.1. Amendment 1 did not change the comparator, which is exactly why it restates the v1.0 hash. |
| `W3_PREREGISTRATION.md:294` (**Amendment 2**, §12.6, v1.2) | `3b0a75079c932b41ec19477388498842` | **SUPERSEDED.** The R-RC branch, the R-RC-4 fatal limb, the infrastructure channel and the `W3-A2` ledger split. |
| `W3_PREREGISTRATION.md:408` (**Amendment 3**, §13.6, v1.3) | **`3950d30fd09c9b56213a02f5e9864e20`** | **THE GOVERNING PIN.** `W3-GRADER-DEF-2`: the `sorted(cands)[-1]` S2b selection replaced by a `len(cands) != 1` uniqueness Refusal. |
| `W3_PREREGISTRATION.md:582` (**Addendum 1**, §14.7, v1.4) | `3950d30f…`, row reads **unchanged** | Confirms Addendum 1 does not touch the grading path. |

**`:131` is not a competing registration of the hash; it is Amendment 1 recording that it did
not move the hash.** Amendments 2 and 3 — both **pre-compute**, both with the §2b condition
driven, not asserted — moved it twice. Every one of those moves is disclosed in the frozen
document at the foot, with `lines whose number changed above this section: 0` proved on bytes.

**FIVE INDEPENDENT READINGS AGREE, and they are the whole of the rule-2 check:**

1. **On disk now**: `md5sum cases/dafoam/curriculum_D12R2/d12y_grade_w3.py` = `3950d30fd09c9b56213a02f5e9864e20`.
2. **The committed HEAD blob**: `git show HEAD:cases/dafoam/curriculum_D12R2/d12y_grade_w3.py | md5sum` = the **same** string. The file that ran **is** the file that is committed.
3. **The run's own witness**: `W3_phase1.out:2` and `W3_phase2.out:2` both carry
   `INSTRUMENT_VERIFIED cases/dafoam/curriculum_D12R2/d12y_grade_w3.py md5=3950d30fd09c9b56213a02f5e9864e20`,
   written by the launcher's `A3` check **against the committed HEAD blob before staging**.
4. **The driver's pin**: `d12y_w3_chain_driver.sh:47` reads `MD5_GRADER=3950d30fd09c9b56213a02f5e9864e20`, asserted before every step. That guard has been shown able to fire: the `2026-08-28T02:15:29Z` launch died `rc=4 reason=grader_md5_drifted` at zero core-minutes on a stale pin (§13.5).
5. **The queue entry**: `launched/W3_chain.json` `instrument_md5s_at_this_commit` names `3950d30f…` as *"THE GRADING PATH, UNTOUCHED by W3 ADDENDUM 1"*.

The launcher (`8a92f3f84f72d6806a2e5c5df88d82ef`) and the driver
(`2b6ac7bbc6a5593940a0f2d217005b10`) likewise match their §14.7 pins and their HEAD blobs
byte for byte. **The grading path is the frozen path. Nothing here is graded on a drifted
instrument.**

---

## 3. THE CHAIN, STEP BY STEP — AND IT IS NOT RUNNING

`STATUS.W3_chain` (case directory), lines 2–12. Confirmed independently: **no `d12y_`
process exists** (`ps -eo pid,etime,args` returns nothing matching), and **every `d12y_w3_`
container is `Exited (0)`** (`docker ps -a`), the most recent 8 h before this reading.

| step | rc | evidence |
|---|---|---|
| `START` / `BEGIN phase1` | — | `2026-09-03T17:22:42Z`, pid 179658, sid 179657 |
| `phase1` | **0** | `END` at **`2026-09-03T21:57:49Z`**, `W3_phase1.out` — 33 of 33 registered stages, `SPENT_CORE_MIN=271.2501 of cap 900.0`, `PHASE1_COMPLETE spent=271.2501 core-min` |
| `plan` | **0** | `W3_plan.out` (5,775 bytes), the full gate JSON; wrote `step_plan.json`, launcher-read md5 `707e3247e62c46c21c5805249ed9afff` |
| `phase2` | **0** | `W3_phase2.out` — **`NO ADMISSIBLE FD STEP AT THIS WINDOW -- the comparator's registered G12R-4 branch fired. Phase 2 is NOT LAUNCHED. That is a RESULT, not a failure`**. Zero containers started. |
| `plan2` | **2** | `W3_plan2.out`, one line: `REFUSAL: G12R-5: only 0 usable sweep steps on disk; a plateau needs at least 3 and one step is never a plateau` |
| chain | `STOPPED_AT_FIRST_NONZERO rc=2` | driver's own note: `a-stop-at-a-registered-no-launch-branch-is-the-registered-terminus` |

**The supervisor's reading of the chain is correct in every particular** — phase-1 rc and
spend, the `step_plan` values, the phase-2 no-launch, the `plan2` refusal text and its status
under `:80`. Two things are added below that the brief did not carry: **`P2` and `P4` are also
gradeable, and both are MISSES** (§4), and **`P4`'s miss is what pays for the physics** (§6).

`STATUS.W3_chain` line 1 (`launcher_rc=2 end=2026-08-31T00:15:22Z`) belongs to the **prior**
`2026-08-30T23:10:12Z` fire, already priced by `docs/COST_CALIBRATION.md` **`C-222`** and
diagnosed in `DEFECT_NOTE_W3_GRADER_DEF_3.md`. It is not this fire and nothing here rests on it.

### 3a. THE GATE TABLE — verbatim from `W3_plan.out`

| gate | verdict | reading |
|---|---|---|
| `G12R-0b` manifest ↔ ledger binding | **PASS** | `n_rows 33`, `n_ledger_stage_lines 33`, `registered 33` |
| `G12R-0` completion (rule 4) | **PASS** | 33 stages; `rc_note: "every stage carried a MEASURED rc"`; **1 infrastructure defect** — `S0: fatal/signal log scan NOT MEASURED (fatal_tokens=None); rc was MEASURED = 0, so R-RC-4's fence is not load-bearing on this row.` That is Amendment 2 leg `R12`'s registered behaviour, not a departure. |
| `G12R-W` where-control | **PASS** | 31 stages witnessed |
| `G12R-1` limit cycle | **PASS** | 2,400 samples, `mean 0.6563231414421499`, `p2p_rel 0.2005483140637519`, `period_steps 18.964426877470355`, 253 sign changes |
| `G12R-3` `δ_window` | **PASS** | `delta_window_exact 4.3857102184485797e-04`, `delta_window_envelope 4.4535e-04`, **used 4.4535e-04**; 401 windows; `degenerate: false`; `periods_per_window 105.46060858691122` |
| `G12R-2` `δ_repeat` | **PASS** | **`0.0`** over `S3_r1/r2/r3`, all three `0.6561057342918396` — bit-deterministic at np=1. See §5 on why this zero is not a blind reader. |
| `G12R-3b` `δ_pert` | **PASS** | `1.660120842239543e-06` (max over 4 components); components 0 and 3 report `delta_pert 0.0` with `detectable: false` |
| `G12R-4` `δ_eff` | **PASS** | `4.4535e-04`, `dominant_term: delta_window`, `excluded_by_name: []`, `window_degenerate: false` |
| **`G12R-4` step sizing** | **`NOT A RESULT`** | **`h_min 9.119302e-02` vs `h_max 5.000e-02`; `g_component 0.48835975139977306`; `steps: []`** |

`G12R-5`…`G12R-11` are phase 2–4 gates and **were never reached** — registered, `:101`.
**No grid family exists here (2,450 cells, one mesh), so standing rule 5 has no row and NO GCI
IS QUOTED.** `St ≈ 0.53` remains a resolution artefact and is never quoted as a Strouhal number.

### 3b. RULE 4, CLAUSE BY CLAUSE, RE-READ FROM THE MANIFEST BY THIS LANE

`G12R-0` is the frozen authority; this is an independent read of the same 33 rows, and it agrees.

| clause | reading over all 33 rows |
|---|---|
| `rc = 0` | 33/33 carry an `rc` key; `docker_exit = 0` on 33/33 |
| `End` line | `end_line_present = True` on 33/33 |
| last time == `endTime` | equal on every row that carries them (`500.0/500.0`, `20.0/20.0` ×22, `10.0`, `3.0`, `24.0`, `0.2` ×2, `0.4` ×2, `0.8` ×2; `S0` is the mesh stage and carries neither) |
| **age guard** | `age_guard_ok = True` on **33/33** |
| cold start | `coldstart_ok = True` on 33/33 (the warm-start trap, `DAFOAM_CHARTER.md` §6) |
| OOM | `oomkilled = false` on 33/33 |
| `ExecutionTime` count == registered steps | **9 rows differ** (`S1a` 7/500, `S4_*` 25/20, 45/40, 85/80, `S5` 2100/2000). This is the **INFRASTRUCTURE** limb Amendment 2 §12.2 split off; the **PHYSICS** limb `time_line_count` matches `expected_steps` exactly on every one of those rows (20/20, 40/40, 80/80, 2000/2000), which is the limb that still refuses (unit `R14`). |

**Independent cost cross-check:** the 33 manifest rows' own `core_min` fields sum to
**271.2501**, identical to the ledger's `PHASE1_COMPLETE spent=271.2501`. Two artefacts, one
figure.

---

## 4. PREDICTIONS `P1`–`P5`, SCORED AGAINST THE FROZEN §6 — HIT / MISS, NEVER ADJUSTED

| # | prediction (frozen, `W3_PREREGISTRATION.md:88-92`) | measured | score |
|---|---|---|---|
| **P1** | `delta_window_exact = 4.385710e-04` **to the printed digits** in `step_plan.json` | **`4.3857102184485797e-04`** → `4.385710e-04` at six significant figures | **HIT** |
| **P2** | `\|g(2000)\|` in **`[1.01, 1.37]`** | **`0.48835975139977306`** | **MISS**, low. **2.07× below the band's lower edge.** |
| **P3 (PRIMARY, BINARY)** | an admissible FD step EXISTS at `W = 2,000`; *"falsified iff `\|g(2000)\| < 0.8907`"* | `admissible: false`; `h_min 0.0911930188193242 > h_max 0.05`; `\|g\| = 0.48836 < 0.8907` | **MISS** — the registered falsifier fired **exactly on its registered condition** |
| **P4** | phase-1 cost **`196.4 ± 15 %` core-min `[167, 226]`** from the ledger's `PHASE1_COMPLETE spent=` | **`271.2501`** core-min, gross, from that exact line | **MISS**, high. Ratio **1.381**. §6. |
| **P5** | conditional on P3 HIT and `G12R-6 PASS` | **NOT REACHED** — P3 MISSED, so the condition never arose | **NOT SCORED**, by the prediction's own terms |

**P1 is the one that matters for the physics, and it is a HIT.** The `1/W` envelope law
registered in §2 — measured off the series at 92 windows with a residual ≤ 0.3 % at the local
maxima, slope **−1.003** on the envelope against **−0.5** for the statistical hypothesis —
reproduced on this run's own 2,400-sample S2b series to every printed digit. `exact/envelope
= 0.98478`, i.e. `W = 2,000` sits at **98.5 % of the envelope**, `105.4606` periods per window
and `degenerate: false`. **The window was not chosen on a baseline minimum**, which is what
W3-A1 was written to prevent, and the exact and envelope readings agreeing to 1.5 % is the
measured proof that it was not.

---

## 5. THE PLANTED-ZERO POSITION, STATED HONESTLY — WHAT FIRED, WHAT DID NOT, AND WHY THE VERDICT SURVIVES IT

`CLAUDE.md` rule 3: **a zero from a reader not shown able to see a non-zero is not evidence.**
Three separate things are true here and they are kept apart.

**(a) TWO LIVE PLANTED CONTROLS FIRED IN THIS RUN, on this run's own bytes.**

- `W3_phase1.out:4` — `INSTRUMENT_ENUMERATION_PLANT_OK saw d12y_run_script.py`: the instrument
  enumerator is shown able to see an instrument before its enumeration is trusted.
- `W3_phase1.out:36` — `COMPLETENESS_PLANT_OK the check found U_0 betaFINuTilda fvSource meshPhi
  nuTilda_0 nut p_0 missing from the intermediate write 0.01 -- it can say NO`: the `FIELD_B`
  completeness reader is shown **reporting a negative** before its positive is believed.

**(b) `G12R-9`, THE REGISTERED PLANTED-ZERO GATE, WAS NOT EVALUATED ON THIS RUN. STATED
PLAINLY RATHER THAN GLOSSED.** `plan()` (`d12y_grade_w3.py:2391-2562`) calls `G12R-0b`,
`G12R-0`, `G12R-W`, `G12R-1`, `G12R-3`, `G12R-2`, `G12R-3b` and `G12R-4` twice. **It does not
call `g9_plant` (`:1028`)**, which belongs to the grade path the chain never reached.
`grep G12R-9` over every `W3_*.out` returns **zero hits**. The gate's own planted-failure legs
(`U-12`, `U-12b`, `U-12c`, and the series reader's `U-02c`) were driven **at freeze time**,
82/82 under `python3` and `python3 -O`, and **neither the driver nor the launcher re-runs
`--selftest` on a fire** — checked, not assumed (`grep selftest` over both scripts returns
nothing).

**(c) THE PLANT'S RAW MATERIAL IS ON DISK AND IS NON-ZERO, and this lane computed the read-back
by hand — labelled as this lane's derivation, NOT as the gate's verdict.** `S7_plant` ran with
`registered_dvIndex 0`, `registered_dvDelta 0.001234` (= the frozen `PLANT_SHAPE = 1.234e-03`)
and `obj_from_log 0.6576249340268902`; `S7_clean` ran with `registered_dvDelta 0.0` and
`obj_from_log 0.6561057342918396`. The relative response is **`2.3154800448288693e-03`**,
which is **six orders above** the frozen `PLANT_FLOOR_REL = 1.0e-9` at which `g9_plant` refuses.
**The objective is demonstrably not blind to a planted shape perturbation on this run's own
bytes.** That is a corroboration; it is **not** the registered gate, and it is not recorded as
one.

**(d) WHY THE VERDICT DOES NOT DEPEND ON (b) — the direction argument, which is the only
honest defence and is stated as such.** A blind reader's failure mode here is a **false zero**
in `δ_window`, `δ_repeat` or `δ_pert`. Every one of those failures drives `δ_eff` **down**,
`h_min` **down**, and `admissible` toward **`true`** — i.e. toward the favourable outcome and
toward launching phase 2. The measured `δ_eff = 4.4535e-04` is **non-zero**, is the term the
grader names `dominant`, and produced `h_min` **1.82× ABOVE** `h_max`, i.e. the **conservative**
outcome. **A reader blindness of the class rule 3 guards against could not have produced this
verdict; it could only have hidden it.** This is why the item is graded rather than refused —
and the gap is recorded so an auditor does not have to re-derive it.

**(e) THE TWO ZEROS INSIDE THE GRADED NUMBERS, both already labelled by the frozen instrument.**
`δ_repeat = 0.0` carries the comparator's own note: *"the EXPECTED reading at np=1 on a
deterministic solver from a byte-identical field. IT IS NOT A CLEARANCE FOR THE FD STEP."*
`δ_pert = 0.0` on components 0 and 3 carries *"a component reporting 0.0 means NO FLOOR WAS
DETECTABLE AT THESE STEPS, which is not the same claim as no floor"*, and both are marked
`detectable: false`. **Neither zero enters `δ_eff`**, which is the max and is carried by
`δ_window` by a factor of 268 over `δ_pert`.

**(f) THE `W3-A2` WINDOW BINDING PASSED, AND ITS DATA WERE RE-READ INDEPENDENTLY.**
`_w_from_record` (`:2437`) ran inside `plan()` and returned `2000` without raising. This lane
re-read the same two artefacts directly: **33 of 33 manifest rows carry `"W": 2000`, zero rows
lack the key, the rows do not disagree**, and `ledger.txt` carries **exactly one**
`W_STEPS=2000 deltaT=1e-2` line. This is the gate that `W2R-GRADER-DEF-1` was written for, and
on W3 it did its job: **the window graded is the window that ran.**

---

## 6. THE PHYSICS — WHAT ACTUALLY KILLED THIS ITEM, WITH THE ARITHMETIC OPEN

### 6.1 The step-sizing identity, and which factor moved

`h_min = 100 · δ_eff / |g|` at the registered `EPS_NOISE_TARGET = 0.01`.

| quantity | value | source |
|---|---|---|
| `δ_window,exact(2000)` | `4.3857102184485797e-04` | this run's S2b series, 401 windows |
| `δ_window,env = C_ENV/W = 0.8907/2000` | `4.4535e-04` | frozen `C_ENV`, `W3-A1` |
| `δ_eff = max(exact, env, δ_repeat, δ_pert)` | **`4.4535e-04`** | the envelope carries it, by 1.55 % |
| `\|g\| = ` `dobj_dshape[0]`, S5 adjoint at `W = 2000` | **`0.48835975139977306`** | `step_plan.json` |
| **`h_min`** | `100 × 4.4535e-04 / 0.48835975139977306` = **`0.0911930188193242`** | reproduced to every digit |

The supervisor's check reproduces: `0.044535 / 0.48836 = 0.09119297…`, which is
`0.0911930188…` to the digits the shorter operands support. **Confirmed.**

**`δ_eff` came in 1.55 % ABOVE its predicted value** (envelope over exact) — that is the
registration's own prediction, HIT. **`|g|` came in at 42.8 % of the value the freeze carried
forward.** The entire miss is in the denominator.

### 6.2 The two ratios the supervisor asked to be checked — both confirmed

| ratio | arithmetic | value |
|---|---|---|
| against the envelope constant, i.e. the registered falsifier `\|g\| < C_ENV` | `0.8907 / 0.48835975139977306` | **`1.8239`** — `\|g\|` is **1.82× below** the falsifier threshold |
| against the freeze's own W2R-continued assumption (`:55`, `:89`) | `1.13984 / 0.48835975139977306` | **`2.3340`** — **2.33× below** |

Both are as the brief states. The freeze's *pessimistic* edge was `0.95` (`:52`); the measured
value is **51.4 % of even that**. The band `[1.01, 1.37]` was not merely missed, it was missed
by more than the band's own full width.

### 6.3 **THE FALLBACK DOES NOT RESCUE THE ITEM — MEASURED, NOT ASSUMED**

`W3_PREREGISTRATION.md:55` registers *"The `W = 2,400` variant (S2b lengthened to 4,800 steps,
margin 1.28–1.53×, phase-1 cost 236.5 core-min) is the registered fallback if this item returns
`admissible: false`"*. Evaluated on the **measured** gradient rather than the assumed one:

```
h_min,env(2400) = 100 · (0.8907 / 2400) / 0.48835975139977306
                = 100 · 3.71125e-04 / 0.48835975139977306
                = 0.075994
```

**`0.075994 > h_max = 0.05` by 1.52×. THE REGISTERED FALLBACK IS NOT ADMISSIBLE ON THE
MEASURED GRADIENT.** Its registered margin of "1.28–1.53×" was computed at `|g| = 0.95…1.14`
and does not survive `|g| = 0.48836`. **Firing the `W = 2,400` fallback as written would spend
a registered 236.5 core-min to return the same `NOT A RESULT` on the same branch.**

### 6.4 The window that WOULD be admissible on this gradient — derived, and it is a CONDITIONAL

Admissibility on the envelope requires `100 · (C_ENV/W) / |g| ≤ h_max`, i.e.

```
W  ≥  100 · C_ENV / (h_max · |g|)
   =  89.07 / (0.05 × 0.48835975139977306)
   =  89.07 / 0.024417988
   =  3647.72        →  W ≥ 3,648
```

The supervisor's `89.07/(0.05·0.48836) = 3647` is confirmed (`3647.719` on the rounded operand,
`3647.721` on the full-precision one). **This figure is a CONDITIONAL, not a prediction**, and
§6.5 is why.

### 6.5 **THE FINDING THE REGISTRATION DID NOT ANTICIPATE: `|g(W)|` IS NOT STABLE, AND `W·|g(W)|` WENT DOWN**

This is the substance of the item and it is measured from three artefacts, not inferred.

| `W` | `\|g(W)\|` = `g_component_0` | artefact |
|---|---|---|
| 300 | **`1.0304158599180422`** | `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady/step_plan.json` |
| 900 | **`1.1398352621255485`** | `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2R-cylinder-unsteady/step_plan.json` |
| 2,000 | **`0.48835975139977306`** | `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady/step_plan.json` |

`|g|` rises **+10.62 %** from `W = 300` to `W = 900`, then falls **−57.16 %** from `W = 900` to
`W = 2,000`. **It is non-monotone and it spans a factor 2.33.**

**`h_min` on the envelope depends on `W` only through the PRODUCT `W·|g(W)|`**, since
`h_min,env = 100·C_ENV/(W·|g(W)|)`. That product, measured:

| `W` | `W·\|g(W)\|` | `h_min,env = 89.07 / (W·\|g\|)` | admissible at `h_max = 0.05`? |
|---|---|---|---|
| 300 | **309.12** | **0.288136** | no |
| 900 | **1025.85** | **0.086825** | no |
| 2,000 | **976.72** | **0.091193** | no |
| *required* | **≥ 1781.4** | ≤ 0.05 | — |

> **TRIPLING THE WINDOW FROM 900 TO 2,000 MADE `h_min` 5.03 % WORSE, NOT 2.22× BETTER.**
> `W·|g|` **fell 4.79 %** across that step, because `|g|` fell faster than `1/W`. Over
> `900 → 2,000` the two-point exponent is `|g| ∝ W^(−1.061)`, and at any exponent steeper than
> `−1` a longer window **raises** `h_min`.

**The best `W·|g|` this family has ever measured is 1025.85 at `W = 900`, and the requirement is
1781.4 — a factor 1.74 short, at the best point, in the middle of the range rather than at its
end.** The registration's whole strategy — "lengthen the window until the noise floor falls
below the gradient" — rests on `|g|` being `W`-independent. **The record now falsifies that
premise directly.**

### 6.6 **MEASURED versus UNMEASURED — separated into their own sentences, and no universal is claimed**

**MEASURED, each with an artefact on disk:**
1. `|g|` at three windows: `1.0304158599180422` (W=300), `1.1398352621255485` (W=900),
   `0.48835975139977306` (W=2000). Three run roots' `step_plan.json`.
2. `W·|g|` at those three windows: `309.12`, `1025.85`, `976.72`. Arithmetic on line 1.
3. `h_min,env` at those three windows: `0.288136`, `0.086825`, `0.091193`. Arithmetic on line 2.
4. `δ_window,exact(2000) = 4.3857102184485797e-04` and its envelope `4.4535e-04`, from this
   run's own 2,400-sample S2b series over 401 windows.
5. The `1/W` envelope law for `δ_window`, at `W = 2,000`, on this run's own series: it held.
6. `h_min(2400)` on the measured gradient is `0.075994`, above `h_max`.

**UNMEASURED — and the required `W` moves with every one of them:**
1. **Any law for `|g(W)|`.** Three points that are non-monotone do **not** determine one, and
   this record does not fit one. The `−1.061` exponent quoted in §6.5 is a **two-point slope
   between the last two windows**, not a fitted law, and a third point sits off it.
2. **`|g(W)|` at any `W` other than 300, 900 and 2,000.** In particular `|g(2400)|`,
   `|g(3648)|` and `|g(4000)|` are **not measured**, so §6.4's `W ≥ 3,648` is what admissibility
   requires **if and only if `|g|` stays at `0.48836`** — a premise this record's own three
   points do not support. If `|g|` continues to fall as `W^(−1.061)`, **no window is admissible
   at `h_max = 0.05`**; if `|g|` recovers toward 1.14, `W ≈ 1,563` would suffice. **The record
   does not distinguish these, and this lane does not pick one.**
3. **The mechanism.** Candidate explanations exist — a startup-transient contribution diluted as
   `1/W`; residual phase-oscillation in the window-averaged sensitivity decaying with more
   periods; a checkpointing or convergence property of the unsteady adjoint that changes with
   `W`. **None is measured.** A linear dilution model `W·g(W) = g_t·N_t + g_LC·(W−N_t)` predicts
   `W·|g|` linear in `W`; the measured slopes are `+1.195` over `300→900` and `−0.045` over
   `900→2000`, so **that model is refuted too** and is recorded as refuted rather than left as a
   plausible story.
4. **Whether `|g|` is even correct at any of the three windows.** `DAFOAM_CHARTER.md` §2: *a
   DAFoam gradient is not a result until a finite-difference table stands beside it at a step
   proved to lie in the plateau.* **No `|g(W)|` in this family has ever been FD-verified — that
   verification is precisely what this item exists to buy and has now failed to buy three
   times.** `|g| = 0.48836` is used here **only as a step-sizing scalar** and is **not quoted as
   a gradient result** anywhere in this record. **The admissibility test divides by an
   unverified number, and that circularity is structural to the item, not a defect of this fire.**

**No sentence in this section says "every", "always" or "no window ever" as a measured claim.**
The conditional in §6.4 is labelled a conditional; the falsification in §6.5 is of a *premise*,
and it is measured.

### 6.7 `δ_window,exact` versus `δ_window,envelope`, and what it implies for a longer window

`exact = 4.3857102184485797e-04`, `envelope = 4.4535e-04`; **`exact/envelope = 0.98478`**. The
comparator's own note: *"W3-A1: delta_window_used = max(exact 4.385710e-04, envelope C_ENV/W =
4.453500e-04) = 4.453500e-04; the degeneracy flag (False) is reported, not applied"*, and
`degeneracy_note`: *"W = 2000 is 105.4606 shedding periods, not within 0.05 of a whole number,
so delta_window is not cancelled by construction and stands on its own."*

**What this establishes:** `W = 2,000` is **not** sitting in one of the deep near-period minima
that `W3-A1` was written to refuse (`W = 1800`: `1.09e-04`; `W = 910`: `2.19e-04`, `:42`). The
exact reading is within **1.5 %** of the envelope, so **the envelope is not a conservative
padding here — it is very nearly the truth at this window**, and `W3-A1` bought only 1.5 % of
`h_min` on this fire. Adding a term to a maximum can only raise `h_min`
(`W3_PREREGISTRATION.md:76`): **`W3-A1` could not have manufactured this `NOT A RESULT`, and
without it `h_min` would have been `0.089805` — still 1.80× above `h_max`.** The verdict is
invariant to `W3-A1`.

**What this implies for a longer window, stated as an implication and not a measurement:**
because the exact reading tracks its envelope at this window, `δ_window` at a longer window is
**well predicted** by `C_ENV/W` **for the baseline series** — the numerator is the part of this
problem that is behaving. `W3_PREREGISTRATION.md:119` still stands unchanged: **`C_ENV` is the
BASELINE series' envelope constant, and the perturbed arms' series are not on record at any
window.** A longer window fixes the numerator and leaves the denominator — the term that
actually failed — entirely untouched.

---

## 7. COST — ESTIMATE VERSUS ACTUAL (`CLAUDE.md` rule 12)

**Registered:** 563.3 core-min point for the whole item (phase 1 **196.4**, phase 2 37.6,
phase 3 62.6, phase 4 ≤ 266.7 as a **bound**), cap `CAP_CORE_MIN = 900.0`, `CAP_S8 = 400.0`,
`ranks 1` (`:63-68`, re-asserted unmoved at `:131`, `:243`, `:595`).

**Actual, this fire:** **271.2501 core-min GROSS**, `ranks 1`, cpuset 1, 8g, SHIPPED row
(`dafoam/opt-packages:latest`, `sha256:9d45679d…`). Two independent readings agree: the
ledger's `PHASE1_COMPLETE spent=271.2501` and the sum of the 33 manifest rows' own `core_min`.

**Gross and cleaned, with the rule named** (`COMPUTE_BUDGET_CHARTER.md` §2, `:99-104`): the one
row over 3,600 wall seconds is **`S5` at 4,073 s = 67.8833 core-min**, so
**cleaned = 271.2501 − 67.8833 = 203.3668 core-min.**

> **AND THE CLEANING RULE MISFIRES HERE, WHICH IS REPORTED RATHER THAN QUIETLY APPLIED.** The
> rule's own justification is that *"cleaning removes what was never solver cost"* (`:108-110`).
> **`S5` at `W = 2,000` was genuine solver cost** — it is the unsteady adjoint, the single most
> expensive registered stage, and its 4,073 s is on the family's own scaling line (654 s at
> `W = 300`, 1,570 s at `W = 900`). Cleaning it out would launder a real cost as an
> infrastructure stall. **The ratio in §8 is therefore taken on the GROSS figure**, which is
> also the like-for-like basis: the 196.4 prediction was fitted on D12R2's 55.5167 and W2R's
> 105.2334, **both of which are gross == cleaned** (their longest rows were 654 s and 1,570 s,
> under the threshold). Comparing a cleaned actual to a gross-anchored prediction would be the
> mismatch, not the correction. **Both figures are stated; neither is hidden.**

**Cap:** 271.2501 of 900.0 = **30.1 %**. No cap was breached and no overrun occurred.

**Dollars, DERIVED and NOT MEASURED** at $0.0513/core-h, c7a.4xlarge, reported-by-owner — the
box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5): **$0.2319 actual** against
**$0.4816 predicted**. Both under the $25 pre-authorisation.

**Waste, this fire: `0.000` core-min.** Zero stages failed, zero were re-launched, zero were
`BLOCKED`, and every one of the 33 returned `rc=0`. The decision that the 271.2501 is **not**
waste is argued in §8 and in the calibration row.

**Prior fires, already priced and NOT re-booked here:** `2026-08-27T03:43:17Z` 0 core-min (`A1`
cap-agreement abort); `2026-08-28T02:15:29Z` 0 core-min (`rc=4 grader_md5_drifted`);
`2026-08-28T16:28:48Z` **5.067 core-min**, booked as waste by Addendum 1 §14.8 and carried in
`C-222`; `2026-08-30T23:10:12Z` **63.2332 core-min**, priced by **`C-222`** (corrected on a
rendering defect by **`C-224`**).

**Calibration row landed:** `docs/COST_CALIBRATION.md` row
**`C-20260904T012050.711056Z-be4243a0`**, appended 2026-09-04 via
`scripts/append_record.py --allocate-id`, naming `C-222` and `C-224` so no census double-counts
this item.

---

## 8. THE PER-STAGE COST STRUCTURE — WHAT THE 271.25 CORE-MIN ACTUALLY BOUGHT

Read from the 33 manifest rows, which is also what makes §9's successor estimates anchored
rather than guessed.

| stage group | n | core-min | share | what it buys |
|---|---|---|---|---|
| `S0` + `S1a` + `S1b` + `S2a` (setup, `W`-independent) | 4 | **1.7500** | 0.6 % | mesh, init, transient discard → `FIELD_B` |
| `S2b` (2,400 fixed steps) | 1 | **6.6833** | 2.5 % | the CD series → `δ_window`, `G12R-1`, `G12R-3` |
| `S3` ×3 (repeatability) | 3 | **19.1000** | 7.0 % | `δ_repeat` — came out **`0.0`** |
| `S3b` ×16 (perturbation pairs) | 16 | **149.2168** | **55.0 %** | `δ_pert` — came out `1.66e-06`, **268× below** the term that decided the verdict, and **undetectable on 2 of 4 components** |
| `S4` ×6 (`n = 20/40/80`) | 6 | **14.7001** | 5.4 % | the memory envelope |
| **`S5` (the unsteady adjoint)** | 1 | **67.8833** | **25.0 %** | **`\|g(2000)\|` — the number the item turned on** |
| `S7` ×2 (plant/clean) | 2 | **11.9166** | 4.4 % | the `G12R-9` material (gate not reached, §5b) |
| **total** | **33** | **271.2501** | | |

**`S3b` is 55 % of the spend and produced a term 268× below the deciding one.** That is the
single largest cost-reduction lever available to a successor, and §9 registers it.

**IS THE 271.2501 WASTE? DECIDED: NO — and the argument is made in both directions before it is
decided, as instructed.**

*The case for waste:* the item returned `NOT A RESULT` and no verified gradient. On a
"bought-a-verdict-you-can-use" test, 271 core-min bought nothing usable.

*The case against, which is the one the charter's own words support:* `COMPUTE_BUDGET_CHARTER.md`
`:109-110` defines the waste split as *"solver cost that bought nothing"* — **an outcome test on
whether the spend produced evidence, not on whether the evidence was favourable.** This spend
produced four things that are on disk, are cited above, and that no cheaper instrument in this
lab could have produced:

1. **`|g(2000)| = 0.48836`** — the third point in the family's `|g(W)|` record and the one that
   falsifies P2 and P3.
2. **`W·|g|` FELL from `W = 900` to `W = 2,000`** (§6.5) — the measurement that **falsifies the
   registered `W = 2,400` fallback** and the whole lengthen-the-window strategy behind it. It is
   only visible because a third window was bought.
3. **`δ_window,exact(2000)` confirming the `1/W` envelope law on this run's own series** (P1
   HIT) — which is what lets §6.7 say the numerator is *not* the problem.
4. **A complete 33/33 phase-1 record** under the repaired launcher, after three consecutive
   fires that reached no physics at all.

**Additionally, the registered no-launch branch prevented the ~367 core-min of phases 2–4 from
being spent on a gradient that could not be verified.** The branch is the item's designed
economy and it worked.

**Decision: the 271.2501 core-min is NOT waste. It is priced spend that bought a measured
falsification, and it is what sizes the successor.** Waste for this fire is recorded as
**`0.000`**. Anyone who disagrees has the counter-argument above in full and does not need to
reconstruct it.

---

## 9. WHAT THE SUCCESSOR MUST DO — AND WHY IT IS NOT "RUN IT AT `W = 4,000`"

Sanaa's 2026-09-04 order makes this item mandatory *"until its at the very least a gate pass"*,
so this `NOT A RESULT` is a **waypoint**. A successor is drafted at
**`cases/dafoam/curriculum_D12R2/W3S_PREREGISTRATION_DRAFT.md`** — **UNFROZEN, NOT QUEUED, NOT
LAUNCHED**, awaiting the supervisor's read and freeze. Its design follows from §6.5 and not from
§6.4:

- **Registering `W = 4,000` blind would spend ~525 core-min on a premise this record
  falsifies.** `W·|g(W)|` is the quantity that must clear 1,781.4, and it **went down** over the
  last window step measured.
- **The successor therefore buys `|g(W)|` at two more windows FIRST**, as a cheap diagnostic arm
  that skips the 16 `S3b` stages (55 % of the spend) and the 6 `S4` stages, before it commits to
  any full window arm.
- **A hard, measured constraint the successor must register:** `S5` wall time fits
  `≈ −81 + 2.0438·W` seconds on the family's three anchors (654 / 1,570 / 4,073 s at
  `W = 300 / 900 / 2,000`). **At `W ≳ 3,560` that exceeds the registered 7,200-s per-stage wall
  bound**, so any window arm at `W ≥ 3,648` **requires the S5 stage bound to be raised** — a
  registered change, which is exactly why it needs a successor registration rather than a
  fallback fired from this one.
- **`S2b` must be lengthened.** `block_averages` **refuses** at `len(cd) < W`
  (`d12y_grade_w3.py:202-209`), and `S2_STEPS` currently stands at **2,400**. `W = 4,000` needs
  `S2b ≥ 4,000` to grade at all and `4,400` to retain 401 sliding windows. That costs, and the
  draft prices it.

---

## 10. WHAT THIS ITEM DOES **NOT** ESTABLISH

`W3_PREREGISTRATION.md:119` stands unchanged and is re-asserted here rather than restated
loosely:

- **Nothing about the PATCHED row.** The two-row rule (`DAFOAM_CHARTER.md` §6) is **carried, not
  discharged**, by this shipped row alone. `--image patched` into `<root>_p` remains registered
  and unfired.
- **Nothing on a second mesh.** 2,450 cells, one mesh, no grid family, **NO GCI**, and standing
  rule 5 has no row here.
- **`St ≈ 0.53` is a resolution artefact** and is never quoted as a Strouhal number.
- **The envelope constant `C_ENV = 0.8907` is the BASELINE series'.** The perturbed arms' series
  are not on record at any window.
- **The unsteady adjoint's memory at `W = 2,000` is not characterised.** It did not OOM under the
  8g cap and `oomkilled = false` on 33/33 rows, but no peak-RSS figure was taken, so the envelope
  is **NOT MEASURED**, only **not exceeded**.
- **`G12R-9` was not evaluated on this run's artefacts** (§5b). The plant's read-back is
  computable and non-zero, and that is recorded as a corroboration, not as the gate.
- **No `|g(W)|` in this family has ever been FD-verified**, at any window. The three values in
  §6.5 are unverified adjoint numbers used as step-sizing scalars.
- **The `G12R-3b` `g_implied_DIAGNOSTIC_ONLY` figures are reported and are NOT evidence about
  the gradient.** Component 0 reads `1.4407169110929194` against the adjoint's `0.48836` — a
  factor 2.95 — but the probe steps `h_a = 1e-06` / `h_b = 1e-05` are **four orders of magnitude
  BELOW** the measured noise floor `δ_eff = 4.4535e-04`, that component's `delta_pert` is
  `detectable: false`, and its `linearity_ratio` is `11.08` against an ideal 1. **The probe is
  measuring noise.** It is stated here rather than left as an unexplained printed discrepancy,
  and it supports **no** conclusion about `|g|` in either direction.

---

## 11. THE FROZEN DOCUMENT WAS NOT EDITED

`W3_PREREGISTRATION.md` is **untouched by this record** (`CLAUDE.md` rule 6). Its body, its
three amendments and its addendum stand exactly as committed; no gate, threshold, band, cap,
label, cost or prediction is moved, restated or reinterpreted here. Every score in §4 is read
off `:88-92` as frozen and none was adjusted after the answer was known. **Where this record
adds something the registration did not anticipate — §6.5's `W·|g|` finding — it is recorded
here, in the results record, and not written back into the frozen document.**
