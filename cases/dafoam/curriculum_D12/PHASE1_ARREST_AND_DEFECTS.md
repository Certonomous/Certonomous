# D12-proper PHASE 1 — **ARRESTED**. Four producer defects, and a REFUTED pre-compute prediction

Dated **2026-08-25**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.
**Nothing here was filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).

---

## 0. HEADLINE

# Phase 1 is `NOT A RESULT`. I stopped it.

**23 stages ran: 4 returned `rc=0`, 19 returned `rc=1`.** Every stage from **S3 onward failed
identically** on a broken `FIELD_B`. **12.0332 core-min spent of the 600.0 runaway guard;
2.7165 core-min of that is WASTE and is named as waste, not absorbed.**

**I stopped the run rather than letting it finish.** ~25 further stages would have failed the
same way in ~4 more core-min. **Cost constraints being lifted is not a licence to let a
known-broken run continue: that is not rigor, it is negligence, and waste is reported.**

**Four defects. All are in the PRODUCER — my launcher — and one is in the frozen
pre-registration's own wording. NONE corrupts a physical number.** Three cause **refusals** and
one causes a **hard crash**. Every artifact on disk is correct as far as it goes; the failure is
that the graded stages could not start.

**AND THE SINGLE MOST IMPORTANT RESULT OF THE NIGHT IS NOT A DEFECT:**
**the pre-compute prediction I registered was REFUTED by measurement, and the frozen code
caught it rather than confirming it** (§5).

---

## 1. DEFECT 1 — `FIELD_B` CANNOT START A SOLVE. **This is what killed phase 1.**

Every S3, S3b stage died at field-read time:

> `--> FOAM FATAL ERROR: cannot find file "/mnt/S3b_c1_bp/0/nut"`

**Measured, from disk:**

| directory | contents |
|---|---|
| `FIELD_B/` (from S2 `t=3.00`) | `U.gz  nuTilda.gz  p.gz  phi.gz` — **four fields** |
| `FIELD_A/` (from S1b `t=10`) | `U.gz U_0.gz betaFINuTilda.gz fvSource.gz meshPhi.gz nuTilda.gz nuTilda_0.gz nut.gz p.gz p_0.gz phi.gz` — **eleven** |
| `mesh/0_orig/` (what a solve is given) | `U epsilon k nuTilda nut omega p` |

**S2's per-timestep time directories hold only four fields. `nut` is not among them.** S1b's
write at `t = 10` holds eleven, including `nut`, `U_0`, `nuTilda_0` and `p_0` — the previous-step
fields a PIMPLE restart wants. The two stages ran the **same run script** and differ in
`writeInterval` (1 vs 100) and in which controlDict was staged.

**THE DEFECT IS NOT THAT DAFOAM WRITES FOUR FIELDS. IT IS THAT MY LAUNCHER FROZE A FIELD SET
WITHOUT EVER CHECKING IT COULD START A SOLVE.** `field_b_write_manifest` computed a per-file
md5 manifest over whatever was in that directory and `field_b_assert` then **re-asserted it
faithfully before every single stage** — twenty-three times — and passed every time. **The
manifest was internally perfect and externally false.**

> **That is precisely the failure the supervisor ruled about hours ago:** *"a launcher staging
> the wrong field consistently produces a self-consistent manifest."* **I named that residual
> risk in `3f0026ea` and then shipped an instrument that fell into it.** The ruling's repair —
> the **comparator** computing the staged field's md5 itself — would not have caught this
> either: both readers would have agreed on the same four files. **What catches it is a
> completeness check against what a solve needs, which neither of us specified.**

**The repair this needs, for the supervisor to rule on:** `FIELD_B` is verified to be
**startable** before it is frozen — the registered field list is asserted present, and/or one
throwaway single-step solve is run from it and required to reach `rc=0`. **A frozen initial
condition that has never been shown to start a solve is a hash of a guess.**

---

## 2. DEFECT 2 — THE AGE GUARD CANNOT ARM. `writeCompression on`.

`age_guard_ok` came back **`None` on every stage after S1a**, with an empty detail string.

**Root cause, measured:** the launcher touches `$D/0/U` as the age datum. The tutorial's
controlDicts all carry **`writeCompression on;`**, so every written field is **`U.gz`, never
`U`**. `test -f "$D/0/U"` is therefore false, `AGE_DATUM` is never set, and the whole guard
block is skipped.

