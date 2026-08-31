# JF1 — L1 FEASIBILITY, FIRST FIELDS

## THIS IS NOT AN AMENDMENT TO THE FROZEN REGISTRATION

**`verification/campaign/JF1_PREREGISTRATION.md` is frozen (commit `12b1bd84`, 2026-08-31T15:29Z)
and is not touched, edited, appended to or reinterpreted by this file.** Nothing here alters a
gate, a threshold, a cap or a label; nothing here is an addendum under rule 2. This is a
**feasibility record**: the five L1 rows it reports are `feasibility` rows under Sanaa's
2026-08-31T15:13Z ruling (`etc/sessions/2026-08-31T1513Z_sanaa_freeze_clock_and_so3_ruling.md`,
commit `927924f1`) — *feasibility rungs need no freeze and no gate scores on them.*

**NO VERDICT OF THE FIXED VOCABULARY IS ISSUED ANYWHERE IN THIS FILE.** No `PASS`, no
`GATE FAIL`, no `NOT A RESULT`, no GCI, no observed order. Every number below carries the label
**FEASIBILITY**. Where this document discusses what a gate *would* read, it says so explicitly and
in the conditional, about a **future gated run**, never about these rows.

Companion record already on disk and not duplicated here:
`verification/campaign/JF1_GATE6_FINDING.md` (the gate-6 finding, raised by a lane and verified by
`cfd-supervisor`). This file reproduces that finding **independently, from the raw artifacts**, and
adds a second one the earlier record does not carry (§6).

---

## 1. THE FIVE ROWS ARE RULE-4 COMPLETE — RE-DERIVED HERE, NOT RELAYED

Run root: `/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/`

| row | rc | `End` lines | last `Time =` | `endTime` | `ExecutionTime` count | fields at 8000 | age guard |
|---|---|---|---|---|---|---|---|
| `JF1_L1_UNBLOWN_A0` | 0 | 1 | 8000 | 8000 | 8000 | `U k nut omega p phi yPlus` | 8000/U newer than 0/U |
| `JF1_L1_BLOWN_CMU005_A0` | 0 | 1 | 8000 | 8000 | 8000 | same | newer |
| `JF1_L1_BLOWN_CMU010_A0` | 0 | 1 | 8000 | 8000 | 8000 | same | newer |
| `JF1_L1_BLOWN_CMU020_A0` | 0 | 1 | 8000 | 8000 | 8000 | same | newer |
| `JF1_L1_BLOWN_CMU040_A0` | 0 | 1 | 8000 | 8000 | 8000 | same | newer |

`rc` from each row's `SOLVER_RC.txt`; the rest from `log.simpleFoam`, `system/controlDict` and
`stat` mtimes on `0/U` and `8000/U`. **All five clauses hold on all five rows.** These runs have no
`0/T` (there is no temperature field in this case); the age guard is taken on `0/U`, which the
launcher writes last, and is stated as such rather than silently substituted.

**Disclosed, because it changes what the unblown row can be compared with:** in
`JF1_L1_UNBLOWN_A0` the `jetSlot` patch is a **wall** with `noSlip`, and `forceCoeffs` integrates
`(airfoil jetSlot)`. In the four blown rows `jetSlot` is a `patch` and `forceCoeffs` integrates
`(airfoil)` only. The frozen §5.2a registers one BC family across the whole sweep, so **the unblown
row here is not a member of the blown family** and cannot serve as the §1.1 unblown reference for
it. This was disclosed in the queue entry before launch
(`cases/JF1_JET_FLAP/queue_drafts/JF1_L1_BLOWN_CMU020_A0.json`) and is repeated, not softened.

---

## 2. THE SHARPEST FINDING — GATE 6's COMPARAND IS A PROJECTION MISMATCH, AND IT IS EXACT

### 2.1 What one command shows

```
grep -h 8000 verification/runs/JF1_jet_flap/JF1_L1_BLOWN_CMU020_A0/postProcessing/jetMassFlow/0/surfaceFieldValue.dat
grep -A3 'Region type' verification/runs/JF1_jet_flap/JF1_L1_BLOWN_CMU020_A0/postProcessing/jetMassFlow/0/surfaceFieldValue.dat
sed -n '/jetSlot/p' verification/runs/JF1_jet_flap/JF1_L1_BLOWN_CMU020_A0/0/U
```

which return, respectively, `sum(phi) = -1.9364916925e-03`, `Area = 5.0000000000e-05`, and the
boundary condition `value uniform (38.72983385 -22.36068000 0)`.

