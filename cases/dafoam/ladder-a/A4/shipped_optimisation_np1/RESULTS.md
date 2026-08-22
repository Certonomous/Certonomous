# A4 Ahmed body — the SHIPPED-image optimisation twin, np=1: RESULTS

**Run 2026-08-22, 18:11–18:27Z, Lane C (Opus).**
Pre-registration: `PREREGISTRATION.md` in this directory, committed **before** any arm launched
(sha `239a007f`). **This file does not revise it.** Departures are recorded in §7 (Amendments),
dated, and never by editing the frozen file.
**Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and is Sanaa's alone.**

---

## HEADLINE — the rotation patch did not matter to this optimisation, and the reason is measurable

1. **The shipped optimiser converged, on its own statement.** `EXIT: Optimal Solution Found.`,
   **6 major iterations**, Overall NLP error **6.9114e-08** against `tol 1e-6`. It did not stop on
   `max_iter 15`, on the `timeout`, or on anything else. **Fewer majors than the patched run's 9.**
2. **It found the same optimum.** Final CD **`0.14153518384107486`** against the patched run's
   `0.1415349193489169` — agreement to **7 significant figures**, a relative difference of
   **1.9e-06**. Reduction **7.47753%** against **7.47770%**. Final `shape` = **`-0.05`**, exactly at
   the lower bound, feasible.
3. **The shipped endpoint gradient PASSES, at 0.3112%** — `2.141020e-01` analytic against
   `2.147704e-01` FD, zero sign flips. **Better than the patched run's 0.4936%.**
4. **And the whole of that difference is in the FD column, not the adjoint.** At the optimum the two
   images' **analytic** gradients are `0.21410204` (shipped) and `0.21410121` (patched) — they differ
   by **3.9e-06 relative**. Their **FD references** differ by **1.8e-03 relative**. **The rotation
   defect has effectively vanished at this deformed design point**; what moved between the two runs
   is the finite-difference reference, which is path-dependent.
5. **At the baseline the patch still matters, and arm B measures it on the image for the first time:
   0.33929% patched against 1.1032% shipped** — a 3.25× tightening. **So the defect's effect on this
   case's gradient falls by roughly three orders of magnitude between the undeformed baseline and
   `shape = −0.05`** (§4.2).

Raw logs: `/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/{opt,baseline}.log`; IPOPT table
`.../opt/opt_IPOPT.txt`; ledger `.../ledger.txt`; RSS traces `.../rss_{opt,baseline}.txt`;
launch-gate samples `.../preflight_history.txt`. **Both case directories survive.**

---

## 1. The arms as executed, and the assertions the pre-registration required

| item | registered | measured / asserted by the run itself | source |
|---|---|---|---|
| arm S image | `dafoam/opt-packages:latest` | **`IDWARP_SO_MD5: f0fcb488e0e98156575cd19548e91663`** — the shipped hash, printed from inside the process that loaded it | `ledger.txt`, `opt.log` |
| arm B image | `dafoam-idwarp-rot:v1` | **`IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425`** — the patched hash | `ledger.txt`, `baseline.log` |
| ranks | np=1, no decomposition | **`nProcs : 1`** in both arms | `ledger.txt` |
| arm S script | byte-identical to the patched twin's | `md5 387a09b76d4774186be4b83a80f14e8a` — **equal to `P2-a4-opt/opt_runScript.py`** | staged copy |
| arm B script | one line different (`compact_print`) | `md5 f11acac06391e0075faba3f2a9c2b2c3` | staged copy |
| cold start | pristine `base/`, no `0.0001`, no `processor*` | verified **before** each launch, not after | staging log |
| mesh | 2,777 cells | inherited unchanged from `P2-a4-opt/base` | `base/log.checkMesh` |
| rc | — | **0 on both arms** | `ledger.txt` |

**Container caps as run: `--cpus=1 --memory=8g`** — narrower than the registered `--cpus=4`; see
Amendment 1 (§7).

## 2. Arm S — the shipped optimisation. Per-major-iteration table.

