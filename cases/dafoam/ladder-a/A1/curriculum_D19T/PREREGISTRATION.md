# CURRICULUM D19T — PRE-REGISTRATION

**The `shape[7]` gradient component whose plateau never closed: is it a broken adjoint, or a near-null direction measured through a convergence bias?**

| | |
|---|---|
| item | `D19T` |
| family | dafoam, ladder-a, A1 — NACA0012 compressible, `DARhoSimpleFoam`, M 0.288, 4,032 cells |
| authority | **SANAA-DIRECT**, §5 of `etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md` |
| run root | `/home/ubuntu/certonomous-runs/CURRICULUM-D19T-a1-naca0012-shape7-primal-tightening` |
| status at freeze | **PENDING** — no compute has run; the run root is asserted ABSENT below |
| verdict ceiling | **`GATE REACHED`** — reason in §9, and it is a real cap, not a hedge |

---

## 0. THE THREE THINGS THIS DOCUMENT SAYS BEFORE IT ASKS FOR ANY COMPUTE

Written first because each one changes what is worth running, and two of them **correct the brief this item was given**.

### 0.1 Sanaa's instruction "converge each perturbed primal to 1e-8" is ALREADY SATISFIED in the run it is meant to fix

`curriculum_D19R/d19r_runScript.py:45` already carries `"primalMinResTol": 1.0e-8`, and D19R's own sweep log reports, **82 times out of 82 solves**:

> `Minimal residual 9.967402926059662e-09 satisfied the prescribed tolerance 1e-08`

*(artefact: `.../CURRICULUM-D19R-.../S8_20260831T225738Z_623705.log`; the achieved residuals span 9.087e-09 to 9.998e-09 across all 82.)*

**Executing §5 literally would re-run the identical experiment and report that nothing changed.** The tightening therefore goes **below** 1e-8 — which is the direction §5 intends, since its stated purpose is "so FD noise is below the plateau", and the measurement in §0.2 shows 1e-8 does not achieve that. The registered ladder is **1e-8 → 1e-10 → 1e-12**, with 1e-8 kept as the **reproduction control**, not as a treatment.

### 0.2 The adjoint is NOT off on `shape[7]`. Sanaa's §5 conditional has a FALSE antecedent, and it is false on artefacts already on disk

§5 says *"**If** the adjoint is off on that component alone, check whether its path depends on a non-differentiated quantity (wall distance)."* The antecedent is measurable now, and it is false:

| component | adjoint `dCD/dshape[i]` | FD at its own flattest step | agreement |
|---|---|---|---|
| `shape[0]` | −7.221767e−03 | −7.220458e−03 (h=3e−3) | **0.018 %** |
| `shape[3]` | +9.290536e−03 | +9.296902e−03 (h=1e−3) | **0.069 %** |
| `shape[6]` | −1.413381e−02 | −1.413313e−02 (h=1e−3) | **0.005 %** |
| **`shape[7]`** | **−2.099480e−04** | **−2.095615e−04 (h=3e−3)** | **0.184 %** |

*(adjoint: `.../CURRICULUM-D19R-.../X2/d19r_X.json`; FD: `.../S8/d19r_S.json`.)*

**`shape[7]`'s adjoint agrees with its own finite difference to 0.184 %.** It is not an outlier; it is the fourth-best of four. **The wall-distance investigation §5 makes conditional is therefore NOT RUN, and this document registers that refusal in advance rather than discovering it afterwards.** A CD-specific frozen-`d` path is separately argued against in §3 (H2).

What actually failed in D19R was the **plateau criterion** — a property of the FD instrument — not the adjoint.

### 0.3 The FD floor is a shared additive BIAS of |ε| ≈ 4.7e−9 in CD, and every noise arm D19R ran measured SCATTER instead

Define ε ≡ (FD(h) − adjoint) · h. A fixed additive error in CD appears here as a **constant**, independent of h. Measured on D19R's landed sweep:

| component | h=3e−4 | h=1e−4 | h=3e−5 | h=1e−5 |
|---|---|---|---|---|
| `shape[0]` | +4.866e−09 | +4.554e−09 | +4.857e−09 | +4.701e−09 |
| `shape[3]` | +4.999e−09 | +4.642e−09 | +4.870e−09 | +4.776e−09 |
| `shape[6]` | −4.658e−09 | −4.840e−09 | −4.056e−09 | −2.892e−09 |
| `shape[7]` | +4.599e−09 | +4.695e−09 | +4.803e−09 | +4.619e−09 |

**Sixteen estimates. The magnitude is ~4.7e−9 everywhere, across four components and a 30× range in h; only the sign is per-component.** That is one number belonging to the instrument, not four numbers belonging to four components.

Three noise figures now exist for this case and they differ by 36×:

| figure | value | what it measures | why it missed this |
|---|---|---|---|
| `eta_raw` | 1.3011e−10 | baseline vs baseline-repeat | same inputs → deterministic |
| D19R arm `N2` | ~7e−10 | 3 repeats at a fixed perturbed geometry | still a repeat |
| **ε (this document)** | **~4.7e−9** | **bias vs the exact solution** | **not visible to any repeat** |

**A repeatability arm cannot bound a convergence bias.** Repeating a solve reproduces the bias exactly, so `eta` and `N2` were both structurally incapable of seeing the thing that broke the plateau. This is the instrument lesson of the item, and it is registered before the run.

---

## 1. WHY `shape[7]` AND NOTHING ELSE FAILS — the mechanism, stated as a prediction

`shape[7]` is the **trailing-edge thickness mode** of the 5×2×2 FFD (`d19r_runScript.py:152-153`: for `i` at the chord ends, `j=0` and `j=1` move in *opposite* y directions, so the edge point is fixed and only local thickness varies). `shape` is the **only** design variable in this set; there is no twist DV.

On a symmetric NACA0012 with a nearly closed trailing edge, thickening or thinning the TE is close to a **null direction of drag**:

| ratio | in CD | in CL |
|---|---|---|
| \|adj[7]\| / \|adj[6]\| | **1.4854 %** | 191.6 % |
| \|adj[7]\| / \|adj[3]\| | **2.2598 %** | 35.7 % |
| \|adj[7]\| / \|adj[0]\| | **2.9072 %** | 45.5 % |

**The mode is not geometrically inert — it is one of the strongest lift modes in the set. It is near-null specifically in drag.** So the same fixed |ε| ≈ 4.7e−9 that is invisible against `shape[6]`'s 1.4e−2 signal is fatal against `shape[7]`'s 2.1e−4.

Two consequences follow arithmetically and are registered as **predictions**:

**(a) The h=1e−5 sign flip is not physical.** D19R's `shape[7]/CD` changes sign between 3e−5 and 1e−5. The ε model predicts FD(1e−5) = −2.0995e−4 + 4.5e−9/1e−5 = **+2.4005e−4**; measured **+2.5192e−4**. The flip is ε/h overtaking the signal, nothing more.

**(b) Closing the fine side needs only a factor 2.23 reduction in |ε|.** The plateau at centre h=1e−3 is graded against decade neighbours 1e−2 and 1e−4. The coarse side is truncation-dominated and already passes at 1.17 %. The fine side needs

> |ε| ≤ 0.10 × |dCD/dshape[7]| × 1e−4 = **2.0995e−09**, against a measured **4.6789e−09**.

If ε is proportional to the achieved primal residual, **1e−10 gives a 45× margin and even 1e−9 would suffice.**

**The precedent is this lane's own.** `DAFOAM_CHARTER.md` §3: at `primalMinResTol 1e-6` "the cold primal stops at its **first** tolerance crossing" and central FD misses the adjoint by 25.9 %; one pair re-run at 1e-8 moves the same cell to **0.032 %** — *"The step was never the problem; the primal's stopping rule was."* D19T is that sentence one rung down, on the one component whose signal is small enough to expose the next decade.

