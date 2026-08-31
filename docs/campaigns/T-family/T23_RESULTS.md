# T23 — RESULTS: the four registered cases of the rescaled Case 3 map, graded against the PHYSICALITY TIER and nothing else

**Graded 2026-08-31 by a heat-transfer `lab-lane` at the heat-transfer-supervisor's
dispatch.** Gates FROZEN at `docs/campaigns/T-family/T23_PREREGISTRATION.md`,
commit **`fe666fd5d3cf148b1266bf693d1199cec3c7d607`**.

**THE GRADING PATH WAS VERIFIED TO BE THE FILE THAT RAN** (`CLAUDE.md` rule 2,
last bullet): the worktree copy of the registration hashes to git blob
`c341476f3680c14ec593c52d12e49214cf83ebb3`, **identical to
`HEAD:docs/campaigns/T-family/T23_PREREGISTRATION.md`**, sha256 prefix
`b46d23c9cbbc945d` on both paths [MEASURED]. The four launched queue entries
each name `prereg_commit fe666fd5…` and `prereg_path` that document, and the
`LAUNCH_LOG.tsv` rows carry the same sha [MEASURED].

**Verdict vocabulary fixed by `CLAUDE.md` rule 1.** No other word appears below
as a verdict.

---

## 0. WHAT THIS DOCUMENT DOES NOT CLAIM — stated first

**T23 registers the PHYSICALITY TIER and nothing else** (registration §0.2).
This record therefore carries **no Nusselt number, no heat-balance closure, no
observed order, no GCI and no Roache classification.** All four are DEFERRED at
registration §4 with reasons.

> **§1 line 5 REGISTERS NO LADDER. Every point ran at L1 only, and A SINGLE MESH
> LEVEL ADMITS NO TRIPLE.** Any Roache classification, GCI or observed order
> quoted from a T23 artifact is a **CATEGORY ERROR**. The grader
> `verification/runs/T-family/T23_runs/analyse_t23.py` emits none, and its own
> selftest drives a check that its per-case output contains no such token — with
> a planted control proving that same reader *does* see the tokens where they
> legitimately appear, so the zero is not a blind zero.

y+ is **MEASURED AND REPORTED, never gated** (§4.4).

---

## 1. THE FOUR ROWS

All four cases: `chtMultiRegionSimpleFoam`, OpenFOAM v2606, 39,680 cells, 1 rank,
`endTime` 10000, `writePrecision 12`.

| case | Q1 `T_max` housing, degC | Q2 areaAvg iface, degC | Q1 − Q2, K | B3 | B2 | B1 (bound 200.0) | **VERDICT** | core-min |
|---|---:|---:|---:|---|---|---|---|---:|
| `T23_P305_U10` | **103.6078** | 101.4498 | +2.158008 | PASS | PASS | PASS, margin **+96.3922 K** | **PASS** | 29.7337 |
| `T23_P305_U20` | **69.0098** | 67.1846 | +1.825226 | PASS | PASS | PASS, margin **+130.9902 K** | **PASS** | 30.2190 |
| `T23_P305_U30` | **55.4389** | 53.8032 | +1.635613 | PASS | PASS | PASS, margin **+144.5611 K** | **PASS** | 30.4898 |
| `T23_P305_U40` | **47.8448** | 46.3448 | +1.499971 | PASS | PASS | PASS, margin **+152.1552 K** | **PASS** | 29.6860 |

All values **MEASURED**. Q1 from the `internalField` of `<10000>/housing/T`; Q2
as the **area-weighted** average of the `value` list of the `housing_to_fluid`
patch in the `boundaryField` of the same file, over **140 faces, total area
4.089318e-04 m²**, with the face areas computed from the housing region's own
`constant/housing/polyMesh` rather than assumed equal. **Q2 reads the `value`
entry and refuses to fall back to `refValue`**, which is a different quantity;
the grader's selftest drives that distinction on a forged patch where the two
differ.