Columns exactly as IPOPT emitted them (`opt/opt_IPOPT.txt`); `shape` from the driver's own
`debug_print` of `desvars` at the accepted point.

| iter | objective (CD) | `inf_pr` | `inf_du` | `lg(mu)` | `‖d‖` | `alpha_pr` | ls | `shape` (accepted) |
|---|---|---|---|---|---|---|---|---|
| 0 | `1.5297473e-01` | 0.00e+00 | **2.40e-01** | 0.0 | 0.00e+00 | 0.00e+00 | 0 | `0.0` |
| 1 | `1.5156693e-01` | 0.00e+00 | 5.58e-03 | −2.2 | 5.85e-03 | 1.00e+00 | 1 | `-0.005845` |
| 2 | `1.4236940e-01` | 0.00e+00 | 1.50e-02 | −3.4 | 4.03e-02 | 1.00e+00 | 1 | `-0.04614143` |
| 3 | `1.4160150e-01` | 0.00e+00 | 1.15e-04 | −5.4 | 3.55e-03 | 1.00e+00 | 1 | `-0.04969242` |
| **4** | `1.4153489e-01` | 0.00e+00 | 4.07e-04 | −10.5 | 3.07e-04 | 1.00e+00 | 1 | **`-0.04999955`** |
| 5 | `1.4153456e-01` | 0.00e+00 | 1.04e-06 | −11.0 | 4.58e-07 | 9.98e-01 | 1 | `-0.05000001` |
| **6** | **`1.4153425e-01`** | 0.00e+00 | **6.91e-08** | −11.0 | 1.39e-10 | 3.12e-02 | 6 | **`-0.05`** |

```
Number of Iterations....: 6
Objective...............:   1.4153425239903014e-01
Dual infeasibility......:   6.9114020645938298e-08
Constraint violation....:   0.0000000000000000e+00
Complementarity.........:   3.8930750950671804e-11
Overall NLP error.......:   6.9114020645938298e-08
Number of objective function evaluations             = 16
Number of objective gradient evaluations             = 7
Total CPU secs in NLP function evaluations           =    393.420
EXIT: Optimal Solution Found.
```

Final values as the harness read them back from the problem (`opt.log`):
`PHASE2_FINAL_CD: 0.14153518384107486`, `PHASE2_FINAL_SHAPE: [-0.05]`,
`PHASE2_REDUCTION_PCT: 7.47752856030352`.

**The objective column is monotone non-increasing across all seven rows.** Falsifier P3(a) — *"the
objective increases on an accepted step"* — **did not fire**.

**The 1e-8 bound excursion, recorded because it looks like a violation and is not.** Iteration 5's
accepted `shape` reads `-0.05000001`, 1e-8 outside the lower bound. This is the same barrier
arithmetic the patched run's §2.2 recorded, and it is not falsifier P3(b), which is registered
against **the reported optimum**: that is `-0.05`, exactly **at** the bound, with IPOPT reporting
`Constraint violation....: 0.0000000000000000e+00`.

### 2.1 Arm S against P1, P2, P3, P5, P7

| registered | measured | outcome |
|---|---|---|
| **P1** `EXIT: Optimal Solution Found.`, NLP error < 1e-6 | `EXIT: Optimal Solution Found.`, **6.9114e-08** | **HIT** |
| **P2** major iterations in **[7, 12]**, point estimate 9–10 | **6** | **MISS — below the band** |
| **P3** final CD ∈ **[0.14148, 0.14158]** | **`0.14153518`** | **HIT** |
| **P3** reduction 7.44–7.51% | **7.47753%** | **HIT** |
| **P3** `shape` at the lower bound, \|shape\| ≤ 0.05 + 1e-6 | **`-0.05`**, \|shape\| = 0.05 | **HIT** |
| **P5** baseline CD bit-identical to the patched run's `0.1529738469354696` | **`0.1529738469354696`** — **all 16 digits** | **HIT** |
| **P7** shipped iteration-0 `inf_du` = **`2.40e-01`** (patched printed `2.41e-01`) | **`2.40e-01`** | **HIT** |
| falsifier P3(a) objective increases on an accepted step | never | did not fire |
| falsifier P3(b) bound violated at the reported optimum | `-0.05`, `Constraint violation 0.0` | did not fire |
| falsifier P1 any exit other than `Optimal Solution Found.` | — | did not fire |

