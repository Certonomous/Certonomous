# VMFL007 — Non-Newtonian Flow in a Pipe — PRE-REGISTRATION

**Frozen 2026-08-25. Drafted by `ansys-lane-opus` for the `ansys-verification`
supervisor to freeze and unlock.** Prediction-first under `CLAUDE.md` rule 2: the
gate, the threshold, the cap and the label below are committed **before** any
graded solver starts. **No directory exists under
`verification/runs/ansys_verification/VMFL007/` at this commit** — that is the
condition, and it was checked by `ls` returning nothing at the writing invocation.

**Amendments before first compute are legal and must state the condition and how
it was checked. After first compute this document is closed**: changes land only
as dated addenda that cannot alter a gate, threshold, cap or label.

---

## 1. Identity, and the manual page

| field | value |
|---|---|
| Case | **VMFL007 — Non-Newtonian Flow in a Pipe** |
| Manual | Ansys Fluid Dynamics Verification Manual, **Release 2026 R1, March 2026** |
| Page | **printed p. 29** (PDF p. 43); results table `.07.1` |
| Reference cited by the manual | **W. F. Hughes and J. A. Brighton, *Schaum's Outline of Theory and Problems of Fluid Dynamics*, McGraw-Hill Book Co., New York, 1991** |
| Physics/Models (manual) | "Steady laminar flow, power law for viscosity" |
| Solver here | OpenFOAM **v2606**, `simpleFoam` (steady, incompressible, SIMPLE) |