**`38.72983385 × 5.0000000000e-05 = 1.9364916925e-03`.** The measured flux is the patch area times
the **x-component** of the jet velocity, to every digit the solver prints. It is not a converged
approximation to anything — the BC is a uniform `fixedValue` on a planar patch, so the flux is
algebraically exact and carries **zero** discretisation or iteration error.

### 2.2 The ratio, per row, to 10 digits — measured, from `postProcessing/jetMassFlow/`

Comparand as the frozen §5.6 hazard-3 clause words it operationally: `V_j · h · t_z [m³/s]`,
`h = 0.005 m`, `t_z = 0.01 m` (measured, §3), `V_j = U_inf sqrt(C_mu_jet/(2h/c))`.

| `C_mu_jet` | `V_j` (m/s) | `Σ phi` measured (m³/s) | `V_j·h·t_z` (m³/s) | ratio | shortfall |
|---|---|---|---|---|---|
| 0.05 | 22.3606797750 | −9.6824584650e-04 | 1.1180339887e-03 | **0.8660254127** | **13.39745873 %** |
| 0.10 | 31.6227766017 | −1.3693064110e-03 | 1.5811388301e-03 | **0.8660254147** | **13.39745853 %** |
| 0.20 | 44.7213595500 | −1.9364916925e-03 | 2.2360679775e-03 | **0.8660254125** | **13.39745875 %** |
| 0.40 | 63.2455532034 | −2.7386127785e-03 | 3.1622776602e-03 | **0.8660254009** | **13.39745991 %** |

`cos(π/6) = 0.866025403784`. The ratio matches it to **8 significant figures on every row**. The
residual ~1e-8 disagreement is **not physics and not convergence**: it is the rounding in the
launcher's written BC. The exact `V_j cos τ` at `C_mu_jet = 0.2` is `38.72983346`; `0/U` on disk
carries `38.72983385`, a relative difference of `1.0e-08` — which is precisely the size of the
ratio's departure from `cos τ`. **The finding reproduces independently and I confirm it.**

Independence of `C_mu_jet` across a 2.83× span of `V_j` excludes every convergence, resolution or
velocity-dependent mechanism. The mechanism is geometric: **`jetSlot` is the blunt base**
(§3.1 of the registration), its face normal is along the chord, and `Σ phi` is a flux through that
face, so it carries only the chord-normal component `V_j cos τ`. The registered comparand
`ρ h V_j` is the full magnitude.

### 2.3 What that means for the frozen gate, stated as the registration is written

> **FROZEN GATE LINE 6 (`JF1_PREREGISTRATION.md:24`) — *jet mass flow through `jetSlot` vs
> `ρ h V_j`, ≤ 0.5 %, else `NOT A RESULT`* — REGISTERS A COMPARAND THAT THE REGISTRATION'S OWN
> BOUNDARY CONDITION (§1.6a: `U_jetSlot = V_j (cos τ, −sin τ, 0)`) AND ITS OWN GEOMETRY
> (§3.1: the slot IS the base, normal along the chord) CANNOT PRODUCE.**
>
> **As frozen, it must read `NOT A RESULT` on every gated row, at a measured 13.3975 % against a
> 0.5 % threshold — 26.8× outside its own band — for a REGISTRATION reason and not a physics
> reason.** The jet delivers exactly the momentum the BC asks of it. What is wrong is the
> comparand, not the solve.

**No fix is proposed as adopted.** Altering a frozen gate, threshold, cap or label is reserved to
Sanaa (`ESCALATION_CHARTER.md`; CLAUDE.md rule 2). §7 below lists the candidate repairs as options
for her desk, with the cost and consequence of each.

---

## 3. `t_z` MEASURED FROM THE MESH — AND A SECOND REGISTRATION MISMATCH

**CONFIRMED: `t_z = 0.01 m`.** Derived independently from `constant/polyMesh` on all five rows, not
taken from any script or readout: the `points` file carries exactly two distinct z values,
**−0.005 and +0.005**. Summing the face-area vectors of the 12 `jetSlot` faces (Newell/fan
decomposition over the face points) gives

- `Σ|Sf| = 5.0000000000e-05 m²`, i.e. **`h × t_z` = 0.005 × 0.01**, with `h` = 0.005 m confirmed
  from the patch's own y-extent (−0.0025 … +0.0025) and its x-extent (1.0 … 1.0, the base plane);
- outward unit normal **(−1, 0, 0)** — which is why `Σ phi` is negative: the jet flows *into* the
  domain. The `airfoil` patch's area-vector sum is the exact negative, `(+5e-05, 0, 0)`, as a
  closed body requires.