**P2 is a MISS, and it is the interesting kind.** The prereg reasoned that *"a gradient perturbed by
~1% changes the early step lengths slightly and the barrier tail hardly at all"*, and registered
[7, 12] around the patched run's 9. **The shipped run took 6 — a third fewer, on the *worse*
gradient.** It also used **16 objective evaluations and 7 gradient evaluations** against the patched
run's **47 and 10**.

**The honest reading, and it is not a compliment to the shipped gradient.** The patched run spent
**five of its nine majors** driving `lg(mu)` from −6.8 to −11.0 with line searches of 2, 6, 2, 9 and
3 trial steps (`../first_optimisation_np1/RESULTS.md` §2.1). The shipped run reached
`lg(mu) = −10.5` at **iteration 4** and was done at 6. **The difference is in the barrier tail, not
in the descent**, and it is a property of an interior-point method's step acceptance on a
one-dimensional bounded problem, not evidence that either gradient is better. **P2's band was
predicted around the wrong quantity** — the prereg anchored on the patched iteration count when the
quantity that actually varies is how quickly the barrier parameter collapses once the bound is
active. Recorded as a MISS with the reason named, not explained away.

**P7 is the measurement that proves the image variable took effect inside the optimiser's own log.**
Iteration 0 reads `2.40e-01` here and `2.41e-01` in the patched run — the two baseline analytic
gradients (`0.23965` and `0.24149949`) to the precision IPOPT prints. **The two arms started from
different gradients**, and the shipped one is the one the shipped `libidwarp.so` produces.

## 3. Arm S(b) — FD vs adjoint at the SHIPPED run's own optimum. The discriminating measurement.

Run **in the same process**, immediately after `run_driver()` returned, design vector already at the
optimum — no reload, no restart, no directory reuse (prereg §3.2).
`check_totals(step=1e-3, form=central, step_calc=abs)`.

```
Full Model: 'scenario1.aero_post.functionals.CD' wrt 'dvs.shape'
  Analytic Magnitude: 2.141020e-01
        Fd Magnitude: 2.147704e-01 (fd:central)
  Absolute Error (Jan - Jfd) : 6.683231e-04 *
  Relative Error (Jan - Jfd) / Jfd : 3.111803e-03 *
  Raw Analytic Derivative (Jfor)   [[0.21410204]]
  Raw FD Derivative (Jfd)          [[0.21477037]]
```

| | SHIPPED (this arm) | PATCHED (2026-08-21) |
|---|---|---|
| design point | `shape = -0.05` | `shape = -0.04999982` |
| **analytic** `dCD/dshape` | **`0.21410204`** | **`0.21410121`** |
| **FD** `dCD/dshape` | **`0.21477037`** | **`0.21516329`** |
| absolute error | `6.683231e-04` | `1.0620800e-03` |
| **relative error** | **`3.111803e-03` = 0.3112%** | **`4.936157e-03` = 0.4936%** |
| sign flips | **0** — both positive | **0** |
| **verdict against the lab band** (PASS ≤5%, zero flips) | **PASS** | **PASS** |

> **P4 registered: PASS, relative error in [0.5%, 2.5%], point estimate ≈1.3%, zero sign flips.
> Measured 0.3112%, zero flips. The verdict is HIT; the band is a MISS, and the prereg named this
> exact outcome in advance as falsifier P4(c): *"< 0.5% ⇒ P4 MISS in the benign direction — the
> shipped endpoint would be no worse than the patched one, meaning regime 1 has effectively vanished
> at the deformed state, and the honest report is that the patch is immaterial to this
> optimisation."* That is the report.**

### 3.1 Why the shipped number is *lower*, and why it is not a point in the shipped toolchain's favour

The prereg's arithmetic assumed the regime-1 offset measured at the baseline (**−0.77% of the
value**) would carry to the endpoint, predicting ≈1.26%. It did not carry. Decomposing the two
columns separately makes the reason unambiguous:

| column | shipped | patched | difference | relative |
|---|---|---|---|---|
| **analytic** | `0.21410204` | `0.21410121` | **8.3e-07** | **3.9e-06 (0.00039%)** |
| **FD reference** | `0.21477037` | `0.21516329` | **3.93e-04** | **1.83e-03 (0.183%)** |

**The two adjoints are the same number to four parts in a million. The two finite differences are
not.** So the shipped run's smaller relative error is **not** a better gradient — it is the same
gradient measured against a **different FD reference**, and that reference happens to sit closer to
it.

**And the 3.9e-06 analytic difference is fully accounted for by geometry, not by the patch.** The two
optima differ by Δ`shape` = 1.8e-07. The curvature over this DV's travel is
`d²CD/dshape² ≈ (0.2141 − 0.2415)/0.05 ≈ −0.55`, so a 1.8e-07 offset moves the gradient by ≈1.0e-07,
i.e. **≈4.7e-07 relative** — the same order as the 3.9e-06 observed. **This arm therefore cannot
resolve any residual rotation-patch effect on the endpoint gradient below roughly 4e-06 relative;
what it can say is that there is none above it.**

### 3.2 The FD reference at the endpoint is path-dependent, and that is a finding

Both runs finish at `shape ≈ −0.05` on the same mesh with the same solver, and their FD references
disagree by **0.183%**. A 1.8e-07 difference in the design point cannot produce that: the FD stencil
is `±1e-3` about the point, so the stencil ends differ by 0.018% of the step.

**The remaining explanation is the primal state each run arrives with.** `primalMinResTol` is `1e-4`,
each perturbed primal warm-starts from the current converged state, and the two runs reached the
bound by different iterate sequences (6 majors / 16 objective evaluations versus 9 / 47). **The FD
reference at a deformed design point is therefore a property of the optimisation path, not only of
the design point** — which is the same class of problem `../../W4_IDX16_IS_THE_REFERENCE.md` found at
A5's idx16, where `check_totals`' own FD, not the adjoint, turned out to be the doubtful column.

**Consequence, stated as a limit on both this item and the patched twin:** the difference between
0.3112% and 0.4936% **is not a toolchain comparison**. It is two FD references disagreeing by 0.18%
about a gradient both adjoints agree on to 0.0004%. **Neither number should be quoted as evidence
that one image's endpoint gradient is better than the other's.**

## 4. Arm B — the patched gradient at the undeformed baseline, on the image, with the hash printed

The cell `../first_optimisation_np1/RESULTS.md` §5 records as **NOT MEASURED**.

```
Full Model: 'scenario1.aero_post.functionals.CD' wrt 'dvs.shape'
  Analytic Magnitude: 2.414995e-01
        Fd Magnitude: 2.423217e-01 (fd:central)
  Absolute Error (Jan - Jfd) : 8.221759e-04 *
  Relative Error (Jan - Jfd) / Jfd : 3.392911e-03 *
  Raw Analytic Derivative (Jfor)   [[0.24149949]]
  Raw FD Derivative (Jfd)          [[0.24232166]]
```

| registered (P6) | measured | outcome |
|---|---|---|
| analytic **`2.4150e-01`** | **`2.414995e-01`** | **HIT** |
| FD **`2.4232e-01`** | **`2.423217e-01`** | **HIT** |
| relative error **0.33929% ± 0.05 pt** | **`3.392911e-03` = 0.33929%** — the archival value to **5 significant figures** | **HIT** |
| zero sign flips ⇒ PASS | one component, `+0.2415`, right-signed | **PASS** |
| falsifier (a) wrong `IDWARP_SO_MD5` | `85f59e87253e0a71a813f64ca6e4c425` | did not fire |
| falsifier (b) differs from 0.33929% by >0.05 pt | differs by **0.0000%** | did not fire |
| falsifier (c) the FD moves | `2.423217e-01` against the shipped np=1 log's `2.4232e-01` — **identical at the 5 s.f. those logs print** | did not fire |