**And the counter-precedent is registered too, because it cuts the other way.** `A5_ubend_internal.md`: tightening solver tolerances 1–2 orders and running 10× more iterations moved the aggregate **46.64 % → 46.21 %** and made sign flips *worse*, 2 → 3. `VERIFICATION_CHARTER.md` §7 warns *"do not prescribe 'converge harder' before checking whether convergence is available."* **A5 is the outcome in which this item fails**, and §3's falsifiers are written so that outcome is reportable rather than explained away.

---

## 2. THE PRIMAL'S CONVERGENCE BUDGET — measured, so the cost is not a guess

From D19R's `S8` log, the reference solve's `U0` initial residual: 1.09e−3 (iter 100) → 3.55e−5 → 1.84e−6 → 9.18e−8 → 4.35e−9 (iter 500), stopping at **iteration 502**.

> **Measured rate: 1.35 decades per 100 SIMPLE iterations.**

| target | extrapolated iterations | vs 502 | fits `endTime 1000`? |
|---|---|---|---|
| 1e−8 | 502 (**measured**) | 1.00× | yes |
| 1e−10 | ~650 (**extrapolated**) | 1.30× | yes |
| 1e−12 | ~800 (**extrapolated**) | 1.59× | yes, with ~200 iterations spare |

**`controlDict` `endTime 1000` is NOT changed.** Only `primalMinResTol` moves. The mesh, schemes, linear solvers, decomposition and producer bytes are all held.

**REGISTERED RISK, with its own outcome.** Whether the residual continues below 1e−9 without stalling is **UNKNOWN** — D19R has no data below 1e−9. If a solve does not reach its registered tolerance within `endTime 1000`, DAFoam prints no "satisfied the prescribed tolerance" line for it, `G-TOL` sees a **short count**, and that arm is **`GATE FAIL`** with the shortfall named. It is not silently graded on an unconverged CD. If 1e−12 is unreachable but 1e−10 is, the item still has its headline and reports 1e−12 as **`BLOCKED`** with the achieved residual quoted.

---

## 3. THE HYPOTHESES, AND WHAT FALSIFIES EACH — registered before the run

Three hypotheses. **The single ε-ladder separates all three**, because they make different predictions about how ε moves with the primal tolerance and about *where* any residue sits.

### H1 — NEAR-NULL DIRECTION MEASURED THROUGH A CONVERGENCE BIAS *(this lane's hypothesis)*

The FD numerator is small because the mode is near-null in drag; the additive CD bias from stopping at the first tolerance crossing is fixed; the ratio explodes as h shrinks. **A property of the baseline and the instrument, not of the adjoint.**

**H1 predicts, and is FALSIFIED if any of these fails:**
1. |ε| falls by **≥ 10×** from tol 1e−8 to 1e−10 (`G-EPS`).
2. The plateau at h=1e−3 **closes two-sided within the UNCHANGED 10.0 % band** at 1e−10 (`G-PLAT7`).
3. The **coarse end does not move**: FD at h=3e−2 and h=1e−2 change by < 1 % relative between 1e−8 and 1e−10, because their error is truncation and tightening does not touch truncation.
4. The **h=1e−5 sign flip disappears** and FD(1e−5) returns to ≈ −2.1e−4.
5. The **contrast control `shape[6]` barely moves** — its ε/h is negligible against a 68× larger signal.

**Predictions 3 and 5 are the ones that make this more than "we tightened it and it got better."** A change that moved the coarse end too, or moved `shape[6]` as much as `shape[7]`, would not be the mechanism claimed here even if the plateau closed.

### H2 — A NON-DIFFERENTIATED DEPENDENCY, SPECIFICALLY WALL DISTANCE *(Sanaa's hypothesis)*

A TE thickness mode moves the surface where the wall-distance field is most sensitive; Spalart–Allmaras depends on `d`; if `d` is frozen in the adjoint, that sensitivity path is missing.

**H2 predicts:** a residual adjoint-vs-FD discrepancy on `shape[7]` that **survives** tightening, on this component alone.

