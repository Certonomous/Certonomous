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

---
---

# AMENDMENT 1 — 2026-09-02 — PRE-COMPUTE — THE `MESH` ARM'S CAP LEAVES NO WALL BUDGET; THE CAP IS RAISED ONTO ITS MEASURED ANCHOR AND ONTO TONIGHT'S MEASURED CONTENTION

**`lines whose number changed above this section: 0`**

## Condition: zero solver core-minutes on this item — checked, not asserted

1. **Zero solver core-minutes spent.** `STATUS.queue.D19T_chain` records `launcher_rc=65`, and `launcher.queue.out` ends at the `MESH` abort and the chain stop. No `ledger.txt` was ever created in the run root — the ledger is written only after a container returns (`d19t_run_arm.sh:340-347`) — and the archived root contains only `base/` and `d19r_runScript.py`. **Spend: 0.0 core-min.**

2. **No `d19t_*` container was ever created.** `docker ps -a` across all states returns zero names matching `d19t_`, **from a reader shown able to see a non-zero**: the same census returns 40 containers, including other lanes' `maaoa_*`, `a1wr_*` and `aoa_*`. A zero from a reader not shown able to see a non-zero is not evidence, so the reader was proved sighted before its zero was accepted.

3. **The driver aborted at the cap assert, before any container existed.** The abort line is the one emitted at `d19t_run_arm.sh:154`, which precedes staging (line 249) and `docker run` (line 304). Corroborated on disk: the archived root carries no `MESH/` directory, no `*.log` and no `*.inspect.txt`; and the age-guard launch sentinel `/home/ubuntu/certonomous-runs/.d19t_datums` **does not exist**, while the siblings' `.d19r_datums`, `.d19o_datums` and `.d19m_datums` do — again a zero from a reader shown able to see a non-zero. The sentinel is stamped at line 254, downstream of the abort.

4. **The run root does not exist.** The staged root from the 22:07:08Z fire was **preserved by `mv`, not deleted**, to `/home/ubuntu/certonomous-runs/CURRICULUM-D19T-a1-naca0012-shape7-primal-tightening_partial_20260902T220708Z` (its launch stamp). `test ! -e` on the original passes; `test -d` on the archive passes; and `d19t_chain_driver.sh assert-absent` was re-executed and printed `D19T_ROOT_ABSENT_ASSERTED … 2026-09-02T22:14:12Z`. §7's literal condition therefore holds again **by execution**, and it was re-asserted a second time immediately before this amendment was appended.

At this amendment `PREREGISTRATION.md` was byte-identical to its committed blob `675da997abfcc890debe1206e0b32abafdfe6b8f` before the append. The freeze window is open and this amendment is legal under rule 2 and §10.

## The defect

`d19t_run_arm.sh:153` computes the in-container deadline as `TMO = int(cap × 60 / ranks) − CAP_MARGIN_S`, with `CAP_MARGIN_S = 60` (line 81), and line 154 asserts `TMO > 0`. For all five registered arms, as frozen:

| arm | cap (core-min) | ranks | `int(cap×60/ranks)` | `− 60` = TMO | `test "$TMO" -gt 0` |
|---|---|---|---|---|---|
| **`MESH`** | **1.0** | **1** | **60** | **0** | **FAILS → `exit 65`** |
| `T08` | 4.0 | 2 | 120 | 60 | passes |
| `T10` | 4.0 | 2 | 120 | 60 | passes |
| `T12` | 4.0 | 2 | 120 | 60 | passes |
| `XT10` | 5.0 | 2 | 150 | 90 | passes |

A fixed 60 s teardown margin is subtracted from a `MESH` budget that is itself exactly 60 s of wall, leaving nothing. `MESH` is the **first** arm, and the chain correctly refuses to continue past a failed arm (`d19t_chain_driver.sh:58-63`), so **no D19T arm could ever run, at any time, under any conditions.** The four solver arms were never reached and are not defective.

**The defect was legible in the frozen text and was not read as fatal.** §6's cap table recorded the `MESH` deadline as `0 s + margin`, and the in-script table at `d19t_run_arm.sh:69` carried an inherited annotation that does not evaluate to this item's arithmetic. A deadline written down as zero was never reconciled against the `> 0` assert that consumes it.