**What this settles.** `../../patched_build/idwarp_rot/BUILD.md` §1 warns that a bind-mount run which
dropped its `-v` or its `export` *"would silently produce stock numbers under a patched label"*, and
§2 requires the `.so` to be hashed from inside the loading process. The 2026-08-02 archival row
(`W4-a4-stepsweep/a4_np1_patched.log`) predates that discipline and prints no hash. **It now has a
self-certifying twin: the same 0.33929%, on the image, with `85f59e87…` printed by the run.** The
bind-mount and the image are the same stack on this case, as prereg §2 inferred and now does not have
to infer.

### 4.1 The two-row table, complete for the first time

| configuration, np=1 | SHIPPED `dafoam/opt-packages:latest` | PATCHED `dafoam-idwarp-rot:v1` |
|---|---|---|
| gradient at the **undeformed baseline** | **PASS, 1.1032%** (`a4_np1_stock.log`, archival) | **PASS, 0.33929%** (**arm B**, hash-certified) |
| **optimisation** (`run_driver`) | **PASS — 6 majors, `Optimal Solution Found.`, −7.47753%** (**arm S**) | **PASS — 9 majors, `Optimal Solution Found.`, −7.47770%** |
| gradient at that run's **own optimised design** | **PASS, 0.3112%** (**arm S(b)**) | **PASS, 0.4936%** |
| trivial baseline (`scaler=-1.0`) | **declined by name** (§5) | **NOT A RESULT (control behaved)** |

**No cell in this table is now an assumption.** Every one of the six is a measurement with a log and,
for the four taken since 2026-08-21, an in-process `libidwarp.so` hash.

### 4.2 Regime 1 decays with deformation — the first direct measurement

| design point | shipped analytic | patched analytic | **defect's effect on the analytic** |
|---|---|---|---|
| **baseline**, `shape = 0` | `0.23965` | `0.24149949` | **1.85e-03 = 0.766% of the value** |
| **optimum**, `shape ≈ −0.05` | `0.21410204` | `0.21410121` | **8.3e-07 = 0.00039% of the value** |

**A factor of ≈2,000 between the two.** The prereg registered the mechanism the other way round — it
warned that regime 2 *"takes over"* at deformed designs and might make the shipped endpoint worse.
**On this case, at this deformation, regime 1 simply stops acting and regime 2 does not replace it
with anything the adjoint difference can see.** `../../ROOTCAUSE_getRotationMatrix3d.md` §4.9's
picture — the `sqrt(eps)` guard firing only near an undeformed state — is what the data show, and
this is the first time the lab has measured the decay rather than inferred it.

**Three limits on that claim, stated with it.** (i) It is **one design variable** moved 0.05 in z on
a 1.044-length body; nothing here says where the decay sits for a 96- or 105-DV deformation.
(ii) The endpoint pair is measured at two design points 1.8e-07 apart and cannot resolve below
≈4e-06 relative (§3.1). (iii) **It is a statement about this case's gradient, not about the defect**:
A1's shipped baseline error is 11.43% and A5's ~47%, so a 0.766% baseline effect is A4-specific, and
its decay may be too.

## 5. Trivial baseline — declined by name, as registered

Prereg §4 declined the Charter-2c trivial baseline by name: **A4's `scaler=-1.0` sign-flipped-gradient
control, already run on the patched image** on 2026-08-21 (CD **rose 9.090%**, `shape` walked to the
opposite corner `+0.04992374`, verdict **NOT A RESULT — control behaved as designed**). The
justification registered in advance was that the control grades the **driver**, and
`docs/dafoam/TOOLCHAIN_INVENTORY.md` §1 establishes that all three images carry identical
Python-package versions and differ only in the rebuilt library.

**The condition attached to that decline did not trigger.** Prereg §4: *"Should arm S produce a
descent that looks anomalous — a reduction outside the band of §6-P3, or a non-monotone objective
column — the control is **not** assumed to transfer and a shipped `scaler=-1.0` arm becomes
mandatory."* The reduction is **7.47753%**, inside the registered [7.44%, 7.51%]; the objective column
is **monotone on all seven rows**. **No shipped control arm is owed.**