**H2 is ALREADY IN DIFFICULTY on landed evidence, and that is stated in advance rather than discovered:**
- The adjoint on `shape[7]/CD` agrees to **0.184 %** (§0.2). There is no discrepancy to explain.
- **`shape[7]/CL` is healthy at exactly the steps where `shape[7]/CD` fails** — two-sided deviations 0.029 % / 0.185 %, and adjoint agreement 0.003 % at h=1e−2. CL and CD are the *same* surface integral over the *same* converged state with the *same* wall-distance field and the *same* `nuTilda`. **A frozen `d` that broke the `shape[7]` path would break `shape[7]/CL` too. It does not.**

**H2 would nonetheless be SUPPORTED if:** `G-EPS` shows ε failing to fall, **and** the residue is confined to `shape[7]/CD` while `shape[6]` and `shape[7]/CL` stay clean. **If that happens, the wall-distance investigation is the next item** — read from the image's own source, never from documentation — and this item reports `GATE FAIL` on H1 rather than dressing the outcome up.

### H3 — PARALLEL REDUCTION BIAS

ε is an artefact of the np=2 reduction order rather than of convergence.

**H3 predicts:** ε is **independent of the tolerance**, and is present for **every** component including the contrast control.

**H3 shares "ε does not fall" with H2 and is separated from it by location:** H3 puts the residue everywhere, H2 puts it on `shape[7]/CD` alone. `G-EPS` reports ε per arm for **both** components precisely so this separation is readable. **If H3 survives, the follow-on is an np=1 arm** — named here as NOT RUN in this item, because changing np and the tolerance together would confound them.

---

## 4. THE REGISTERED DESIGN

### 4.1 Steps — Sanaa's four, verbatim, plus a trivial baseline

`STEPS = [3.0e-2, 1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5]`

- **`1e-2, 1e-3, 1e-4, 1e-5`** are Sanaa's four, unchanged.
- **`3e-2` is the `DAFOAM_CHARTER.md` §4 trivial baseline** — the same probe at a deliberately wrong step, 30× the registered centre. It is measured as a row and is **never a plateau centre**. On D19R's landed data it sits **29.83 %** from the adjoint, and §5 predicts it **stays failed** under tightening.

### 4.2 The plateau reading

| | |
|---|---|
| centre | **h = 1e−3** — the only one of Sanaa's four with both decade neighbours present AND inside `VERIFICATION_CHARTER.md` §7 step 5's sanctioned range [1e−3, 1e−2] for `shape` |
| neighbours | h = 1e−2 (coarse) and h = 1e−4 (fine) |
| stride | **1 index**, because this is a DECADE grid — proved against the ladder by `assert_decade_stride()`, not asserted in prose. D19R needed stride 2 on its half-decade grid; the *decade separation* is identical and the band is not relaxed by regridding |
| band | **10.0 %, two-sided, max over both sides and BOTH functions** — byte-for-byte D19R's `G19R-1b`. A tightened primal graded on a looser band would be answering an easier question than the one that failed |
| h = 1e−4 as a centre | measured and **REPORTED NOT GRADED** — below §7's sanctioned range |

**No step selection happens in this item.** The centre is registered, not chosen, so `DAFOAM_CHARTER.md` §3's "selecting the step after seeing which one agrees" is unreachable by construction. There is consequently no selection-sensitivity control, and that absence is stated rather than papered over with an inapplicable one.

### 4.3 Components

| | |
|---|---|
| **GRADED** | `shape[7]` — Sanaa's "that component only" |
| **CONTRAST CONTROL, NON-GRADED** | `shape[6]` (leading-edge thickness) at the same steps |

`shape[6]` is registered as a control, not as a second graded row. The signature separating H1 from H3 is **differential** — "the noise-limited component moved and the signal-rich one did not" is a claim about two numbers, and measuring one cannot make it.

### 4.4 Arms

| arm | ranks | mode | `primalMinResTol` | purpose |
|---|---|---|---|---|
| `MESH` | 1 | — | n/a | mesh, cell count, and D15 byte-identity |
| **`T08`** | 2 | T | **1e−8** | **REPRODUCTION CONTROL** — re-measures D19R's condition with *this* harness |
| `T10` | 2 | T | 1e−10 | treatment |
| `T12` | 2 | T | 1e−12 | third point of the scaling law |
| `XT10` | 2 | X | 1e−10 | adjoint at the treatment tolerance |