## The repair: `MESH` cap 1.0 → **3.0 core-min**, deadline **120 s**

`TMO = int(3.0 × 60 / 1) − 60 =` **120 s**, and the launcher's own back-check (line 155) returns `(120 + 60) × 1 / 60 = 3.000000`, equal to the registered cap exactly. Verified by evaluating the edited file's own tables: all five arms now return `TMO > 0` with exact back-checks (`MESH` 120 s, `T08`/`T10`/`T12` 60 s, `XT10` 90 s).

### The anchor is MEASURED, and it is this document's own

The `MESH` arm — `preProcessing.sh`, `checkMesh`, and the frozen-mesh md5 assert, at np=1 on the same 4,032-cell base — has run to `rc=0` four times in this family:

| item | ledger | wall s | core-min | siblings at launch |
|---|---|---|---|---|
| **D19R** | `/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-plateau/ledger.txt` | 11 | 0.183 | 1 |
| **D19** | `/home/ubuntu/certonomous-runs/CURRICULUM-D19-a1-naca0012-subsonic-opt/ledger.txt` | **28** | **0.467** | **0** |
| D19O | `/home/ubuntu/certonomous-runs/CURRICULUM-D19O-a1-naca0012-subsonic-optimisation/ledger.txt` | 10 | 0.167 | 0 |
| D19M | `/home/ubuntu/certonomous-runs/CURRICULUM-D19M-a1-naca0012-subsonic-multipoint/ledger.txt` | 10 | 0.167 | 0 |

D19R is the closest analogue — same image digest as this item's registered PATCHED row, same base, same np=1 — and §6 already tags its 0.183 core-min **MEASURED** as this item's `MESH` prediction. **The anchor is not new evidence; it is the anchor the freeze already used.** Worst case in the family is D19's 28 s / 0.467 core-min.

### Why 3.0 and not 2.0 — decided by a measurement taken on this box tonight

2.0 core-min (a 60 s deadline, 2.14× the worst measured `MESH` wall) was drafted first and is **rejected**, because **three of the four anchor measurements above were taken with an EMPTY sibling census** and the fourth with one sibling. They are quiet-box measurements, and D19T will run against a box carrying 40 containers.

**That is precisely the failure this item's own sibling suffered hours ago.** `A1WR` lost **all six** of its cold controls — `rc=97` from an in-container `rc=124` at the 3,300 s `COLD_TMO`, `wall_s` 3316–3317, no time directory written at all, **331.7 core-min for zero physics** (`docs/LAB_STATE.md` dafoam `S-26` §4). The cause is measured and it is ours: **0.56 it/s under 8-way concurrency against ~2.36 it/s at 3-way** — a deadline sized from a rate measured on a quiet box and then spent on a box the same item had just filled. **A deadline sized without its own concurrency is a deadline sized for a different experiment.**

`S-27` §8 later **narrowed** `S-26` on this point, and the narrowing strengthens the case rather than weakening it: `rc=97` means **timeout, not solver failure**, and **three of the six colds were incompressible and healthy — killed while succeeding**, `cold_I_4` at `p` residual 3.884e-06 and still falling. The 331.7 core-min waste figure stands and its cause is **doubly established**: the deadline, not the physics, is what stopped them. Both blocks are cited here rather than `S-26` alone, because citing a claim its own author has since corrected would be citing a superseded reading.

**Applying that measured contention factor to this arm:** 28 s × (2.36 / 0.56) = **118.0 s** — `DERIVED` from two `MEASURED` figures, not itself measured. **The registered 120 s deadline is the contention-scaled worst case**, not a round number chosen for comfort. It is additionally the enforced in-container wall under which `MESH` completed `rc=0` in both D19O and D19M.

**A second and independent reason 3.0 is better than 2.0.** At a 120 s deadline a contention-stretched `MESH` arm **completes and reports its cost into the ledger**, where `G-CAP` judges it. At 60 s the same arm is killed at the deadline and returns nothing. A number the grader can refuse is strictly more informative than an `rc=124` that yields no number at all — and this item has just spent an evening on the difference.

## `CAP_MARGIN_S` is unchanged at 60 s — and the reason first recorded for that was wrong