| stage | `0/U` present? | `age_guard_ok` |
|---|---|---|
| S1a | yes — its `0` came from `mesh/0_orig`, the tutorial's **uncompressed** source | **`True`** ("all 8 fields at endTime newer than 0/U") |
| S1b, S2, all later | **no** — their `0` came from a **written** time directory, so `U.gz` | **`None`** |

**THE GUARD FAILED SAFE, AND THAT IS THE ONLY GOOD NEWS HERE.** I deliberately made `G12R-0`
refuse on `None` as well as on `False` — *absence of a check is not a pass* — so this would have
produced a refusal, never a false clearance. **But a guard that silently cannot arm on the
normal on-disk representation of a field is a guard in name only**, and it passed on S1a
purely because that one stage happened to start from uncompressed source files. **A control
that passes only where the filename convention accidentally suits it has not been tested.**

`CLAUDE.md` rule 4 names the datum as `0/T` for the thermal family. **The rule's intent — a
datum touched last at launch — is sound; my transliteration to a bare `0/U` assumed an
uncompressed filename.** The repair is to resolve the datum as `0/U` **or** `0/U.gz`, and to
**refuse rather than skip** when neither exists.

---

## 3. DEFECT 3 — `obj_from_log` READS `CL`, NOT `CD`. **The frozen pre-registration specifies this.**

`PREREGISTRATION.md` §5 `G12R-0` freezes: *"the JSON `obj` equals the **LAST `average:` value**
in the stage's own log to ≤ `1.0e-12` relative."* My launcher implements that **literally**.

**But the solver prints `average:` on TWO lines per timestep** — measured, 1,993 of each in the
S2 log:

```
CD: 0.7007394482227842 average: 0.6377885661084924
CL: 0.6459163754222785 average: 0.03880790477545
```

**The LAST `average:` is CL's.** On S1b, measured:

| quantity | value |
|---|---|
| JSON `obj` (the objective, CD) | **`0.6377885661084924`** |
| `obj_from_log` as my launcher recorded it (**CL**) | **`0.03880790477545`** |
| the last **`CD:`** line's average — what it should read | **`0.6377885661084924`** |

**The correct reading agrees with the JSON TO THE LAST DIGIT. The frozen reading disagrees by
93.9 %, against a tolerance of `1.0e-12`.** So this clause — the one whose whole purpose is
*"the series reader and the solver must agree on the one number they both compute"* — **would
have refused every stage in the item.**

**THIS IS A MIS-SPECIFIED GATE QUANTITY THAT COULD NEVER HAVE PASSED**, the same class this lab
recorded against `VMFL059`. It was written by a lane that never ran the solver, and it is frozen.

**The comparator is NOT affected, and I checked rather than assumed.** `d12r_grade.py`'s
`read_series` uses an **anchored** `^CD:\s*(\S+)\s+average:\s*(\S+)$`. Run against the real S2
log it returns **2,400 samples, minimum `0.589739`, maximum `0.757656`, ZERO negative values** —
and `CL` swings negative about half the time, so **zero negatives is a positive demonstration of
zero contamination, not an absence of evidence.** **The silent-corruption path into `δ_window`
and `δ_eff` does not exist.** Only the launcher's loose `findall` is wrong.

---

## 4. DEFECT 4 — `time_line_count` IS NOT A VALID STEP PROXY FOR A STEADY `PYDAFOAM` STAGE

`G12R-0`'s step-count limb requires the primal's `Time = ` line count to **equal** the registered
steps. Measured on S1a: **6 lines against 500 registered** — the steady `simpleFoam` driver
prints `Time = ` every 100 iterations (`Time = 300`, `400`, `500`).

**The launcher's own cross-check did not catch it and could not**: it compares the *registered*
count against the *staged controlDict's* count, and both say 500. **They agree with each other
and both disagree with the log.** The limb is correct for the unsteady stages — S1b **200/200**,
S2 **2400/2400**, exact — and wrong for the one steady stage.

---

## 5. **THE PRE-COMPUTE PREDICTION WAS REFUTED — AND THE FROZEN CODE CAUGHT IT**

This is the most valuable thing phase 1 produced, and it is a *result*, not a defect.