The same figure is printed independently in the function-object header
(`postProcessing/jetMassFlow/0/surfaceFieldValue.dat`, `# Area : 5.0000000000e-05`) and is
consistent with `# Aref : 1.0000000000e-02` in the `forceCoeffs` header (`= c × t_z`).

**So the per-unit-span comparand is `ρ V_j h t_z`, and the supervisor's `t_z = 0.01 m` is CONFIRMED
from the mesh itself.**

### 3.1 SECOND FINDING, NOT IN `JF1_GATE6_FINDING.md`

The frozen registration §5.6 registers **`t_z = 1.0 m` exactly** with `Aref = 1.0`, and §7.4
registers a comparator refusal: *`area(jetSlot) = 0.005 m²` to 1e-9, else the comparator refuses
(exit 2)*. **The measured area is `5.0e-05 m²` — a factor of 100 out.** On these feasibility
meshes that registered cross-check would refuse.

**This is a mesh/registration mismatch, not a wrong coefficient.** `Aref` was set to `1.0e-02` to
match the mesh's actual span, so `CL` and `Cd` are correctly non-dimensionalised and the very
hazard §5.6 was written to catch **was** caught by whoever built the case. But the frozen document
registers a *specific* `t_z` and a *specific* area check, and the feasibility meshes satisfy
neither. **A future gated run must either be built at `t_z = 1.0 m`, or Sanaa must rule on §5.6's
number.** Reported, not repaired.

Related and also reported: these feasibility rows run on a **39,984-cell O-mesh** (408 × 98 × 1,
farfield circle of radius 26 m), not the registered **46,180-cell C-mesh with the 3c wake box**
(§3.2, §4.2). `build_jf1.py` prints at every build that the O-mesh does not satisfy §1.3's wake
box. **That alone bars any gated or theory row from being computed on these meshes**, and it is why
§4 below is presented as physics reconnaissance and nothing more.

---

## 4. THE HEADLINE TABLE, BOTH WAYS

### 4.1 Achieved jet momentum coefficient

The registration defines `C_mu_jet` **algebraically**, not by momentum flux: §0 gives
`C_mu_jet = (rho_j h V_j²)/(0.5 rho_inf U_inf² c)` and §2 inverts it to
`V_j = U_inf sqrt(C_mu_jet/(2 h/c))`, verifying against `C_mu_jet = 2(h/c)(V_j/U_inf)²`. **Checked
against §0 and §2 and stated: the registration's `C_mu_jet` is the algebraic formula, and it is the
formula that sets the BC.** It is *not* defined as the measured momentum flux, and the registration
nowhere reconciles the two.

They differ, because the momentum actually leaving through the base patch is
`J = ṁ V_j = ρ h t_z V_j² cos τ`. Derived from the **measured** flux (`ṁ = |Σ phi|` with ρ = 1;
`J = ṁ V_j`; `C_mu_achieved = J / (0.5 ρ U_inf² c t_z)`), **not** by multiplying by cos 30°:

| `C_mu` nominal | `ṁ` measured (kg/s) | `J` (N) | **`C_mu` achieved** | achieved/nominal |
|---|---|---|---|---|
| 0.05 | 9.6824584650e-04 | 2.1650635317e-02 | **0.0433012706** | 0.8660254127 |
| 0.10 | 1.3693064110e-03 | 4.3301270734e-02 | **0.0866025415** | 0.8660254147 |
| 0.20 | 1.9364916925e-03 | 8.6602541246e-02 | **0.1732050825** | 0.8660254125 |
| 0.40 | 2.7386127785e-03 | 1.7320508019e-01 | **0.3464101604** | 0.8660254009 |

The reasoning `C_mu_achieved = C_mu_nominal · cos τ` is therefore **confirmed by measurement**, to
8 significant figures, with the residual traced to BC rounding (§2.2). It is also consistent at the
level of the reaction vector: the momentum-flux reaction is
`C_mu_achieved (−cos τ, +sin τ, 0)`, whose component on the registered `liftDir` is
`C_mu_achieved sin(τ + α)` — the registered §1.6 form with the achieved coefficient substituted.

### 4.2 The table

Jet-reaction convention is **the registration's**: `C_mu_jet · sin(τ + α)`, §1.6 and §1.6a, with
α = 0 here so `sin(τ + α) = sin 30° = 0.5`. (The commissioning directive's `C_mu sin(τ)` is *not*
used; at α = 0 the two coincide numerically, and this record uses the registered one by name.)
Theory is the registration's §1.4/§7.3 corrected form, **the whole bracket under the root**:
`dCL/dτ = sqrt( 4π C_mu (1 + 0.151 sqrt(C_mu) + 0.139 C_mu) )`, `CL_theory = τ · dCL/dτ`,
`τ = π/6`.