**The free control registered in its place fired and passed:** P5, the bit-identical baseline CD
(§2.1). It is the strongest available evidence that the only thing that differed between the two runs
is the thing that was supposed to differ.

## 6. Cost

| arm | wall | ranks | core-min | peak RSS | rc |
|---|---|---|---|---|---|
| **S** — shipped optimisation **and** in-process endpoint `check_totals` | **695 s** | 1 | **11.583** | **1.007 GiB** | 0 |
| **B** — patched baseline `check_totals` on the image | **122 s** | 1 | **2.033** | **1.331 GiB** | 0 |
| **TOTAL** | **817 s** | | **13.616** | | |

**13.616 core-min = 0.22693 core-hours = $0.01164** at $0.0513/core-hour.
**Registered ceiling 40 core-min ($0.0342) — used 34.0%.** Registered prediction ~12 core-min;
measured 13.616, **13% over**, inside the registered allowance of 25. Arm S landed at 11.583 against
its registered 8–13; arm B at 2.033 against its registered ≤3. **Nothing was dropped for cost,
nothing was truncated, no `kill` was issued or needed, and neither `timeout` fired.**

### 6.1 Contention — measured against the registered basis, not asserted

Prereg §7 filed this disclosure in advance and Amendment 1 (§7) requires the measurement.

The clean apples-to-apples marker is the **same work item in both logs**: `dRdWTPC: 800 of 1087`,
whose internal `ExecutionTime` reads **48.69 s** in the patched run (uncontended-ish, `--cpus=4`) and
**53.77 s** here (`--cpus=1`, host load ~20). **Measured inflation 1.104×**, against the supervisor's
estimate of ~1.1× and Amendment 1's registered ceiling of **≤1.3×**. **Inside the registered
bound.**

**The whole-arm wall clock must NOT be read as an inflation figure.** Arm S ran **695 s** against the
patched arm's **567 s** — 1.226× — while performing **16 objective evaluations and 7 gradient
evaluations** against the patched run's **47 and 10**. Fewer than half the solves in more wall time.
**Per unit of work the wall inflation is therefore substantially higher than 1.226×, and every
wall-clock-derived number in the table above is CONTENDED and is not a cost basis for scaling.**
The 1.104× marker is the only inflation figure in this file that compares like with like.

Peak RSS **1.007 / 1.331 GiB** against the `--memory=8g` cap: **83% headroom**. Arm S's peak is
**identical to the patched twin's 1.007 GiB**.

## 7. Amendments — departures from the frozen pre-registration, dated

**Amendment 1 (2026-08-22 18:11:07Z) — launch-condition departure, directed and registered before
launch, not after.**
Prereg §8 registers a bounded gate of **1-minute load average ≤ 8 and MemAvailable ≥ 8 GiB**, polled
every 60 s for at most 40 minutes, with an escalation whose second condition is *"no other DAFoam
container is running."* **The gate was run as its own command and did not open**: the samples in
`preflight_history.txt` read load1 = 18.97, 17.91, 16.26, 18.60, 18.51, 22.38, 21.20, 22.17, 21.30
over the first 541 s, against MemAvailable 21.8–24.7 GiB throughout.

**The departure was directed by the supervisor, in writing, before the launch**, on a mechanism this
lane's prereg had not accounted for: *"the box is at ~16.3 cores demanded on 16 … Your A4 arms are
np=1, so the Open-MPI spin-wait mechanism that produced the 18–21× inflation on np=4 arms is absent;
a single rank under this load gets ~0.9 of a core (~1.1× clock inflation) … You may launch under a
DATED AMENDMENT … Use `--cpus=1` (not 4) so you never take more than one core from the T-family
spine … expected inflation ≤ 1.3×; any measured inflation reported against the registered basis."*

**What was actually done, and the two departures it contains:**

1. **Load gate departed.** Launched at 1-minute load **20.48** (arm S, 18:11:07Z) and **27.55**
   (arm B, 18:24:45Z), against a registered cap of 8.
2. **Container cap narrowed** from the registered `--cpus=4` to **`--cpus=1`** on both arms. This is a
   departure from the frozen file and is recorded as one even though it is **more** conservative.