**`T08` is the experiment's own planted zero.** A before/after with no demonstrated "before" is one measurement wearing two labels. `G-REPRO` requires T08 to (a) reproduce D19R's landed `shape[7]/CD` at every step within **5 %**, and (b) **FAIL the plateau, as D19R did**. **T08's plateau failure is its success condition**, is registered as non-graded for row purposes (`ARM_PLATEAU_GRADED`), and cannot be granted as an excuse afterwards to a reproduction arm that disappointed. If T08 *closes* the plateau, this harness is not D19R's instrument and every downstream claim is **withdrawn**.

**np = 2 on every solver arm**, matching D19R's `S8` and `X2` exactly (`scotch`, 2 subdomains). A4 measured a 16,600× spread between two decompositions of one mesh; changing np would confound the decomposition with the tolerance and destroy the reproduction control. `DAFOAM_CHARTER.md` §5's serial-first clause is satisfied by the case's existing np=1 history, and an np=1 confirmation is named in §3 (H3) as a follow-on this item does not run.

### 4.5 The instrument change, and the three readings that prove it took

`primalMinResTol` is applied by mutating `ns["daOptions"]` in the exec'd namespace **before** `Top()` is instantiated. **The frozen producer `d19r_runScript.py` is borrowed UNEDITED** and its md5 is asserted in the launcher, in the executor, and at staging.

1. `d19t_xf.py` asserts the mutation landed in the namespace and **refuses** if not.
2. It emits `primalMinResTol_requested` and `..._in_namespace` into the artefact.
3. **`G-TOL` reads the ARM LOG** and requires every registered solve to print `satisfied the prescribed tolerance <R>` with R the registered value.

**Reading 3 is the load-bearing one**: 1 and 2 can only prove what this process *believed*; 3 is the solver stating what it *honoured*. `G-TOL` **fails closed on a count of zero** — no lines is not "nothing contradicted it" — and fails on a short count, which is how an unconverged solve is caught.

### 4.6 `system/decomposeParDict` — pre-normalised, and no gate is widened

D19R2 was BLOCKED here: the age guard refused `MANIFEST_ENTRY_MUTATED` on this path in exactly the three np=2 arms, five `kahipCoeffs` lines that `decomposePar` writes back into the dictionary it read. **That refusal was correct**, and D19M's guard explicitly declines to add an exclusion because doing so is a gate-design decision reserved to Sanaa.

**D19T excludes nothing and widens nothing.** Staging writes the dictionary **already normalised**, so the bytes the manifest pins are the bytes `decomposePar` will write, and `G-MANIFEST` still requires **ZERO** mismatches on every arm — a strictly stronger outcome than D19R achieved.

**The fixed point is measured, not assumed:** D19R's `X2` and `S8` arms wrote this file independently and both landed on md5 `c3f5f05d45f0b9a70d645b107a837727` from the same `68ecc827562886fb43c3aedb0627b344` input. Two independent writes, one result. Staging asserts that md5 before the manifest is built and **refuses** otherwise.

*(Recorded because it is the kind of thing that otherwise passes silently: the first reconstruction of this block produced md5 `d5a844d94d93929888b4879d189f48e0`, because two of the five lines carry a trailing space that OpenFOAM writes and a hand-retyped block does not. **The md5 assert caught it before the freeze.** A "pre-normalisation" that merely looked right would have re-created the D19R2 blocker at run time.)*

---

## 5. THE GATES — thresholds, bands and labels, frozen here