**Title-page verification (`CLAUDE.md` rule 15, charter §4.2), done in this lane
and not inherited.** The sidecar's head reads *"Ansys Fluid Dynamics Verification
Manual / ANSYS, Inc. / Release 2026 R1 / March 2026 / Southpointe / 2600 Ansys
Drive / Canonsburg, PA 15317"*. The PDF beside it reports `Title: Fluid Dynamics
Verification Manual`, `Creator: DocBook XSL Stylesheets V1.76.1`,
`Producer: XEP 4.22`, **290 pages**. These agree with the charter's recorded
fingerprint. Sidecar sha256
`577659469a30e0f318b026545ad45e1efe2276fc0719404689db8c5a78f9c922` — recorded as
an identifier, **not** as the verification, which was done on the title page.

### 1.1 The manual's own numbers, quoted for context and **never used as the gate**

| | Target | Ansys value | Ratio |
|---|---|---|---|
| Pressure drop (Fluent, table .07.1) | **60.52 kPa** | 60.41 kPa | 0.998 |
| Pressure drop (CFX, table .07.2) | **60.52 kPa** | 61.52 kPa | 1.0165 |

Charter §5.1: Ansys's own reported value is **context, not the gate**.

---

## 2. The archive, re-verified in this lane rather than inherited

Read from **`/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/VM2026R1_FLUENT_ARCHIVES/VMFL007_WB.wbpz`**
— the canonical home ruled by charter Amendment 1.1, **outside the repository**.
sha256 `2ba6f97b935eccc299335556688beb166b888e666819744b8ebcd7f3213ff5a4`,
**identical before and after** the read. The container was **copied** to
`/tmp/claude-1000/` and unpacked **there**; nothing under
`/home/ubuntu/ansys-vm2026r1/` was written, moved, renamed or deleted, and
nothing was unpacked inside the repository.

Read **byte-exact from the configured case's own settings blob**
(`dp0/FLU/Fluent/VMFL007_powerlaw-visc-1.cas.h5`):

```
(materials ((fluid fluid ... (density (constant . 1000)) ...
   (viscosity (non-newtonian-power-law 10 0.4 0 0) (constant . 9.999999699999999e-06)) ...
```

| quantity | archive | manual p. 29 | agree |
|---|---|---|---|
| density | `(density (constant . 1000))` | 1000 kg/m³ | yes |
| viscosity method | `non-newtonian-power-law` | "Viscosity: Power law" | yes |
| k | `10` | k = 10 | yes |
| n | `0.4` | n = 0.4 | yes |
| **min / max viscosity limits** | **`0 0` — BOTH DISABLED** | (not stated) | — |
| dimensionality | **`(rp-axi? . #t)`, `(rp-3d? . #f)`**, a zone named `axis` | — | **2-D axisymmetric** |
| pipe length / diameter | profile export at x = 0.1 m; r_max = 1.2357e-3 < R | 0.1 m / 0.0025 m | yes |

**Three findings from the archive that the brief did not carry, each load-bearing:**

1. **The inlet is NOT uniform.** The manual's Boundary Conditions cell reads
   *"Fully developed velocity profile at inlet with an average velocity of 2 m/s"*.
   The archive holds `VMFL007_powerlaw-visc.set.prof`, a 20-point profile export
   at x = 0.1 m. Its `velocity-magnitude` column is reproduced by the analytic
   fully-developed power-law profile `u(r) = u_max (1 − (r/R)^3.5)`,
   `u_max = 3.142857142857143 m/s`, **to 0.09–0.15 % on a 20-cell mesh** — e.g.
   at r = 6.143237e-04 the archive reads 2.879059 against the formula's 2.881510.
   A uniform 2 m/s inlet would need an entrance length of ≈ 0.05·Re·D ≈ 0.0106 m,
   ~10 % of the pipe, and would **not** give the manual's target. **This case is
   run with the analytic fully-developed profile imposed at the inlet, and the
   profile is asserted on two independent channels (§9).**
2. **`(viscosity ... (constant . 9.999999699999999e-06))`** sits beside the
   power-law method as an unused leftover. **That number is exactly the value
   that makes the `powerLaw`-class trap of §3 a factor of 1000.** It is recorded
   here because it is the specific stray constant an incorrect port would pick up.
3. **The archive's own stored result disagrees with the manual's printed one.**
   `VMFL007_validate_table_pressure2.srp` reads
   `Average of Facet Values / Static Pressure [Pa] / inlet  60498.203`, i.e.
   **60.498 kPa (−0.0360 % from 60520 Pa)**, against the manual's printed Fluent
   value of **60.41 kPa (−0.1818 %)**. The archive's stored solution is **five
   times closer** to the target than the number the manual tabulates for it.
   **This is recorded, not resolved.** It changes nothing here — the gate is the
   manual's **Target**, not either Fluent number — and it is drafted as an `N-AV`
   entry for the supervisor (§13).

---

## 3. REFERENCE-KIND CLASSIFICATION

**A required field of every registration and close-out from this case forward.**

> ### **REFERENCE KIND: CLOSED-FORM / EXACT — category 1.**

**The ground, stated so a cold reader can check it.** The manual's Target of
**60.52 kPa** is not an experiment, not a benchmark computation and not a
correlation. It is **the exact analytical solution** for fully developed laminar
flow of a power-law fluid in a circular pipe (Rabinowitsch–Mooney), evaluated at
the manual's own material properties and geometry. The closed form of §4 gives
**60521.96938383448 Pa**; the manual prints **60.52 kPa**. They agree to
**+0.0032541042 %** — which is *within the rounding of the manual's own four
significant figures*. **The manual's target IS the closed form, printed short.**

**What this classification buys and what it forbids** (charter §6; `COVERAGE_ROWS.md`;
the supervisor's relay of Sanaa's ruling of 2026-08-25):

| column | available? | why |
|---|---|---|
| **V** — the code converges to the exact solution | **YES, and it must be MEASURED** | The exact solution exists. But `N-AV7` is binding: **a small GCI does NOT license the V column.** V is earned only if the Richardson extrapolate lands **on** the exact value; VMFL005 had a 0.0502 % GCI and extrapolated *away* from exact. |
| **G** — a converging grid triple | **YES** | Laminar, **no wall function**, so `N-AV10` does not apply and a ratio-2 **radial** triple is legitimate (§7). |
| **P** — validation against a public primary source | **NO** | A closed-form reference **buys V and never P.** |

> ### **TIER CEILING, DECLARED IN ADVANCE: `GATE REACHED`.**
> **`HOLDS` is not claimable on this case**, because P is unavailable for a
> closed-form reference. **`GATE REACHED` is a SUCCESS CONDITION for this team,
> not a shortfall.** This registration will not tier above what the case holds —
> **and it will not tier below it either**: if the triple is `CONVERGING` and the
> gate is met, the row is `GATE REACHED` and is a credential.

**One thing this section does NOT do.** `COVERAGE_ROWS.md` §202 flags to the
supervisor an unresolved question about what the **P** column actually asks for
(a public primary source, versus a frozen pre-registration that passed) — the two
readings are visibly in tension in that file's own row 3. **That question is not
resolved here and this lane does not resolve it.** The ceiling above is declared
on the supervisor's instruction under the reading that P means a public primary
source. If the supervisor rules otherwise, the ceiling is the supervisor's to
change **before** compute, as a §14 amendment.

---

## 4. The closed form — derived independently in this lane

**The supervisor derived this personally and asked to be told if it is wrong.
It is not wrong.** Re-derived here from the Rabinowitsch–Mooney relation without
reference to the supervisor's arithmetic, and cross-checked by a second, formally
independent route (Metzner–Reed) that agrees to **15 significant figures**.

For fully developed laminar flow of a power-law fluid `τ = k γ̇ⁿ` in a pipe:

```
apparent (Newtonian) wall shear rate   8V/D                       = 6400          1/s
Rabinowitsch-Mooney correction         (3n+1)/(4n)                = 1.375         -
true wall shear rate                   γ̇_w = 1.375 × 6400         = 8800          1/s
wall shear stress                      τ_w = k γ̇_w^n              = 378.2623086489655  Pa
pressure drop                          Δp  = 4 L τ_w / D          = 60521.96938383448  Pa
                                                                  = 60.5219693838      kPa
```

| check | value |
|---|---|
| **τ_w** | **378.2623086489655 Pa** — supervisor's 378.2623 Pa **CONFIRMED** |
| **Δp** | **60521.96938383448 Pa** — supervisor's 60521.969 Pa **CONFIRMED** |
| **vs the manual's printed 60.52 kPa** | **+0.0032541042 %** — supervisor's +0.0033 % **CONFIRMED** |
| **Re, generalised** | **84.59737930087186** — supervisor's 84.60 **CONFIRMED**; firmly laminar (transition ≈ 2100) |

The Reynolds number was computed two ways that share no algebra:
`Re = 8ρV²/τ_w = 84.59737930087186` and the Metzner–Reed form
`Re = ρ V^(2−n) Dⁿ / (k ((3n+1)/(4n))ⁿ 8^(n−1)) = 84.59737930087188`. They differ
in the last digit only. **The derivation is sound.**

These five constants are frozen into `grade_vmfl007.py` to full double precision,
and the comparator **refuses** if its own `closed_form()` ever stops reproducing
them (clause `F1`).

---

## 5. THE GATE

> ### **GATE: `|Δp_lab − 60520 Pa| / 60520 Pa ≤ 0.005` (0.5 %).**
> ### **Band: `[60217.40, 60822.60] Pa`. Applied to the FINE level, `L3_100x100`.**

`Δp_lab = ρ · ( areaAverage(p)|inlet − areaAverage(p)|outlet )` at `endTime`,
`ρ = 1000 kg/m³`, from
`postProcessing/{pInlet,pOutlet}/0/surfaceFieldValue.dat`.

### 5.1 How the tolerance was chosen — on the physics and the reference's precision

**Not on what would be easy to pass.** The reasoning, in the order it was applied:

1. **The reference's own precision sets the floor.** 60.52 kPa is printed to four
   figures, so the reference is known only to **± 5 Pa = ± 0.00826 %**. A gate
   tighter than that would be grading the manual's typesetting.
2. **The pre-registered one-signed error budget (§6) sums to ≈ +0.011 %.** Every
   term whose sign and size are known *before* the run — the printed rounding
   (+0.0033 %), the wedge modelling bias (+0.0038 %), the inlet quadrature
   (+0.06 % at L1, falling with refinement) — is small.
3. **The unmeasured term is discretisation**, and it is the one a tolerance must
   leave room for. 0.5 % leaves **≥ 3× headroom** over the known budget plus a
   plausible fine-grid GCI.
4. **The gate must be able to fail, and it must fail something real.** At 0.5 %:

| value | Pa | deviation | gate |
|---|---|---|---|
| exact closed form | 60521.97 | +0.0033 % | **PASS** |
| wedge-corrected exact (what this model should give) | 60524.27 | +0.0071 % | **PASS** |
| the archive's own stored solution | 60498.20 | −0.0360 % | **PASS** |
| **Ansys Fluent, as the manual prints it** | 60410 | −0.1818 % | **PASS** |
| **Ansys CFX, as the manual prints it** | **61520** | **+1.6523 %** | **GATE FAIL** |

   **Ansys CFX's own reported value FAILS this gate.** The gate is therefore not
   a formality: it is **3.3× tighter than CFX's own agreement** with the manual's
   target and **6× tighter than the manual's own stated 3 % accuracy goal**
   (`N-AV1`).
5. **0.25 % was considered and rejected**, honestly and on the record: it would
   leave under 2.5× headroom on an *unmeasured* discretisation term, which is
   choosing a threshold one cannot yet justify. 0.5 % is the tightest band this
   lane can defend before seeing a number.

### 5.2 What would FAIL — stated explicitly, as required

**Any Δp outside `[60217.40, 60822.60] Pa`.** Concretely, and these are the
failures this case is actually exposed to:

| failure | Δp would read | deviation | outcome |
|---|---|---|---|
| the manual's `k = 10` used raw as a **kinematic** coefficient | **959 208.6 Pa** | +1485 % | **GATE FAIL** by a factor of 15.85 |
| the **wrong `powerLaw` class** seeded from a Newtonian `nu0 = 1e-05` | **3 818.7 Pa** | −93.69 % | **GATE FAIL** |
| a **uniform 2 m/s** inlet instead of the developed profile | entrance loss added over ~10 % of the pipe | — | caught earlier by the §9 profile clause |
| a value 0.75 % out in either direction | 60 066 / 60 974 | ∓0.75 % | **GATE FAIL** |

### 5.3 The DIAGNOSTICS — printed beside the verdict, **never the gate**

| # | reference | value (Pa) | band | what it isolates |
|---|---|---|---|---|
| **D1** | the exact closed form | **60521.96938383448** | **0.25 %** | the whole model chain against the continuum answer |
| **D2** | the **wedge-corrected** closed form, `D1 × sec(0.5°)` | **60524.27396273022** | **0.15 %** | **discretisation alone**, with the known azimuthal bias of §6 removed |

**D2 is the scientifically informative one and it is still a diagnostic.** It
exists so the wedge bias of §6 is *testable* rather than merely declared: the bias
is exactly computable, so a model carrying it should land on D2, not on D1.
Neither D1 nor D2 can change the verdict.

---

## 6. THE ERROR BUDGET, before the freeze — including the wedge bias

**Charter v1.4 Clause A: every pre-registration for a case on an OpenFOAM
axisymmetric `wedge` states the wedge's geometric bias, with its sign and
magnitude, in its error budget, BEFORE the case is frozen.**

### 6.1 The wedge bias — and the term that reaches a Δp gate is **`sec(t/2) − 1`**

An N-sided flat wedge does not represent a circular cross-section. Two deficits,
and **they do not cancel**. Derived here independently, because the distinction is
the one a lane corrected the supervisor on today and the correction was right:

From the fully developed force balance `Δp · A = τ_w · P · L`, with `P` the wetted
perimeter of the cross-section and `A` its area:

```
true circular sector   A = ½R²t          P = R t             P/A = 2/R
flat-sided wedge       A = ½R² sin(t)    P = 2R sin(t/2)     P/A = 2/(R cos(t/2))
ratio (wedge / true)   = 1/cos(t/2) = sec(t/2)          ->  Δp biased HIGH
```

**At the chosen `t = 1°`:**

| quantity | flat wedge ÷ true circle | deficit |
|---|---|---|
| cross-sectional **AREA** | `sin(t)/t` = 0.9999492312032947 | 0.005076879670529166 % |
| **WALL ARC** length | `sin(t/2)/(t/2)` = 0.9999873076558379 | 0.001269234416212406 % |
| **their RATIO** = `sec(t/2)` | **1.00003807838573699** | **Δp biased HIGH by +0.003807838573699485 %** |

> **The number that reaches this Δp gate is the third row, `sec(t/2) − 1`, NOT the
> `sin(t)/t` area deficit.** `N-AV9`'s headline states the area deficit, which is
> right for an area and is **not** the bias on the graded quantity here.

**SIGN, which is part of the obligation: `HIGH`.** The modelled Δp is biased
**upward**. So if this case's measured Δp comes in above the exact value, this
bias is a candidate explanation and should be **subtracted** before any claim of
model error; if it comes in below, the true departure is **larger** than measured.

**No refinement removes it.** The bias is **azimuthal**; the wedge holds one cell
of angle `t` while the Roache triple refines `r` and `x`. It is invisible to the
triple, invisible to the GCI, and invisible to every convergence check here. That
is why it is a **setup obligation with a deadline — this freeze — and not a
diagnostic to be recalled afterwards.**

### 6.2 Why `t = 1°` and not the team's 5° — a stated criterion, not a preference

`N-AV9` names the mitigation itself: *"use a smaller wedge angle (the deficit is
`O(t²)` … so 1° cuts it ≈ 25×)"*. **The criterion applied here:**

> **The wedge modelling bias must sit BELOW the reference's own rounding
> half-width — so that a bias no refinement can remove is also a bias the
> reference cannot resolve.**

| | Δp bias | vs the reference's ± 0.00826 % | criterion |
|---|---|---|---|
| t = 5° (VMFL003, VMFL005) | +0.09526851633199218 % | **11.5× larger** | **fails** |
| **t = 1° (chosen)** | **+0.003807838573699485 %** | **0.46× — below it** | **meets** |

**The cost of the departure from team precedent, disclosed:** the campaign's
wedge angle is no longer uniform across cases, so `t` must be read from each
case's own `blockMeshDict.template` rather than assumed. The template states it in
its header and the comparator carries it as a frozen constant.

**Measured confirmation that the wedge geometry is what this arithmetic says**
(from the smoke test, so it is on the record before the freeze): the solver's own
inlet-patch area header reads **`1.363469252911e-08 m²`** against the flat-wedge
formula `½R² sin(t) = 1.363469252912774e-08 m²` — **agreement to 12 significant
figures.** The geometry is measured, not assumed.

### 6.3 The whole budget

| # | term | size | sign | removed by refinement? |
|---|---|---|---|---|
| 1 | the manual's printed rounding (reference precision) | ± 0.00826 % | ± | no — it is the reference |
| 2 | closed form vs the printed target | +0.0032541042 % | + | no |
| 3 | **wedge azimuthal bias, `sec(0.5°) − 1`** | **+0.003807838573699485 %** | **+ (HIGH)** | **NO — azimuthal** |
| 4 | inlet-profile quadrature (measured at L1: `sum(phi)/(V·A) = 1.000600`) | +0.060 % at L1 | + | **yes**, ~4× per level |
| 5 | radial/axial discretisation of Δp | **unmeasured — this is what the GCI is for** | ? | yes |
| 6 | `nuMin`/`nuMax` clipping | **asserted ZERO** (§9) | — | n/a |
| 7 | entrance adjustment from the imposed profile to the discrete equilibrium | O(h²) on an O(h²) departure | ? | yes |
| | **one-signed terms known before the run (2+3)** | **≈ +0.0071 %** | + | |

---

## 7. THE GRID FAMILY AND THE ROACHE TRIPLE

**`N-AV10` does not apply, and this is stated explicitly because it is the reason
a genuine `G` column is attainable here.** `N-AV10` constrains a ratio-2 **radial**
triple only where a **standard wall function** is in play, and it is derived from
the y⁺ window `[30, 0.2R⁺]` that such a function needs. **VMFL007 is LAMINAR.
There is no wall function, no y⁺ window and no wall-treatment regime to hold
fixed.** Radial refinement is therefore not merely permitted, it is the
**correct** thing to refine, because the discretisation error in Δp lives in the
resolution of the power-law velocity profile across the radius.

| level | Nx × Nr | cells | h ratio | `checkMesh` (measured, smoke test) |
|---|---|---|---|---|
| `L1_25x25` | 25 × 25 | 625 | 4 h₃ | Mesh OK |
| `L2_50x50` | 50 × 50 | 2 500 | 2 h₃ | Mesh OK |
| `L3_100x100` | 100 × 100 | 10 000 | h₃ | Mesh OK |

**Refinement is by exactly 2 in BOTH directions**, so the representative `h`
halves unambiguously and `RATIO = 2.0` is exact by construction, not estimated.
Radial cells are **uniform** — deliberately ungraded, so `h` has one meaning.

Measured mesh quality, identical at all three levels (the smoke test's
`log.checkMesh.L{1,2,3}`, committed at `23091132`): **non-orthogonality max 0**,
**skewness 0.3332**, **aspect ratio 160.0**, cell openness ~1.6e−16. All inside
`docs/standards/MESH_STANDARD.md` §3 (70° / 4 / 1000-advisory) with wide margin.
*Disclosed:* no `birth_certificate.json` is minted, which is the same
**CHECKED-BUT-UNCERTIFIED** gap charter v1.4 records for this team's other 23
meshes; it is named, not silently passed.

Roache at **`Fs = 1.25`**, ratio 2. **A triple that is not `CONVERGING` makes the
row `NOT A RESULT` whatever its value**, and no GCI is quoted when the three
values are not monotone (`CLAUDE.md` rule 5).

### 7.1 THE OBSERVED ORDER, DECLARED BEFORE THE FACT

| | |
|---|---|
| **formal order of the scheme** | **2** (`Gauss linear`, `corrected` snGrad, `steadyState`) |
| **DECLARED EXPECTED BAND** | **`p ∈ [1.0, 2.5]`** |
| **`p` below 2** | **expected, and it has a NAMED cause** (below) |
| **`p` above 2.5** | **SUSPICIOUS — reported as such** |

**Why below 2 is expected here, named in advance so it is not rationalised
afterwards.** The power-law viscosity is **singular on the axis**: with `n = 0.4`,
`ν(r) = ν_wall · (r/R)^(−1.5) → ∞` as `r → 0`. The truncation error near the axis
therefore involves derivatives of `ν` that do not converge at the scheme's formal
rate. What reaches Δp is dominated by the **wall** region, so the effect should be
modest — but its direction is **downward** on the observed order.

> **AN ORDER ABOVE THE FORMAL ORDER IS NOT A GOOD RESULT. IT IS A SIGN THE TRIPLE
> IS NOT ASYMPTOTIC**, and a GCI computed from it bounds nothing. **Both of this
> team's compressible cases were bitten by exactly this** — VMFL045-R2 measured
> `p = 3.3862` against a formal order of 2, and its `G` column is recorded as
> unclean. The comparator prints `SUSPICIOUS` beside any `p > 2.5`. **It does not
> by itself change the verdict** — a flag that silently overrode a frozen gate
> would be a gate chosen after the fact — but no `V` or `G` column may be claimed
> from a triple carrying that flag.

### 7.2 The `V` column is MEASURED, not inferred from the GCI

`N-AV7` is binding: **a small GCI is a statement about grid convergence ONLY.**
The comparator prints the Richardson extrapolate against **both** the exact value
and the wedge-corrected exact value, because the wedge bias is azimuthal and
**survives extrapolation**. The `V` column is earned only if the extrapolate lands
on the exact solution — as VMFL001-R2's did (3.7 ppm) and VMFL005's did not.

---

## 8. STRICT COMPLETION AND ITERATIVE CONVERGENCE

### 8.1 `CLAUDE.md` rule 4 — every clause, and no clause loosened

The comparator **refuses (exit 2) rather than degrades** on any failure.

| clause | requirement | comparator |
|---|---|---|
| C1 | `rc = 0` | `RUN_RC.txt` |
| C2 | an `End` line in `log.simpleFoam` | regex, anchored |
| C3 | **last time == `endTime`** = **10000** | last `Time = ` line |
| C4 | `ExecutionTime` count == `endTime` = **10000** | line count |
| C5 | fields present at `endTime`: **`U p phi nu`** | on disk |
| C6 | **AGE GUARD** — every field at `endTime` **NEWER** than the case's own `0/U` | mtimes |
| — | the guard **refuses a case where `0/` or a time directory already exists** | in the launcher, before any copy |

**The declared departure from the rule-4 text, stated on the face of this document
and TIGHTER, never looser.** Rule 4's field list `T U p_rgh alphat nut k omega`
is the **thermal family's**. This case is incompressible and laminar and has no
`T`, no `p_rgh`, no `alphat`, no `nut`, no `k`, no `omega`. The list here is
`U p phi nu`, and it **adds** two files the rule does not ask for: **`phi`**, and
**`nu` — the viscosity field itself**, which is what makes the class assertion of
§9 possible. **The age-guard marker is `0/U`**, touched last at launch by the
launcher, in place of the thermal family's `0/T`.

### 8.2 Iterative convergence — the plateau is PRIMARY, the residual is a BACKSTOP

**`endTime = 10000` SIMPLE iterations, IDENTICAL at every level**, so the triple
measures grid refinement and not iteration count. There is **no `residualControl`**:
an early exit would break clause C3.

**PRIMARY, binding — the plateau, in `MONITOR_STANDARD.md` S13's v1.12 form.**
This is a deliberate departure from the clause frozen in `grade_vmfl051.py` and
`grade_vmfl045_r2.py`, and charter v1.4 disclosure 1 says a new registration
*"should gate on a fixed window and say so"*. **This one does, and says so:**

| | S13 form, adopted here | the frozen precedent |
|---|---|---|
| window | **FIXED: the last 1000 iterations**, sampled every 100 → **10 samples** (S13 floor is 9) | last **20 % of the run** |
| normaliser | **the range the series spanned over the whole run** | an **absolute** peak-to-peak |
| threshold | **0.02 %** of that range | 1.0e−3 absolute |
| null clause | a series that never resolvably moved (range < 1 Pa) is **refused**, never passed | — |

A fraction-of-run window *"silently loosens as a run is extended, so the same case
passes by being run longer"*; a mean-normalised criterion measures the **offset**
on a quantity that carries one, and Δp carries a large one.

**SECONDARY, binding, and deliberately LOOSER than VMFL001's — with the reason
stated rather than hidden.** Final initial residual: **`Ux ≤ 1e−5`, `p ≤ 1e−4`.**
VMFL001 run 1 was refused `NOT A RESULT` because its L3 final residual measured
**1.19876e−06 against a frozen `< 1e−6`** — it missed by 20 %. `N-AV5` records
that the fixed-iteration residual *"degrades sharply and NOT by a constant factor"*
with cell count. **A residual threshold at a round number is a lottery, not a
convergence criterion.** So here the residual is what it honestly is — a
**backstop against a solve that stalls at a wrong plateau** — and the *convergence*
question is answered by the plateau, which measures whether **the graded answer**
has stopped moving. **Both bind: failing either is `NOT A RESULT`.**

### 8.3 MONITOR_STANDARD S8 (Courant) — a MEASURED exemption, not an omission

This team has just established that **neither existing compressible comparator
reads Courant at all**. That gap is not repeated here, and it is not papered over
with "a steady solver has no Courant number" either. **A steady `simpleFoam` run
prints no `Courant Number` line, and the comparator ASSERTS that count is ZERO
(clause C7) and refuses if it is not.** The exemption is therefore read off the
artifact. Had a transient solver been chosen, S8 (lines 456–489) would bind and
the comparator would have to read the run **maximum**, never the final line.

---

## 9. THE CONTROLS, AND THE ASSERTS THAT CLOSE THE `powerLaw` TRAP

### 9.1 The trap, characterised exactly from the v2606 sources

**This box carries TWO selectable models named `powerLaw`, with DIFFERENT
dictionary keys, and which one is instantiated is decided SILENTLY by the
laminar/turbulence model.** Read from source, not from memory:

| | **A — CHOSEN** | **B — the trap** |
|---|---|---|
| class | `viscosityModels::powerLaw` | `laminarModels::generalizedNewtonianViscosityModels::powerLaw` |
| path | `src/transportModels/incompressible/viscosityModels/powerLaw/` | `src/TurbulenceModels/…/generalizedNewtonian/…/powerLaw/` |
| selected by | `transportProperties: transportModel powerLaw` | `laminar { model generalizedNewtonian; }` |
| keys | **`k`, `n`, `nuMin`, `nuMax`** | **`n`, `nuMin`, `nuMax` — there is NO `k`** |
| viscosity | `ν = clamp(k · γ̇^(n−1))`, `k` carries `dimViscosity` | `ν = clamp(ν₀ · γ̇^(n−1))`, **`ν₀` from the transport model** |

**A case written for A and run under B does not fail loudly.** `powerLawCoeffs_`
is read with `optionalSubDict` and only `n`/`nuMin`/`nuMax` are `readEntry`-ed, so
a stray `k` is **silently ignored** and the viscosity is wrong by `k/ν₀`. **Seeded
from a Newtonian `ν₀ = 1e−05` — which is exactly the leftover constant sitting in
this case's own archive (§2 finding 2) — that factor is EXACTLY 1000**, and Δp
would read ≈ **3819 Pa** instead of ≈ 60522 Pa.

### 9.2 The kinematic conversion, shown rather than asserted

**Fluent's power law is DYNAMIC**: `μ = k γ̇^(n−1)` in `kg/m-s`, so the manual's
`k = 10` is `Pa·s^n`. **OpenFOAM class A's `k_` is constructed with `dimViscosity`
= `m²/s` — KINEMATIC.** Therefore:

> **`k_OF = k_manual / ρ = 10 / 1000 = 0.01`. The conversion IS needed, it is
> exactly 1000, and getting it wrong inflates Δp by `1000^n = 15.848931924611133`
> to 959 208.6 Pa.**

A **second** factor of 1000 runs the **opposite** way: `simpleFoam`'s `p` is
kinematic (`m²/s²`), so `Δp_Pa = ρ · Δp_foam`. Both are asserted; neither is a
comment.

`strainRate()` is `sqrt(2)·mag(symm(grad(U)))`, which in simple shear equals
`|du/dr|` exactly — so `γ̇` in the model is the same `γ̇` as in §4's closed form.

### 9.3 The asserts — four independent channels, and each one can fail

| # | channel | assert | what it catches |
|---|---|---|---|
| S1 | `log.simpleFoam` | says `Selecting incompressible transport model powerLaw` | class B, or a Newtonian fallback |
| S2 | `log.simpleFoam` | says `Selecting laminar stress model Stokes`, and **never** `generalizedNewtonian` | class B |
| S3 | `constant/transportProperties` as the run consumed it | `k == 0.01` **exactly**, `n == 0.4`, `transportModel powerLaw` | the unconverted `k = 10` |
| S6 | **the `nu` field on disk at `endTime`** | `min(nu) ∈ [2e−05, 8e−05]` | **class B reads ≈ 4.30e−08 — a factor of 1000 out** |

The continuum wall value is `ν_wall = k_OF · γ̇_w^(n−1) = 4.298435325556426e−05
m²/s`; predicted `min(nu)` per level is 4.433/4.365/4.331e−05, approaching it from
above. The band is a factor of ~2 either side and still **465× above** what the
wrong class would give.

**The launcher runs S3 and the class check BEFORE any solver starts**, and it
does so on the dictionary, so a wrong `k` never reaches a mesh. *(One real defect
was found and fixed while testing this: a bare `grep -q generalizedNewtonian`
flagged the dictionary's own warning **comment**. The test now strips comments and
looks for a **selecting line**; both arms are exercised.)*

### 9.4 `nuMin` / `nuMax` must NEVER BIND — asserted, because the archive disables both

The archive runs with **both Fluent viscosity limits set to zero**
(`non-newtonian-power-law 10 0.4 0 0`) — no clipping. OpenFOAM class A
**requires** `nuMin` and `nuMax`, so this case must **prove** its clips are inert:

- `nuMin = 1e-08` — the smallest physical ν is 4.30e−05, **4300× above it**.
- `nuMax = 1.0` — ν exceeds 1.0 only inside `r/R < 1.227e−03`, i.e. `r < 1.53e−06 m`,
  which is **below the finest level's first cell centre** (`r/R = 0.005`). Predicted
  `max(nu)`: 0.0152 / 0.0430 / 0.1216 at L1/L2/L3.
- **Clauses S7:** `max(nu) < 0.5` and `min(nu) > 10·nuMin`, else **REFUSE**.
  *"The clip never fired"* is then a **measured fact**, not a design intention.

### 9.5 The inlet profile — asserted on two independent channels

| # | channel | assert | measured in the smoke test |
|---|---|---|---|
| S5 | `sum(phi)` on the inlet — the **MEAN** | `\|Q\| / (V·A)` within 1 % | **1.000600** (+0.060 %) |
| S5 | `max(U)` on the inlet — the **SHAPE** | `Ux_max ∈ [3.10, 3.15]` | **3.142847411860** |

**The shape clause is the decisive one: a uniform 2 m/s inlet reads exactly
2.0000 and FAILS it.** The flow-rate clause alone could not tell the two apart.

### 9.6 Planted-zero controls (`CLAUDE.md` rule 3)

**A zero from a reader not shown able to see a non-zero is not evidence.**

| # | plants | into | reads back | refuses if |
|---|---|---|---|---|
| **PZ1** | `1.234e-03` | a **COPY** of the gate `.dat`'s last row | **from disk** | not seen to `1e-12` |
| **PZ2** | `7.77e-02` | a **COPY** of the `endTime` `nu` field | **from disk** | not seen to `1e-9` |
| **PZ3** | wrong values into the **arithmetic** | the gate and the Roache logic | — | a wrong-class Δp, an unconverted-`k` Δp, or a 2×-tolerance value **PASSES**; or a non-converging triple yields a **GCI** |

The `--selftest` also plants into an **unplanted** copy and confirms it reads back
zero — so the control is shown able to **fail**, not only to pass.

**`--selftest` result at this freeze: 58 checks, 0 failures**, with real negative
arms throughout (§5.2's four failure modes, all six Roache states, an
above-formal-order triple flagged SUSPICIOUS, and both reader refusals).

---

## 10. COST (`CLAUDE.md` rule 12)

| | |
|---|---|
| **Point estimate** | **15 core-minutes** |
| **CAP** | **60 core-minutes** — enforced by `timeout 3600` per level in the launcher |
| ranks | **1 (serial), three levels run sequentially**; core-min = wall_s × 1 / 60 |
| **derived dollars at the cap** | **$0.0513** at $0.0513/core-h |
| `cost_basis` | **DERIVED from a MEASURED lab record, scaled — not measured, and not a guess** |

**The basis, so it can be checked.** VMFL001's `RESULTS.md` records **104 wall s
for 16 384 cells × 3000 SIMPLE iterations, serial** — that is
`2.115e−6 core-s per cell-iteration` for a laminar `simpleFoam` case on this box.
This family is 625 + 2 500 + 10 000 cells × 10 000 iterations = **1.3125e8
cell-iterations**, giving **4.6 core-min** at that rate. **×4** for the power-law
viscosity update and the stiffer pressure solve — the smoke test's first iteration
needed **429 GAMG sweeps**, so the multiplier is not invented — gives the **15
core-min** point estimate, and the cap is **4× the estimate**.

**This is trivially cheap and the numbers say so:** the cap is **$0.05**, which is
**487× under** the $25 pre-authorisation. **The cap still binds** — a blanket
authorisation is not a per-item reading (`CLAUDE.md` rule 9) — and **an overrun
STOPS the run; it does not get a new budget.** The rate is **owner-stated, not
measured**: this box cannot read its own billing.

**Estimate-versus-actual calibration is owed at completion** (rule 12, charter
§5.7): ratio actual/predicted, attribution, and one row in
`docs/COST_CALIBRATION.md`. **A close-out without that row is incomplete.**

---

## 11. THE GRADING PATH, FIXED AT THIS COMMIT

| artifact | path | blob at `23091132` |
|---|---|---|
| **comparator** | `cases/ansys_verification/VMFL007/grade_vmfl007.py` | **`9a727216a73eedcdfbeff2b40c0f5a8f65db65e6`** |
| **launcher** | `cases/ansys_verification/VMFL007/run_vmfl007.sh` | **`71d26af229d24a6467de0b78e4a2e2da08bf259d`** |
| `case/0/U` | | `b626d65ada23d57c62337f1a26e411c1bdc3cd16` |
| `case/0/p` | | `54562f8cbc730c083492ac97d21c9d7c214414a3` |
| `case/constant/transportProperties` | | `db848a12eb939d1ac0ad81bedea135f536926f38` |
| `case/constant/turbulenceProperties` | | `f68f346789696b45b8d245b57ef06e1fc0aaad55` |
| `case/system/blockMeshDict.template` | | `9ea967ebeedf20eb9428c7785abf966eadbf01a3` |
| `case/system/controlDict.template` | | `fe8524ab1fb2abe1c440b3685c65cb16202e8f65` |
| `case/system/fvSchemes` | | `ad718abf3cdc834b17478c2c391affeba1dbf2b2` |
| `case/system/fvSolution` | | `70953b4ea8d71a0b4744b1df695ceac9e24fa820` |

**`run_vmfl007.sh --prereg-sha <sha>` refuses to start a solver unless `<sha>` is a
real commit carrying this file, and unless
`grade_vmfl007.py --verify-frozen <sha>` confirms the comparator on disk IS the
committed blob.** Run outputs go to
`verification/runs/ansys_verification/VMFL007/<level>/` and nowhere else.

**The evidentiary ordering, which is the point of committing in two acts:** the
machinery landed at **`23091132`, 2026-08-25T16:46:36Z**, in a commit whose
message states that no graded compute had run and none was created. **This
document — the gate, the threshold, the cap, the label — lands separately and
afterwards.** The gate therefore cannot have been chosen to fit an answer, because
at neither commit did an answer exist.

---

## 12. THE PRE-FLIGHT SMOKE TEST (charter v1.4 Clause B) — ALREADY RUN, AND WHAT IT FOUND

**One `simpleFoam` iteration on the coarsest mesh (625 cells), plus `blockMesh`
and `checkMesh` at all three levels, in a scratch directory under
`/tmp/claude-1000/` — OUTSIDE `verification/runs/ansys_verification/`**, so it
cannot create a `0/` or a time directory that would trip the age guard or consume
the run the guard protects. Evidence lives under **the case directory**,
`cases/ansys_verification/VMFL007/smoke_2026-08-25/`, **not** in the runs tree.

**The gate channel was read ONLY through `--dryrun-reader`, which prints structure
and NO value.** Nothing about the answer could reach this document.

**It earned its place — it found three real faults, before the freeze:**

1. `volFieldValue` takes **`operation`**, not `operations`. The solver exited
   `FOAM FATAL IO ERROR` on the viscosity monitor. **A comparator `--selftest`
   would never have found this: a selftest proves the GRADER, never the CASE.**
2. The launcher handed its smoke directory back through
   `$(smoke | tail -1)` — a **command substitution**, i.e. a **subshell**, where
   every `exit 1` inside the function would have killed only the subshell and left
   the script running with an empty value. **The same silent-non-gating class as
   `( set -e; … )`.** Fixed to a file handoff with the status gated in the parent.
3. The `generalizedNewtonian` guard fired on the dictionary's own **warning
   comment**. Fixed to strip comments and match a **selecting line**; both arms
   are now tested.

**Result after the fixes: `rc = 0`, an `End` line, all six monitors written, the
`endTime` directory holding `U nu p phi`, and the log reading `Selecting
incompressible transport model powerLaw` / `Selecting laminar stress model
Stokes`.** Clause B is discharged, and it will run again inside the graded
launcher before the graded run starts.

---

## 13. RECORD-UPDATE DUTY — DRAFTED, NOT LANDED (charter §7, v1.4 Clause C)

Drafted for the supervisor's read; **this lane lands none of them**, and ids are
to be derived **by hand from the tail at the committing invocation**, never from a
count and never with `scripts/append_record.py`, which the supervisor has measured
to assign ids that already exist.

1. **`N-AV12`** *(next in family; strict and permissive maxima agree at 11 —
   re-derive at commit)* — **OpenFOAM v2606 offers TWO selectable `powerLaw`
   viscosity models with different keys, and the wrong one fails SILENTLY by
   `k/ν₀`.** With the sources, the key lists, the `optionalSubDict` mechanism that
   swallows a stray `k`, and the measured factor of 1000 for `ν₀ = 1e−05`.
2. **`N-AV13`** — **for a Δp gate the wedge bias is `sec(t/2) − 1`, not the
   `sin(t)/t` area deficit**, with the force-balance derivation of §6.1 and the
   12-significant-figure area confirmation. This **sharpens** `N-AV9`, whose
   headline states the area deficit; it does not correct it, because `sin(t)/t` is
   exactly right for an area.
3. **`N-AV14`** — **the manual's tabulated Ansys Fluent value for VMFL007 (60.41
   kPa, −0.1818 %) does not match the archive's own stored solution for the same
   case (60498.203 Pa, −0.0360 %)** — the archive is 5× closer to the target than
   the manual says it is. **Recorded, not resolved.**
4. **A `LESSONS` candidate** — **a comparator `--selftest` proves the grader,
   never the case, and never the launcher.** This case is a third specimen beside
   charter v1.4 Clause B's VMFL045 and VMFL003: a clean 58-check selftest coexisted
   with a fatal dictionary key error and a subshell that could not stop the script.
5. **Charter / doc line (Clause C):** the `CASE_MAP.md` and `COVERAGE_ROWS.md`
   rows for VMFL007, and the reference-kind field of §3 as a standing registration
   field. **Not `NONE`** — this case reached the numerics file and the case map.

---

## 14. WHAT THIS LANE COULD NOT VERIFY, AND THE DECLARED RISKS

Stated plainly, before the run, so none of it can be discovered afterwards and
presented as expected.

1. **That the run converges at all.** `endTime` and the relaxation
   (`p 0.3 / U 0.7`) are chosen from precedent, not from a converged run — a
   converged run before the freeze would be exactly the information rule 2
   forbids. **If a level misses the §8.2 clauses the row is `NOT A RESULT`, which
   is an honest outcome and costs ≈ 15 core-minutes.**
2. **The observed order.** §7.1 declares the band and the axis-singularity reason
   it may fall below 2. It is a prediction and may be wrong.
3. **Whether the `V` column is earned.** Measured at grading, per `N-AV7`; not
   claimable now.
4. **Ansys's own discrepancy (§2 finding 3)** is unexplained. It does not touch
   this gate.
5. **A stale worktree copy of the charter, found and NOT touched.** While reading
   for this item, `docs/charters/ANSYS_VERIFICATION_CHARTER.md` in the working
   tree measured **289 lines** against **662 lines** in the same path at `HEAD`
   (identical blob `f5d5c8a7…` at `HEAD` and at `75030b12`) — the worktree copy is
   missing the dated note, Amendment 1.3 and **Amendment 1.4**, which is the
   amendment binding this registration. **This document was written against the
   `HEAD` blob.** `git status` reports the path `MM`. **It was INSPECTED, NEVER
   REVERTED** (`CLAUDE.md` rule 10); it is somebody's unfinished work and the
   index is the chief's call. **Referred to the supervisor.**

---

## 15. THE VERDICT VOCABULARY THIS CASE MAY PRODUCE

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`,
and nothing else. Current state: **`PENDING`** —
`verification/runs/ansys_verification/VMFL007/` does not exist.

**The route to each, decided now:**

- **triple not `CONVERGING`** → **`NOT A RESULT`**, value and both triples printed.
- **triple `CONVERGING` and Δp inside `[60217.40, 60822.60] Pa`** → the gate is
  met; with `P` unavailable the row tiers at **`GATE REACHED`** (§3), which is a
  **credential and a success**.
- **triple `CONVERGING` and Δp outside the band** → **`GATE FAIL`**, kept in the
  register with its numbers, never softened to `PENDING`.
- any completion, control or assert clause failing → the comparator **refuses,
  exit 2**, and the row is **`NOT A RESULT`**.

**The gate can only turn a `PASS` or `GATE FAIL` INTO `NOT A RESULT`, never the
reverse.**

---

## 16. Amendment record

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-25 | Frozen. Gate 0.5 % on the manual's 60.52 kPa; cap 60 core-min; ceiling `GATE REACHED`. No graded compute had run at this commit and none existed to run against. |