`CL_aero`, `Cd`, `CmPitch` are the Time-8000 row of
`verification/runs/JF1_jet_flap/<row>/postProcessing/forceCoeffs/0/coefficient.dat`, columns read
from that file's own header.

**FEASIBILITY. NO GATE SCORES ON ANY OF THIS.**

| `C_mu` nom | `CL_aero` | `Cd` | `CmPitch` | jet reac (nom) | `CL_total` (nom) | `CL_theory` (nom) | **% diff (nom)** | jet reac (ach) | `CL_total` (ach) | `CL_theory` (ach) | **% diff (ach)** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.4057332 | 0.0077399 | −0.0880672 | 0.0250000 | 0.4307332 | 0.4234034 | **1.7311 %** | 0.0216506 | 0.4273838 | 0.3934010 | **8.6382 %** |
| 0.10 | 0.5488464 | 0.0049076 | −0.1170796 | 0.0500000 | 0.5988464 | 0.6047757 | **0.9805 %** | 0.0433013 | 0.5921477 | 0.5614336 | **5.4706 %** |
| 0.20 | 0.7439992 | −0.0011546 | −0.1554041 | 0.1000000 | 0.8439992 | 0.8687422 | **2.8482 %** | 0.0866025 | 0.8306018 | 0.8053458 | **3.1360 %** |
| 0.40 | 1.0099942 | −0.0137092 | −0.2060399 | 0.2000000 | 1.2099942 | 1.2594770 | **3.9288 %** | 0.1732051 | 1.1831993 | 1.1648869 | **1.5720 %** |

**Both columns are presented and neither is picked.** They disagree in a structured way: the
nominal column is flat-good and *worsens* with `C_mu`; the achieved column is worse at low `C_mu`
and *improves* with it. Note that the `C_mu = 0.40` row is **outside the gate by registration**
(§7.3) and is here only as the theory-departure exhibit.

> **WHICH `C_mu` THE FROZEN THEORY GATE WOULD BE EVALUATED AT, AS THE REGISTRATION IS WRITTEN:
> THE NOMINAL ONE.** §7.3 tabulates `CL_theory` against the *swept* `C_mu_jet` values
> {0.05, 0.10, 0.20} and registers those ten-digit numbers as the comparands; §0 and §2 define
> `C_mu_jet` algebraically from `V_j`; and the jet-reaction term §1.6 registers is
> `C_mu_jet sin(τ + α)` with the same symbol. Nothing in the frozen document defines a
> flux-measured coefficient or authorises substituting one. **The nominal column is the frozen
> reading. The achieved column is reported here because the measurement says the jet does not
> deliver the nominal momentum, and a reader is entitled to see both.** Choosing between them is a
> change to the registration, which is Sanaa's.

### 4.3 The unblown row

`JF1_L1_UNBLOWN_A0`, Time 8000: **`CL = 5.5059547188e-05`**, **`Cd = 1.1037782810e-02`**,
`CmPitch = −3.7195094527e-07`.

`CL = 5.5e-05` is **consistent with a symmetric section at α = 0**, where the exact answer is zero:
it is 4 orders of magnitude below the smallest blown `CL_aero` (0.406) and comparable to the
residual level of the solve. It is a small non-zero rather than a machine zero because the mesh is
not bit-symmetric about y = 0 and the base is truncated. **This is a consistency reading, not a
validation** — `Cd = 0.01104` is not compared with any reference here, and under ruling O4 the
registration has **no gated `Cd` arm at all** and gate V is `BLOCKED`.

---

## 5. PHYSICALITY — REPORTED, NOT GRADED

Residuals are **initial** residuals at iteration 8000 from
`postProcessing/contErr/0/solverInfo.dat`; continuity from the last
`time step continuity errors` line of `log.simpleFoam`; `y+` from
`postProcessing/yPlus/0/yPlus.dat` at Time 8000; `max|U|` from
`postProcessing/minMaxU/0/fieldMinMax.dat` at Time 8000.