| gate | reads | threshold | verdict if not met |
|---|---|---|---|
| `G-TOL` | the arm log's own tolerance statements | every registered solve prints the registered tolerance; count == 22 | `NOT A RESULT` on zero lines; `GATE FAIL` on wrong tolerance or short count |
| `G-PLAT7` | `shape[7]` FD, both functions | two-sided decade deviation ≤ **10.0 %** at h=1e−3 | `GATE FAIL` |
| `G-REPRO` | T08 vs D19R's landed values | every step within **5 %**, **and** T08 fails its plateau | `GATE FAIL` |
| `G-ADJ` | adjoint vs FD at h=1e−3 | ≤ **10.0 %** | `GATE FAIL` |
| `G-TRIVIAL` | adjoint vs FD at h=3e−2 | **MUST EXCEED 10.0 %** | `GATE FAIL`, and it **WITHDRAWS** `G-ADJ` |
| `G-EPS` | ε at h=1e−4, 1e−5, three arms | \|ε(1e−8)\| / \|ε(1e−10)\| ≥ **10×** | `GATE FAIL` — H1 not supported |
| `G-COMPLETE` | rc, terminal statement, fatal tokens, age guard | all clauses (rule 4) | `GATE FAIL` |
| `G-MANIFEST` | input manifest per arm | **0** mismatches | `GATE FAIL` |
| `G-CAPS` | ledger core-minutes | per-arm cap and item ceiling | `GATE FAIL` |
| `G-NP` | ledger ranks | np == registered per arm | `GATE FAIL` |
| `G-PLACE` | ledger cpuset | cpuset == `5,13` | `GATE FAIL` |
| `G9-TOOLCHAIN` | image digest, `libidwarp.so` md5 | the registered PATCHED row | `GATE FAIL` |
| `G-STAGES` | declared vs executed | 5 of 5 arms | `NOT A RESULT` |

**Verdict vocabulary is the six tokens and nothing else.** The grader refuses on any token outside it.

### 5.1 The planted-zero controls (rule 3)

**Six readers, each planted at grade time into a separate copy, read back through the real reader function, both legs required:**

| reader | feeds | the hazard |
|---|---|---|
| `R1_read_ledger` | caps, np, placement, toolchain | no ledger → no rows → every cap gate green |
| `R2_read_fatal_tokens` | `G-COMPLETE` | an unreadable log yields zero fatal tokens and reads as clean |
| `R3_read_tolerance_lines` | **`G-TOL`** | zero lines must not read as "nothing contradicted it" |
| `R4_read_fd` | plateau, adjoint, ε, reproduction | a missing row read as absent rather than as a failure |
| `R5_read_adjoint` | `G-ADJ`, `G-EPS` | a zero adjoint makes every relative agreement trivially small |
| `R6_read_manifest_mismatches` | `G-MANIFEST` | **zero IS the pass condition** |

Both legs are required of each: the reader **sees** a planted non-zero, **and** returns empty on clean input. `n_not_born != 0` or `n_zero_leg_unproved != 0` is a **refusal (exit 2)**, not a footnote, and the register is emitted into the graded JSON.

The FD-side plant is `plant = K · (band/100) · |d_ref|` with **K = 5.0 crossing** and the **sufficiency red leg K = 0.5 not crossing** — sized to the band by construction, because `SO-2M` was lost to an absolute plant that was 2.48 % of its own reference and could not cross its own 5 % band.

### 5.2 The selftests, run before this freeze

- `d19t_xf.py --selftest` — **OK**. Decade stride proved against the ladder and driven red on a half-decade one; the tolerance refused off-ladder (exit 2) and when omitted (exit 64); both plant legs.
- `d19t_age_guard.py --selftest` — **OK**. Every red leg fired.
- `d19t_grade_selftest.py` — **OK**. Green leg composes to uncapped `PASS` → capped `GATE REACHED`; **12 red legs all fire**; a blinded `R3` **refuses** the whole grading (`CONTROL_READER_NOT_BORN`); L-332 assert counter proved against a planted assert.

---

## 6. COST — costed here, per rule 12, and the provenance of every figure is tagged