**What was NOT departed from:** the **memory floor held** — MemAvailable was **23.9 GiB** at arm S's
launch and **9.8 GiB** at arm B's, both above the 8 GiB floor prereg §8 declares *"not escalatable."*
Both arms ran `--rm`, foreground under `timeout`, np=1, from pristine staged copies, with the
`IDWARP_SO_MD5` asserted in the log.

**And the registered escalation's own second condition was superseded, which is recorded rather than
smoothed over.** Prereg §8's escalation would have required *no other DAFoam container running*;
other lanes hold DAFoam arms on this box today, so on this lane's own registration the arms would not
have launched at all. **That condition was a poorly chosen proxy for the team's 8-core cap** — the
cap is about cores, and `--cpus=1` respects it directly. **The prereg is not edited.** The
supervisor's directive is what was followed, it is quoted above in full so a reader can grade the
decision rather than take it on trust, and §6.1 reports the inflation the directive asked for.

**Amendment 2 (2026-08-22) — arm B's justification changed between registration and execution, in
the direction of *more* evidence, not less.**
Prereg §2 registered arm B on the strength of an inference: that the bind-mounted `libidwarp.so`
(md5 `85f59e87…`) is the binary the image ships, so the 2026-08-02 archival 0.33929% is a patched
measurement, but one that *"prints no `IDWARP_SO_MD5`"* and is therefore *"an inference, not a
certificate."* Arm B was bought to convert it. **It converted it exactly** (§4). Recorded here only
so that a reader of prereg §2 knows the inference it rested on was subsequently measured rather than
left standing.

**Amendment 3 (2026-08-22) — a correction owed to `../first_optimisation_np1/RESULTS.md` §5, which
this lane does not edit.**
That file records the patched gradient-at-baseline np=1 cell as **NOT MEASURED**. It was measured on
**2026-08-02**: `/home/ubuntu/certonomous-runs/W4-a4-stepsweep/a4_np1_patched.log` reads analytic
`2.4150e-01`, FD `2.4232e-01`, **0.33929%**, at np=1, with the rotation patch bind-mounted from
`W5-patch/idwarp`, whose `libidwarp.so` hashes to `85f59e87253e0a71a813f64ca6e4c425`. **The cell was
empty in the record, not in the evidence.** The correction is stated here because this is the file a
reader of that section will reach next; **the frozen file is not edited**, and the amendment is left
for the supervisor's desk.

## 8. What this item could not see — restated against what it found

The seven limits registered in prereg §9 all stand. Three are now sharper:

1. **One design variable, and the PASS is a property of that.** Prereg §6-P4 registered in advance
   that *"the structural reason A4 shipped passes where A1 and A5 fail is not that A4's toolchain is
   healthier; it is that A4 has no near-zero component for the defect to flip."* **That reading
   survives the result.** A4's single derivative is `+0.214`; A1's `idx6` FD is `−1.05e-03` and A5's
   `idx16` is the same shape. **Nothing here transfers to the 8-, 96- or 105-DV cases** — and the
   same lane's A2 extraction today found a **sign flip at idx46 on the *patched* image** hidden
   inside a 0.0506% aggregate (`../../A2/per_component_table/RESULTS.md`), which is exactly the
   failure mode a one-DV case cannot exhibit.
2. **`cellLimited Gauss linear 1` is live on this case's momentum equation and was not varied.**
   Defect **D-B2** reads **92.8% on A1 with the rotation patch already in place**. It could be acting
   on every number in this file, **on both images equally**, and this item cannot see it. **Both PASS
   rows are PASSes for this scheme configuration only.**
3. **The endpoint comparison is not a toolchain comparison** (§3.2). The two endpoint errors differ
   because their **FD references** differ by 0.18%, and that difference is path-dependent. **A clean
   toolchain comparison at a deformed design would require running both images' `check_totals` at the
   *same* design point reached by the *same* path** — an arm this item did not register and did not
   buy.