| row | `Ux` | `Uy` | `k` | `omega` | `p` | continuity `sum local` | max `y+` `airfoil` | max `y+` `jetSlot` | max\|U\| | `2 V_j` | ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| UNBLOWN | 2.26e-08 | 5.63e-09 | 2.19e-08 | 5.42e-11 | 2.95e-08 | 1.853e-11 | 0.19142 | 0.06919 | 11.8526 | — | — |
| CMU005 | 7.54e-08 | 4.63e-09 | 4.99e-08 | 5.66e-11 | 4.39e-08 | 8.893e-11 | 0.22562 | **N/A — not a wall** | 24.1525 | 44.7214 | 0.540 |
| CMU010 | 3.24e-07 | 1.03e-08 | 1.32e-07 | 9.85e-11 | 1.04e-07 | 1.868e-10 | 0.25557 | **N/A — not a wall** | 34.1852 | 63.2456 | 0.541 |
| CMU020 | 1.06e-06 | 1.66e-08 | 3.26e-07 | 3.41e-10 | 1.97e-07 | 5.536e-10 | 0.31646 | **N/A — not a wall** | 48.3684 | 89.4427 | 0.541 |
| CMU040 | 3.99e-06 | 3.55e-08 | 1.05e-06 | 5.18e-10 | 4.38e-07 | 1.228e-09 | 0.39817 | **N/A — not a wall** | 68.4111 | 126.4911 | 0.541 |

**`max(y+)` on `jetSlot` is `N/A` on the blown rows and is recorded as `N/A`, never as a pass and
never as a zero** (rule 3). `jetSlot` is a `patch`, not a wall, on those rows; `y+` is not defined
there and the `yPlus` function object correctly writes no line for it. The reader is demonstrably
not blind: **the same reader returns a real `jetSlot` row on the unblown case** (0.06919 at Time
8000), where `jetSlot` *is* a wall. That is the planted control for this zero.

Also reported: `global` continuity ranges −5.68e-12 … +5.77e-10; `cumulative` −4.955e-06 …
+1.169e-06 (both REPORTED, never gated, §5.5b). No row shows a `SIMPLE solution converged` line —
all five ran to the `controlDict` cap of 8000 rather than converging out of the 1e-6 criterion.

### 5.1 FORWARD-LOOKING ONLY — what a **future gated run** would face

*Conditional statement about a hypothetical gated row on a compliant C-mesh. **Not a verdict on
these rows, which are feasibility and score nothing.***

- **Line 7 (`max(y+) ≤ 1`)** — would be met with wide margin on this geometry and near-wall
  spacing: the largest airfoil `y+` measured anywhere in the family is **0.398** at `C_mu = 0.40`,
  a factor 2.5 under the ceiling. Caveat: the gated mesh is a different (finer) mesh, and §4.1
  refines the first cell with the ladder, so `y+` there would be smaller still.
- **Line 8 (continuity `sum local < 1e-6`, ruling O6)** — would be met on every row: the largest
  value in the family is **1.228e-09**, three orders under the gate. The registration's own §17.3
  exemplar predicted 3.0e-09 and the measurement lands the same order.
- **Line 6 (jet mass flow ≤ 0.5 %)** — would **not** be met on any blown row, at 13.3975 %, for
  the registration reason set out in §2.3 and for no other reason. No mesh, iteration count or
  relaxation setting can close a cosine.
- The `max|U|` blow-up guard (`2 V_j`) is comfortable throughout: **0.541 of the guard** on every
  blown row, and the peak sits at the slot lip `(1.0010, −0.0027)` as expected.

---

## 6. COST CALIBRATION (CLAUDE.md rule 12)

Unit: core-minutes = wall s × ranks ÷ 60. **`ranks = 1` on every row**, read from each row's own
`RUN_STATUS.<CASE_ID>.txt`, which is also where `wall_s` is captured (inside the launcher's EXIT
trap, never around a `setsid` line).

| row | wall s | **actual core-min** | registered estimate | ratio actual/pred | cap 45.0/row |
|---|---|---|---|---|---|
| `JF1_L1_UNBLOWN_A0` | 1426 | **23.7667** | 12.71 † | 1.870 | 52.8 % consumed |
| `JF1_L1_BLOWN_CMU005_A0` | 1466 | **24.4333** | 33.90 | **0.721** | 54.3 % |
| `JF1_L1_BLOWN_CMU010_A0` | 1305 | **21.7500** | 33.90 | **0.642** | 48.3 % |
| `JF1_L1_BLOWN_CMU020_A0` | 1340 | **22.3333** | 33.90 | **0.659** | 49.6 % |
| `JF1_L1_BLOWN_CMU040_A0` | 1512 | **25.2000** | 33.90 | **0.743** | 56.0 % |
| **four blown rows** | 5623 | **93.7166** | 135.60 | **0.691** | none breached |
| **all five rows** | 7049 | **117.4833** | 148.31 | **0.792** | none breached |