**Measured basis** *(from D19R's `ledger.txt`, arm `S8`: rc=0, wall 182 s, ranks 2, **6.067 core-min**, 82 converged primal solves)*:

> **0.0740 core-min per converged primal solve at tol 1e−8** — **MEASURED**, artefact `.../CURRICULUM-D19R-.../ledger.txt`.

**Solves per T arm: 22** = 2 components × 5 steps × 2 sides + baseline + baseline-repeat.

| arm | solves | per-solve factor | predicted core-min | tag |
|---|---|---|---|---|
| `MESH` | — | — | 0.183 | **MEASURED** (D19R `MESH`) |
| `T08` | 22 | 1.000 | **1.628** | **MEASURED** basis |
| `T10` | 22 | 1.295 | **2.108** | **EXTRAPOLATED** (§2 iteration count) |
| `T12` | 22 | 1.590 | **2.589** | **EXTRAPOLATED** (§2) |
| `XT10` | 1+adj | 1.295 | **1.726** | **EXTRAPOLATED** from D19R `X2` = 1.333 core-min MEASURED |
| | | **total predicted** | **8.234 core-min** | |

**Caps.** Worst case per solve is the primal running to `endTime 1000` instead of stopping at 502: 0.1474 core-min (**EXTRAPOLATED**). 22 × 0.1474 = 3.243 core-min per T arm.

| arm | cap (core-min) | in-container deadline |
|---|---|---|
| `MESH` | 1.0 | 0 s + margin |
| `T08`, `T10`, `T12` | **4.0** each | 60 s each |
| `XT10` | **5.0** | 90 s |
| **ITEM CEILING** | **18.0** | checked after **every** arm |

Cap/predicted = **2.19×**. **An overrun stops the run and does not get a new budget** — enforced in `d19t_run_arm.sh` (per-arm, exit 9) and in `d19t_chain_driver.sh` (item ceiling, after every arm).

**Dollars are DERIVED, never measured** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). At the owner-stated $0.0513/core-h: predicted 8.234 core-min = 0.1372 core-h → **$0.0070 DERIVED**; ceiling 18.0 core-min = 0.30 core-h → **$0.0154 DERIVED**. Under the $25 pre-authorisation, and costed anyway, because a blanket is not a per-item read.

**"Cost is not a constraint" removes the approval barrier, not the costing obligation.** The estimate-versus-actual row for `docs/COST_CALIBRATION.md` is **OWED AT ITEM COMPLETION** and this item is not complete.

**Memory: `4g`**, sized from measurement — the A1 4,032-cell adjoint peaked at 1137–1189 MiB (`ADJOINT_MEMORY_ENVELOPE.json`) and D12R2's measured peak RSS is 1.3461 GiB; 4g is ~3.0× the measured peak. The 20g inherited elsewhere in this family is ~15× oversized and has already caused one avoidable memory-guard collision.

**Placement: cpuset `5,13`**, distinct from D19R's `1,15` and D19M's `13`, gated by `G-PLACE`.

---

## 7. THE ABSENCE ASSERT, BY EXECUTION

`d19t_chain_driver.sh assert-absent` was executed at this freeze and printed:

> `D19T_ROOT_ABSENT_ASSERTED /home/ubuntu/certonomous-runs/CURRICULUM-D19T-a1-naca0012-shape7-primal-tightening does not exist at 2026-09-01T16:22:01Z`

The chain **re-asserts** this immediately before the first arm and **refuses** if the root exists. An existing root may carry a `0/` or a time directory from an earlier attempt, and rule 4's age guard exists precisely because that case is not distinguishable after the fact. **The refusal is not a prompt to delete it.**

At this freeze the box was idle: no `d19t_`/`d19*` containers running, no run directory touched within 10 minutes, `docker ps` empty.

---

## 8. THE INSTRUMENT TABLE — every file this item EXECUTES or IMPORTS (`DAFOAM_CHARTER.md` §18.3)

Existence asserted before md5; md5s computed at this freeze.