Amendment 2 §A2.4 registered, **before any compute**, that the shedding period would be
**≈ 50 timesteps** (`St ≈ 0.2`), making `W = 300` **≈ 6.0 periods exactly** and `δ_window`
**degenerate**. The supervisor independently checked the same arithmetic and agreed.

**MEASURED, from S2's own 2,100 retained samples:**

| quantity | predicted (registered pre-compute) | **measured** |
|---|---|---|
| shedding period | ≈ 50.0 timesteps | **`18.9955` timesteps** |
| Strouhal number | 0.2000 | **`0.5264`** |
| `W / period` | ≈ 6.0 — **degenerate** | **`15.7932` — NOT degenerate** |
| `δ_window` | cancelled by construction | **`1.274958e-03` (rel `1.942378e-03`) — LIVE** |

> ### **THE PREDICTION IS REFUTED. The measured period is `0.38×` the predicted one.**

`G12R-1` returns **`PASS`**: 221 sign changes about the mean (registered minimum 6) and a
peak-to-peak of **19.40 %** of `|mean|` (registered minimum 1 %). Mean `CD = 0.6563506540`.
**A limit cycle is established.**

**AND THE GATE DECIDED FROM THE MEASURED PERIOD, NOT THE PREDICTED ONE**, exactly as the
supervisor's second ruling requires: `g3_delta_window` computed `k = W/P` from `G12R-1`'s
measurement and returned `degenerate: False`, `period_prediction_held: False`. **The
degeneracy branch was frozen before the data and it declined to fire.** Had it been hard-coded
from the prediction it would have excluded a noise term that is real — *an assumption wearing a
measurement's clothes*, which is the thing the ruling forbids.

**Honest caveat on the period:** `G12R-1` estimates it as `2(n−1)/sign_changes`, a
**mean-crossing** estimator. On a signal with harmonics that **underestimates** the fundamental,
so `18.9955` is a lower bound on the period and `0.5264` an upper bound on `St`. **No spectral
estimate was bought.** `St ≈ 0.53` is not absurd at `Re_D = 1.0e6` (post-drag-crisis), but on a
2,450-cell 2D URANS mesh with wall functions **it is not a validated Strouhal number and must
never be quoted as one.**

### WHAT THIS IMPLIES FOR `G12R-4`, STATED AS A DIRECTION AND NOT A RESULT

With `δ_window` live at `1.274958e-03` and **not** degenerate, `δ_eff` will be dominated by it —
`δ_pert` was `1.65e-06` on the *probe*, three orders smaller. Then
`h_min = 100·δ_eff/|g| ≈ 1.10` against a registered `h_max = 0.05`: **`h_min` exceeds `h_max` by
~22×, and the registered NO-ADMISSIBLE-STEP branch would fire.**

**THIS IS NOT A RESULT AND IS NOT OFFERED AS ONE.** `|g|` here is the *probe's* `1.1623e-01`,
not `S5`'s — **S5 never ran.** It is stated because the pre-registration registered that branch
in advance as *"a RESULT, not a failure"*, and the supervisor should know phase 1 was heading
there before the crash, so that outcome is not later read as caused by these defects.

---

## 6. WHAT RAN CLEAN

| stage | rc | what it produced |
|---|---|---|
| **S0** mesh | 0 | mesh built; 0.05 core-min |
| **S1a** spin-up `potentialFoam` + `simpleFoam` 500 | 0 | `500/` written, 8 fields |
| **S1b** PIMPLE to `t = 10`, 200 steps | 0 | **FIELD_A**, 11 fields; `200/200` steps; JSON/log agree exactly on CD |
| **S2** diagnostic, 2,400 steps | 0 | **2,400 CD samples**, `2400/2400` steps, `ExecutionTime` 2400 — §5's entire measurement |

**All five launcher pre-flight asserts fired correctly** — instrument md5 vs committed blobs,
image ID, the cap against the registered value, the instrument-existence predicate with its
planted **and negative** control, and the run-root guard. **`OOMKilled false` on every stage;
`MemAvailable` never fell below 16.9 GiB against my 14.0 floor and the 12 GiB hold.**

---

## 7. COST — AND THE WASTE, NAMED