The margin stays at `d19t_run_arm.sh:81`, verified byte-identical to the HEAD blob. **The reason first given for keeping it — that 60 s was "deliberately matched" to this family's container kill-grace — was checked and is false:** line 311 uses `timeout -s TERM -k 30`, a **30 s** grace. That premise is withdrawn rather than quietly repaired, and the conclusion survives on a better one:

**`CAP_MARGIN_S` is a global constant serving all five arms, and one arm's mis-sized budget is not a reason to move a global.** Lowering it to rescue `MESH` would silently shorten the teardown allowance of the four solver arms, which are not defective and were never consulted. At 60 s it is **conservative relative to the measured 30 s kill-grace** — it is not claimed to equal it. **The margin was never the defect; the `MESH` budget was, and that is what moved.**

## What else does not move

**No other arm's cap moves.** `T08`, `T10` and `T12` stay at 4.0 and `XT10` at 5.0; their deadlines stay 60, 60, 60 and 90 s.

**The item ceiling is unchanged at 18.0 core-min.** It is a **spend** ceiling checked against the ledger's summed `core_min` (`d19t_chain_driver.sh:65-66`; `d19t_grade.py:753`), **not** an identity on the sum of arm caps. With `MESH` at 3.0 the arm caps sum to 20.0 while the ceiling stays 18.0; that is not an inconsistency but the conservative direction — the ceiling binds and stops the chain before every arm could exhaust its individual cap. Predicted item spend is unchanged at **8.234 core-min**, so §6's `Cap/predicted = 2.19×` stands, as do the derived dollars: 18.0 core-min = 0.30 core-h → **$0.0154 DERIVED** at the owner-stated $0.0513/core-h. Dollars remain derived, never measured — the box cannot read its own billing.

**§6's cap-table row for `MESH` is superseded by:** `| MESH | 3.0 | 120 s |`. **The original row is struck, not rewritten.**

## The instrument re-pin

`d19t_run_arm.sh` changes on **two** lines — the `cap_core_min()` entry at line 84, and the in-script registered-cap comment at line 69, which is corrected in the same edit so the file's own table cannot contradict its code. §8's pin is superseded:

| file | old md5 | new md5 | bytes |
|---|---|---|---|
| `d19t_run_arm.sh` | `c1013f8ce5d927428ac75fdc0c76bef4` | **`9b04d68ebed675e2d3df6c55d1e52956`** | 18,962 (unchanged) |

The diff was taken against the **HEAD blob**, not `git status`, and is exactly two changed lines. `bash -n` passes on the result.

**The grading path is NOT affected, and this was EXECUTED rather than inferred.** `d19t_grade.py` is not edited; its md5 **`bc6d694a7805a0d507be024dda8fd4fa`**, pinned at §8, was confirmed unchanged both before and after. `d19t_grade_selftest.py` — which reads `G.ARM_CAP_CORE_MIN` at its line 92 — was run to completion with `__pycache__` cleared first (the stale-bytecode trap that can invert a mutation test): **`D19T GRADER SELFTEST OK`, rc=0**; green leg composes to uncapped `PASS` → capped `GATE REACHED`; **all 12 red legs fire, `RED-CAP` among them**; the blinded `R3` reader refuses the whole grading with `CONTROL_READER_NOT_BORN`; the L-332 assert counter is born. **`RED-CAP` firing is the planted control for the cost gate itself: the cap reader is shown able to return a refusal, so its silence on a real run will mean something.** The pins for `d19t_xf.py`, `d19t_age_guard.py`, `d19t_chain_driver.sh`, `d19t_grade_selftest.py` and `d19r_runScript.py` are unchanged.

## The two-registrations asymmetry — disclosed, and REFERRED UPWARD rather than resolved

The `MESH` cap is registered in **two** executables: the launcher's `cap_core_min()`, and the grader's `ARM_CAP_CORE_MIN` (`d19t_grade.py:84`), which `g_caps()` (line 744) uses as the `G-CAP` per-arm refusal threshold. **This amendment moves only the launcher's. The grader keeps 1.0 core-min for `MESH`.**