† The unblown row's estimate is **12.71** core-min, not 33.9 — read from
`verification/queue/cfd/launched/JF1_L1_UNBLOWN_A0.json` and already calibrated as ledger row
**C-227**. The **33.9** figure is the *blown* rows' registered estimate and is in
`cases/JF1_JET_FLAP/queue_drafts/JF1_L1_BLOWN_CMU0*_A0.json` (`cost_core_min_estimate`), **not** in
the `RUN_STATUS` files, which carry only `cap_core_min 45.0`. Stated because the brief that
commissioned this record located it in `RUN_STATUS`; it is not there.

**Gap attribution for the four blown rows — MISPREDICTION, conservative direction, no waste, no
contention.** The estimate came from the 15:35Z timing pilot (`_pilot_2026-08-31T1535Z`), which
reached iteration 468 at ClockTime 119 s **under load average 22.81 on 16 cores** — deliberate,
and the `cost_basis` says so: `119/60/468 = 4.2378e-03` core-min/iteration × 8000 = 33.90. The real
blown runs had the box far less loaded; the measured rates are `1466/8000/60 = 3.0542e-03`,
`2.7188e-03`, `2.7917e-03`, `3.1500e-03` core-min/iteration, i.e. **1.35–1.56× faster than the
pilot rate**. The iteration count was predicted correctly (the estimate was taken at the full
`endTime` rather than at hoped-for convergence, and all four ran to 8000). **The single cause of
the 0.691 ratio is that the pilot's contention was not representative of the run window.** Nothing
here is waste: every artifact these numbers cite is on disk and re-readable, and no row approaches
the 3600 s stall rule (longest 1512 s). **Gross = cleaned = 117.4833 core-min.**

**WASTE, NAMED SEPARATELY AND NEVER ABSORBED INTO THE RATIO** (`COMPUTE_BUDGET_CHARTER.md` §6):
**0.0167 core-min** — attempt 1 of the unblown row, launcher rc 1 at 1 wall second, retained at
`verification/runs/JF1_jet_flap/JF1_L1_UNBLOWN_A0.attempt1_FAILED_2026-08-31T1538Z`. Already booked
in **C-227** and **not double-counted here**. Separately again and **not waste**: **1.9833
core-min** for the pilot, which is the instrument that produced the estimate and is an input to it.

**Dollars — DERIVED, NOT MEASURED**, at the owner-stated $0.0513/core-h for c7a.4xlarge
(reported-by-owner; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5):
**$0.10045** for all five rows, **$0.08013** for the four blown rows.

### 6.1 How much of the frozen 300 core-min family cap remains — **AND THE ANSWER DEPENDS ON A READING NOBODY HAS RULED**

Frozen gate line 9 caps the case at **300 core-min**, Sanaa's number. §12's registered matrix
totals **270.64** core-min (**282.00** with S2), and **contains no feasibility line at all** — F4 is
an L1 *first-order* feasibility item at 4.54 core-min and is not what these five rows are.

- **Reading A — feasibility spend is outside the cap.** This is what the queue entries assert
  (`budget_note`: *"That is the GATED budget and these feasibility rows are not gated spend"*).
  Then the cap is untouched, **300.00 core-min remains** against a registered programme of 270.64
  (282.00 with S2), and the registered slack of **29.36** (or **18.00**) core-min stands.
- **Reading B — the cap is literal and caps the case.** Line 9 says *cost cap, 300 core-min* with
  no feasibility exemption. Then **117.4833 core-min are spent and 182.5167 remain**, against a
  registered gated programme needing **270.64** — a shortfall of **88.12** core-min, and the
  registration's own §12/O7 clause would put gate G **`BLOCKED` on budget**.

**THIS RECORD DOES NOT PICK ONE.** A lane does not resolve a cap question in the direction that
frees budget. The reading is the supervisor's to raise and Sanaa's to settle, and it is stated here
with both arithmetics done so nobody has to redo them.

### 6.2 DRAFT `docs/COST_CALIBRATION.md` ROW — NOT COMMITTED, ID IS A PLACEHOLDER

**The id below is `C-<NEXT>` and is deliberately not filled in.** The highest existing C-number at
HEAD is **227** (re-derived at HEAD, not recalled), but rule 11 requires the id to be taken from
the **maximum existing number re-derived in the same shell invocation as the commit** — peers
append to this ledger constantly. Whoever commits this assigns the id then, and checks the row
renders at exactly ten cells with no unescaped vertical bar (the `C-224` defect).