| file | md5 | bytes | role |
|---|---|---|---|
| `d19t_xf.py` | `bd72246dab1dd7035c85e13662894b56` | 26,726 | executor |
| **`d19t_grade.py`** | **`bc6d694a7805a0d507be024dda8fd4fa`** | 47,169 | **THE GRADING PATH** |
| `d19t_grade_selftest.py` | `e82d2ceba2306b10e44a96fa9b5cc588` | 16,521 | grader selftest |
| `d19t_age_guard.py` | `370549193036912d2332e44092bcfd38` | 26,763 | age guard + manifest |
| `d19t_run_arm.sh` | `c1013f8ce5d927428ac75fdc0c76bef4` | 18,962 | arm launcher |
| `d19t_chain_driver.sh` | `07aa0d5aba0c7475ec141339f3ca45e9` | 4,092 | chain + ceiling |
| `d19r_runScript.py` | `a5e18503ea29d0e37c3cf1668533cd34` | — | **BORROWED FROM D19R, UNEDITED** |

Toolchain, by digest and library hash, never by version string:

| | |
|---|---|
| image | `dafoam-idwarp-rot:v1`, row **PATCHED** |
| digest | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` |
| `libidwarp.so` | `85f59e87253e0a71a813f64ca6e4c425` |

**The grading path is fixed at this commit.** Verify by hashing `d19t_grade.py` against the committed blob before grading.

---

## 9. THE VERDICT CEILING, AND WHAT THIS ITEM DOES NOT CLOSE

**`VERDICT_CEILING = "GATE REACHED"`.** Applied last in every composition; it can only make a verdict worse.

**The reason, named rather than felt.** Sanaa's §0 says *"Every gated case runs its grid convergence study automatically; a case without one is not a result."* **D19T does not carry one.** Its graded quantity is an **instrument property** — whether an FD plateau closes — on one 4,032-cell mesh, and a plateau is not a physical prediction a grid triple would band. **Whether §0 reaches an instrument-verification item is a GATE-DESIGN question, and gate design is reserved to Sanaa.** This item does not decide that question in its own favour by ignoring it, nor against itself by declaring `NOT A RESULT` on a rule that may not reach it. It caps, and says why on the row.

**The item ceiling is composed from the UNCAPPED row verdict.** `d19m_grade.py:1526` composes the item from `rows[r]["verdict"]` — already passed through `_apply_ceiling` — so D19M's item-level ceiling **can never fire** and its `capped_by_ceiling` is always `false` however the item was actually bounded. `D19T-COMPOSE-DEF-1` is repaired here, and `RED-CEIL` in the selftest runs **both** compositions on one fixture and requires them to disagree: D19T reports `capped_by_ceiling: true`, D19M's reports `false`. *(D19O's `compose_item` additionally fails open on `NOT A RESULT`; that defect is not inherited either.)*

**What this item does NOT close, stated so nobody reads it as more than it is:**

1. **The wing grid-convergence study** that §5 also requires — L2 (~100k) and L3 (~300k), CD at fixed CL, p and GCI, gradient verification repeated on L2. **NOT IN THIS ITEM.** Without it the optimisation result carries no band.
2. **The shape-vs-incidence decomposition** (4° → 0.8°) §5 requires before any percentage. **NOT IN THIS ITEM.**
3. **np = 1 confirmation** — named in §3 (H3) as the follow-on if ε proves tolerance-independent.
4. **The wall-distance source reading** — not run, because §0.2's antecedent is false. If `G-EPS` fails while the residue sits on `shape[7]/CD` alone, it becomes the next item.
5. **Whether `shape[7]` should stay in the design set.** §5 offers "close it, **or** exclude the variable with the disclosure on the row." On the evidence in §0.2 the component is **not defective** and there is nothing to exclude; if `G-PLAT7` nonetheless fails at every registered tolerance, the exclusion route returns with its disclosure. **That choice is not made in advance in whichever direction flatters the item.**

**SUBMISSIONS PARKED.** Nothing here is sent, filed, uploaded or posted outside this box.

---

## 10. FREEZE

| | |
|---|---|
| frozen | 2026-09-01, before any compute |
| compute run at freeze | **ZERO solver core-minutes** |
| run root | asserted **ABSENT** by execution, §7 |
| gates, thresholds, caps, labels | fixed above; after first compute they close, and changes land only as dated addenda that cannot alter a gate, threshold, cap or label |

Amendments before first compute are legal and **must state the condition and how it was checked**, naming the run directory that does not exist.