**This is disclosed rather than resolved, and the reason it is not resolved is a limit of authority, not an oversight.** Raising the grader's `ARM_CAP_CORE_MIN["MESH"]` would **widen the `G-CAP` gate threshold**, and widening a gate threshold is reserved above this team even before first compute. It is therefore **referred upward, not decided here.**

**Nothing is loosened by the asymmetry.** The two values serve different purposes and equality between them is not required: the launcher's cap answers *"do not let this run away forever"*, the grader's answers *"was this cost anomalous"*. The grader is the **stricter** of the two and remains the binding cost gate — a `MESH` arm costing more than **1.0 core-min is still `GATE FAIL` at grading**, whatever the launcher permitted. On the measured band (0.167–0.467 core-min) a `MESH` arm that completes normally lands well inside 1.0, so the two thresholds cannot disagree about any ordinary run; they differ only in the window `1.0 < spend ≤ 3.0`, where the launcher lets the arm finish and the grader refuses its cost. **That is the safe direction, and it is the informative one: the number is bought, recorded and then judged, instead of being destroyed by a deadline.**

## Gates untouched

**`G-PLACE` is untouched** — cpuset stays `5,13` (`d19t_run_arm.sh:61`), distinct from D19R's `1,15` and D19M's `13`. **`G-NP` is untouched** — `ranks_of()` is unchanged and was verified against the HEAD blob: `MESH` np=1, all solver arms np=2. `MESH`'s np=1 is a registered condition and is exactly what makes this arithmetic what it is; it was **not** adjusted to dodge the assert, which would have confounded the decomposition with the tolerance this item exists to vary.

`G-MANIFEST`, `G-COLD`, `G-ROOT.1`, `G-ROOT.2`, `G-ROW`, `G9-TOOLCHAIN`, `G-EPS`, `G-PLAT7`, the `VERDICT_CEILING = "GATE REACHED"` and its reason, and every threshold, band and label in §3–§5 and §9 are unchanged. **No gate, threshold, label or verdict class moves, and no verdict class is made reachable that was not reachable at the freeze.**

**SUBMISSIONS PARKED.** Nothing in this amendment is sent, filed, uploaded, registered or posted outside this box.

---

# AMENDMENT 2 — 2026-09-03 — PRE-COMPUTE — **THE CAPS ARE RE-SET ON THE *EFFECTIVE SOLVER BUDGET*, NOT THE NOMINAL CAP; `T10` AND `T12` WERE REGISTERED TO TIME OUT AT THEIR OWN PREDICTED SPEND; AND THE ASSERT THAT WOULD HAVE CAUGHT BOTH IS ADDED AND EXECUTED**

**`lines whose number changed above this section: 0`**

## Condition: still zero solver core-minutes — checked by execution at 2026-09-03T16:31:03Z, not asserted

1. **Run root absent.** `d19t_chain_driver.sh assert-absent` re-executed and printed
   `D19T_ROOT_ABSENT_ASSERTED /home/ubuntu/certonomous-runs/CURRICULUM-D19T-a1-naca0012-shape7-primal-tightening does not exist at 2026-09-03T16:31:03Z`.
2. **Both partial roots preserved by `mv`, never deleted:** `..._partial_20260901T164955Z` and `..._partial_20260902T220708Z`.
3. **Zero `d19t_` containers in any state, from a reader shown able to see a non-zero:** the same census returns **40** containers.
4. **The age-guard launch sentinel `.d19t_datums` does not exist**, while the siblings' `.d19r_datums`, `.d19o_datums` and `.d19m_datums` all do — again a zero from a reader proved sighted.
5. **No `ledger.txt` has ever been written under any D19T root.**

**Spend to date: 0.0 solver core-min.** Amendments before first compute are legal under `CLAUDE.md` rule 2 and §10. At this amendment `PREREGISTRATION.md` was byte-identical to its committed blob `f64f82fd66be80d4c5d769064388c4a3e0797086` (md5 `2a39628367d421ba5f0720fae6171520`) before the append, and this amendment is a **pure append** — verified by the prefix-identity method, not by a diffstat.

## THE DEFECT AMENDMENT 1 REPAIRED ONE ARM OF AND LEFT IN THE OTHER FOUR

Amendment 1 stated: *"The four solver arms were never reached and are not defective."*
**That sentence is FALSE by this document's own predicted spend, and it was asserted without ever being evaluated.** It is struck here, not rewritten, and the correction is attributed to the lane evaluation that produced it.