> `| C-<NEXT> | 2026-08-31 | cfd | ` **JF1 L1 FEASIBILITY BLOWN SWEEP, four rows — feasibility, NO
> GATE, and the row exists because rule 12 owes a calibration at every process completion including
> the ones that score nothing.** Blown jet-flap NACA 0012, `C_mu_jet` 0.05/0.10/0.20/0.40, α 0,
> τ 30°, `Re_c` 1e6, `simpleFoam`/`kOmegaSST` low-Re, 39,984-cell O-mesh, 1 rank, 8000 iterations
> each, launcher rc 0, `End` written, last time == `endTime`, age guard held on all four. Figures
> read from each row's `RUN_STATUS.<CASE_ID>.txt` and from
> `verification/campaign/JF1_L1_FEASIBILITY_FIRST_FIELDS.md`, not from memory. Companion to
> **C-227** (the unblown row), which is **not** re-counted here.
> ` | ` **135.60 core-min** (4 × 33.90; `cost_core_min_estimate` in
> `cases/JF1_JET_FLAP/queue_drafts/JF1_L1_BLOWN_CMU0*_A0.json`; basis 4.2378e-03 core-min/iteration
> × 8000) ` | ` **93.7166 core-min MEASURED** (1466 + 1305 + 1340 + 1512 = 5623 wall s × 1 rank ÷
> 60, from the launchers' own inside-the-wrapper captures) ` | ` gross == cleaned == 93.7166; no
> row approaches the 3600 s stall rule (longest 1512 s) ` | ` **0.691** ` | ` **MISPREDICTION,
> CONSERVATIVE DIRECTION, SINGLE CAUSE, NO WASTE AND NO CONTENTION IN THE RUN WINDOW.** The
> estimate's per-iteration rate was measured on the 15:35Z pilot under **load average 22.81 on 16
> cores**, deliberately, so that it would be conservative. It was: the four real runs measure
> 3.0542e-03 / 2.7188e-03 / 2.7917e-03 / 3.1500e-03 core-min per iteration, **1.35–1.56× faster**.
> The iteration count was predicted **exactly** — 8000, because the estimate was taken at the
> `controlDict` cap and not at hoped-for convergence, which is the correction C-227 asked for and
> it worked. **LESSON: a rate measured under heavy contention is a ceiling, not an estimate. It
> protects the cap and it degrades the calibration; a future estimate should carry both the loaded
> and the unloaded rate and say which is which.** ` | ` **WASTE: 0.000 core-min on these four
> rows.** The 0.0167 core-min of the unblown attempt-1 failure is already booked in **C-227** and is
> not double-counted; the 1.9833 core-min pilot is the instrument that produced the estimate, is an
> input to it, and is not an overrun. ` | ` DOLLARS **DERIVED, NOT MEASURED**, owner-stated
> $0.0513/core-h, reported-by-owner (`COMPUTE_BUDGET_CHARTER.md` §5): **$0.0801** actual, $0.1159
> estimated, $0.1539 at the 4 × 45.0 registered caps. **No cap breached** — the fullest row consumed
> 56.0 % of its 45.0; the cap was not raised and never is. ` | ` Record
> `verification/campaign/JF1_L1_FEASIBILITY_FIRST_FIELDS.md`; finding
> `verification/campaign/JF1_GATE6_FINDING.md`; registration `verification/campaign/JF1_PREREGISTRATION.md`
> frozen `12b1bd84`; run roots `verification/runs/JF1_jet_flap/JF1_L1_BLOWN_CMU0{05,10,20,40}_A0/`.
> **Family-cap position is REPORTED UNRESOLVED — see §6.1 of the record: 300.00 or 182.52 core-min
> remain depending on whether feasibility spend counts against frozen gate line 9, which no ruling
> settles.** `|`

---

## 7. FOR SANAA'S DESK — THE CANDIDATE REPAIRS, AS OPTIONS AND NOT AS DECISIONS

**The gate is frozen. Altering a gate, threshold, cap or label is reserved to Sanaa, and none of
the following is adopted, applied or assumed by this record.** They are listed with their cost and
their consequence so the choice can be made on arithmetic already done.

| # | Option | Compute cost | Consequence |
|---|---|---|---|
| **R1** | **Correct the comparand to `ρ h V_j t_z cos τ`** — i.e. gate the flux against the projection the geometry actually produces. | **0 core-min.** No re-run; the check is arithmetic on data already on disk. | Gate 6 becomes satisfiable and would read **~1e-8** relative mismatch — a genuinely tight, genuinely informative check on the BC chain. **But it changes a frozen threshold's comparand**, which is exactly what rule 2 forbids a lane and a supervisor from doing. |
| **R2** | **Raise `V_j` so the achieved `C_mu` equals the nominal**, i.e. set `V_j' = V_j / sqrt(cos τ)` (a 7.46 % increase). | **~93.7 core-min** to re-run the four blown feasibility rows; the gated map is unaffected in count. | Makes the *physics* match the registered `C_mu_jet` sweep, so §7.3's ten-digit `CL_theory` comparands stay valid as frozen. **But gate 6 still fails**, because the flux is still `ρ h V_j' t_z cos τ` ≠ `ρ h V_j'`. **This fixes the coefficient, not the gate.** |
| **R3** | **Slot the jet through a face whose normal is the jet direction** — a τ-inclined slot rather than the chord-normal base. | **Mesh rebuild at all three levels plus the full ladder — ≥ 200 core-min**, and it re-opens §3.1's gate-integrity argument for the base slot. | Gate 6 becomes satisfiable *as literally frozen*, with no comparand change. **But it changes the registered geometry** (§3.1), which is a bigger change than the one it avoids, and §3.1's reasoning for the base slot is sound. |
| **R4** | **Leave the gate frozen and let it read `NOT A RESULT` on every gated row**, recording the reason. | 0 core-min. | Rule-2-pure and completely honest. **But it makes the whole gated ladder unusable**: rule 5's ordering is one-way, a physicality gate can only turn a row *into* `NOT A RESULT`, and so gates 2, 3, 4 and 5 would carry no reportable verdict on any row. This is the `F23b` outcome. |

**MY RECOMMENDATION, OFFERED AS A RECOMMENDATION: R1.** It is the only option that costs nothing,
changes no physics, and repairs the thing that is actually wrong. The measurement is unambiguous
about *what* is wrong — the comparand omits a projection the registration's own §1.6a and §3.1
require — and R1 changes exactly that and nothing else. R2 spends 93.7 core-min and does not fix
the gate. R3 spends more than the whole family's remaining budget and undoes a well-argued
geometry choice. R4 is correct-by-rule and throws the ladder away.

**Against my own recommendation, stated because it is the strongest argument on the other side:**
R1 is a comparand change to a frozen gate, and the reason rule 2 exists is that a comparand chosen
*after* seeing the data is not evidence. The defence is that the corrected comparand is derivable
from the registration's own §1.6a and §3.1 with no reference to any measurement — but that defence
is exactly what a motivated repair would also claim, and **that is why this is Sanaa's call and not
mine.**

---

## 8. WHAT COULD NOT BE ESTABLISHED

1. **Whether these rows' physics is right.** The mesh is a 39,984-cell **O-mesh** with no wake box,
   and `build_jf1.py` prints at every build that it is inadequate for a blown row. The `CL` values
   in §4.2 establish that the jet BC chain runs, meshes, converges and delivers a measurable
   momentum. **They establish nothing about the jet-flap physics**, and the agreement figures in
   §4.2 — good-looking as they are — must not be read as theory agreement.
2. **Whether the frozen theory gate would pass on a compliant mesh.** Not knowable from these rows.
3. **The registered `t_z`.** §5.6 registers `t_z = 1.0 m` and §7.4 registers an `area(jetSlot) =
   0.005 m²` refusal; the mesh gives `t_z = 0.01 m` and `5.0e-05 m²`. I established the
   **measurement** but not the **intent**: whether the registration's `t_z = 1.0` is a requirement
   on the mesh or a placeholder that the `Aref` bookkeeping already satisfies is not resolvable
   from the document.
4. **The family-cap reading (§6.1).** Two defensible readings give 300.00 or 182.52 core-min
   remaining. No ruling settles it and I did not pick one.
5. **The `1.0e-08` residual in the flux ratio.** I traced it to the BC written in `0/U`
   (`38.72983385` against the exact `38.72983346`), and the size matches. I did **not** read
   `run_jf1_blown.sh` to identify which rounding step produces it, so the attribution is
   consistent-with rather than demonstrated.
6. **Iterative convergence.** No row wrote a `SIMPLE solution converged` line; all five ran to the
   8000-iteration cap with `p` residuals at 4e-08 … 4e-07. That is *tight*, but the frozen 1e-6
   all-channel criterion was never *declared* met by the solver, and I have not established
   plateau in the rule-5 sense (which needs a triple, and there is only one level here).
7. **Anything about `α ≠ 0`, L2, L3, the Roache triple, GCI or observed order.** No such run
   exists.