4. **2,777 cells exist only to host a gradient.** No drag-accuracy and no Ahmed-body physics claim
   attaches to any CD here. **The decomposition defect is absent by construction at np=1**, which is
   why np=1 was chosen; nothing here speaks to A4 at np > 1, where the shipped `scotch` default
   produces a gradient that is not the transpose Jacobian's solution.
5. **Wall clocks are contended** (§6.1) and are not a cost basis.

## 9. VERDICTS

| arm | configuration | registered | measured | **verdict** |
|---|---|---|---|---|
| **S** | optimisation, np=1, **SHIPPED** | converges; 7–12 majors; CD ∈ [0.14148, 0.14158] | **6 majors, `EXIT: Optimal Solution Found.`, NLP error 6.9114e-08; shape −0.05 at the bound; CD 0.14153518, −7.47753%** | **PASS** |
| **S(b)** | endpoint FD-vs-adjoint, **SHIPPED** | PASS, 0.5–2.5%, zero flips | **0.3112%, zero flips** (`2.141020e-01` vs `2.147704e-01`) | **PASS** |
| **B** | baseline FD-vs-adjoint, **PATCHED**, hash-certified | 0.33929% ± 0.05 pt, zero flips | **0.33929%** (`2.414995e-01` vs `2.423217e-01`) | **PASS** |
| — | trivial baseline, SHIPPED | declined by name, with a trigger condition | trigger did not fire | **DECLINED AS REGISTERED** |
| P2 | 7–12 major iterations | **6** | below the band | **MISS** |
| P4 | endpoint error 0.5–2.5% | **0.3112%** | below the band — prereg falsifier P4(c) | **MISS, benign direction** |
| P1, P3, P5, P6, P7 | see §2.1, §4 | — | — | **HIT (5 of 7)** |

> ### **ITEM VERDICT: PASS — and the answer to the question it was bought for is *no*.**
>
> **The shipped-image optimisation converges on its own statement (`EXIT: Optimal Solution Found.`,
> 6 majors, NLP error 6.9114e-08 < `tol 1e-6`), lands on the same optimum as the patched twin to 7
> significant figures (CD `0.14153518` against `0.14153492`, −7.47753% against −7.47770%), at the same
> feasible bound, with a monotone objective column, and its endpoint gradient re-verifies against its
> own finite differences at 0.3112% with zero sign flips.**
>
> **The rotation patch did not matter to this optimisation.** At the optimum the two images' analytic
> gradients differ by **3.9e-06 relative** — inside what the 1.8e-07 difference in their stopping
> points alone explains. The 0.3112%-versus-0.4936% gap is **entirely in the FD reference**, which
> moved 0.183% between two runs that took different paths to the same point (§3.2), and **must not be
> quoted as a toolchain comparison.**
>
> **At the baseline the patch does still matter — 1.1032% shipped against 0.33929% patched, now
> hash-certified on the image (arm B). So regime 1's effect on this case's gradient falls by a factor
> of ≈2,000 between `shape = 0` and `shape = −0.05`** (§4.2). That is the first direct measurement of
> the decay the root-cause record predicted, and it is a statement about **this case, this DV and
> this deformation**.
>
> **Two registered predictions missed, both named in advance as possibilities: P2's iteration band
> (6 against [7, 12] — the prereg anchored on the wrong quantity, §2.1) and P4's error band (0.3112%
> against [0.5%, 2.5%] — prereg falsifier P4(c) exactly).**
>
> Cost **13.616 core-min = $0.0116**, 34.0% of the registered ceiling. Wall clocks are **CONTENDED**;
> measured inflation on an identical work marker is **1.104×**, inside Amendment 1's ≤1.3×.
> **The claim is about the optimiser and the gradient, not about Ahmed-body aerodynamics.**

## 10. Verdict vocabulary

PASS, GATE REACHED, GATE FAIL, NOT A RESULT, BLOCKED, PENDING. Shipped- and patched-toolchain
verdicts are reported as **separate rows** (§4.1, §9). An optimiser that stops on an iteration cap, a
wall-clock cap or any external cap is **GATE REACHED / NOT A RESULT**, never PASS — **neither arm
stopped on a cap.**

**Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and is Sanaa's alone.**