| | |
|---|---|
| predicted, phase 1 portion | ~52 core-min (S0–S7) |
| **actual, arrested** | **12.0332 core-min** |
| runaway guard | 600.0; spend was **0.020×**; **the guard never fired** |
| **WASTE** | **2.7165 core-min — 22.6 % of the spend**, being the 19 `rc=1` stages, **every one of them my own instrument defects** |
| derived | **$0.010288** at $0.0513/core-h, c7a.4xlarge, reported-by-owner — **DERIVED, NOT MEASURED** |

**The waste is named separately and is netted off neither the spend nor any ratio**
(`COMPUTE_BUDGET_CHARTER.md` §6). **No actual/predicted ratio is quoted**: the process did not
complete, and a ratio against a phase that was arrested would be a fabrication wearing a
decimal point. **Contention: UNMEASURED** — load ran 13–16 of 16 cores throughout and no
uncontended control was bought.

---

## 8. WHAT THE SUPERVISOR MUST DECIDE

The pre-registration is **frozen** — first compute happened at 22:08Z. **Every repair below is
therefore a `VERIFICATION_CHARTER.md` §2d.1 exception and is the supervisor's call, not a
lane's** (`CLAUDE.md` rule 9). I have pre-satisfied the four conditions so the ruling is cheap:

| §2d.1 condition | status |
|---|---|
| **(1)** repairs a **demonstrable error**, not a preference | **YES ×4.** A field set that cannot start a solve; a guard that cannot find its datum; a reader taking CL where the objective is CD; a step proxy the solver does not emit. **None is a matter of taste.** |
| **(2)** established by an instrument **independent of the hypothesis**, one that **grades nothing** | **YES ×4.** (1) the FOAM fatal error naming the missing file, and `ls` of three directories; (2) `test -f` on `0/U` versus `ls` showing `U.gz`, plus `grep writeCompression`; (3) the last `CD:` line agreeing with the JSON **to the last digit** while the last `average:` disagrees by 93.9 % — **a near-identity that grades nothing and has no direction to be selected toward**; (4) `grep -c '^Time = '` against the staged controlDict. **Every one is a reader that renders no verdict.** |
| **(3)** record **discloses**, **names the instrument**, **quantifies what moved** | **This file.** |
| **(4)** pre-repair values recorded **beside** the published ones | **The run root is preserved byte-for-byte** at `/home/ubuntu/certonomous-runs/CURRICULUM-D12-cylinder-unsteady/` — `ledger.txt`, `manifest.jsonl` with the wrong `obj_from_log` and the `None` age guards, and all 23 stage directories. **Nothing is deleted or rewritten.** |

**And one question that is NOT a §2d.1 repair and is the real one:** *should `FIELD_B` be built
from a per-step write at all?* `FIELD_A` — a `writeInterval 100` write — carries the eleven
fields a restart needs; S2's per-step writes carry four. **The registered pipeline may simply be
asking S2 for something S2's write settings do not produce**, in which case the repair is to the
**pipeline**, not to the launcher.

## 9. THE SUPERVISOR'S SECOND RULINGS — WHAT I DID AND DID NOT DO

`SUPERVISOR_D12_RULINGS_2.md` (`2e7069e7`) arrived while phase 1 was failing. Recorded honestly:

- **The units registration for `applied_magnitude` (required before phase 3): NOT DONE.** Phase 3
  was never reached. The supervisor's point stands and is sharper than my own residual: **the
  WHERE-control is strong on index and sign — a positive scaler moves neither — and
  CONDITIONAL on magnitude**, which is `D4-DEF-4` surviving inside the control built to catch it.
- **The comparator-side FIELD_B md5 readback: NOT IMPLEMENTED**, and §1 records why it would not
  have caught this defect anyway — both readers would have agreed on the same four files. **It is
  still the right repair for the risk it targets; it is simply not sufficient for this one.**
- **`δ_window` must never emit a numeric zero when degenerate: NOT YET IMPLEMENTED.** It did not
  bite here — **`δ_window` measured LIVE, so the degenerate branch never fired** — but the
  requirement stands and the code still returns a number rather than excluding it by name.

**SUBMISSIONS ARE PARKED. Nothing here has been sent, filed, uploaded, registered, posted or
commented, and sending is Sanaa's decision alone.**

**Calibration row: `C-93` in `docs/COST_CALIBRATION.md`.**