**FOUR PASS, ZERO FLAGS — and the registration is explicit that zero flags was
never the requirement** (§1 line 4: *"Zero flags was never the requirement of
this tier and must not be engineered for"*). Nothing was engineered for it: the
grader's B1 branch is the registered one and its FLAGGED arm is driven in the
selftest.

### 1.1 **(305 W, 20 m/s) DID NOT FLAG, and the registration predicted the question, not the answer**

§2.7 registered this point **UNDECIDED** before compute at **+2.70 K** under the
bound, on a model whose two closures differ by **1.763× in h**. It came in at
**69.0098 degC — 130.99 K under the bound**, a clean PASS. **That is a
registered-in-advance outcome landing on one of its two registered sides, not a
surprise; and had it flagged, that too would have been registered rather than a
failure.**

### 1.2 The registered predictions, reported beside the values and never used as gates

| case | DB predicted | FP predicted | solved | solved − DB | solved − FP |
|---|---:|---:|---:|---:|---:|
| `T23_P305_U10` | 329.1 | 195.1 | 103.6078 | −225.49 K | −91.49 K |
| `T23_P305_U20` | 197.3 | 120.3 | 69.0098 | −128.29 K | −51.29 K |
| `T23_P305_U30` | 148.0 | 92.4 | 55.4389 | −92.56 K | −36.96 K |
| `T23_P305_U40` | 121.6 | 77.4 | 47.8448 | −73.76 K | −29.56 K |

---

## 2. **THE REGISTERED CONTINGENCY OF §6.2 HAS FIRED ON ALL FOUR POINTS**

§6.2 registered, one-way and before compute:

> *"if the solved values disagree with **both** closures by more than the 1.763×
> spread between them, the **lumped model of §2 is the thing that was
> falsified** — a reportable finding about the level-selection instrument — and
> **that does not change B1, B2 or B3**, which grade the solved temperature and
> not the model."*

**THE COMPARISON IS TAKEN ON THE TEMPERATURE RISE ABOVE `T_inf`, AND THE READING
IS STATED RATHER THAN LEFT IMPLICIT.** The lumped model is
`T_max = T_inf + P·R_tot(U)` (§2.1), so `T_inf` is **common to the model and the
solve** and carries no information about either. Comparing absolute degC would
divide two numbers that share a 288 K offset and would flatter the model by
construction. `T_inf` = 288.0 K is REGISTERED at §2.1 and is also MEASURED as
the inlet `fixedValue` in each case's own `0.orig/fluid/T`.

| case | solved rise, K | DB rise / solved rise | FP rise / solved rise | vs spread 1.763 |
|---|---:|---:|---:|---|
| `T23_P305_U10` | 88.758 | **3.541** | **2.031** | **FIRED** |
| `T23_P305_U20` | 54.160 | **3.369** | **1.947** | **FIRED** |
| `T23_P305_U30` | 40.589 | **3.280** | **1.911** | **FIRED** |
| `T23_P305_U40` | 32.995 | **3.235** | **1.896** | **FIRED** |

**The lumped series-resistance model of §2 overpredicts the housing temperature
rise by 1.90× to 3.54×, and it does so beyond the 1.763× spread between its own
two closures — so this is NOT an artefact of choosing between Dittus-Boelter and
the flat plate.** Even the optimistic closure is out by a factor of ~1.9.

**WHAT THIS DOES AND DOES NOT TOUCH, stated exactly as §6.2 registered it.**

* It **changes B1, B2 and B3 not at all.** Those grade the solved temperature,
  not the model. All four verdicts stand as PASS.
* It is a finding about the **LEVEL-SELECTION INSTRUMENT** of §2, which §1 line 2
  registered as **NOT a referent**: *"The two closed-form correlations of §2 are
  used only to choose the levels before compute and are NOT referents: nothing is
  graded against them, and §2.7 registers in advance that they may be wrong."*
  §2.7 was right.
* **It has a consequence for the twelve deferred points, and it is the honest
  one:** §2.5's flag arithmetic (**2 of 16 under DB, 0 of 16 under FP**) was
  DERIVED from this same lumped model. §6.4 already recorded that the 2-of-16
  figure is *"registered arithmetic and is not measured by this rung."* **It is
  now not merely unmeasured but measured against — the instrument that produced
  it overpredicts by ~1.9× to ~3.5×, so on the solved physics the rescaled levels
  would flag ZERO of 16, not 2.** Nothing in this record re-registers anything:
  **the flag count of a later registration is that registration's to choose, and
  §2.5's committed numbers are not rewritten** (rule 6).
* **It does not falsify the RESCALE.** §2.3's structural incompatibility argument
  and Sanaa's *"5. Rescale"* ruling are untouched by this record. What is
  falsified is the *magnitude* the lumped model assigns, not the *ordering* it
  used to bracket the isotherm.

---

## 3. **THE `Ux` CONVERGENCE ASSERTION, AND WHY `Ux` IS EXCLUDED FROM IT**

**THIS IS A REPORTING DECISION AND NOT AN AMENDMENT. Compute has run, the frozen
gates are closed, and T23 CARRIES NO RESIDUAL GATE AT ALL** — §3.1 registers
convergence as *"an ASSERTION on the log, never a stopping rule"* and does **not**
name which residuals the assertion covers. Nothing below moves any gate, and the
frozen registration is not edited (rule 6).

**In this 5° wedge, `x` is the CIRCUMFERENTIAL direction, the mesh is one cell
thick with `wedge` patches front and back, and `Ux` is identically zero BY
GEOMETRY.** Its linear-solver residual is normalised by its own field scale, and
when that scale is machine zero the ratio is noise of order one.

**MEASURED PER CASE by this lane on each case's own `10000/fluid/U`, never
recited from another case:**

| case | max\|Ux\|, m/s | max\|Uz\|, m/s | **max\|Ux\| / max\|Uz\|** | final `Ux` initial residual |
|---|---:|---:|---:|---:|
| `T23_P305_U10` | 2.306527e-15 | 1.053664e+01 | **2.189e-16** | 1.265467e-01 |
| `T23_P305_U20` | 3.829139e-15 | 2.089689e+01 | **1.832e-16** | 1.370473e-01 |
| `T23_P305_U30` | 5.167530e-15 | 3.121971e+01 | **1.655e-16** | 3.097094e-02 |
| `T23_P305_U40` | 6.483336e-15 | 4.152703e+01 | **1.561e-16** | 1.400066e-01 |

**A reader who greps the last `Ux` residual and stops there reports EVERY run of
this family as unconverged.**

**THE CONVERGENCE ASSERTION THIS RECORD MAKES, in full:**

> **Asserted over `Uy`, `Uz`, `h`, `p_rgh`, `k` and `omega` at 1e-06, on the last
> `Time = 10000` block of each case's own `log.solve`: IT HOLDS ON ALL FOUR
> CASES. `Ux` is EXCLUDED, on the measured ground that max\|Ux\|/max\|Uz\| is
> between 1.561e-16 and 2.189e-16 — i.e. `Ux` is zero to machine precision — so
> its residual is a 0/0 normalisation carrying no information. THE EXCLUSION
> CHANGES NO GATE, BECAUSE T23 HAS NO RESIDUAL GATE.**

Excluded-component residuals are **printed, never suppressed**, on the face of
the grader's output beside the ratio that justifies the exclusion. The grader's
selftest drives a control confirming that, had `Ux` been asserted, the forged
case would report NOT converged — so the exclusion is load-bearing and is shown
to be.

The final asserted residuals, all four cases, MEASURED:

| case | `Uy` | `Uz` | `h` | `p_rgh` | `k` | `omega` |
|---|---:|---:|---:|---:|---:|---:|
| `U10` | 8.241267e-10 | 5.571990e-12 | 9.440276e-10 | 1.273286e-08 | 9.931450e-10 | 9.580583e-10 |
| `U20` | 5.477766e-10 | 3.754062e-12 | 9.574012e-10 | 9.923047e-09 | 9.729099e-10 | 6.090902e-10 |
| `U30` | 5.427521e-10 | 3.751892e-12 | 9.540190e-10 | 1.025923e-08 | 9.534448e-10 | 8.724115e-10 |
| `U40` | 7.235645e-10 | 7.719644e-12 | 9.651411e-10 | 7.689558e-09 | 9.902131e-10 | 5.737583e-10 |

---

## 4. y+ — MEASURED AND REPORTED, NEVER GATED (§4.4), AND A FALSE ZERO CAUGHT ON THE WAY

**MEASURED** by `chtMultiRegionSimpleFoam -postProcess -func yPlus -region fluid
-time 10000`, run **in a scratch copy of each case so no graded artifact was
written**; the resulting log is filed as each case's `log.yPlus.fluid`.

| case | max y+ on `fluid_to_housing` (**the housing surface**) | min | average | max y+ on `duct_wall` |
|---|---:|---:|---:|---:|
| `T23_P305_U10` | **0.4037** | 0.3951 | 0.3990 | 1.441 |
| `T23_P305_U20` | **0.7515** | 0.7334 | 0.7416 | 2.396 |
| `T23_P305_U30` | **1.079** | 1.052 | 1.064 | 3.229 |
| `T23_P305_U40` | **1.397** | 1.362 | 1.378 | 4.000 |

**FINDING, and §4.4 registered exactly this outcome before compute: max y+ on the
housing EXCEEDS 1 at U = 30 and U = 40 m/s.** §4.4's own words: *"If the measured
y+ exceeds 1, that is a reportable finding that BLOCKS the correlation tier and
the triple — neither of which this rung claims — and it does not void the
physicality rows, whose content is a temperature bound and not a heat-transfer
coefficient."* **The four PASS verdicts stand untouched.** The correlation tier
(§4.1) and the map's triple (§4.2) were already DEFERRED; this adds a second,
independent reason they cannot be taken at L1 as built.

### 4.1 **A LIVE FALSE ZERO, CAUGHT AND REFUSED — `CLAUDE.md` rule 3 in the wild**

The first y+ measurement pass used the **generic** utility,
`postProcess -func yPlus -region fluid`. It exited **rc 0** and printed, in this
order:

```
Unable to find turbulence model in the database: yPlus will not be calculated
patch fluid_to_housing y+ : min = 0, max = 0, average = 0
```

**A reader that parses only the second line reports y+ = 0 on the housing wall of
every case in this family — a perfect zero from a reader the tool had ALREADY
SAID cannot see a non-zero.** The zeros were **REFUSED, not read**; the same
field measured through the solver's own `-postProcess` returns 0.395 … 1.397.

The grader now carries that refusal as a guard, with **both limbs driven** in its
selftest: a BLIND log returns the sentinel and its zeros never reach a value
slot, and **the same reader on a good log returns 1.39698600399**, so the BLIND
result is a reading and not blindness.

---

## 5. COMPLETION UNDER RULE 4 — AND **TWO CONJUNCTS THAT WERE UNEVALUABLE FROM THEIR REGISTERED EVIDENCE**

Marked by `verification/runs/T-family/T23_runs/mark_done_t23.py`, exit **0**, four
`DONE.T23_P305_U*` markers written. **There was no T23 marker; the pattern used is
`T19_runs/mark_done_t19.py`** — the most recent marker this family froze, and the
one that already carries the L-342 physics/infrastructure field split — with
three registered differences (per-region field tuple per §3.5 conjunct 4;
age-guard reference `0/housing/T` per conjunct 6; `STATUS` inside the case
directory) and one forced difference recorded in §5.1 below. Selftest **PASS, 0
failed, under both `python3` and `python3 -O`**, with `__pycache__` cleared before
each run.

| # | conjunct | four cases | evaluated from |
|---|---|---|---|
| 1 | `rc = 0` | holds | **NOT `STATUS` — see §5.1.** DERIVED from `log.solve` |
| 2 | an `End` line | exactly **1** each | `log.solve` [MEASURED] |
| — | **zero `FOAM FATAL`** | **0** each | `log.solve` [MEASURED] |
| 3 | last time == `endTime` | **10000 == 10000** | time directories [MEASURED] |
| 4 | fields present | `T p` in `10000/{core,housing}`; `T U p p_rgh alphat nut k omega` in `10000/fluid` | disk [MEASURED] |
| 5 | `ExecutionTime` count == `endTime` | **10000** each at `deltaT 1` | `log.solve` [MEASURED] |
| 6 | **age guard** | every field at 10000 NEWER than that case's own `0/housing/T` | `st_mtime` [MEASURED] |

### 5.1 **CONJUNCT 1 IS UNEVALUABLE FROM `STATUS`, AND SAYING SO IS THE POINT**

`run_t23.sh` writes `rc` **inside** the wrapper on the line immediately after the
solver call — never around a `setsid` — together with `wall_s`, `ranks`,
`core_min`, `cap_core_min`, `timeout_s`, `capped` and `solver`. **The queue
runner overwrote every `STATUS.T23_*` after the launcher wrote it.** What
survives is three keys, and the file disclaims itself on its own face:

```
launcher_rc=0 end=2026-08-31T18:02:47Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc
```

* **`launcher_rc` IS NOT `rc` AND WAS NOT ACCEPTED AS `rc`**, even at 0 — a zero
  there is exactly the shape of the `setsid` trap the launcher exists to avoid.
  The marker refuses it explicitly and says so on every line it prints.
* **`rc = 0` IS THEREFORE `DERIVED-FROM-LOG`, NEVER `READ`**, from: exactly one
  `End` line, **zero** `FOAM FATAL`, and last time == `endTime`. Every marker line
  for these cases carries the literal tokens `UNEVALUABLE FROM STATUS` and
  `rc_source=DERIVED-FROM-LOG`.
* **THE DERIVATION IS NOT A RUBBER STAMP AND ITS SELFTEST PROVES IT.** Three
  arms are driven negative: `launcher_rc=0` with a `FOAM FATAL` in the log →
  **NOT DONE**; with no `End` line → **NOT DONE**; with last time 9000 → **NOT
  DONE**. A derivation that cannot return NOT DONE is not a derivation.
* **CORROBORATION, offered as corroboration and not as the basis.** The launched
  queue entry's `launch_cmd` is `["bash", ".../run_t23.sh"]` and that wrapper's
  final line is `exit "$rc"` [MEASURED], so `launcher_rc` **does** in fact
  propagate the solver's status through this particular argv — the same reading
  the T22 calibration row made. **Two independent paths agree on `rc = 0`. The
  marker still derives rather than reads**, because the runner's own note
  disclaims the propagation in general and a grader should not depend on a
  coincidence of wrapper shape.
* **SANAA'S UNIVERSAL RULE OF 2026-08-26 GOVERNS THE CHOICE NOT TO REFUSE:
  bookkeeping never voids physics.** The destroyed INFRASTRUCTURE fields
  (`wall_s`, `ranks`, `core_min`, `cap_core_min`, `timeout_s`, `capped`,
  `solver`) are reported **NOT MEASURED** and do not void the runs. The
  PHYSICS-CRITICAL conjuncts were all evaluated — on the log rather than on the
  ledger — and each says which.
* **`queue_runner.py` IS CFD'S INSTRUMENT. The clobber is ESCALATED, NOT REPAIRED
  BY THIS TEAM.** It is the same defect the T22 calibration row
  (`C-20260831T172527.907664Z-b006f781`) already recorded; **this is its second
  occurrence, now across five cases.**

### 5.2 **THE SECOND UNEVALUABLE CONJUNCT: §5.4's CONTENTION PRECONDITION HAS NO `START` FILE**

§5.4 registers, one-way and before the fact: *"a run whose recorded load average
at launch shows a saturated box produces a COST but NOT a calibration row … Each
launcher writes a `START.<case>` file **before** the solver starts, carrying
`start_utc`, all three `/proc/loadavg` windows and `nproc`."*

**NO `START.T23_P305_U*` FILE EXISTS FOR ANY OF THE FOUR CASES, AND
`run_t23.sh` CONTAINS NO CODE TO WRITE ONE** [MEASURED, on disk and in the
launcher's own text]. **This is a divergence between §5.4's registered text and
the launcher actually used, and it is reported rather than smoothed over.** The
frozen document is not edited (rule 6); the launcher is not retro-fitted.

**The precondition was therefore evaluated from a different artifact, and the
substitution is named:** the queue runner's own `verification/queue/runner.log`
records the box state at each of the four launch instants [MEASURED]:

| case | launch | box busy | cores busy | MemAvailable |
|---|---|---:|---:|---:|
| `T23_P305_U10` | 2026-08-31T17:33:02Z | **11.9 %** | ~1.9/16 | 29.0 GB |
| `T23_P305_U20` | 2026-08-31T17:34:07Z | **12.7 %** | ~2.0/16 | 28.9 GB |
| `T23_P305_U30` | 2026-08-31T17:35:12Z | **22.3 %** | ~3.6/16 | 28.6 GB |
| `T23_P305_U40` | 2026-08-31T17:36:17Z | **25.7 %** | ~4.1/16 | 28.5 GB |

**The box was NOT saturated at any launch — worst reading 25.7 % of 16 cores — so
§5.4's refusal condition is NOT met and the calibration row of §6 is
admissible.** Said plainly: the conjunct could not be evaluated from the
instrument the registration named, and it *was* evaluated from a named substitute
whose reading is recorded above.

---

## 6. COST CALIBRATION — `CLAUDE.md` rule 12, discharged

`docs/COST_CALIBRATION.md` row **`C-20260831T183346.079343Z-d971eca8`**. **That id was MINTED BY
`scripts/append_record.py --allocate-id` in the same shell invocation that landed
this record**, and is substituted here from the tool's own output — it is not a
number this lane chose. The module is the sole producer of that id form and
**refuses any rows text that hand-writes one**, which is why the T22 row is cited
elsewhere in this document by its date and subject rather than by its id.

| figure | value | tag |
|---|---:|---|
| registered SUBSET POINT | **123.2 core-min** | **REGISTERED**, §5.2 |
| registered SUBSET CAP | **400.0 core-min** hard | **REGISTERED**, §5.2 |
| **actual, gross == cleaned** | **120.1285 core-min** | **MEASURED** |
| **ratio actual/predicted** | **0.9751** | **DERIVED** |
| cap utilisation | **30.03 %** | **DERIVED** |
| USD at actual | **$0.102710** | **DERIVED, NOT MEASURED** |
| measured per-cell-iteration rate | **4.541148e-06 s** | **MEASURED** |

Per case, from each case's own `log.solve` `ExecutionTime` line at 1 rank:
**29.7337 / 30.2190 / 30.4898 / 29.6860 core-min**, against a per-case POINT of
30.8 and a per-case CAP of 100.0 enacted as `timeout 6000s`.

**GROSS AND CLEANED ARE IDENTICAL, and that is stated rather than assumed.** The
`COMPUTE_BUDGET_CHARTER.md` §2 stall rule matches a row over **3600 wall s**; the
longest case ran **1829.39 s**, so the rule matches nothing and no judgement
enters the figure.

**WASTE, NAMED SEPARATELY AND NEVER FOLDED INTO THE RATIO** (charter §6):
**0.0 core-min.** All four cases launched clean on the first attempt; there is no
failed T23 launch. Separately named and also not in the ratio: the **y+
measurement passes cost 2 wall s total at 1 rank = 0.0333 core-min** [MEASURED],
which is analysis cost, not waste and not part of the registered solve budget.

**ATTRIBUTION.** **CONTENTION: measured and small** — §5.2's table shows 11.9 %
to 25.7 % box busy at launch, and the four cases ran concurrently on a 16-core
box, so ~4 of 16 cores were in use by this rung; the four ExecutionTimes span
only 1781.16–1829.39 s, a **2.7 % spread**, which is what a low-contention
sequence looks like. **WASTE: 0.0.** **MISPREDICTION: the entire 2.5 % residual,
and it is conservative by design.**

> **THE TRANSFERABLE FINDING, and it is a second confirmation rather than a new
> claim.** The registered POINT took the **conservative end** of a MEASURED
> Cartesian bracket — `T5_CUBE_m` 4.1541e-06 and `T5_CUBE_f` 4.6476e-06 s per
> cell-iteration — and the ACTUAL rate is **4.541148e-06**, which lands **INSIDE
> that bracket**, near its `_f` end. **So a 5° wedge with two solid regions, two
> conjugate `mappedWall` interfaces, a sector-scaled volumetric source and a
> `kOmegaSST` fluid region costs, per cell-iteration, what a Cartesian
> single-solid sourceless case costs.** §5.1 registered the anchors as *"a LOWER
> BOUND on the per-cell rate, not a bracket around it"*; **the measurement says
> they are a bracket.** T22 said the same at 4.22999e-06 on the same geometry at
> half the iteration count. **Two independent same-geometry measurements now
> agree, and this is offered as a MEASUREMENT and not as a rule** (Sanaa's
> 14-day plumbing freeze, `etc/sessions/2026-08-31T1544Z_sanaa_plumbing_freeze.md`).

**THE CONTRAST WORTH RECORDING, because it is the calibration lesson.** T19b's
ladder missed by **3.25×** while T22 and T23 landed at **0.908** and **0.9751**.
The difference is not luck and is not effort: **T19b borrowed its rate ACROSS A
GEOMETRY CHANGE** (T1c, a **pipe**, lent its rate to a **plane channel**), while
T22 and T23 borrowed **across DIMENSIONALITY at similar geometry** (a Cartesian
single-solid CHT cube lending to a CHT wedge). **A borrowed per-cell-iteration
rate survives a change of dimensionality and does not survive a change of
geometry family.**

### 6.1 **§5.3's COST FINDING IS NOW ANSWERABLE, AND THE ANSWER IS NOT THIS DOCUMENT'S TO REGISTER**

§5.3 recorded that the directive's own three figures are mutually inconsistent,
and that *"the resolution belongs to the later registration of §6.4, informed by
the ACTUAL per-case cost the four cases of §6.2 will measure."* **That cost is
now measured: 30.0321 core-min per case.**

Arithmetic, offered to the later registration and registering nothing here:
16 points × 30.0321 = **480.5 core-min POINT**, comfortably inside the
directive's 700 core-min Case 3 cap and within 0.1 % of the directive's own
*"~8 core-h"* (480 core-min). At this rung's 3.25× headroom the CAP would be
**1,562 core-min**, still **2.23×** the directive's 700. **The tension §5.3
identified is unchanged in kind and slightly reduced in size, and choosing
between the two remains a registration decision — reserved, not taken here.**

---

## 7. **§6.4's TWO NAMED PRECONDITIONS FOR THE TWELVE DEFERRED POINTS ARE NOW BOTH DISCHARGED**

§6.4 named exactly two things the later registration of the twelve deferred
points needs, *"so the deferral is actionable rather than decorative"*:

| § 6.4 precondition | status |
|---|---|
| **1. a measured per-case cost for this geometry** | **DISCHARGED** — 30.0321 core-min per case, MEASURED, §6 above |
| **2. a demonstrated completion at this geometry BY A CASE THAT RAN UNDER A FROZEN REGISTRATION** (not by T22) | **DISCHARGED** — four cases, all six rule-4 conjuncts, under `fe666fd5` |

**Both are met. The twelve points of §6.4 are therefore writable as a successor
registration, and writing it is the supervisor's call and not this lane's.** What
that successor must weigh, from this record: the §2 lumped model that chose the
levels is falsified by 1.9×–3.5× (§2 above), so its 2-of-16 flag arithmetic no
longer describes the solved physics; and max y+ exceeds 1 on the housing at
U ≥ 30 m/s at L1 as built (§4).

**Nothing here amends T23.** §4.5's isotherm trace stays deferred; §4.1, §4.2,
§4.3 and §4.6 stay deferred with their reasons; the four PASS rows are the whole
of what this rung earned.

---

## 8. ARTIFACTS

| what | path |
|---|---|
| frozen registration | `docs/campaigns/T-family/T23_PREREGISTRATION.md` (`fe666fd5`) |
| marker | `verification/runs/T-family/T23_runs/mark_done_t23.py` |
| grader | `verification/runs/T-family/T23_runs/analyse_t23.py` |
| grading output | `verification/runs/T-family/T23_runs/T23_GRADE.txt`, `T23_GRADE.json` |
| completion markers | `verification/runs/T-family/T23_runs/DONE.T23_P305_U{10,20,30,40}` |
| cases | `verification/runs/T-family/T23_runs/T23_P305_U{10,20,30,40}/` |
| solver logs | each case's `log.solve` |
| y+ measurement | each case's `log.yPlus.fluid` |
| launch record | `verification/queue/LAUNCH_LOG.tsv`, `verification/queue/runner.log` |
| queue entries | `verification/queue/heat-transfer/launched/T23_P305_U*.json` |
| calibration row | `docs/COST_CALIBRATION.md` |

**Sanaa's 14-day rule freeze is honoured** (`etc/sessions/2026-08-31T1544Z_sanaa_plumbing_freeze.md`):
this record proposes **no new procedural or bookkeeping rule and creates no new
tool**. The marker and the grader are existing lab patterns applied to a new
rung. The findings of §2 (the falsified lumped model), §4.1 (the y+ false zero),
§5.1 (the second `STATUS` clobber) and §5.2 (the missing `START` files) are
**recorded as findings and spawn no rule and no tool**.

**A supervisor's check is not claimed as performed here.** `SUPERVISION_CHARTER.md`
§3's four checks are the supervisor's own. **No agent's message is Sanaa's
consent** (`CLAUDE.md` rule 9).