**THE STRUCTURAL FINDING, WHICH IS THE REAL CONTENT OF THIS AMENDMENT.** The solver never receives `cap`. It receives

> **`cap − CAP_MARGIN_S × ranks / 60`**, which at `CAP_MARGIN_S = 60` is exactly **`cap − ranks`** core-min.

At `ranks = 2` a 4.0 cap delivers **2.0** — **half the budget goes to a margin nobody costed.** And the launcher's back-check

> `(TMO + CAP_MARGIN_S) × ranks / 60 == cap`

is **structurally incapable of catching this, because it adds back the very margin the solver never gets**: it reconstructs `cap` by *undoing the subtraction it should be auditing*. **A self-consistency check that inverts the subtraction it should audit will pass forever.**

**What that left on the ground, against this document's own §6 predictions:**

| arm | cap | ranks | `TMO` | effective budget | §6 registered prediction | |
|---|---|---|---|---|---|---|
| `MESH` (Amendment 1) | 3.0 | 1 | 120 s | 2.0 | 0.183 **MEASURED** | fits, 10.93× |
| `T08` | 4.0 | 2 | 60 s | 2.0 | 1.628 | fits, but only 1.23× |
| **`T10`** | 4.0 | 2 | 60 s | **2.0** | **2.108** | **REGISTERED TO TIME OUT** |
| **`T12`** | 4.0 | 2 | 60 s | **2.0** | **2.589** | **exceeds by 1.30×** |
| `XT10` | 5.0 | 2 | 90 s | 3.0 | 1.726 | fits, 1.74× |

**Two of five arms were registered to die at their own deadlines on a QUIET box, before any contention factor.** `MESH`'s original defect was the **absolute** form (`TMO = 0`) and it was loud: an assert fired. `T10` and `T12` are the **relative** form — `0 < TMO < the arm's own predicted wall` — and it is **silent**: nothing fires, the arm launches, and it dies at its deadline having bought nothing. **The silent form is the expensive one.**

## THE RULING: CAPS SET ON THE EFFECTIVE BUDGET AT ~3×

Sanaa's 2026-09-03 ~18:00Z envelope law, item 2, verbatim: a hard per-run cap *"set by the team at ~3× its own estimate, not by me"*, and *"the estimate is an instrument, not a permission slip."* **That factor is applied to the EFFECTIVE SOLVER BUDGET, not to the nominal cap** — applying it to the nominal cap is precisely the error that produced this defect twice.

| arm | ranks | **cap** | `TMO` | **effective core-min** | §6 prediction | ratio |
|---|---|---|---|---|---|---|
| `MESH` | 1 | **3.0** *(unchanged)* | 120 s | 2.0 | 0.183 | **10.93×** |
| `T08` | 2 | **7.0** | 150 s | 5.0 | 1.628 | **3.07×** |
| `T10` | 2 | **8.5** | 195 s | 6.5 | 2.108 | **3.08×** |
| `T12` | 2 | **10.0** | 240 s | 8.0 | 2.589 | **3.09×** |
| `XT10` | 2 | **7.5** | 165 s | 5.5 | 1.726 | **3.19×** |

**§6's cap table is superseded by the rows above. The originals are struck, not rewritten.**

Back-check exact on all five: `(120+60)×1/60 = 3.0`, `(150+60)×2/60 = 7.0`, `(195+60)×2/60 = 8.5`, `(240+60)×2/60 = 10.0`, `(165+60)×2/60 = 7.5`.

## `G-BUDGET` — THE ASSERT THIS ITEM DID NOT HAVE, ADDED AND **EXECUTED**

Registered at `d19t_run_arm.sh`, evaluated per arm at run time, refusing with **exit 65** on failure:

```
TMO = int(cap*60/ranks) - CAP_MARGIN_S
assert TMO > 0                                  # NECESSARY AND NOT SUFFICIENT -- retained, and documented as such
assert TMO*ranks/60 >= 3.0 * pred_core_min(arm) # G-BUDGET: THE ONE THAT WAS MISSING
assert abs((TMO + CAP_MARGIN_S)*ranks/60 - cap) <= 1e-6
```

`pred_core_min()` is a new registered table carrying §6's own per-arm predictions (`MESH` 0.183 **MEASURED**, `T08` 1.628, `T10` 2.108, `T12` 2.589, `XT10` 1.726). **These are predictions and are never used as caps.**

**EXECUTED OVER ALL FIVE ARMS, from the edited file's own tables, 2026-09-03 — because an assert nobody ran is what put this item here:**

```
D19T_G_BUDGET arm=MESH cap_core_min=3.0  margin_cost_core_min=1.000 effective_core_min=2.000000 predicted=0.183 ratio=10.9290 required=3.0x PASS  [TMO=120s backcheck=3.000000]
D19T_G_BUDGET arm=T08  cap_core_min=7.0  margin_cost_core_min=2.000 effective_core_min=5.000000 predicted=1.628 ratio=3.0713  required=3.0x PASS  [TMO=150s backcheck=7.000000]
D19T_G_BUDGET arm=T10  cap_core_min=8.5  margin_cost_core_min=2.000 effective_core_min=6.500000 predicted=2.108 ratio=3.0835  required=3.0x PASS  [TMO=195s backcheck=8.500000]
D19T_G_BUDGET arm=T12  cap_core_min=10.0 margin_cost_core_min=2.000 effective_core_min=8.000000 predicted=2.589 ratio=3.0900  required=3.0x PASS  [TMO=240s backcheck=10.000000]
D19T_G_BUDGET arm=XT10 cap_core_min=7.5  margin_cost_core_min=2.000 effective_core_min=5.500000 predicted=1.726 ratio=3.1866  required=3.0x PASS  [TMO=165s backcheck=7.500000]
ALL FIVE ARMS PASS TMO>0, G-BUDGET >= 3.0x, AND THE EXACT BACK-CHECK: True
```

**HONEST LIMIT ON THAT EVALUATION.** The launcher **refused** to run its own assert path against a scratch `BASE` — `G-ROOT.1` fired and would not accept a root that is not this item's registered one. That is the guard working, and it means the numbers above were produced by evaluating **the tables and constants read out of the edited file** under the identical arithmetic, **not** by the launcher executing them in place. **The launcher's own execution happens at launch**, prints `D19T_G_BUDGET` per arm to the log, and records `eff_core_min`, `pred_core_min`, `budget_ratio` and `tmo_s` into `ledger.txt` — where the `MESH` arm's line is the first live confirmation and is checked on landing.

## `G-QUIET` — THE CONCURRENCY PRECONDITION, ENFORCED AND RECORDED

**Every cap in this item rests on a QUIET-BOX cost basis, and until now that was an unstated assumption rather than a checked condition.** The measured compressible contention factor on this hardware is **3.1198×** (`probe_C` 1.5599 it/s at 2-way against `cold_C_4` 0.5000 it/s at 8-way, `A1WR/STAGE12/CHAIN_LEDGER.tsv`). At that factor **every arm's spend would exceed the grader's unchanged `G-CAP` threshold and this item could return nothing but `GATE FAIL` on cost alone.**

**The gate is NOT widened to accommodate that. The precondition is enforced instead.** Before each arm the launcher:

1. proves its container reader **sighted** — `docker ps -a` must return a non-zero count, else **exit 66** with the reason that a zero from an unsighted reader is not evidence (rule 3);
2. refuses to launch (**exit 66**) if any competing solver container is live;
3. records `g_quiet_utc` and `g_quiet_census_all` into `ledger.txt` beside the arm's cost.

**This is the exact repair for the A1WR failure class.** A1WR's deadline assumed a quiet box and **nothing enforced it**; six cold controls died at the deadline for **331.7 core-min of zero physics**. **A quiet-box cost basis with no quiet-box gate is a prediction with no premise.**

**Residual risk, stated rather than hidden:** `G-QUIET` is checked at each arm's launch. A peer that starts a solver *mid-arm* is not caught, and the resulting contention would show as an over-cap spend at grading. That is the safe direction — the cost is bought, recorded, and then judged.

## THE GRADER DOES NOT MOVE, AND THE RELATIONSHIP IS NOW THE CORRECT ONE

**`d19t_grade.py` is not edited. Its md5 is `bc6d694a7805a0d507be024dda8fd4fa`, confirmed identical to its HEAD blob before and after.** `ARM_CAP_CORE_MIN` stays `{MESH 1.0, T08 4.0, T10 4.0, T12 4.0, XT10 5.0}`. Widening a `G-CAP` threshold is reserved above this team.

**The two caps are not duplicates and are not meant to be equal:**

- **the launcher's cap is a RUNAWAY STOP** — it bounds how long an arm may occupy the box;
- **the grader's cap is the COST GATE** — it decides whether the spend was anomalous, and it is the **stricter** of the two and remains binding.

On §6's quiet-box predictions **every arm lands inside the grader's caps** — `MESH` 0.183/1.0 (5.46×), `T08` 1.628/4.0 (2.46×), `T10` 2.108/4.0 (1.90×), **`T12` 2.589/4.0 (1.54×, the tightest)**, `XT10` 1.726/5.0 (2.90×) — **so the two cannot disagree about a normal run.** They differ only where an arm runs long, and there the launcher lets it finish and the grader refuses its cost: the number is bought, recorded and then judged, instead of being destroyed by a deadline.

## WHAT ELSE DOES NOT MOVE

**The item ceiling is unchanged at 18.0 core-min.** It is a **spend** ceiling on the ledger's summed `core_min` (`d19t_chain_driver.sh:65-66`), **not** an identity on the sum of arm caps. Cap sum rises to **36.0** and the effective-budget sum to **27.0**, while the ceiling stays **18.0** and therefore **binds first** — against a quiet predicted item spend of **8.234 core-min**, cumulative spend after each arm is 0.183, 1.811, 3.919, 6.508, 8.234, all well inside. Predicted item spend is unchanged at **8.234 core-min**; derived dollars unchanged at **$0.0070** predicted and **$0.0154** at the ceiling, at the owner-stated $0.0513/core-h — **DERIVED, never measured**, the box cannot read its own billing.

**`CAP_MARGIN_S` stays at 60 s.** It is a global serving all five arms; one arm's mis-sized budget is never a reason to move a global. **The margin was never the defect — the budgets were, and that is what moved.**

**Gates untouched:** `G-PLACE` (cpuset `5,13`), `G-NP`, `G-MANIFEST`, `G-COLD`, `G-ROOT.1`, `G-ROOT.2`, `G-ROW`, `G9-TOOLCHAIN`, `G-EPS`, `G-PLAT7`, and `VERDICT_CEILING = "GATE REACHED"`. **No existing gate, threshold, label or verdict class moves, and no verdict class is made reachable that was not reachable at the freeze.** `G-BUDGET` and `G-QUIET` are **new refusals** — they can only stop a launch, never license one, and neither can turn a `GATE FAIL` into a pass.

## THE INSTRUMENT RE-PIN

| file | old md5 | new md5 | role |
|---|---|---|---|
| `d19t_run_arm.sh` | `9b04d68ebed675e2d3df6c55d1e52956` | **`8bcdb9c306d1df659a1cb97e050cfcf9`** | launcher |
| **`d19t_grade.py`** | `bc6d694a7805a0d507be024dda8fd4fa` | **`bc6d694a7805a0d507be024dda8fd4fa` — UNCHANGED** | **THE GRADING PATH** |

`bash -n` passes on the edited launcher.

**⚠ THE LEDGER ROW GAINS SIX FIELDS AND THE GRADER'S PARSE WAS RE-PROVED AGAINST IT, BY EXECUTION.** `ledger.txt` now also carries `eff_core_min`, `pred_core_min`, `budget_ratio`, `tmo_s`, `g_quiet_utc` and `g_quiet_census_all`. The frozen grader's `_LEDGER` regex was run against a row in the new format and **every field it consumes still parses correctly** — `core_min`, `ranks`, `cpuset`, `cap_core_min`, `rc`, `wall_s`, `digest`, `row` — the old format still parses, and the reader's zero leg (no rows → `{}`) still returns empty. **This was executed, not inferred, because changing the ledger format under a frozen grader is exactly the kind of change that is assumed safe and is not.**

**SUBMISSIONS PARKED.** Nothing in this amendment is sent, filed, uploaded, registered or posted outside this box.
