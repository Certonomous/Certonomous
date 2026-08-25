# K0d. Turbulent mixed convection against Blay, Mergui and Niculae (1992): pre-registration

**NO SOLVER RUNS UNTIL THE PRIMARY IS ON DISK AND TITLE-PAGE VERIFIED (L-144).
NO CASE DIRECTORY IS BUILT BY THIS DOCUMENT. NO COMPUTE HAS RUN.**

**THE REFERENCE COLUMN OF SECTION 7 IS UNARMED.** Every reference cell reads
*to be armed by addendum on receipt of the primary*. Arming it is a **dated
addendum** appended at the foot of this file under rule 6, and **that addendum
may not alter any GATE, THRESHOLD, CAP or LABEL** registered here. It may fill
reference values, their stated uncertainties, their page or figure locators and
their digitisation increments — nothing else. If arming the reference column
would require a band to move, the correct action is to record that this
pre-registration was wrong and to say so, **not** to move the band.

**Why this document exists before the paper does.** Rule 2: the freeze is this
document's entire evidentiary content — it proves the gate could not have been
chosen to fit the answer. Sanaa has purchased the ASME volume carrying Blay
1992; the PDF is not yet on disk. Written now, the day the PDF lands the only
remaining step is the reference addendum, and by then every band is a matter of
public record.

Campaign F14 (cooling ladder), gate **K0d**, the turbulent mixed-convection rung
and the physics the DC-cooling spine actually needs: an isothermal supply jet
entering a cavity against a buoyant floor plume — the aisle physic. Written
2026-08-24T19:18:14Z, **before any case directory existed**: checked in the same shell
invocation as this write with `ls -d verification/runs/F14-cooling-ladder/K0d_runs`,
which returned *No such file or directory*, and `find verification/runs/F14-cooling-ladder
-maxdepth 1 -iname '*K0d*'`, which returned nothing. Run tree, **which does not
exist**: `verification/runs/F14-cooling-ladder/K0d_runs/`.

**Rule 2 pre-compute amendment window.** No K0d compute has run, so amendments
to this file are legal until the first solver starts, and each must state its
condition and how it was checked — by naming that same non-existent run
directory and the command that showed it absent. After the first solver starts
the gates close and only dated addenda are legal.

**Verdict today: `PENDING` — not yet run.** `PENDING` here is the display/queue
state of `VERIFICATION_CHARTER.md` §9, used because the rung has not run. It is
not a softened `GATE FAIL`. When the rung runs without the primary held, its
graded rows are `BLOCKED`; that is a different state and Section 7.4 says which
applies when.

---

## 0. Relationship to the existing K0d document, stated so nothing is duplicated or quietly overridden

`K0d_TURBULENT_MIXED_CONVECTION_GATE.md` (written 2026-08-17, zero compute)
already exists and is **the sourcing record**: it evaluated three candidates,
recommended the Blay cavity, recorded the acquisition failure with its dated
checks, and fixed a provisional row list in its §5. **That document is not
edited by this one and nothing in it is rewritten** (rule 6).

This file is the **pre-registration**: the half that must be frozen before a
solver starts — the mesh family, the closures, the bands and their conversion
rule, the three standing instruments, the cost, the stop rules and the
predictions. Where the two differ, **this file governs from its freeze commit**,
and the differences are named here rather than left for a reader to find:

| item | gate doc §5, 2026-08-17 | this pre-registration | why |
| --- | --- | --- | --- |
| temperature band | "within 0.5 K after the floor-temperature arbitration of 3.3" | **±1.0 K = ±0.05 × ΔT_band**, with ΔT_band fixed at **20.0 K** | 0.5 K was written as provisional and conditional on an arbitration that has not happened. A band conditional on a future fact is not a frozen band. §7.2 makes the scale a **boundary condition**, so the number is fixed today and the arbitration cannot move it |
| velocity band | "REL <= 15 percent at the jet peak" | **±0.10 × U_in = ±0.057 m/s**, absolute | A relative band is undefined on a profile that crosses zero. §7.2 |
| TKE | "REPORT-ONLY initially" | **REPORTED, never graded** (row R1) | Kept, and made permanent for this rung rather than "initially" |
| circulation | "exact match required" | kept, as structural row **S1** | Unchanged |
| status | "TREND-ONLY" | **the rung's graded rows are `BLOCKED` until the primary is held**, per §7.4 | `TREND-ONLY` is not in the rule-1 vocabulary |

`README.md` lines 89, 104, 145 and 174 and `docs/THERMAL_CAPABILITY_STATE.md`
§1 all record K0d as NOT RUN with the primary NOT OBTAINED. **None of them is
edited by this commit**; they become stale only when the rung actually runs, and
the results record will carry that update.

---

## 1. The rung in one paragraph

A plane isothermal wall jet enters a square air-filled cavity through an 18 mm
slot at the top of one vertical wall at 0.57 m/s and 15 °C, runs along the
ceiling, turns down the far wall and leaves through a 24 mm slot at the bottom
of the opposite wall. The floor is held about 20 K hotter than every other
surface, so a buoyant plume rises into the returning stream. Inertia and
buoyancy contend at comparable strength: **Re = 654** on the inlet slot height,
**Ra = 2.13 × 10⁹** on the cavity height. It is the only rung in this campaign
where a supply stream and a heated surface fight each other, and it is the
closest published analogue of a cold aisle discharging over a hot floor. Every
K0c rung before it was buoyancy-only. **What K0d tests, once its reference is
held, is whether a steady two-equation RANS closure with a resolved thermal
wall reproduces the measured mid-plane temperature and velocity fields at the
grid limit** — not on the finest mesh built (T1b, D440).

---

## 2. The reference: `NOT OBTAINED` today, and exactly what that costs

**What is missing.** Blay, D., Mergui, S. and Niculae, C. (1992), *Confined
turbulent mixed convection in the presence of a horizontal buoyant wall jet*,
Fundamentals of Mixed Convection, ASME HTD Vol. 213, pp. 65–72. Needed: the
full text; its tabulated or plotted mean temperature and velocity profiles at
the two mid-planes; **and the authors' stated measurement uncertainty**, which
is the only quantity in §7.2's conversion rule that this lab cannot supply
itself.

**Checked on disk in the same session as this write, and stated as a fact:**
`find docs/papers -iname '*blay*' -o -iname '*mergui*' -o -iname '*niculae*'`
returned **nothing**; `find /home/ubuntu -iname '*blay*'` returned **nothing**;
`grep -ril 'blay' docs/papers/` returned **fifteen files, every one of them a
secondary** that cites Blay 1992 and none of them the primary. **There is no
Blay / Mergui / Niculae PDF anywhere on this box.**

**Which rows it blocks.** G1–G8 and S1 of §7.3 — every graded row. It does not
block the mesh ladder, the iterative-convergence measurement, the heat-balance
guard, the three discrimination arms (C_lam, B_hi, I_hi), the wall-resolution
report or the cost science, all of which are measured and reported whatever the
reference status.

**Why it was not obtained, with the checks named and dated.** All from
`K0d_TURBULENT_MIXED_CONVECTION_GATE.md` §2, checks dated 2026-08-17: no DOI
exists (CrossRef bibliographic query on the full title returned no matching
record; ASME HTD volumes of that era are unregistered); no OA copy found; venue
metadata independently corroborated by CiNii record CRID 1573105974176827520
(title, first author, 1992, ASME, HTD Vol. 213; no abstract, no page numbers).
The measured profiles exist today only as figures inside secondary papers.

**The acquisition route, and its current state.** Sanaa has **purchased** the
ASME volume. Standing directive this week, verbatim: *"The purchased book (the
ASME mixed-convection volume carrying Blay 1992) unblocks K0d on arrival —
[ORCH] holds the K0d prereg armed so it fires the day the PDF lands."* That is
the sole registered acquisition path; **nothing in this lab sends, requests,
files or contacts anyone about it** (rule 7).

**On arrival, before one number is carried out of it:** the PDF is
**title-page verified** — first author, full title, year, venue and volume read
from the printed page 1, never from the filename, the file type or a hash
(L-144, and the two wrong author lists T3 §2.1 caught). Its sha256 goes into
the reference addendum beside the page number of every value.

### 2.1 What IS held: two open secondaries, and exactly what they are allowed to do

Both are on disk with `.txt` sidecars and both were read in this session at the
lines cited:

| paper | path | what was read |
| --- | --- | --- |
| Zou, Y., Zhao, X. and Chen, Q. (2018), *Building Simulation* 11(1), 165–174 | `docs/papers/data_center_indoor_airflow/zou_zhao_chen_2018_building_simulation.txt` | sidecar lines 667–705: the geometry, the inlet and outlet slot heights, the inlet velocity and temperature, the wall and floor temperatures, the Boussinesq treatment, and the statement that the flow is turbulent in the entire domain and the data of high quality |
| Oulghelou, M., Beghein, C. and Allery, C. (2020), arXiv:2009.06724v2 | `docs/papers/data_driven_rans/oulghelou_beghein_allery_2020_2009.06724.txt` | sidecar lines 688–726: cavity dimensions and guard cavities, Ra and Re with their definitions, the inlet turbulence pair, the wall BCs, the solver, the mesh size and achieved `y+`, and the normalisation of the plotted profiles |

**They supply the CASE. They may never supply a graded REFERENCE VALUE.** Both
plot the Blay symbols in figures and neither tabulates them. Any number taken
from those figures is a **digitisation of a secondary's reproduction of a
primary's figure** — two removes from the measurement — and this rung does not
grade against it under any circumstance. If a physics-stage comparison against
a secondary digitisation is ever wanted, it is `REPORTED` with its provenance
and increment printed at every row and it decides no verdict, exactly as T3 §2.1
handles Smirnov 2016.

---

## 3. The case, with every number's provenance and its confirmation status

**Every row marked `secondary` is `secondary, to be confirmed against the primary
on receipt`.** No number below was recalled; each was read from the sidecar line
range named in §2.1. Where the two secondaries disagree, both values are printed
and §3.3 says what the disagreement costs.

### 3.1 Geometry

| item | value | source | status |
| --- | --- | ---: | --- |
| cavity cross-section | 1.04 m (H) × 1.04 m (L) | Zou 2018 line 675; Oulghelou 2020 line 690 | **secondary, to be confirmed against the primary on receipt** — two independent secondaries agree |
| span | 0.7 m, with guard cavities at the spanwise ends; flow reported two-dimensional | Oulghelou 2020 lines 690–691 | secondary, to be confirmed against the primary on receipt |
| inlet slot | horizontal, at the **top** of one vertical wall, height **h_in = 0.018 m** | Zou 2018 line 675; Oulghelou 2020 (Re definition, line 698) | secondary, to be confirmed against the primary on receipt |
| outlet slot | at the **bottom** of the **opposite** vertical wall, height **h_out = 0.024 m** | Zou 2018 line 675 | secondary, to be confirmed against the primary on receipt |
| slot spanwise extent | full span assumed for the 2D design | **this document's design choice**, not a source | design choice, §10 says what it cannot see |

The registered 2D domain is therefore `x ∈ [0, 1.04]`, `y ∈ [0, 1.04]`, with the
inlet patch `x = 0, y ∈ [1.022, 1.040]` and the outlet patch `x = 1.04,
y ∈ [0, 0.024]`.

### 3.2 Boundary and fluid conditions

| item | value | source | status |
| --- | --- | ---: | --- |
| inlet velocity | `u = 0.57 m/s`, `v = 0` | Zou 2018 line 676; Oulghelou 2020 line 706 | secondary, agreed by both, to be confirmed against the primary on receipt |
| inlet temperature | `θ_in = 15 °C` | Zou 2018 line 677; Oulghelou 2020 line 707 | secondary, agreed by both, to be confirmed against the primary on receipt |
| floor | isothermal, **35 °C** (Zou 2018 line 678; Oulghelou 2020 line 708 imposes 35 °C in its own solve) — **but Oulghelou 2020 line 696 states `θ_hot = 35.5 °C` in defining Ra** | both | **secondary AND INTERNALLY DISPUTED**, to be arbitrated by the primary on receipt. §3.3 |
| ceiling and both vertical walls | isothermal **15 °C**, no slip | Zou 2018 line 677; Oulghelou 2020 lines 708–709 | secondary, agreed by both, to be confirmed against the primary on receipt |
| outlet | zero gradient on `U`, `T` and every turbulent variable | Oulghelou 2020 lines 709–710 | secondary, to be confirmed against the primary on receipt |
| inlet turbulence | `k = 1.25e-3 m²/s²`, `ε = 5.76e-3 m²/s³` | Oulghelou 2020 lines 707–708 | **NOT A MEASURED VALUE — that paper's own choice.** Registered as the default and swept in arm `I_hi` (§5). To be replaced only if the primary states a measured level |
| fluid | air | both | secondary, to be confirmed against the primary on receipt |
| `ν` | **1.55e-5 m²/s** at the reference temperature 298 K | **this document**, standard air property; not from any held source | design value, stated as such |
| `Pr` | **0.71** | **this document**, standard air property | design value, stated as such |
| `Pr_t` | **0.85** everywhere, **never tuned** | lab standing value, K0c line | design value |

### 3.3 The floor-temperature discrepancy, and what this rung does about it

Oulghelou 2020 quotes `θ_hot = 35.5 °C` when defining `Ra = 2.13e9` (line 696)
and imposes `35 °C` on the floor in its own solve (line 708). Zou 2018 states
`35 °C` (line 678). **0.5 K on a 20 K driving difference is 2.5 % of it.**

Three things are registered now, before any answer is known:

1. **The runs impose `35.0 °C`.** It is the value both secondaries actually
   solved with and it is the smaller driving difference, hence the **stricter**
   band under §7.2.
2. **`ΔT_band` is fixed at exactly 20.0 K for all time in this rung**, and the
   primary's arbitration **cannot widen it**. Had 35.5 °C been chosen the bands
   would be 2.5 % looser; freezing the smaller value closes that channel.
3. **Guard row `B`** (§7.5) runs the discrepancy as a measurement: arm `B_hi`
   imposes 35.5 °C on the medium level and the difference is read at every
   graded station. If it exceeds a graded row's band, **that row is
   `NOT A RESULT` until the primary arbitrates** — registered here, not
   discovered later.

### 3.4 Non-dimensional groups

| group | value | definition | status |
| --- | --- | --- | --- |
| `Re` | **654** | on the inlet velocity 0.57 m/s and the inlet slot height 0.018 m | Oulghelou 2020 lines 697–698 — secondary, to be confirmed against the primary on receipt. Re-derived here from the stated `u` and `h_in`: `Re = 0.57 × 0.018 / ν` gives 654 at `ν = 1.569e-5 m²/s`, so the quoted 654 and the geometry are **mutually consistent** and that consistency is the check |
| `Ra` | **2.13 × 10⁹** | on the cavity height 1.04 m and `θ_hot − θ_cold` | Oulghelou 2020 lines 694–697 — secondary, to be confirmed against the primary on receipt |
| `Gr` | **`Ra / Pr` = 3.00 × 10⁹** at `Pr = 0.71` | derived here | **derived from the secondary, not read from one** |
| `Ri` | **`Gr / Re_H²`** | on the CAVITY height, the only length on which a mixed-convection Richardson number is meaningful here. `Re_H = u h_in-based Re × (H/h_in) = 654 × 57.78 = 3.78e4`; `Ri = 3.00e9 / (3.78e4)² = ` **2.10** | **derived here, and it is the reason this rung exists**: `Ri ≈ 2` is neither forced (`Ri ≪ 1`) nor free (`Ri ≫ 1`) convection. It is the mixed regime by arithmetic, not by assertion. **No source states a Richardson number for this case**; this figure is this document's derivation from the secondaries' Ra, Re and geometry and is labelled **derived, not read** |

### 3.5 The Boussinesq assumption and its validity, measured by this lab

Both secondaries used Boussinesq (Zou 2018 line 678; Oulghelou 2020 lines
702–703) and so does this rung: `buoyantBoussinesqSimpleFoam`, OpenFOAM v2606
stock — **confirmed present on this box** at
`/usr/lib/openfoam/openfoam2606/applications/solvers/heatTransfer/buoyantBoussinesqSimpleFoam`.

The lab does not take that on trust. **K2e measured where the Boussinesq model
stops being right** — `docs/campaigns/F14-cooling-ladder/K2e_RESULTS.md` §1,
`K2e_PREREGISTRATION.md` frozen at `0869284` before any K2e solver ran:

- **Velocity separates first**, in the bracket **ε = β·ΔT ∈ (0.0333, 0.0500]**
  on 48², with the divergence law `D(u_max*) = 24.91 · (β·ΔT)^1.005 %` — **first
  order** in `β·ΔT`.
- **The Nusselt number moves last**, `D(Nu_h) = 6.355 · (β·ΔT)^1.968 %` —
  **second order**, protected to leading order, and it does not reach a 1 %
  separation until `ε ∈ (0.30, 0.40]`.

**This case sits at `ε = β·ΔT = 20.0 / 298 = 0.0671`** — above the velocity
separation bracket, and a swept point of K2e's own sweep (0.0667), so the laws
are **interpolated in ε, not extrapolated**. Substituting:

| quantity | K2e law at ε = 0.0671 | what it means here |
| --- | ---: | --- |
| peak velocity | **≈ 1.65 %** | a **model-form floor** on every velocity row, well inside the ±10 % band of §7.3 |
| Nusselt | **≈ 0.031 %** | negligible against the ±10 % band on G6 |

**Both figures are ESTIMATES, not measurements, and the reason is stated rather
than smoothed:** K2e measured those exponents on the de Vahl Davis
*differentially heated laminar* cavity at `Ra = 1e5`, not on a turbulent
mixed-convection cavity with a jet. **The exponents are K2e's; carrying them
across flow classes is this document's extrapolation.** They are registered as a
**REPORTED model-form floor printed beside every velocity row**, never as a
correction and never subtracted from a deviation. `docs/physics_rules.yaml`
line 279 governs `boussinesq_beta_dT_max: 0.1`; **0.0671 is inside it**, and
K2e §10 already records that this single number cannot serve both quantities.

---

## 4. The mesh family: three levels, `r = 1.40`, read from disk before any solve

**Three horizontal blocks**, conformal, `blockMesh`, chosen so both slots are
patches of block faces rather than of a graded interior:

- **Block A**, `y ∈ [0, 0.024]` — the outlet band. Outlet patch is its right face.
- **Block B**, `y ∈ [0.024, 1.022]` — the cavity interior.
- **Block C**, `y ∈ [1.022, 1.040]` — the inlet band. Inlet patch is its left face.

Two-sided geometric grading to every wall and to both slot lips, **with the
reciprocal written by hand for the second half of each direction** (the K0cS
form; L-142).

| level | `N_x` | `n_A` | `n_B` | `n_C` | `N_y` | **cells** | first wall cell (m) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **L1 coarse** | 160 | 12 | 138 | 10 | 160 | **25 600** | 1.09e-3 |
| **L2 medium** | 224 | 17 | 193 | 14 | 224 | **50 176** | 7.78e-4 |
| **L3 fine** | 314 | 24 | 270 | 20 | 314 | **98 596** | 5.56e-4 |

**Effective refinement ratios, computed from the CELL COUNTS and not from this
paragraph:** `r21 = sqrt(50176 / 25600) = ` **1.4000**; `r32 = sqrt(98596 / 50176)
= ` **1.4018**. Both are **≥ 1.30**, which is the condition for a defensible
observed order, and the comparator uses the **unequal-ratio fixed-point form**
(T3 §7.1) rather than assuming they are equal. `L3` at 98 596 cells is
deliberately the same order as K0cG's finest square-cavity level (94 249) and
below Oulghelou 2020's 120 000, so the ladder is comparable to both.

**First wall cells** from `y_cell = 2 y⁺ ν / u_τ` with `u_τ = u_in sqrt(C_f/2)`,
`C_f = 0.005` (wall-jet value), `ν = 1.55e-5 m²/s`, `y⁺ = 1`.

**Every mesh is read from `constant/polyMesh` BEFORE any solver runs**
(`check_k0d_mesh.py`, §9). Registered refusal conditions, all checked from disk:

| # | condition |
| --- | --- |
| A | total cell count equals the design value exactly on each level |
| B | the inlet slot spans **≥ 10 / 14 / 20** cells (L1/L2/L3), and the outlet slot **≥ 12 / 17 / 24** |
| C | every block's cell count scales by **1.40 ± 0.05** between consecutive levels |
| D | the first wall-normal cell equals the design value to 1 % **and** is the smallest wall-normal cell in its block |
| E | each graded half is geometric to `1e-6` |
| F | block heights sum to 1.040 m and block widths to 1.040 m, to `1e-9` |
| G | **the planted-positive test FIRES**: an inverted grading and a slot one cell short are each injected and each must be refused |

`checkMesh` birth certificate per case. **T1b attempt 1 lost 57 core-hours to a
grading direction nobody read from disk; this rung reads it.**

---

## 5. The cases and the closures, registered in advance

**Solver:** `buoyantBoussinesqSimpleFoam`, steady, `g = (0, −9.81, 0)`,
Boussinesq, `T_ref = 298 K`, `β = 1/298 = 3.356e-3 K⁻¹`.

**Closures — two, because `NUMERICS_KNOWLEDGE` K0c-T says *quote two models or
quote none*.** Both confirmed present on this box:

- **`kOmegaSST`** — `/usr/lib/openfoam/openfoam2606/src/TurbulenceModels/turbulenceModels/RAS/kOmegaSST/`. The lab's thermal spine; the model K0cS, K0cT, K0cX and K0cG all graded.
- **`RNGkEpsilon`** — `/usr/lib/openfoam/openfoam2606/src/TurbulenceModels/turbulenceModels/RAS/RNGkEpsilon/`. **Chosen because it is the model Oulghelou 2020 used on this exact case** (line 699), so the lab's solve is comparable to a published reproduction rather than only to itself.

Both **wall-resolved**, `y⁺` target ≤ 1, `Pr_t = 0.85`, never tuned.

| case | closure | level | cells | registered `endTime` | purpose |
| --- | --- | --- | ---: | ---: | --- |
| `M1_c` | kOmegaSST | L1 | 25 600 | 40 000 | ladder |
| `M1_m` | kOmegaSST | L2 | 50 176 | 40 000 | ladder |
| `M1_f` | kOmegaSST | L3 | 98 596 | 40 000 | ladder, **the graded level** |
| `M2_c` | RNGkEpsilon | L1 | 25 600 | 40 000 | ladder |
| `M2_m` | RNGkEpsilon | L2 | 50 176 | 40 000 | ladder |
| `M2_f` | RNGkEpsilon | L3 | 98 596 | 40 000 | ladder, **the graded level** |
| `C_lam` | laminar | L2 | 50 176 | 40 000 | **Charter 2c discrimination control** |
| `B_hi` | kOmegaSST, floor **35.5 °C** | L2 | 50 176 | 40 000 | **the §3.3 arbitration guard** |
| `I_hi` | kOmegaSST, inlet `k`, `ε` **× 4** | L2 | 50 176 | 40 000 | **the §3.2 unmeasured-inlet-turbulence sweep** |

Nine cases, all serial, all 2D. Every non-ladder arm sits on **L2** so each
comparison is like against like.

**Wall resolution is measured, not assumed.** Achieved `y⁺` is read from the
solution on every wall face of every case. **Registered window: `y⁺_max ≤ 5.0`
on L1 and `≤ 3.3` on L2 and L3** — 3.3 is Oulghelou 2020's own measured maximum
on this case (line 719), so it is a published figure and not a preference. A
case outside its window carries the flag *wall resolution outside the registered
window* and its rows are **REPORTED, not graded**.

---

## 6. Convergence, and what is NOT the criterion

`endTime 40000`, `deltaT 1`, `writeInterval 4000`, `purgeWrite 2`.
`writeInterval` is strictly less than `endTime` because that is a durability
property (L-140) and because the convergence test needs two checkpoints.

**`residualControl` is not written, and the residual is not the instrument.**
T1c recorded a genuinely unconverged case at residual `4e-05` (L-141). The
registered criterion is the field test:

> **CONVERGED** means the largest change of any cell value of `T`, and
> separately of `U`, between the written checkpoints at `endTime − 4000` and
> `endTime` is at most **`1e-6` of that field's range**.

A case that has not converged at 40 000 may be **extended** from `latestTime`
under the T1b §6 disclosure rule: new log, new STATUS, first extension `Time`
exactly `endTime + 1`, the marker re-judged across both segments, **and the
decision to extend taken on the convergence state alone, never with a graded
value in view.** One extension of **+20 000 iterations** is registered; a second
is not authorised by this document.

**A ladder level that is NOT CONVERGED makes every triple containing it
`NOT A RESULT`** (§8, order 1). The criterion is not relaxed after the fact.

---

## 7. The gate: rows, bands, and the conversion rule that is registered instead of the answer

### 7.1 Deviation

`REL(q) = 100 × |q_solve − q_ref| / |q_ref|` where the quantity does not cross
zero (K0cS gate, line 351), taken **on the fine level `f`**, gated by §8.
Where the quantity **does** cross zero — every velocity profile here — the
deviation is **absolute**, `ABS(q) = |q_solve − q_ref|`, and the band is
absolute. §7.2 says why that is not a weakening.

### 7.2 THE BAND CONVERSION RULE — registered now, in a form that does not need the reference value

This is the clause the whole freeze turns on, so it is stated as an algorithm.

**The insight that makes it possible: the band SCALES of this case are BOUNDARY
CONDITIONS, which are known today, not solution values or reference values.**
The inlet velocity `U_in = 0.57 m/s`, the driving difference `ΔT_band = 20.0 K`
and the cavity height `H = 1.04 m` are all fixed by §3 and cannot move. So the
bands below are **already absolute numbers**; only the reference *values* they
are measured from are unarmed.

For every graded row `r`:

```
  S(r)      = the registered SCALE of row r, from the table of 7.3.
              One of: DT   = 20.0 K      (temperature rows)
                      UIN  = 0.57 m/s    (velocity rows)
                      HGT  = 1.04 m      (length rows)
                      REF  = |q_ref(r)|  (strictly positive rows only: Nusselt)
  R(r)      = the registered RELATIVE FIGURE of row r, from the table of 7.3.
  u_exp(r)  = the PRIMARY's stated measurement uncertainty for row r,
              in the units of row r.  ZERO if the primary states none.
  u_dig(r)  = the digitisation increment, if q_ref(r) had to be read from a
              figure IN THE PRIMARY.  ZERO if the primary tabulates it.
  u_val(r)  = sqrt( u_exp(r)^2 + u_dig(r)^2 )

  BAND(r)   = +/- max( 2 * u_val(r) , R(r) * S(r) )
```

Four properties of this rule, each registered because each closes a channel:

1. **It is computable today for every row whose scale is `DT`, `UIN` or `HGT`.**
   Those bands appear as absolute numbers in §7.3 and the addendum cannot touch
   them. Only the `REF`-scaled row (G6) waits on the reference.
2. **The addendum can only ever WIDEN a band, and only through a property of the
   reference** — the primary's own stated uncertainty, or the increment of a
   figure read out of the primary. It can never narrow one and it can never
   widen one by a choice.
3. **`max`, not `min`, and the reason:** a band tighter than the instrument that
   measured the reference grades measurement noise. A band tighter than the
   registered relative floor grades the digitisation. Neither is evidence.
4. **THE ANTI-WIDENING GUARD, registered now.** If `2·u_val(r) > 3 × R(r)·S(r)`
   for any row, **that row is REPORTED, not GRADED**, and the record says *the
   reference is too imprecise to discriminate at this rung's registered
   resolution*. This exists so that an addendum arming a large `u_exp` cannot
   turn the gate into a formality that everything passes.

**Profile rows.** A profile row is graded at **eleven registered stations**, in
the normalised coordinate, fixed now:

`0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95`

The row **PASSES only if every station with a reference value lies inside
`BAND(r)`**. The comparator prints the count inside, the count outside, and the
worst station with its value, its reference and its miss. Where the primary
supplies no value within `±0.01` of a registered station, **that station is
`UNMEASURED`, is named, and the denominator shrinks with the missing stations
printed** — a tally is never silently renormalised.

### 7.3 The rows

**The reference column is UNARMED. Every cell in it is filled by the dated
addendum of §12, and by nothing else.**

| row | quantity | levels graded on | scale `S` | rel. figure `R` | **BAND, absolute, registered TODAY** | **REFERENCE** | one-line justification |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| **G1** | mean temperature `Θ` on the vertical mid-plane `x/H = 0.5`, 11 stations floor→ceiling | L1,L2,L3; graded on L3 | `DT` | 0.05 | **± 1.00 K** | *to be armed by addendum on receipt of the primary* | The plane both secondaries plot and the one that carries the floor plume and the ceiling jet in a single profile |
| **G2** | mean temperature `Θ` on the horizontal mid-plane `y/H = 0.5`, 11 stations | L1,L2,L3; graded on L3 | `DT` | 0.05 | **± 1.00 K** | *to be armed by addendum on receipt of the primary* | The orthogonal cut; a model can match one mid-plane and miss the other, and only two planes can show it |
| **G3** | mean horizontal velocity `u` on `x/H = 0.5`, 11 stations | L1,L2,L3; graded on L3 | `UIN` | 0.10 | **± 0.0570 m/s** | *to be armed by addendum on receipt of the primary* | The quantity that separates the wall jet from the return flow; crosses zero, so the band must be absolute |
| **G4** | mean vertical velocity `v` on `y/H = 0.5`, 11 stations | L1,L2,L3; graded on L3 | `UIN` | 0.10 | **± 0.0570 m/s** | *to be armed by addendum on receipt of the primary* | The plume-versus-downflow signature; the one quantity buoyancy owns outright |
| **G5a** | ceiling wall-jet **peak speed** `\|U\|_max` on `x/H = 0.5` | L1,L2,L3; graded on L3 | `UIN` | 0.10 | **± 0.0570 m/s** | *to be armed by addendum on receipt of the primary* | The jet-peak magnitude is what discriminates wall treatments in every published comparison of this case |
| **G5b** | wall-normal **location** of that peak, `(H − y)/H` | L1,L2,L3; graded on L3 | `HGT` | 0.02 | **± 0.0208 m** | *to be armed by addendum on receipt of the primary* | A peak of the right size in the wrong place is a different error and must not hide inside G5a |
| **G6** | **floor-averaged Nusselt number** `Nu_floor = q̄_floor H / (k ΔT)` | L1,L2,L3; graded on L3 | `REF` | 0.10 | **± 10 % of `\|q_ref\|`** — *the only row whose absolute band waits on the reference* | *to be armed by addendum on receipt of the primary* | The engineering quantity the DC-cooling spine needs, and the one K2e proved is second-order-protected against the Boussinesq assumption |
| **G7** | **stratification**: `Θ(y/H = 0.75) − Θ(y/H = 0.25)` on `x/H = 0.5` | L1,L2,L3; graded on L3 | `DT` | 0.05 | **± 1.00 K** | *to be armed by addendum on receipt of the primary* | Aisle stratification is the whole point of the spine; a difference of two graded stations, so it is not a new measurement |
| **G8** | **jet penetration length**: horizontal distance from the inlet wall to where the ceiling-jet peak speed first falls to `0.5 U_in` | L1,L2,L3; graded on L3 | `HGT` | 0.10 | **± 0.104 m** | *to be armed by addendum on receipt of the primary* | Whether the supply stream reaches the far wall before the plume turns it is the regime question this rung was built to ask |
| **S1** | **global circulation structure**: number and sense of the primary recirculation cells, and presence of the inlet-side upper-corner secondary cell | L1,L2,L3; graded on L3 | — | — | **EXACT MATCH REQUIRED, no band** | *to be armed by addendum on receipt of the primary* | A flipped or fragmented circulation is a **regime** error, not a percentage error; the published reproductions disagree here and a band would hide it |
| **R1** | turbulent kinetic energy on both mid-planes | L1,L2,L3 | — | — | **REPORTED, NEVER GRADED** | *reported against the primary when held* | Fluctuation measurements carry the largest experimental uncertainty in this rig class; the gate doc §5 said REPORT-ONLY and this rung makes it permanent |
| **M0** | the **Boussinesq model-form floor** of §3.5, `≈ 1.65 %` on velocity and `≈ 0.031 %` on Nusselt | — | — | **REPORTED beside every velocity row and G6** | — | An estimate carried across flow classes; it is printed so a reader can see the floor, and **it is never subtracted from a deviation** |

**Graded row count: 10** (G1, G2, G3, G4, G5a, G5b, G6, G7, G8, S1). Two rows
(R1, M0) are reported and grade nothing.

**The `N of M` tally of this rung is `0 of 10` until the primary is held, and
that is the honest count.**

### 7.4 The verdict ladder for every graded row

Evaluated **in this order**, and the order is part of the freeze:

1. any ladder level **NOT CONVERGED** (§6) → **`NOT A RESULT`**
2. the grid triple **not `CONVERGING`** (§8) → **`NOT A RESULT`**, with the fine value, both triples and both observed orders printed beside it
3. the case outside its registered **`y⁺` window** (§5) or its **guard** failed (§7.5) → **`NOT A RESULT`** or **REPORTED**, per the guard's own registered clause
4. **no primary reference file on disk** → **`BLOCKED`**, with the fine value, the triple, the GCI and the achieved `y⁺` printed as `REPORTED` information
5. **primary held** → **`PASS`** if the fine value lies inside `BAND(r)` of §7.2, else **`GATE FAIL`**

### 7.5 Guards — each withdraws the run, never the hypothesis (Charter 2c)

| guard | test | registered consequence |
| --- | --- | --- |
| **HB** | heat balance on every case, kinematic units. `Q_floor` from `alpha_eff (dT/dn) A` with `alpha_eff = ν/Pr + alphat_w` and **`alphat_w` read from the written patch** (T1b: dropping it reports only the molecular part); `Q_adv` from the written `phi` over inlet and outlet. `imbalance % = 100 \|Σ Q\| / Σ (Q > 0)` | against **0.5 %**, the governed value at `docs/physics_rules.yaml:324` (`heat_balance_tol_pct`). Over it → every graded row of that case is `NOT A RESULT`. Counted in no tally |
| **B** | `\|Θ(B_hi) − Θ(M1_m)\|` at every registered station of G1, G2 and G7 | **if it exceeds 1.00 K at any station, rows G1, G2 and G7 are `NOT A RESULT` until the primary arbitrates the floor temperature of §3.3** |
| **I** | `\|G5a(I_hi) − G5a(M1_m)\|` and `\|G8(I_hi) − G8(M1_m)\|` | **if either exceeds its own band, rows G5a, G5b and G8 are REPORTED, not graded**, with the flag *inlet turbulence unmeasured*. Registered because Oulghelou's `k`, `ε` are that paper's choice, not a measurement (§3.2) |
| **DC** | Charter 2c: `C_lam` (laminar) against `M1_m` on G6 | **MET** if they differ by more than **25 %**. If within 25 %, **G6 grades nothing and the record says so** — K0c's F8 finding was that the set of rows kOmegaSST passed which a laminar solve did not also pass was **empty** (`K0c_THERMAL_CLOSURE_SYNTHESIS.md` line 117; D411, D433). `UNMEASURED` if `C_lam` is not converged |
| **MB** | mass imbalance across inlet and outlet | reported; `heat_balance_open_case_gates_mass_imbalance: true` at `physics_rules.yaml:402` binds it |

### 7.6 The reference slot, which does not exist today

Path, registered: `verification/runs/F14-cooling-ladder/K0d_runs/K0d_reference_primary.json`.
**Neither the file nor its parent directory exists, and this commit creates
neither.** Schema:

```
{"provenance": {"citation": "Blay, D., Mergui, S., Niculae, C. (1992), ASME HTD 213, 65-72",
                "page_or_table": "...", "figure": "...", "sha256": "...",
                "title_verified_page1": true, "digitised": false,
                "digitisation_increment": null},
 "rows": {"G1": {"stations": {"0.05": {"value": 0.0, "u_exp": 0.0}, ...},
                 "units": "K"},
          "G6": {"value": 0.0, "u_exp": 0.0, "units": "-"},
          "S1": {"n_cells": 0, "sense": "...", "corner_cell": true}, ...}}
```

`u_exp` is **the authors' stated figure**, in the units of the row. If a value
had to be read from a figure **in the primary**, `digitised` is true and
`digitisation_increment` is recorded; the comparator then adds it in quadrature
per §7.2. **The person who fills this file reads it from the printed page
(L-144) and writes the page number.** Nothing in the comparator changes when it
appears.

---

## 8. The three standing instruments, registered explicitly

### 8.1 Planted-zero control — a zero from a reader not shown able to see a non-zero is not evidence

Matching this family's existing comparators (`verification/runs/T-family/T3_runs/analyse_t3.py`,
`PLANT = 1.234e-03`, `plant_into_T()`, refusal at approximately line 801;
`T10a_runs/analyse_t10a.py:846`) and `FILING_CHARTER.md` §5.

`analyse_k0d.py` **plants before it reads anything that will be graded**:

| # | plant | into | read back through | refusal |
| --- | --- | --- | --- | --- |
| P1 | `PLANT_T = 1.234e-03` (K) | a **copy** of `M1_f/<endTime>/T`, **by line index**, never by regex over the value | the **production** field reader, the same call the graded path uses | if the reader does not see `1.234e-03` at that index, **exit 2** |
| P2 | `PLANT_U = 1.234e-03` (m/s) into the **x-component** | a copy of `M1_f/<endTime>/U` | the production vector reader | **exit 2** if unseen. Registered separately because six of the ten graded rows are velocity rows and a scalar plant does not exercise the vector parser |
| P3 | **negative control**: a plant of exactly `0.0` | a copy of `M1_f/<endTime>/T` | the production reader | the reader must report **NOT DISTINGUISHABLE FROM THE BACKGROUND**. If P3 "fires", the control is broken and the comparator **exits 2** |

**And the standing consequence:** if any graded row returns a deviation of
**exactly zero**, that row is `NOT A RESULT` unless P1/P2 demonstrated on the
**same reader in the same invocation** that a non-zero is visible. **A zero is a
result only when it is a supported zero.**

The comparator **refuses (exit 2) rather than degrades**, on every clause of
this section.

### 8.2 The strict completion rule with the age guard — quoted in full from `T1b_L4_AMENDMENT.md` §7

`mark_done_k0d.py` applies, for the thermal field set, the rule that section
states verbatim:

> **Completion.** `mark_done_t1b_L4.py` writes `DONE.R_*_x` under the six tests
> of `mark_done_t1b.py`, importing its field list and parsers and reading
> `STATUS.<case>` (the pool format `rc= wall= checkMesh_rc=`) in place of
> `STATUS2`: rc = 0; an `End` line; last time = `endTime`; `T U p_rgh alphat
> nut k omega` present; `ExecutionTime` count = `endTime`; every field at
> `endTime` NEWER than the case's own `0/T`.
>
> **Age guard (D438, L-143).** `run_one_t1b_L4.sh` creates `0` from `0.orig`
> and touches `0/T` LAST, so its mtime dates the run allowed to produce the
> answer; G3 refuses a case in which `0` or any numeric time directory already
> exists, so a stray write from any earlier process can neither be overwritten
> nor certified.

**Read as this rung's binding conditions, all of which must hold:**

1. `rc = 0`
2. an `End` line in the log
3. **last time == `endTime`**
4. **`T U p_rgh alphat nut k omega` all present** at `endTime` (`C_lam` is
   exempt from `nut k omega` and that exemption is registered here, not
   discovered later)
5. **`ExecutionTime` count == `endTime`**
6. **every field at `endTime` NEWER than the case's own `0/T`** — the age
   guard, because `0/T` is touched **last** at launch and so dates the run
   allowed to produce the answer
7. **the launch guard refuses a case in which `0` or any numeric time directory
   already exists**

For an extended case (§6), the extension form applies: both STATUS files
`rc = 0`, `End` in both logs, counts summing to `endTime`, the first extension
`Time` exactly one past the original count, fields newer than `0/T` **and** than
`STATUS.<case>`; a failing extended case has any stale marker **REMOVED** with
the reasons printed.

**`analyse_k0d.py` refuses (exit 2) unless all nine `DONE.<case>` markers are
present.** A run that fails any clause is not done, and this rung does not
degrade it into a partial result.

### 8.3 Roache triple gating — the exact ordering, and the direction the gate may move a verdict

Per rule 5 and `T1b_L4_AMENDMENT.md`, evaluated in this order:

1. **any level not iteratively converged or not plateaued → `NOT A RESULT`**
2. **triple `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` → `NOT A RESULT`**,
   with **the value, both triples and both observed orders printed beside it**
3. **`CONVERGING` → `PASS`** inside the pre-registered band, **else `GATE FAIL`**,
   **GCI printed**

**GCI at `Fs = 1.25`. Never quote a GCI when the three values are not
monotone.** Observed order and GCI use the **effective** ratios from the cell
counts with the **unequal-ratio fixed-point form** (`r21 = 1.4000`,
`r32 = 1.4018`), and the comparator asserts it reproduces the equal-ratio
`gci()` when the ratios are made equal.

**THE GATE CAN ONLY TURN A `PASS` OR A `GATE FAIL` *INTO* `NOT A RESULT`. NEVER
THE REVERSE.** A row inside its band on a `DIVERGENT` triple is `NOT A RESULT`,
not a `PASS`. T1b's frozen comparator returned four `PASS`es on four `DIVERGENT`
or `STAGNANT` triples because it graded the finest mesh and stored the triple
without reading it; `analyse_k0d.py` reads it **first**.

**Profile rows.** The triple is evaluated **per station**. A profile row is
`CONVERGING` only if **every** graded station's triple is `CONVERGING`;
otherwise the row is `NOT A RESULT` with the count of non-`CONVERGING` stations
and the worst station's two triples and orders printed.

**`--selftest` proves each branch** on synthetic triples, including that a
`DIVERGENT`, `STAGNANT` or `OSCILLATORY` triple **with a value inside the band**
still returns `NOT A RESULT`, and that with a `CONVERGING` triple the verdict is
reachable **both ways** by moving the fine value — the mutation control. A
selftest whose mutants do not all fire is a **refusal**, not a warning.

---

## 9. Build, verification and launch discipline

- `build_k0d.py` writes the nine cases; **it does not run and nothing in this
  commit runs it.**
- `check_k0d_mesh.py` reads every `constant/polyMesh` and refuses on A–G of §4
  **before any solver runs**; its planted-positive test **must FIRE**.
- `checkMesh` birth certificate per case (Charter 9). High aspect ratio near the
  slots is expected and is **reported with its number, not hidden**.
- `launch_k0d.sh` takes `LAUNCH_LOCK` atomically; refuses if any process has the
  case directory as its cwd (identified by `readlink /proc/<pid>/exe`); refuses
  if `0` or any numeric time directory exists (L-143). **Fleet agents are
  invisible to `pgrep` (L-41), so the launch check reads run-directory mtimes
  and `git log` as well as processes.**
- `run_one_k0d.sh` detaches with `setsid nohup`, creates `0` from `0.orig` and
  **touches `0/T` LAST**, writes `STATUS.<case>`. **Nothing in this rung kills a
  process and nothing needs to.**
- **Concurrency cap 6 solver processes.** The box is shared with the DAFoam,
  closure, cfd, verification and ansys-verification teams.
- Before analysis, `analyse_k0d.py` is **hashed against its committed blob**
  (Charter 2d test) and the run refuses on a mismatch.
- **Tooling disclosure, complete:** **no smoke test, no pilot, no scratch solve
  and no case directory was created for this rung, before or during this
  commit.** Charter 2d asks what was readable before the freeze: **nothing at
  all.** That is stronger than T3, which disclosed a 200-iteration scratch smoke
  test, and it is stated so the difference is on the record.

---

## 10. Cost, registered before the run — POINT and CEILING

### 10.1 The basis, and its solver class (L-271)

**Sibling used: `K0cS`**, the square-cavity turbulent re-gate.
`K0cS_PREREGISTRATION.md` §2.1, measured on this box on 2026-08-18:

| pilot | cells | iterations | s/(cell·iteration) |
| --- | ---: | ---: | ---: |
| coarse 120² | 14 400 | 300 | 1.556e-6 |
| fine 192² | 36 864 | 300 | **1.593e-6** |

The two rates agree to **2.4 % per cell**, which is the check that the number is
a rate and not an artefact of one mesh. **1.593e-6** is taken — the larger-mesh
figure, the closer analogue of L2 and L3.

**SOLVER CLASS OF THE BASIS, stated because L-271 makes it binding:**
`buoyantBoussinesqSimpleFoam`, **steady**, **2D**, **Boussinesq buoyancy
active**, **wall-resolved two-equation RANS with a coupled energy equation plus
`alphat`, `k` and `ω`**, single rank, on this c7a.4xlarge. **K0d is the same
solver class in every one of those six respects.** That is why K0cS is the
basis and not one of the other measured siblings:

| sibling | measured | why NOT the basis |
| --- | ---: | --- |
| **K0cS** | **206.5 core-min** | **CHOSEN.** Same solver class, same dimensionality, same closure family, buoyancy active, and its per-cell-iteration rate is *published in its own pre-registration*, which none of the others is |
| K0cT | 95.0 core-min | Same class, but a tall cavity at `Ra ~1e6`, three decades below; its 1.6× developed-flow multiplier is **borrowed below**, its rate is not |
| K0cX | 321.8 core-min | Cross-geometry aggregate over three models; not a single-case rate |
| K0cG | 300.6 core-min at 1.35× overrun | A two-case third-level rung; the overrun is a warning carried into §10.4, not a rate |
| K2b | 65.4 core-min | **Wrong class** — its estimate went VOID mid-rung because it priced *steady* runs for an *unsteady* question (`K0cS_PREREGISTRATION.md` §2) |

**CONTINGENCY ON THE RATE: 1.6×**, stated rather than hidden. The K0cS pilots
were 300 iterations into a developing flow where `p_rgh` converged in few PCG
sweeps; a developed field takes more. **1.6× is the multiplier K0cT registered
and it has been calibrated once on this case class** — K0cT came in at 95.0
core-min against 119.6 estimated, so it was not generous.

**POINT rate = 1.593e-6 × 1.6 = 2.549e-6 s per cell-iteration.**
**CEILING rate = 2 × POINT = 5.098e-6**, covering mixed-convection stiffness
(§10.4) and box contention. Registering a point **and** a ceiling is the
`L-291` shape, so both ratios are computable at completion.

### 10.2 The POINT estimate

| case | cells | iterations | core-s | **core-min** |
| --- | ---: | ---: | ---: | ---: |
| `M1_c` | 25 600 | 40 000 | 2 610.2 | **43.50** |
| `M1_m` | 50 176 | 40 000 | 5 115.9 | **85.27** |
| `M1_f` | 98 596 | 40 000 | 10 052.9 | **167.55** |
| `M2_c` | 25 600 | 40 000 | 2 610.2 | **43.50** |
| `M2_m` | 50 176 | 40 000 | 5 115.9 | **85.27** |
| `M2_f` | 98 596 | 40 000 | 10 052.9 | **167.55** |
| `C_lam` | 50 176 | 40 000 | 3 836.9 | **63.95** — **0.75 × the L2 turbulent line**, the two closure transport equations removed. **The 0.75 is a registered ESTIMATE, not a measurement**, and its ratio is a named calibration item |
| `B_hi` | 50 176 | 40 000 | 5 115.9 | **85.27** |
| `I_hi` | 50 176 | 40 000 | 5 115.9 | **85.27** |
| **solver subtotal** | | | | **827.11** |
| meshing + `checkMesh`, 9 cases at 5 core-s | | | 45 | **0.75** (bounded ≤ 2.00) |
| `check_k0d_mesh.py`, three `polyMesh` reads | | | | **0.50** |
| `mark_done_k0d.py` + `analyse_k0d.py` + `--selftest` | | | | **1.00** — deliberately **not** over-priced; C-34 recorded a comparator over-predicted by ≥ 30× |
| **REGISTERED POINT TOTAL** | | | | **829.36 core-min** |

**829.36 core-min = 13.823 core-h.** At **$0.0513 per core-h**, c7a.4xlarge:
**$0.709**.

**`cost_basis`: rate reported-by-owner, NOT MEASURED — this box cannot read its
own billing (`COMPUTE_BUDGET_CHARTER.md` §5). The core-minute figures are
predictions from a MEASURED per-cell-iteration rate; the dollar figures are
DERIVED, not measured.**

### 10.3 The CEILING, the continuation reserve, and the stop rules

**Continuation reserve:** one extension of +20 000 iterations (half length) on
any case missing the §6 convergence criterion. Worst case, all nine:
**413.56 core-min**.

| component | core-min |
| --- | ---: |
| first pass at the **CEILING** rate (2 × 827.11) | 1 654.23 |
| continuation reserve at the **CEILING** rate | 827.11 |
| instruments, bounded | 3.50 |
| **REGISTERED CEILING / TOTAL CAP** | **2 484.84 core-min** |

**2 484.84 core-min = 41.414 core-h = $2.125 derived.**

**STOP RULES, fixed now:**

1. **THE TOTAL CAP IS 2 484.84 core-min. Reaching it STOPS THE RUN.** The rung
   reports what it has, **with the unrun cases named**. A reduced run is never
   silently relabelled as the rung. **An overrun does not get a new budget**
   (rule 12); more work is a **new pre-registration with a corrected
   `cost_basis`**.
2. **PER-CASE HARD STOP: 10× that case's registered POINT line.** This is the
   heat-transfer team's registered practice — `COST_CALIBRATION.md` C-1
   (T10a-R), C-21 (E4a), C-34 (E4a2) all record a 10× per-case stop threshold
   registered in the pre-registration. Worked: `M1_c`/`M2_c` 435.0 core-min;
   `M1_m`/`M2_m`/`B_hi`/`I_hi` 852.7; `M1_f`/`M2_f` 1 675.5; `C_lam` 639.5.
   **Honest note, stated rather than left for a reader to find: for every case
   except the two coarse ones the RUNG CAP of rule 1 binds BEFORE the 10×
   per-case threshold. Both are in force and whichever is reached first stops
   the run.**
3. **RE-ESTIMATE TRIGGER at 1.6× a case's own line** (`K0cS_PREREGISTRATION.md`
   §2.3 rule 2). It does **not** stop the run: it forces the estimate to be
   re-made and the difference disclosed **before** the next case launches. An
   estimate that turns out low is not a licence to continue quietly.
4. **A case that cannot meet §6 after its one registered continuation has its
   rows REPORTED AS REFUSED with the measured spread.** An unsteady leg is
   **proposed, not executed**, inside this authorisation (§11).

**Against the $25 pre-authorisation:** the POINT is **2.8 %** of it and the
CEILING **8.5 %**. **The authorisation is not the binding constraint; the cap of
rule 1 is.** Sanaa's 2026-08-21 blanket is not a per-item read (rule 9), which is
exactly why this section exists.

**Wall clock, and one disclosure.** All nine cases serial, run concurrently
under the cap of 6: the critical path is `M1_f` / `M2_f` at **10 053 s ≈ 2.8 h**
at the point rate, **≈ 5.6 h** at the ceiling. **Those two rows exceed 3 600
wall s by design.** `COMPUTE_BUDGET_CHARTER.md`'s rule that a row over 3 600
wall s is a stall does **not** apply to them and they are **not** cleaned:
a stall here means `ExecutionTime` stops advancing, which `STATUS.<case>` and
the log detect separately. **This is registered now so that no one later reads
a 10 000 s row as a stall, and no one uses the stall rule to clean a legitimate
row out of the actual.**

### 10.4 What would blow this estimate, named in advance

1. **Mixed convection is stiffer than the natural convection the basis was
   measured on.** A shear layer and a plume interacting under SIMPLE may need
   more `p_rgh` sweeps per outer iteration than K0cS's buoyancy-only field.
   **This is why the ceiling is 2× and not 1.5×, and it is the single most
   likely consumer of it.**
2. **`RNGkEpsilon` on a `y⁺ < 1` mesh.** K0cS ran `kEpsilon` outside its wall
   treatment's design range on purpose and disclosed it; `RNGkEpsilon` is
   registered here because a published reproduction used it on this case, and if
   it diverges rather than converging to a wrong answer **that is a reported
   outcome, not a retry**.
3. **`Ra = 2.13e9` with a jet may not reach a steady state at all.** §6 decides
   that, not residuals, and a refusal is a **reported outcome, not an overrun**.
4. **K0cG overran by 1.35 %** — 1.35× — on this same campaign at a comparable
   mesh size. That is the measured precedent for this class of miss and it is
   inside the 2× ceiling.
5. **Contention.** Five peer teams share this 16-core box. Contention can only
   **inflate** an actual, so it is covered by the ceiling and it will be
   **named separately** at completion rather than absorbed into the ratio
   (`COMPUTE_BUDGET_CHARTER.md` §6).

### 10.5 The calibration obligation, registered now

At rung completion, rule 12's calibration is **not optional and a completion
report without it is incomplete**: actual core-minutes from `STATUS.<case>` and
`ExecutionTime`, the ratio **actual / POINT** and **actual / CEILING**, the gap
attributed (contention, waste, misprediction — **waste named separately, never
absorbed into the ratio**), dollars **derived at $0.0513/core-h and labelled
derived**, and the whole thing landing as a row in **`docs/COST_CALIBRATION.md`**
under that file's append rules and the rule-10 private-index protocol. **Two
named calibration items are registered in advance**: the `0.75` laminar scale
factor of §10.2, and the `1.6×` developed-flow contingency of §10.1.

---

## 11. Registered predictions, written before any solver exists

These are numbers and verdicts, not directions, so each can be wrong.

**The honest prior, stated first.** `docs/THERMAL_CAPABILITY_STATE.md` §1:
*"No turbulence model has passed a turbulent thermal gate in this lab. Three
models, two geometries, three Rayleigh decades, zero passes."* The record behind
it: K0cS `GATE FAIL` (`kOmegaSST` 8 of 10, `kEpsilon` 6 of 10,
`LaunderSharmaKE` **REFUSED**); K0cX `GATE FAIL` on all three models, 24 of 42
rows (D420 corrected the denominator from 60); K0cT `GATE FAIL`, and its Nusselt
regrade excluded at **3.1–4.6 `u_val`**. **And K0cG bounded the discretisation
error, so the misses are attributable: `kOmegaSST`'s square-cavity
deviation/GCI ratios are 43×, 84×, 112×, 233× and 722×** across `uv_peak`,
`Nu_hot`, `Sp`, `Nu_cold` and `Vpeak` (`K0cG_RESULTS.md` §2) — *"Refining the
mesh cannot account for a gap 43 to 722 times the discretisation uncertainty."*

> **One correction to the brief that spawned this document, recorded rather than
> repeated.** The figure *"0 of 18 model/geometry/quantity combinations"* **could
> not be reproduced from the records.** What the records support is the sentence
> quoted above plus the three per-rung tallies. **18 is not asserted here.** If a
> combination count is wanted it must be derived from the three results files and
> published with its denominator, the way D419 and D420 corrected K0c's and
> K0cX's denominators.

Now the predictions:

1. **Both closures return `GATE FAIL` on at least one of G1–G8.** The prior above
   is three geometries deep and has never once gone the other way.
2. **At least one graded row comes back not `CONVERGING`** and is therefore
   `NOT A RESULT` under §8.3. `K0cG` found `kEpsilon`'s triples `STAGNANT` on
   two quantities and `DIVERGENT` on three — **five of five non-`CONVERGING`** —
   and `RNGkEpsilon` is the same family. **The prediction names `M2` as the more
   likely of the two to produce it.**
3. **The temperature rows land closer than the velocity rows.** K2e measured the
   order: velocity and symmetry are **first order** in `β·ΔT`, wall heat flux is
   **second order**. At this rung's `ε = 0.0671` the Boussinesq model-form floor
   alone is **≈ 1.65 % on velocity against ≈ 0.031 % on Nusselt** (§3.5). If the
   ordering comes out the other way, that is a finding about the closure and not
   about the Boussinesq assumption, and the record will say so.
4. **`S1` is reproduced by both closures**: one large primary circulation with
   the jet along the ceiling and a plume off the floor, plus a secondary
   recirculation in the inlet-side upper corner. **If a closure does not
   reproduce it, that is a `GATE FAIL` on a regime, not a percentage**, and it
   is the more interesting outcome of the two.
5. **Guard `B` holds**: `B_hi` moves the temperature rows by **less than 1.00 K
   at every station**, i.e. the 0.5 K floor-temperature discrepancy of §3.3 is
   inside the band and does not by itself decide the gate. **If it does not
   hold, G1, G2 and G7 are `NOT A RESULT` until the primary arbitrates** — and
   that is registered here, before the number is known.
6. **Guard `I` is the one most likely to fire.** `I_hi` moves `G5a` (jet-peak
   speed) by **5–15 %**. Inlet turbulence is a known sensitivity for wall jets
   and the level is **not a measured quantity** (§3.2).
7. **`C_lam` differs from `M1_m` on `G6` by more than 25 %.** If it does not,
   **`G6` grades nothing** and the rung says so — K0c's F8 finding was that the
   set of rows `kOmegaSST` passed which a laminar solve did not also pass was
   **empty**.
8. **Achieved `y⁺_max` on `M1_f` is at or below 3.3**, Oulghelou's measured
   maximum on a 120 000-cell mesh of this case.

### 11.1 What a `GATE FAIL` here would and would not mean — registered before it happens

**It WOULD mean:** that on this geometry, at `Ra = 2.13e9`, `Re = 654`,
`Ri ≈ 2.1`, with these two wall-resolved two-equation closures and `Pr_t = 0.85`,
**at the grid limit**, the solution lies outside the experiment's band; and — if
the deviation/GCI ratio is large, as it was 43–722× on the square cavity — that
the miss is **model error, not grid error**. It would be the **first such result
in mixed convection** in this lab: every prior thermal failure was
buoyancy-only, so it would extend the "zero passes" record into a regime where
inertia and buoyancy contend. **That extension is the new information, and it is
what makes this rung worth its 829 core-minutes.**

**It WOULD NOT mean:** that RANS fails on data-centre aisle flows generally —
this is **one** geometry, **2D**, **one** Ra and **one** Ri; that Blay's data
are wrong; that a Reynolds-stress closure, a different wall treatment, a
different `Pr_t`, an unsteady RANS or an LES would also fail — **none of those
is run here** (§12); that the F14 cooling spine is invalidated — **K0d is a
rung, not the spine**; or that `Nu_floor` specifically is unusable — a model can
miss the mid-plane profiles and land the integrated wall flux, and G6 exists
separately precisely so that can be seen.

**And a `PASS` would not mean the converse.** A `PASS` on ten rows at one Ra on
one geometry is a rung, and this lab's own K0c line is the reason that sentence
is written down before the answer rather than after it.

---

## 12. The registered alternative: what this rung does if a case will not converge

**In the spirit of `T3_PREREGISTRATION.md` §11, and binding.**

A steady RANS of a jet-and-plume flow at `Ra = 2.13e9` may reach a **limit
cycle** rather than a steady state: the residuals plateau, the field oscillates
with a repeatable period, and the §6 criterion is never met.

**IF THAT HAPPENS, THIS RUNG REPORTS THE LIMIT CYCLE. IT DOES NOT AVERAGE IT.**

Registered, in full, before the answer is known:

1. The case is `NOT CONVERGED`. Every row depending on it is **`NOT A RESULT`**
   under §7.4 order 1. **No time-average, no last-checkpoint value and no
   "settled" value is graded.** An averaged limit cycle is a number with no
   uncertainty channel and it is exactly the failure this clause exists to
   prevent.
2. **What IS reported**, for the record and for the successor rung: the period
   in iterations, estimated from the checkpoint series; the **peak-to-peak
   amplitude of every graded scalar** over the last registered window; whether
   the amplitude is growing, flat or decaying; and the same three for the
   iterative residuals.
3. **One extension of +20 000 iterations is authorised** (§6), taken on the
   convergence state alone and **never with a graded value in view**. A second
   is not authorised by this document.
4. **An unsteady leg — `buoyantBoussinesqPimpleFoam`, URANS, with a
   time-averaging window and its own convergence and averaging criteria — is
   PROPOSED, NOT EXECUTED, inside this authorisation.** It is a **different
   solver class**, so it needs its own cost basis (L-271), its own
   pre-registration and its own freeze. K2b's estimate went VOID mid-rung for
   precisely this — pricing steady runs for an unsteady question — and that
   mistake is not repeated by absorbing an unsteady leg into a steady rung's
   budget.
5. **The verdict word for a rung that ends here is `NOT A RESULT`, with the
   count of cases that reached a limit cycle printed beside it.** It is not
   `PENDING`, it is not `BLOCKED`, and there is no softer word available
   (rule 1).

---

## 13. What this rung cannot see

- **Agreement with the experiment, until the primary is held.** Every graded row
  is `BLOCKED` (§7.4 order 4).
- **Three-dimensionality.** A 2D design on a rig with a 0.7 m span and guard
  cavities. The secondaries call the flow two-dimensional; **this rung cannot
  measure whether it is.**
- **Unsteadiness.** A steady RANS of a flow whose jet shear layer may flap. §12
  reports a limit cycle; it does not resolve one.
- **Any closure other than `kOmegaSST` and `RNGkEpsilon`**, and `Pr_t` at any
  value other than 0.85. A Reynolds-stress closure is the first extension to
  propose if the rung gates — K0cR already measured that `SSG` was **19 points
  better on velocity and 30 points worse on heat flux** on the square cavity.
- **Whether the inlet turbulence level is right.** It is not a measured
  quantity (§3.2); arm `I_hi` measures the sensitivity, guard `I` acts on it,
  and neither supplies the true value.
- **Which floor temperature the experiment actually used**, until the primary
  arbitrates (§3.3). Guard `B` measures what the ambiguity costs.
- **The exact Boussinesq error of this flow.** §3.5's 1.65 % / 0.031 % are K2e's
  exponents **carried across flow classes** — an estimate, labelled as one, never
  subtracted from a deviation.
- **Whether the digitised figures in the two secondaries faithfully reproduce
  Blay's measurements.** They are never graded against and this rung does not
  test them.
- **A mesh-converged value on any row whose triple comes back not `CONVERGING`**
  (§11 prediction 2). A fourth mesh level, in that event, is **proposed, not
  run** — and it needs its own costed pre-registration, exactly as D495 records
  for T3's `R_ff`.

---

## 14. Status at this freeze

**REFERENCE `NOT OBTAINED`. TEN GRADED ROWS, ALL `BLOCKED` BY CONSTRUCTION.
DESIGN, BANDS, INSTRUMENTS, COST AND STOP RULES REGISTERED. ZERO COMPUTE SPENT.
NO CASE DIRECTORY EXISTS AND NONE WAS CREATED —
`verification/runs/F14-cooling-ladder/K0d_runs/` DOES NOT EXIST, CHECKED IN THE
SAME SHELL INVOCATION AS THIS WRITE.**

The one remaining step, the day the ASME volume's PDF lands on disk:

1. **Title-page verify** the PDF from its printed page 1 (L-144); record its
   sha256.
2. Fill `K0d_reference_primary.json` per §7.6 from the printed pages, with page
   numbers, stated uncertainties and — only if a value had to be read from a
   figure **in the primary** — the digitisation increment.
3. Append the **dated reference addendum** at the foot of this file under rule 6,
   with the version bump and the assertion `lines whose number changed above this
   section: 0`, and **verify the frozen text above is byte-identical to its
   committed blob**.
4. **Nothing else changes.** No band, no threshold, no cap, no label, no
   comparator line.

**The frozen file's sha256 is recorded in this commit's message so that a later
addendum can prove the file that ran is the file that was frozen** (rule 2).

**Submissions remain PARKED** (rule 7): nothing about this rung, its reference,
its acquisition or its result is sent, filed, requested or shown outside this box
by any agent, at any level, ever. That is Sanaa's decision and hers alone.

---

# AMENDMENT 1 — 2026-08-24, BEFORE FIRST COMPUTE. Version 1.0 -> 1.1.

**lines whose number changed above this section: 0.**

## A1.0 The condition under which this amendment is legal, and how it was checked

Standing rule 2: *"Before first compute, amendments are legal and must state the
condition and how it was checked (name the run directory that does not exist)."*

**The run directory that does not exist is
`verification/runs/F14-cooling-ladder/K0d_runs/`.** Checked by the heat-transfer
supervisor **in the same shell invocation as this write**, twice, by two
independent means:

```
ls -d verification/runs/F14-cooling-ladder/K0d_runs
    -> No such file or directory
find verification/runs -maxdepth 2 -iname '*K0d*'
    -> no output
```

**K0d has never run. No solver, no mesh, no case directory, no partial output.**
The frozen document's own sha256 was re-verified against the commit that froze
it (`193b62a1`) before this amendment was written:
`829542696ffa5b1a512bfb6c8b3d29716b32b8971a704eb9d14f6c59f4312751` — identical.

**This amendment therefore alters no gate, threshold, cap or label**, and could
legally do so; it does not, and each ruling below says so explicitly. Every
section above this line is byte-unchanged.

Three items were left open by the drafting lane for the supervisor to rule on.
All three are ruled here. A fourth matter was checked and found sound, and that
is recorded too, because a check that finds nothing is worth as much as one that
finds something and is the only way to tell a checked claim from an unchecked one.

---

## A1.1 RULING on the "18 combinations" figure — the drafting lane's refusal is RATIFIED, and the number is now IDENTIFIED

**§11's refusal stands, unchanged.** The lane was right not to assert a figure it
could not reproduce, and right to say so in the document rather than silently
dropping it. What the records support is the registered sentence — *"Three
models, two geometries, three Rayleigh decades, zero passes"* — plus the three
per-rung tallies. **No gate, threshold, cap or label moves.**

**The supervisor's ruling adds what the lane could not: 18 is now identified.**
It is reconstructible, exactly, as a **grid size**:

| axis | count | members |
| --- | ---: | --- |
| turbulence models | **3** | `kOmegaSST`, `kEpsilon`, `LaunderSharmaKE` |
| geometry x Rayleigh condition | **3** | square cavity Ra 1.58e9 (K0cS); tall cavity AR 28.7 Ra 8.6e5; tall cavity AR 28.7 Ra 1.43e6 (K0cT / K0cX) |
| graded quantity class | **2** | one **velocity** quantity, one **heat** quantity |

`3 x 3 x 2 = 18`. **That is where the number comes from, and it is a grid size.**

**And a grid size is not a denominator.** This is the ruling, and it binds:

1. **At least one of the 18 cells is unpopulated by refusal.**
   `LaunderSharmaKE` **REFUSED** on the square cavity (K0cS). A cell that refused
   produced no measurement, so it can be neither a pass nor a fail. **18 is
   therefore a strict upper bound on any tally, never a tally.**
2. **This lab has already corrected exactly this error twice, in this campaign.**
   **D419** cut K0c's denominator from 24 to 20; **D420** cut K0cX's from 60 to
   42, and its own wording is the precedent verbatim: *"EIGHTEEN OF SIXTY K0cX
   ROWS THAT GRADED NOTHING LEFT THE TALLY."* Publishing 18 as a denominator
   would reintroduce, in a headline, the defect two docket items were spent
   removing from the rows beneath it. **The coincidence that D420's own
   correction is also the number 18 is a coincidence and must not be read as a
   derivation** — D420's 18 counts non-discriminating *rows* in one rung; this
   18 is a product of three axes across three rungs. They are different
   quantities that happen to share a value.
3. **Therefore:** if a combination count is ever wanted, it is derived from the
   three results files, published **with its denominator**, and the denominator
   **excludes every cell that graded nothing**. `18` may be quoted only as *"the
   grid is 3 x 3 x 2 = 18 cells, of which N were populated and 0 passed"*, with
   `N` measured. **`18` is never quoted bare.**

**A correction this ruling forces on a record outside this document.** The
registered sentence's phrase **"three Rayleigh decades" over-reads the coverage
it describes** and is corrected in `docs/THERMAL_CAPABILITY_STATE.md` §1 by
quote-and-strike in the same commit as this amendment. The three Rayleigh
numbers are **8.6e5, 1.43e6 and 1.58e9** — `log10` = 5.93, 6.16, 9.20. The two
low values differ by a factor of **1.66**, not by a decade; they are essentially
one Rayleigh condition sampled twice. A *bin* reading (they fall in the `1e5`,
`1e6` and `1e9` bins) makes "three decades" literally defensible, and that
defence is recorded here rather than suppressed — but the phrase reads as
**three decades of coverage**, and the true span is **two effectively distinct
Rayleigh conditions ~1100x apart**. The honest wording, which is what the
corrected record now carries: *"three Rayleigh numbers from 8.6e5 to 1.58e9, at
two effectively distinct conditions."*

**This weakens the prior slightly and is registered before the run for exactly
that reason.** §11's prediction 1 rests on that prior, and a prior stated in
this document must not be stronger than its evidence at the moment the
prediction is graded.

---

## A1.2 RULING on the derived `Ri ~ 2.1` — INDEPENDENTLY REPRODUCED, STANDS, and is now FENCED

**§3.4's `Ri` row stands unchanged. No gate, threshold, cap or label moves.**

**The supervisor re-derived it independently, by a different route than the
document uses, and it holds.** §3.4 forms `Re_H` by scaling the slot-based
Reynolds number: `654 x (H/h_in) = 654 x 57.78 = 3.78e4`. The check formed it
directly from the primitive quantities instead:

- `Re_H = u H / nu = 0.57 x 1.04 / 1.569e-5 =` **3.7782e4** — against the
  document's 3.7788e4, agreeing to **0.02 %**. The two routes are algebraically
  the same identity but are arithmetically independent, and the agreement
  confirms the geometry, the velocity and the viscosity are mutually consistent.
- `Ri = Gr / Re_H^2 = 3.00e9 / (3.7782e4)^2 =` **2.102**, against the document's
  **2.10**.

**A stronger check the document does not perform, done here.** `Ra` itself was
re-derived from first principles rather than taken from the secondary:

`Ra = g beta dT H^3 / (nu alpha)`, with `g = 9.81`, `beta = 1/298 = 3.356e-3`,
`dT = 20.0 K`, `H = 1.04 m`, `nu = 1.569e-5`, `alpha = nu/Pr = 2.2099e-5`:

`Ra = 9.81 x 3.356e-3 x 20.0 x 1.124864 / (1.569e-5 x 2.2099e-5) =` **2.136e9**

against Oulghelou's stated **2.13e9** — agreeing to **0.3 %**. **The entire
non-dimensional set of §3.4 is therefore reproducible from the geometry and the
fluid properties alone, without trusting the secondary's arithmetic.** That is a
materially stronger statement than "derived, not read", and it is recorded.

**THE FENCE, which is the operative part of this ruling and is new:**

**No gate, threshold, band, cap or label in this rung may depend on `Ri`.** `Ri`
is **descriptive**: it establishes that the case sits in the mixed-convection
regime, which is why the rung exists. It is **not** a graded quantity and it is
**not** an input to any band. The reason this must be written down is that `Ri`
inherits the provisional status of its parents: `Ra` and `Re` are both marked
*"secondary, to be confirmed against the primary on receipt"*. **A gate resting
on `Ri` would be a gate resting on an unconfirmed secondary, laundered through
two divisions until it looked like a property of the case.** It was checked, at
this amendment, that no such dependence exists today: `Ri` appears in §3.4 and in
§11.1's prose and nowhere in §7's rows, bands or conversion rule. **This fence
keeps it that way.**

If the primary moves `Ra` or `Re`, `Ri` moves with them and **nothing graded
moves**, which is the property the fence buys.

---

## A1.3 RULING on the K2e Boussinesq carry-across — ARITHMETIC REPRODUCED, TREATMENT UPHELD, and one REGISTERED DEFECT REPAIRED

**§3.5's `M0` treatment stands: the floor is REPORTED beside every velocity row
and G6, is never a correction, and is never subtracted from a deviation. No
gate, threshold, cap or label moves.**

**The arithmetic reproduces.** At `epsilon = 20.0/298 = 0.06711`:

- `D(u_max*) = 24.91 x epsilon^1.005 = 24.91 x 0.066216 =` **1.6495 %** -> §3.5's **1.65 %**
- `D(Nu_h)  = 6.355 x epsilon^1.968 = 6.355 x 4.8974e-3 =` **0.03112 %** -> §3.5's **0.031 %**

**The document's honesty about the extrapolation is upheld and is the right
treatment.** K2e measured those exponents on the **de Vahl Davis differentially
heated laminar cavity at Ra 1e5**. This rung is a **turbulent mixed-convection
cavity with a jet**. §3.5 says so in its own words — *"carrying them across flow
classes is this document's extrapolation"* — and that sentence is why the
treatment survives review. Note also, correctly stated in §3.5 and re-checked
here: `epsilon = 0.0671` is **interpolated** against K2e's own swept point
0.0667, so the *`epsilon`-dependence* is interpolated even though the *flow
class* is extrapolated. Those are two different axes and the document does not
conflate them.

**THE DEFECT, and it is the substantive finding of this amendment.**

§11 prediction 3 reads, in its closing clause:

> *"If the ordering comes out the other way, that is a finding about the closure
> and not about the Boussinesq assumption, and the record will say so."*

**As written, that clause makes the carry-across unfalsifiable by this rung.**
Trace the two branches. If the temperature rows land closer than the velocity
rows, the prediction is confirmed and `M0` is credited. If they do not, the
clause **pre-assigns** the outcome to the closure — so `M0` is credited in that
branch too. **No possible result of K0d can count against the carry-across.**

An estimate that no outcome can disconfirm is not reported evidence. It is an
assumption wearing a number, and printing it beside every velocity row gives it
the appearance of a measured floor while insulating it from the one experiment
that could test it. **That is the `evidence-annotated-as-non-binding` failure
class**: a figure whose status is declared rather than earned.

**THE REPAIR, registered now, before first compute, and it adds a branch rather
than changing a prediction:**

Prediction 3's closing clause is **struck** — struck, not rewritten, per rule 6 —
and replaced by a **three-way** disposition. **The prediction itself is
unchanged**: the temperature rows still land closer than the velocity rows.
Only the *disposition of a contrary outcome* is disambiguated, and it was
ambiguous, not registered.

> ~~*"If the ordering comes out the other way, that is a finding about the
> closure and not about the Boussinesq assumption, and the record will say so."*~~
>
> **REPLACED, 2026-08-24, before first compute:** If the ordering comes out the
> other way, the record **names both live hypotheses and states which the
> evidence discriminates**, rather than pre-assigning the outcome:
>
> **(i)** it is a finding about the **closure** — the model's thermal error
> exceeds its momentum error on this flow, which is what §11 prediction 3
> expects to be false; **or**
>
> **(ii)** it is a finding about the **carry-across itself** — the K2e exponents
> measured on a laminar differentially heated cavity **do not transfer** to a
> turbulent mixed-convection cavity with a jet, i.e. `M0` is the wrong floor for
> this flow class.
>
> **The discriminator, registered here so it is not chosen afterwards:** the two
> hypotheses are separated by **magnitude**, not by sign. `M0` predicts a floor
> of **1.65 % on velocity against 0.031 % on Nusselt — a ratio of ~53x**.
> Hypothesis (ii) is preferred over (i) **only if** the observed velocity-to-heat
> deviation ratio is **inverted AND the heat deviation exceeds 1.65 %**, i.e.
> the thermal row misses by more than the floor `M0` assigns to *velocity* — a
> magnitude `M0` cannot produce under any closure, because `M0` is a bound on the
> Boussinesq model form and not on the turbulence model. **Below that magnitude
> the outcome does not discriminate**, and the record says **NEITHER
> hypothesis is established** rather than defaulting to (i).
>
> **`M0` remains REPORTED and is still never subtracted from a deviation**, in
> every branch. This clause changes what the *record must say*; it changes no
> number, no band and no verdict.

**Why this is legal here and would not be after first compute.** It adds a
registered branch to the *interpretation* of an outcome. Rule 2 permits that
before compute and forbids it after, which is precisely why it is being done
now, at zero compute, with the run directory absent.

---

## A1.4 CHECKED AND FOUND SOUND — §7.6's unarmed `G6` band is NOT a defect

Recorded because a supervisor's check that finds nothing must be
distinguishable from a check never made.

`G6`'s row in §7.3 reads *"± 10 % of |q_ref|"* and *"to be armed by addendum on
receipt of the primary"*, and §7.6 registers a reference slot whose file does not
exist. **On a first reading this looks like an unarmed gate**, which would be
fatal: rule 2 closes gates at first compute and permits only addenda that
*"cannot alter a gate, threshold, cap or label"* — so a band armed by addendum
*after* first compute could never be legally graded.

**It is not an unarmed gate, and the design is sound.** The **threshold is
frozen**: it is the *relative* band **± 10 %**, fixed now, in §7.2's registered
**band conversion rule** — which is registered *"in a form that does not need the
reference value"*. What §7.6 supplies later is **data**, not a threshold: the
reference value the frozen rule is applied *to*. Filling a registered schema slot
with a number read from a printed page is not amending a gate.

**The distinction that makes it safe, and it is the whole point:** the band
cannot be widened or narrowed by what arrives, because ± 10 % is already frozen;
`q_ref` can only move where the band sits, not how wide it is. **The freeze is
on the rule; the reference is evidence.** §7.6's own sentence — *"Nothing in the
comparator changes when it appears"* — is the correct test and it is satisfied.

**One condition attached, which is a restatement of the existing design and not
a new gate:** if the primary has not arrived when the comparator runs, `G6` is
`PENDING` — a queue state, per rule 1 — and is **never** graded against a
reference taken from a secondary, nor softened into a pass. K0d's secondaries
(Zou 2018, Oulghelou 2020) may not fill §7.6's slot; §7.6 already says the person
who fills it *"reads it from the printed page (L-144) and writes the page
number"*, and that stands.

---

## A1.5 What this amendment did NOT do

- **No gate moved. No threshold moved. No cap moved. No label moved.** The rows
  of §7.3, the conversion rule of §7.2, the verdict ladder of §7.4, the guards of
  §7.5, the instruments of §8 and the cost of §10 are all byte-unchanged.
- **No prediction was weakened.** §11's predictions 1-8 stand as registered.
  Prediction 3's *prediction* is unchanged; only the disposition of a contrary
  outcome was disambiguated, and it was ambiguous rather than registered.
- **No compute ran.** `verification/runs/F14-cooling-ladder/K0d_runs/` still does
  not exist at the moment of this write, and this amendment does not create it.
- **Nothing was sent** (rule 7).

**K0d remains FROZEN, ARMED AND UNFIRED.**

*Amendment written by the heat-transfer supervisor, 2026-08-24. Zero compute.*

---

# AMENDMENT 2 — 2026-08-25, BEFORE FIRST COMPUTE. Version 1.1 -> 1.2.

**Lines whose number changed above this section: 0.** Nothing above is edited.
**No gate, threshold, band, cap, label or prediction is created, moved, retired
or weakened by this amendment.** It adds one **pre-compute abort condition** and
nothing else.

## A2.1 The condition, and how it was checked

Rule 2 permits amendment **only before first compute**, and requires the
condition be stated with the check that established it.

**Checked in the shell invocation that wrote this file:**
`verification/runs/F14-cooling-ladder/K0d_runs/` **does not exist**, and a
`find` across `verification/runs/` for any path matching `*K0d*` returns
**nothing**. **K0d has no case directory and has never consumed a core-second.**
The prereg on disk is byte-identical to its blob at HEAD (sha256
`90365bde…5b5b44`, the post-`AMENDMENT 1` hash; the original v1.0 freeze at
`193b62a1` was `829542…312751`, and the difference is `AMENDMENT 1` appended at
the foot at `935d4114`, which is disclosed there).

**This is the last window in which this amendment is legal. After first compute
it closes permanently.**

## A2.2 The gap being closed — A COMPARATOR SELFTEST PROVES THE GRADER, NOT THE CASE

**This finding is the ansys-verification team's and is cited as theirs.**

VMFL045 **crashed at wall 0 s** on a missing `fvSolution` solver entry. Its
comparator's selftest had passed **45 / 45 with real negative controls** — and
**could never have caught it**, because **nothing in the pre-compute checks
exercised the actual solver dictionary set.**

**K0d's exposure is exactly this.** §8 of this pre-registration registers three
instruments — the planted-zero control, the strict completion rule with its age
guard, and Roache triple gating — and `AMENDMENT 1` audited them. **All of that
is about the GRADER. None of it establishes that K0d's case dictionaries survive
contact with the solver.** This team has now built and passed a planted-zero
control on the T1b chain and knows precisely how reassuring an instrument audit
feels; **that reassurance does not extend to the case, and this amendment exists
to stop it being read as though it did.**

## A2.3 THE MECHANISM IS A REGIME BOUNDARY, AND K0d CROSSES ONE

**The part worth understanding, not merely recording.** VMFL045's `solvers`
block was **byte-identical to VMFL051's**, and **VMFL051 ran 1 693 timesteps
successfully with the same missing entry.** The difference is physical:
**VMFL051 is inviscid, VMFL045 viscous**, and the solver enters the implicit
corrector — the path that needs the missing key — **only when μ > 0**. Proved
with the reader shown able to see both states: **implicit solve counts of 0
across VMFL051's entire successful run against 1 in VMFL045 before it died.**

**A dictionary can be complete for one regime and incomplete for another, and the
defect is LATENT rather than visible.** It does not announce itself in review; it
announces itself as a crash at wall 0 s, or worse, does not announce itself at
all.

**K0d is turbulent mixed convection.** Any configuration inherited across a
regime change — **Boussinesq to compressible, laminar to turbulent, steady to
transient** — carries this defect class.

**And it lands directly on `AMENDMENT 1` §A1.3, the K2e Boussinesq
carry-across.** A1.3 examined that carry-across as a **modelling** question:
whether the K2e arithmetic transfers, and how `M0` is disposed. **It did not ask
whether the carried dictionaries are COMPLETE for K0d's regime, because that
question had not been posed to this lab yet.** **A1.3's ruling stands unaltered**
— nothing in it is withdrawn — **but it is now explicitly recorded as NOT having
covered the latent-dictionary dimension**, which this amendment covers instead.
**A carry-across is two questions, and the lab had been asking one.**

## A2.4 REGISTERED: a pre-flight smoke test, as an ABORT CONDITION on first compute

**Before any graded K0d solve, and as a precondition of it:**

1. **One timestep on the COARSEST mesh**, with K0d's own `constant/`, `system/`
   and `0/` dictionaries as they will be used for the graded run.
2. **In a scratch directory OUTSIDE `verification/runs/`.** This is not a
   preference. **This team's own control lane established that `measure()` writes
   into whatever directory it is handed** (`log.writeCellCentres`, `Cx`, `Cy`,
   `V`), and **two irreplaceable single-rank solvers have been running in
   `verification/runs/T-family/T1_runs/` throughout this session** — at the time
   of writing, ~250 core-hours that cannot be re-bought. A smoke test that writes
   into the run tree to prove the run tree is safe is self-defeating.
3. **On failure: ABORT. No graded solve starts.** The failure is a **finding
   about the case**, triaged, not worked around (`SUPERVISION_CHARTER.md` §3
   check 2 — a crash is a finding until triage says otherwise).
4. **On success it proves ONE thing and it is stated narrowly: the dictionaries
   are sufficient for the solver to take a step in this regime.** It is **not**
   evidence about the physics, the mesh quality, convergence, or any graded
   quantity, and it may not be cited as such.

**The existing guard is unchanged and remains absolute:** a run refuses where
`0/` or a time directory already exists. **That guard is what stands between this
lab and a corrupted case**, and this session supplied fresh evidence for it — the
ansys-verification supervisor read "no run directory", concluded a lane was dead
and dispatched a second **at 01:35:26Z, when the first had launched at
01:36:45Z**; **the second launcher refused at exit 2 because the directory
existed, and that refusal is the only reason nothing was corrupted.** *A stale
read is not only a git-tree failure; it is an agent-dispatch failure with the
same shape.*

## A2.5 Why this is an amendment and not a gate change

**The smoke test can only ever PREVENT a graded run from starting. It can never
turn a `GATE FAIL` into a `PASS`, and it produces no graded number.** That is the
same asymmetry rule 5 fixes for the triple gate and that this team registered for
the T1b planted-zero control: **an instrument admitted late is safe precisely
when it can only subtract.**

**Cost:** one timestep on the coarsest mesh — **seconds**, well inside the $25
pre-authorisation, **$-negligible, derived not measured**
(`COMPUTE_BUDGET_CHARTER.md` §5). **It is charged to K0d's rung and appears in
K0d's calibration row.** **No cap is registered and none is claimed** — this
team's standing ruling that a prediction is not a cap applies.

## A2.6 What is unchanged

- **Every gate, threshold, band, cap, label and verdict of §§1–11 stands
  byte-unchanged**, including §7.2's conversion rule, §7.4's verdict ladder,
  §7.5's guards, §8's instruments and §10's cost.
- **No prediction is weakened.** §11's predictions 1–8 stand as registered, and
  `AMENDMENT 1`'s three-way disposition of prediction 3 stands.
- **`AMENDMENT 1` §§A1.1–A1.4 stand in full.** A2.3 adds a dimension A1.3 did not
  cover; it withdraws nothing.
- **`G6` remains `PENDING` on Blay 1992**, which is still NOT OBTAINED.
- **No compute ran.** `verification/runs/F14-cooling-ladder/K0d_runs/` does not
  exist at the moment of this write, and this amendment does not create it.
- **Nothing was sent** (rule 7).

**K0d remains FROZEN, ARMED AND UNFIRED.**

*Amendment written by the heat-transfer supervisor, 2026-08-25. Zero compute.*

---

# AMENDMENT 3 — 2026-08-25, BEFORE FIRST COMPUTE. Version 1.2 -> 1.3.

**Lines whose number changed above this section: 0.** Nothing above is edited.
**No gate, threshold, band, cap, label or registered prediction is created,
moved, retired or weakened by this amendment.** It replaces one unsatisfiable
enumeration inside §8.2 clause 4 with a per-closure enumeration registered in
advance, and it does so in the pre-compute window that rule 2 leaves open.

**Written by the heat-transfer lane on the supervisor's ruling**, implementing
the disposition of
`docs/campaigns/F14-cooling-ladder/K0d_PREFLIGHT_EXECUTABILITY_FINDING.md`
(commit `af7f64c7`), which the supervisor verified personally before ruling.

## A3.0 The condition under which this amendment is legal, how it was checked, and the proof that nothing above moved

Standing rule 2: *"Before first compute, amendments are legal **and must state
the condition and how it was checked** (name the run directory that does not
exist)."*

**The run directory that does not exist is
`verification/runs/F14-cooling-ladder/K0d_runs/`.** Both checks below were run
**in the same shell invocation that wrote this file**, and their output is
recorded **verbatim**:

```
$ ls -d verification/runs/F14-cooling-ladder/K0d_runs
cannot access 'verification/runs/F14-cooling-ladder/K0d_runs': No such file or directory

$ find verification/runs -iname '*K0d*'
(no output)
```

**And the reader was shown able to see a match** — a `find` that reports nothing
while being incapable of reporting anything is not evidence (rule 3, applied to
a search). The identical `find`, with the pattern changed one character to the
sibling rung that does exist:

```
$ find verification/runs -iname '*K0c*' | head -3
verification/runs/F14-cooling-ladder/K0cG_runs
verification/runs/F14-cooling-ladder/K0cR_runs
verification/runs/F14-cooling-ladder/K0cP_runs
```

**The pattern matches when there is something to match. `*K0d*` matches
nothing. K0d has never consumed a core-second, has no case directory, no mesh
and no partial output.**

**The freeze was re-verified before one byte was appended.** `sha256` of
`docs/campaigns/F14-cooling-ladder/K0d_PREREGISTRATION.md` **on disk** against
its **committed blob at `HEAD`** (`21c2c0aeb627b90c641b94afc06deefbe7af4eec`), computed in this same invocation:

```
disk = 8b1340d69cce6262c2e545692b15aed2da9c174d3930986dc91b35e3c9da0918
blob = 8b1340d69cce6262c2e545692b15aed2da9c174d3930986dc91b35e3c9da0918
```

**Identical.** The document this amendment is appended to is the document that
was frozen, and the appended text was built onto the **`HEAD` blob**, not onto
the working-tree copy.

**THE `lines whose number changed above this section: 0` ASSERTION IS
ARITHMETIC HERE, NOT A PROMISE, and this is how it is proved.** The three
conditions were established mechanically in the writing invocation:

1. **The child file was produced by CONCATENATION onto the `HEAD` blob.** The
   base was obtained with `git show HEAD:<path>` and no byte of it was read,
   modified and written back. There is no edit path by which a line above could
   move.
2. **The base is a BYTE-EXACT PREFIX of the child.** The first **86688**
   bytes of the new file were compared byte-for-byte against the `HEAD` blob and
   are identical. A single changed, inserted or deleted byte anywhere above this
   section would have failed that comparison and aborted the write.
3. **The commit is INSERTIONS ONLY, ZERO DELETIONS.** Verified after the commit
   from `git diff HEAD~1 HEAD --numstat`, which is recorded in the commit
   message. A pure append cannot renumber a preceding line.

**Other records cite this file by line** — §8.2 clause 4 is cited at lines
560–562 and the §5 case table at lines 327–329 in the pre-flight finding, and
§7.2's station list at line 432 and `G7` at line 455 in §A3.6 below. **All of
those citations remain valid after this commit**, which is exactly what rule 6
protects and why the assertion above is proved rather than asserted.

**This amendment could legally alter a gate, threshold, cap or label — the
window is open. It does not, and §A3.8 says so item by item.**

---

## A3.1 THE RULING — the pre-flight lane's refusal is UPHELD, and the exposure it named is confirmed

The dispatched launch lane refused to fire this rung and recorded why in
`docs/campaigns/F14-cooling-ladder/K0d_PREFLIGHT_EXECUTABILITY_FINDING.md`
(committed `af7f64c7`). **The heat-transfer supervisor has verified that finding
personally — `SUPERVISION_CHARTER.md` §3 check 2, crash-and-abort triage, which
is not delegable — and rules that the refusal was correct.** This amendment
implements that ruling. It does not re-open it.

**What the frozen document binds, quoted exactly.** §8.2 introduces seven
conditions as *"this rung's binding conditions, all of which must hold"*.
Clause 4 reads:

> 4. **`T U p_rgh alphat nut k omega` all present** at `endTime` (`C_lam` is
>    exempt from `nut k omega` and that exemption is registered here, not
>    discovered later)

**`omega` is named literally. Exactly one exemption is registered: `C_lam`.**

**What §5 registers against it.** Three of the nine cases — `M2_c`, `M2_m`,
`M2_f` — run **`RNGkEpsilon`**. A `k`–`ε` closure carries no `ω` field and
`buoyantBoussinesqSimpleFoam` writes none for it. **Those three cases can
therefore never satisfy clause 4, however cleanly they solve.**

**And the exposure is the whole rung, not the `M2` leg.** §8.2 closes:

> **`analyse_k0d.py` refuses (exit 2) unless all nine `DONE.<case>` markers are
> present.**

Nine cases would run to completion; three could not earn a marker; the
comparator would exit 2 and grade **nothing** — not `GATE FAIL`, not
`NOT A RESULT` on the `M2` rows alone, but no verdict at all. **The exposure is
the registered POINT of `829.36` core-min, not `M2`'s `296.32`.** Arithmetic
re-checked at this amendment from §10.2: `43.50 + 85.27 + 167.55 = 296.32` for
the `M2` leg, against the registered rung POINT of `829.36`.

**This is an internal contradiction inside one frozen document**, not a defect
of any lab standard. §A3.3 establishes that, with the evidence, because the
alternative reading — that the lab's completion rule is itself wrong — would
escalate as a charter matter and it does not.

---

## A3.2 THE COUNTER-READING, recorded in full and ANSWERED, not suppressed

The refusing lane recorded a second reading of §8.2 and declined to adopt it,
referring both. **It is reproduced here in full because a ruling that hides the
argument it defeated is not a ruling**, and a later reader must be able to
reconstruct the choice and disagree with it.

**The counter-reading, in full.** §8.2's own preamble says:

> `mark_done_k0d.py` applies, **for the thermal field set**, the rule that
> section states verbatim

On that reading, *"the thermal field set"* is the generic obligation; the
enumerated `T U p_rgh alphat nut k omega` is merely the **`kOmegaSST` instance**
of it, quoted from `T1b_L4_AMENDMENT.md` §7 — and `T1b` is a `kOmegaSST` rung —
and a correctly written `mark_done_k0d.py` would take each case's own model
field set, `epsilon` for `M2` and `omega` for `M1`. **On that reading there is no
defect at all, only a script yet to be written correctly, and this amendment is
unnecessary.**

**It is not frivolous.** §8.2's preamble does say *"for the thermal field set"*,
`T1b_L4_AMENDMENT.md` is a `kOmegaSST` document, and §A3.3 below shows that
every other marker script in this lab does exactly what the counter-reading
describes. The reading is defeated on the clause's own words, not on its
plausibility.

**THE ANSWER, and it is clause 4's own parenthetical.** Clause 4 says the
`C_lam` exemption *"is registered here, **not discovered later**"*. **That is an
explicit, frozen instruction that exemptions to this clause are pre-registered
rather than inferred at grading time.** A lane writing `mark_done_k0d.py` under
the counter-reading would be inferring a **second, unregistered** exemption —
substituting `epsilon` for `omega` on three cases — on its own authority, at
grading time, against a frozen instrument, and doing precisely what the sentence
immediately beside it forbids. **The counter-reading is not merely unregistered;
it is registered against.**

**And the second reason, which is what freezing is for.** Rule 2 makes the
freeze *"the document's entire evidentiary content"*. **A pre-registration that
must be reinterpreted in order to be satisfiable has lost that content**: if the
enumeration can be read as an instance when it fails and as a rule when it
succeeds, then the completion instrument is decided after the fact by whoever
writes the script, which is the exact failure freezing exists to prevent. The
defect is not that the counter-reading gives a bad answer — it may well give the
right *fields*. The defect is that it must be **chosen**, by an agent, after the
document was frozen.

**Disposition: the counter-reading is REJECTED as an interpretation and ADOPTED
as a specification.** The fields it would have inferred are exactly the fields
§A3.4 now registers. What changes is that they are **registered in advance, in
the open pre-compute window, by a supervisor's ruling** — not inferred later by a
script author. **That distinction is the entire content of this amendment**, and
it costs zero core-seconds to make now and cannot legally be made after first
compute.

---

## A3.3 THE DEFECT IS K0d's, NOT THE LAB's — evidence re-verified for this amendment

**This section exists because the two readings differ in what they escalate.**
If clause 4's enumeration were a lab-wide invariant, then this lab's completion
rule would forbid `k`–`ε` thermal work outright, every `k`–`ε` thermal verdict
already on the books would be void, and the matter would escalate as a charter
question under `ESCALATION_CHARTER.md`. **It is not, and it does not.** Each
item below was re-checked from disk for this amendment rather than carried from
the lane's report.

**Evidence 1 — `k`–`ε` thermal cases have earned `DONE` markers in this very
campaign, repeatedly.** Nine of them, found on disk at this amendment:

| marker | rung directory |
| --- | --- |
| `DONE.S_KE_x` | `verification/runs/F14-cooling-ladder/K0cG_runs/` |
| `DONE.S_KE_c`, `DONE.S_KE_f` | `verification/runs/F14-cooling-ladder/K0cS_runs/` |
| `DONE.X_lo_c_KE`, `DONE.X_hi_c_KE`, `DONE.X_lo_f_KE`, `DONE.X_hi_f_KE`, `DONE.P_hi_f_KE`, `DONE.X_hi_x_KE` | `verification/runs/F14-cooling-ladder/K0cX_runs/` |

**Nine `k`–`ε` markers. Not one of those cases wrote an `omega` field.** If
clause 4's enumeration were the lab's invariant, none of them could exist.

**Evidence 2 — the field sets on disk, read with the reader shown able to see
both states** (rule 3 discipline applied to a directory listing; a listing that
reports "no `omega`" while being unable to see an `omega` anywhere is worthless):

| completed case | closure | `omega` at latest time | `epsilon` at latest time | `nut` | `k` | `alphat` |
| --- | --- | --- | --- | --- | --- | --- |
| `K0cS_runs/S_SST_f` | `kOmegaSST` | **PRESENT** | absent | present | present | present |
| `K0cS_runs/S_KE_f` | `kEpsilon` | **ABSENT** | **PRESENT** | present | present | present |
| `K0cS_runs/C1_laminar` | laminar | absent | absent | **absent** | **absent** | present |

**Both branches fire.** `S_SST_f` is the non-zero the reader was shown able to
see; `S_KE_f`'s absent `omega` is therefore a measurement and not a blind spot.

**The laminar row is load-bearing for §A3.4 and is why the `C_lam` exemption is
carried across unchanged and not narrowed:** `C1_laminar` wrote **neither `nut`
nor `k`** as well as neither `omega` nor `epsilon`. Clause 4's registered
exemption — *"exempt from `nut k omega`"* — is exactly right, and any restatement
that exempted `C_lam` only from `nut` and the second turbulence field, leaving
`k` required, **would make `C_lam` unsatisfiable and would recreate this
amendment's own defect on a different case.** §A3.4 therefore carries the
three-field exemption over verbatim.

**Evidence 3 — `RNGkEpsilon` specifically.** No `RNGkEpsilon` case exists
anywhere on this box, so its written field set is **not** measured from a
completed run and this amendment does not pretend otherwise. What was read
instead, from the model's own source on this box at
`/usr/lib/openfoam/openfoam2606/src/TurbulenceModels/turbulenceModels/RAS/RNGkEpsilon/RNGkEpsilon.H`:
the class declares its two transported members as **`volScalarField k_`** and
**`volScalarField epsilon_`** (lines 120–121), and the string `omega` occurs in
that header **zero** times — against **four** occurrences in `kOmegaSST.H`, which
is the control showing the reader can see `omega` in a header when it is there.
**`RNGkEpsilon` transports `k` and `epsilon` and has no `omega` to write.**

**Evidence 4 — marker scripts in this lab carry a PER-RUNG field tuple, never a
fixed lab-wide list.** Read from the scripts themselves at this amendment:

| marker script | its registered field tuple |
| --- | --- |
| `T-family/T10a_runs/mark_done_t10a.py` | `NEEDED = ("T", "qr")` |
| `T-family/T10aR_runs/mark_done_t10aR.py` | `NEEDED = ("T", "qr")` |
| `T-family/T9a_runs/mark_done_t9a.py`, `T9aH_runs/mark_done_t9a.py` | `NEEDED = ("T", "DT")` |
| `T-family/E4_runs/mark_done_e4a.py` | `NEEDED = ("p", "U", "phi")` |
| `T-family/T1_runs/mark_done_t1b.py` | `NEEDED = ("T","U","p_rgh","alphat")` **plus** `NEEDED_TURBULENT = ("nut","k","omega")` |
| `T-family/T3_runs/mark_done_t3.py` | `NEEDED = ("T","U","p_rgh","alphat","phi")` **plus** `NEEDED_TURBULENT = ("nut","k","omega")` |
| `T-family/T1_runs/mark_done_t1b_ext1.py` | imports both tuples and applies `need = NEEDED if is_laminar(case) else NEEDED + NEEDED_TURBULENT` (line 116) |

**Four different tuples across seven scripts, and the two thermal ones already
split the list into a base set and a turbulence set with a laminar exemption
applied per case.** `mark_done_t1b_ext1.py` line 116 is the lab's existing,
executable statement that the turbulence half of the tuple is selected
**per case from the case's own closure**. K0d's clause 4 is the only place in
this lab where that selection was flattened into a literal enumeration and then
had a differently-closed case registered against it.

**THE CONCLUSION, and it is the operative finding of this section.** Standing
rule 4's parenthetical — *"fields present (`T U p_rgh alphat nut k omega` for the
thermal family)"* — **describes the `T1b` instance from which it was drawn. It is
not a lab-wide invariant, and the evidence above is what establishes that.**
Therefore:

- **No standing rule is amended by this amendment.** Rule 4's clauses — `rc = 0`,
  the `End` line, `last time == endTime`, fields present, the `ExecutionTime`
  count, and the age guard — all stand untouched. What is registered here is
  *which* fields, for *this* rung's three closures.
- **No charter clause is amended, and nothing escalates as a charter matter**
  under `ESCALATION_CHARTER.md`. There is no cross-family arbitration here and
  no standard is retired.
- **No prior `k`–`ε` verdict is disturbed.** The nine markers of Evidence 1 stand.
- **The defect is local and exact:** K0d's clause 4 transcribed the `T1b`
  `kOmegaSST` field set literally, and §5 then registered three `RNGkEpsilon`
  cases against it. **One frozen document contradicting itself.**

---

## A3.4 THE REPAIR — clause 4's enumeration becomes PER-CLOSURE, registered in advance

Per rule 6 the frozen text above is **not edited**. Clause 4 is **struck and
replaced here**, at the foot, and this section governs from this amendment's
commit.

> ~~4. **`T U p_rgh alphat nut k omega` all present** at `endTime` (`C_lam` is
>    exempt from `nut k omega` and that exemption is registered here, not
>    discovered later)~~
>
> **REPLACED, 2026-08-25, BEFORE FIRST COMPUTE. Clause 4 now enumerates PER
> CLOSURE, and every enumeration is registered HERE, not discovered later:**
>
> **4.** The **registered completion field set of the case's own closure** is
> **all present** at `endTime`:
>
> | closure | cases | **registered completion field set** |
> | --- | --- | --- |
> | `kOmegaSST` | `M1_c`, `M1_m`, `M1_f`, `B_hi`, `I_hi` (five) | **`T U p_rgh alphat nut k omega`** |
> | `RNGkEpsilon` | `M2_c`, `M2_m`, `M2_f` (three) | **`T U p_rgh alphat nut k epsilon`** |
> | laminar | `C_lam` (one) | **`T U p_rgh alphat`** — i.e. exempt from `nut`, from `k` **and** from the second turbulence field, which is exactly the exemption clause 4 already registered, carried across **unchanged and no wider** |
>
> **Nine cases, three closures, three enumerations, all three fixed at this
> amendment and none inferable later.**
>
> **AND THE GENERALISED FORM OF CLAUSE 4's OWN INSTRUCTION, which is new and is
> a tightening:** *no exemption and no field substitution may be inferred at
> grading time.* A case whose closure does not appear in the table above **has
> no registered completion field set**, and `mark_done_k0d.py` **refuses
> (exit 2) rather than infer one**. §5 registers no such case today; the clause
> exists so that adding one later cannot be done silently by a script author.

**Everything else in §8.2 is untouched**: clauses 1, 2, 3, 5, 6 and 7 stand
verbatim, the extended-case form stands verbatim, and
**`analyse_k0d.py` still refuses (exit 2) unless all nine `DONE.<case>` markers
are present** — that refusal is not weakened, and after this amendment all nine
markers are for the first time *obtainable*.

---

## A3.5 THIS TIGHTENS AND CANNOT LOOSEN — shown, in a form a reader can refuse

**The claim is not asserted; it is shown, case by case, so that a reader who
thinks it false can point at the cell where it fails.**

| case | closure | clause 4 **AS FROZEN** required | clause 4 **AS AMENDED** requires | satisfiable **before** | satisfiable **after** |
| --- | --- | --- | --- | --- | --- |
| `M1_c` | kOmegaSST | `T U p_rgh alphat nut k omega` | **identical** | YES | YES |
| `M1_m` | kOmegaSST | `T U p_rgh alphat nut k omega` | **identical** | YES | YES |
| `M1_f` | kOmegaSST | `T U p_rgh alphat nut k omega` | **identical** | YES | YES |
| `B_hi` | kOmegaSST | `T U p_rgh alphat nut k omega` | **identical** | YES | YES |
| `I_hi` | kOmegaSST | `T U p_rgh alphat nut k omega` | **identical** | YES | YES |
| `M2_c` | RNGkEpsilon | `T U p_rgh alphat nut k` **`omega`** | `T U p_rgh alphat nut k` **`epsilon`** | **NO** | YES |
| `M2_m` | RNGkEpsilon | `T U p_rgh alphat nut k` **`omega`** | `T U p_rgh alphat nut k` **`epsilon`** | **NO** | YES |
| `M2_f` | RNGkEpsilon | `T U p_rgh alphat nut k` **`omega`** | `T U p_rgh alphat nut k` **`epsilon`** | **NO** | YES |
| `C_lam` | laminar | `T U p_rgh alphat` | **identical** | YES | YES |

**Read the two columns that differ, and only those.** On the three `M2` rows,
and nowhere else:

1. **One requirement is REMOVED: `omega`.** It was never a check. A condition no
   run of that closure can satisfy does not discriminate between a good run and
   a bad one — **it refuses both**. Removing it removes a guaranteed refusal, not
   a test.
2. **One requirement is ADDED: `epsilon`.** **Clause 4 as frozen does not impose
   this on any case.** Nothing in the frozen text obliged `M2_c`, `M2_m` or
   `M2_f` to have written their second turbulence field at all. **The amendment
   is the first instrument in this rung to require it.**

**Counted, because "more checkable" should be a number.** Field-presence
assertions that a compliant run can actually be tested against:

| | satisfiable assertions | assertions no run could satisfy |
| --- | ---: | ---: |
| clause 4 **as frozen** | `5×7 + 0 + 1×4 =` **39** | `3×7 =` **21** |
| clause 4 **as amended** | `5×7 + 3×7 + 1×4 =` **60** | **0** |

**60 checkable field assertions after, against 39 before — a 54 % increase — and
zero assertions were removed from any case that was capable of satisfying
them.** Add the new refusal clause of §A3.4 (an unregistered closure is refused
outright), which has no counterpart in the frozen text at all.

**The asymmetry that makes this safe, and it is the same one `AMENDMENT 2` §A2.5
registered for the smoke test.** A completion instrument can only ever **prevent
a case from being certified**. It produces no graded number, it cannot move a
value, and **it cannot turn a `GATE FAIL` into a `PASS`**. What this amendment
changes is *which cases are capable of being certified at all* — from six to
nine — and it does so by making three cases testable that were previously only
refusable. **A rung that grades nothing is not a stricter rung. It is a rung
with no verdict.**

---

## A3.6 CHECKED AND FOUND — three further items, DISCLOSED HERE, NOT REPAIRED HERE, REFERRED

Recorded under the practice `AMENDMENT 1` §A1.4 established: a check that finds
something must be recorded, and a check that finds nothing must be
distinguishable from a check never made. **The ruling this amendment implements
did not anticipate the first two. Neither is repaired by this amendment** — each
would touch a row definition, a band or a registered prediction, which §A3.8
forbids this amendment to do — **and both are referred to the supervisor while
the pre-compute window is still open.**

**FINDING 2 — `G7` is defined on two stations that §7.2 does not register, and
its own justification says otherwise.** §7.2 (line 432) freezes the eleven graded
stations:

> `0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95`

§7.3's `G7` row (line 455) defines stratification as
`Θ(y/H = 0.75) − Θ(y/H = 0.25)` on `x/H = 0.5`, and justifies itself with
*"a difference of two graded stations, so it is not a new measurement"*.
**Neither `0.25` nor `0.75` is in the registered list.** `G7` is therefore two
new interpolation locations, and its justification is false against §7.2. The
consequence is narrower than Finding 1 and it is stated narrowly: this is a
**grading-time** gap, not an executability failure — the cases run and complete
regardless. But §7.2's `UNMEASURED` machinery is written for *"a registered
station"* and does not cover a station that was never registered, so the
reference addendum has no registered rule for what to do if Blay tabulates no
value at `0.25` or `0.75`. **Checked with a control:** `grep` for `0.75` over the
frozen file returns lines 455, 695, 699 and 797 — the reader can plainly see the
string elsewhere in the document, so its absence from line 432 is a measurement
and not a search failure.

**FINDING 3 — `I_hi`'s perturbation is registered in `k`–`ε` variables on a
`k`–`ω` case, and no conversion is registered.** §5 (line 332) registers `I_hi`
as *"kOmegaSST, inlet `k`, `ε` × 4"*, and §3.2 (line 187) registers the inlet
pair as `k = 1.25e-3`, `ε = 5.76e-3`. **`I_hi`, `M1_*` and `B_hi` are all
`kOmegaSST` cases: they have no `epsilon` field and no `0/epsilon` boundary
condition.** Their inlet turbulence must be imposed as `k` and `omega`, and
**this document registers no `ε → ω` conversion anywhere** — checked by `grep`
across the whole file for a conversion, a `C_μ`, or an inlet `omega`, which
returned only line 332 itself, against a control showing the string `omega`
occurs three times in the file and is therefore visible to the reader. Two
consequences, both stated because neither is obvious:

- **The inlet `omega` of five of the nine cases is an unregistered free
  parameter**, chosen by whoever writes `build_k0d.py`.
- **Under the standard identity `ω = ε / (C_μ k)`, scaling `k` and `ε` by the
  same factor of four leaves `ω` EXACTLY unchanged** — `4ε / (C_μ · 4k) = ω`.
  So the registered "× 4" sweep would perturb inlet `k` by 4× and inlet `ω` by
  nothing, with inlet `ν_t = k/ω` moving 4×. That is a real perturbation and
  **not** a null one, so this is not a second unexecutable clause; but it is not
  the "four times the inlet turbulence" a reader of §5 would picture, and §11
  prediction 6 — *"`I_hi` moves `G5a` by 5–15 %"* — is a prediction about a
  perturbation the document never fully specifies. **Referred, unruled.**

**FINDING 4, minor — `phi` is depended on but not required.** §7.5's guard `HB`
computes `Q_adv` *"from the written `phi`"*, and guard `MB` reads mass
imbalance; **`phi` is not in clause 4's field list, before or after this
amendment.** Sibling `mark_done_t3.py` puts `phi` in its `NEEDED` tuple for
exactly this reason and `mark_done_t1b.py` does not — K0d inherited the `T1b`
list while registering `T3`-style guards. In practice
`buoyantBoussinesqSimpleFoam` writes `phi`, and all three completed cases
inspected in §A3.3 have it, so no case is expected to fail on this. It is an
**under-specification, not a contradiction**, and it is left unrepaired for the
same reason as Findings 2 and 3: **adding `phi` to clause 4 was not the ruling
this amendment implements, and this lane does not widen a supervisor's ruling on
its own authority** (rule 9 — an approval is only as wide as what was approved).

**CHECKED AND FOUND SOUND, recorded so it is distinguishable from unchecked.**
The `M2` cost arithmetic (`43.50 + 85.27 + 167.55 = 296.32`), the rung POINT
(`829.36`) and the CEILING (`1 654.23 + 827.11 + 3.50 = 2 484.84`) all reproduce
from §10.2 and §10.3 exactly. `AMENDMENT 1` §§A1.1–A1.4 and `AMENDMENT 2`
§§A2.1–A2.6 were re-read in full at this amendment and **nothing in either is
withdrawn or altered**.

---

## A3.7 CREDIT, and one correction to the record carried rather than dropped

**The finding is the refusing lane's and is credited to it, not to this
amendment.** `docs/campaigns/F14-cooling-ladder/K0d_PREFLIGHT_EXECUTABILITY_FINDING.md`,
committed `af7f64c7`, found it, refused to launch, refused equally to
reinterpret the frozen clause on its own authority, and referred both readings
upward. **That is the behaviour this lab wants and the record says so.**

**Its sharpest distinction is preserved here because it is the reason the abort
happened before the smoke test rather than after it.** `AMENDMENT 2`'s
pre-flight smoke test **could not have caught this defect.** The smoke test is a
**case** finding, found by **running** — it proves K0d's dictionaries suffice for
the solver to take one step. This is a **document** finding, found by
**reading**. They are different instruments aimed at different objects, and the
smoke test would have passed cleanly on a rung that then graded nothing.
**Recording that keeps `AMENDMENT 2`'s instrument from being credited with a
catch it could not have made** — and it is the second time in two amendments that
this rung has found an instrument audit reassuring about the wrong object
(§A2.2's own words: *"that reassurance does not extend to the case"*).

**And the smoke test's question remains open.** Nothing in this amendment
answers it. **It has not been run**, and this amendment does not run it.

**The correction the lane made to its own dispatch brief, carried forward.** The
brief that dispatched it stated *"THE BOX IS CURRENTLY IDLE — no solver is
running anywhere."* **That was true at the 15:28Z reading it was built on and
stale by the time it was dispatched.** The `cfd` team's `pimpleFoam`, **pid
2150855**, was running then and was re-verified live at this amendment
(`ps` at 2026-08-25T16:30Z: pid 2150855, `pimpleFoam`, 938 s elapsed).

**It does not obstruct K0d** — one rank of sixteen against §9's registered
concurrency cap of six — **and the lane was right to correct it anyway.** A
launch plan resting on a stale read is a defect independent of whether the stale
read happened to be harmless, and this rung has already recorded what that shape
of failure costs: `AMENDMENT 2` §A2.4's account of a supervisor reading "no run
directory", concluding a lane was dead, and dispatching a second launcher
**79 seconds before** the first had launched. **A stale read is an agent-dispatch
failure, not only a git-tree one**, and the guard of §9 is what stood between
that and a corrupted case.

*(Method note for the record: `pgrep -af -i k0d` at this amendment returned only
this amendment's own shell — the L-41/`pkill` self-match trap. The absence of a
K0d process is established by §A3.0's directory checks, which cannot self-match,
not by that `pgrep`.)*

---

## A3.8 WHAT THIS AMENDMENT DID NOT DO — each stated explicitly

- **No GATE moved.** §7.3's ten graded rows `G1, G2, G3, G4, G5a, G5b, G6, G7,
  G8, S1` stand as registered; §7.4's verdict ladder stands; §8.3's Roache triple
  gating stands; §8.1's planted-zero control stands.
- **No THRESHOLD and no BAND moved.** `± 1.00 K`, `± 0.0570 m/s`, `± 0.0208 m`,
  `± 0.104 m`, `± 10 % of |q_ref|`, `EXACT MATCH REQUIRED`, §7.2's conversion
  rule and its anti-widening guard — all byte-unchanged.
- **No CAP moved.** The registered **POINT of 829.36 core-min** and the
  **CEILING / TOTAL CAP of 2 484.84 core-min** stand exactly, with §10.3's stop
  rules, the 10× per-case hard stop, the 1.6× re-estimate trigger and the
  827.11 core-min continuation reserve unchanged. `cost_basis` is unchanged and
  still says the rate is **reported-by-owner, not measured**.
- **No LABEL moved**, and no verdict word outside rule 1's vocabulary is used
  anywhere in this amendment.
- **No PREDICTION moved.** §11's predictions 1–8 stand as registered, including
  `AMENDMENT 1` §A1.3's three-way disposition of prediction 3. **Prediction 2's
  naming of `M2` as the more likely non-`CONVERGING` leg is untouched** — this
  amendment makes `M2` gradeable; it says nothing about what `M2` will grade to.
- **The NINE CASES do not change**, the **CLOSURES do not change**, the mesh
  family of §4 does not change, and the `endTime` of 40 000 does not change.
- **`G6` remains `PENDING` on Blay 1992**, which is still `NOT OBTAINED`. All ten
  graded rows remain `BLOCKED` by construction under §7.4 order 4. The rung's
  tally is still **`0 of 10`**.
- **`AMENDMENT 1` and `AMENDMENT 2` stand in full.** Nothing in either is
  withdrawn, and `AMENDMENT 2`'s pre-flight smoke test remains a registered
  **abort condition on first compute**, unrun.
- **NO COMPUTE RAN.** `verification/runs/F14-cooling-ladder/K0d_runs/` does not
  exist at the moment of this write (§A3.0), and **this amendment does not create
  it**. No case directory was built, no mesh was generated, no smoke test was
  run. **Zero core-seconds.**
- **Nothing was sent** (rule 7). Submissions remain **PARKED**.

**One thing this amendment deliberately does NOT do, stated because a reader
should not have to infer it:** it does not authorise the launch. **The
supervisor must read this amendment as a diff before any compute** — an
undelegatable check under `SUPERVISION_CHARTER.md` §3 — and Findings 2 and 3 of
§A3.6 are referred and unruled while the pre-compute window is still open.

**K0d remains FROZEN, ARMED AND UNFIRED.**

*Amendment drafted by the heat-transfer lane on the supervisor's ruling,
2026-08-25. Zero compute.*

---

# AMENDMENT 4 — 2026-08-25, BEFORE FIRST COMPUTE. Version 1.3 -> 1.4.

**Lines whose number changed above this section: 0.** Nothing above is edited.
**No gate, threshold, band, cap, label or registered prediction is created,
moved, retired or weakened by this amendment.** It registers the one input that
five of the nine cases cannot be built without and that this document nowhere
determined — the inlet `omega` — and it registers the two profile stations on
which an already-frozen gate row, `G7`, is already defined. Both are additions.
Neither is a choice, because §A4.0 shows that at the moment of this write no
number this amendment could be tuned to fit exists anywhere: the reference is
`NOT OBTAINED` and no solver has run.

## A4.0 The condition under which this amendment is legal, how it was checked, and the proof that nothing above moved

Standing rule 2: *"Before first compute, amendments are legal **and must state
the condition and how it was checked** (name the run directory that does not
exist)."*

**The run directory that does not exist is
`verification/runs/F14-cooling-ladder/K0d_runs/`.** All three checks below were
run **in the same shell invocation that wrote this file**, and their output is
recorded **verbatim**:

```
$ ls -d verification/runs/F14-cooling-ladder/K0d_runs
ls: cannot access 'verification/runs/F14-cooling-ladder/K0d_runs': No such file or directory

$ find verification/runs -iname '*K0d*'
(no output)
```

**And the reader was shown able to see a match.** A `find` that reports nothing
while being incapable of reporting anything is not evidence — rule 3's
planted-zero principle applied to a search. The identical `find`, with the
pattern changed **one character** to the sibling rung that does exist:

```
$ find verification/runs -iname '*K0c*' | head -3
verification/runs/F14-cooling-ladder/K0cG_runs
verification/runs/F14-cooling-ladder/K0cR_runs
verification/runs/F14-cooling-ladder/K0cP_runs
```

**The pattern matches when there is something to match. `*K0d*` matches
nothing. K0d has never consumed a core-second, has no case directory, no mesh
and no partial output.** This control is the previous lane's invention and is
used here on its authority, not re-derived.

**The freeze was re-verified before one byte was appended.** `sha256` of
`docs/campaigns/F14-cooling-ladder/K0d_PREREGISTRATION.md` **on disk** against
its **committed blob at `HEAD`** (`23091132c4971eb94dbcdf9243559b9c3e556304`),
computed in this same invocation:

```
disk = 1861a223972c30cec10ff6bb87074519130e15061e95c477747c9143c4183966
blob = 1861a223972c30cec10ff6bb87074519130e15061e95c477747c9143c4183966
```

**Identical.** The document this amendment is appended to is the document that
was frozen, and the appended text was built onto the **`HEAD` blob**, not onto
the working-tree copy.

**THE `lines whose number changed above this section: 0` ASSERTION IS ARITHMETIC
HERE, NOT A PROMISE.** The three conditions were established mechanically in the
writing invocation, in the form `AMENDMENT 3` §A3.0 fixed:

1. **The child file was produced by CONCATENATION onto the `HEAD` blob.** The
   base was obtained with `git show HEAD:<path>`; no byte of it was read,
   modified and written back. There is no edit path by which a line above could
   move.
2. **The base is a BYTE-EXACT PREFIX of the child.** The first
   **117916** bytes of the new file were compared byte-for-byte
   against the `HEAD` blob and are identical. A single changed, inserted or
   deleted byte anywhere above this section would have failed that comparison and
   aborted the write.
3. **The commit is INSERTIONS ONLY, ZERO DELETIONS**, verified after the commit
   from `git diff HEAD~1 HEAD --numstat`. A pure append cannot renumber a
   preceding line.

**Other records cite this file by line**, and every one of those citations was
re-verified **after** this commit rather than assumed: §3.2's inlet-turbulence
row at **line 187**, §5's `I_hi` row at **line 332**, §7.2's station list at
**line 432**, §7.3's `G7` row at **line 455**, and §8.2 clause 4 at
**lines 560–562**. All still read what they read before.

**This amendment could legally alter a gate, threshold, cap or label — the
window is open. It does not, and §A4.10 says so item by item.**

---

## A4.1 THE RULING, and the order it is implemented in

The heat-transfer supervisor has ruled on the three items §A3.6 referred. **This
amendment implements that ruling and does not re-open it.** The order is not
cosmetic: **Finding 3 blocks firing and is repaired first**, because until it is
repaired five of the nine cases cannot be built at all without an unregistered
choice being made by a script author.

| §A3.6 finding | ruling | where implemented |
| --- | --- | --- |
| **Finding 3** — inlet `omega` unregistered on five kOmegaSST cases; no `ε → ω` conversion anywhere in the document | **REPAIRED. It blocks firing.** Register the conversion, name the constant, fix its value from disk, and register the resulting explicit inlet `omega` per case | §A4.2, §A4.3 |
| **Finding 3, second limb** — the `I_hi` sweep leaves `ω` unchanged under that conversion | **DISCLOSED, NOT ALTERED.** State what the perturbation IS in solver variables. Prediction 6 is not restated and not rescued | §A4.4 |
| **Finding 2** — `G7` is defined on two unregistered stations and its justification is false | **REPAIRED.** Register `0.25` and `0.75`; 11 stations become 13; strike the false justification; give the `UNMEASURED` machinery a rule for the two new stations | §A4.5, §A4.6 |
| **Finding 4** — `phi` is read by guards `HB` and `MB` and is in no completion field set | **DISCLOSED AND CARRIED, NOT REPAIRED.** It blocks nothing | §A4.7 |

---

## A4.2 FINDING 3, REPAIRED — the `ε → ω` conversion, registered, with its constant read from disk and not from memory

**Why this blocks firing, stated once so the priority is not mistaken for
drama.** §5 registers five `kOmegaSST` cases — `M1_c`, `M1_m`, `M1_f`, `B_hi`,
`I_hi`. A `kOmegaSST` case has no `epsilon` field and no `0/epsilon` boundary
condition; its inlet turbulence is imposed as `k` and `omega`. §3.2 registers
the inlet pair in `k`–`ε` variables only. **The document therefore does not
determine the inlet `omega` of five of its own nine cases**, and whoever wrote
`build_k0d.py` would have chosen it. **A pre-registration that does not
determine the run's own inputs is not a freeze**; the freeze's whole evidentiary
content is that the inputs and the gate could not have been chosen to fit the
answer, and an input chosen at build time by an unnamed author is exactly the
hole rule 2 exists to close.

**REGISTERED, 2026-08-25, BEFORE FIRST COMPUTE — the conversion rule:**

> **`omega = epsilon / (C_mu * k)`**, in SI units, `[s^-1] = [m²/s³] / ([m²/s²])`.
>
> **`C_mu` for the purpose of this conversion is `kOmegaSST`'s own `betaStar`,
> and its registered value is `0.09` — dimensionless, exact as written.**

**WHERE THAT VALUE WAS READ, on this box, at this amendment — not quoted from
memory.** OpenFOAM `api=2606, patch=0`
(`/usr/lib/openfoam/openfoam2606/META-INFO/api-info`):

| what | value | file and line, read at this amendment |
| --- | ---: | --- |
| `kOmegaSST` `betaStar`, compiled default | **0.09** | `/usr/lib/openfoam/openfoam2606/src/TurbulenceModels/turbulenceModels/Base/kOmegaSST/kOmegaSSTBase.C` **line 341**, inside the `getOrAddToDict("betaStar", …)` block opening at line 335 |
| the same value in the model's own documented coefficient set | **0.09** | `…/Base/kOmegaSST/kOmegaSSTBase.H` **line 96** (`betaStar 0.09;` in the `\verbatim` default-coefficients block) |
| the model's own `ε`/`k` relation, which is what makes `0.09` the right constant here | `epsilonByk = betaStar_*omega_()` | `…/Base/kOmegaSST/kOmegaSSTBase.C` **line 163**, declared at `…/kOmegaSSTBase.H` **line 266** with the comment *"Return epsilon/k which for standard RAS is betaStar*omega"* |
| `RNGkEpsilon` `Cmu`, compiled default | **0.0845** | `/usr/lib/openfoam/openfoam2606/src/TurbulenceModels/turbulenceModels/RAS/RNGkEpsilon/RNGkEpsilon.C` **line 108**, inside the `getOrAddToDict("Cmu", …)` block opening at line 102; the model's `nut_ = Cmu_*sqr(k_)/epsilon_` is at **line 45** |

**THE TWO VALUES ARE DIFFERENT AND THE RULING'S WORDING DID NOT ANTICIPATE THAT.
It is resolved here explicitly rather than silently.** The ruling instructed that
`C_mu` be named and its value fixed by reading *"the actual value the OpenFOAM
RNGkEpsilon/kOmegaSST models use on this box"*. **Read on this box, those are two
different numbers: `0.09` for `kOmegaSST`, `0.0845` for `RNGkEpsilon`.** The
conversion registered here is used **only** to set the inlet `omega` of the five
`kOmegaSST` cases. **`0.09` is therefore the correct constant and `0.0845` is
not**, for a reason internal to the solver rather than to taste: in the
`kOmegaSST` implementation on this box, `ε ≡ betaStar · k · ω` is not an
approximation imported from another model — it is **the model's own definition
of its dissipation**, at `kOmegaSSTBase.C:163`. Using `RNGkEpsilon`'s `0.0845`
would import the *other* closure's constant into a case that never evaluates it,
and would leave the five `kOmegaSST` inlets inconsistent with the very relation
their own solver uses.

**The size of the choice, stated so nobody has to wonder whether it mattered:**
`0.0845` would give an inlet `omega` of **54.5325 s⁻¹** against the registered
**51.2 s⁻¹**, a ratio of **1.0651** — a **6.51 %** difference in inlet `omega`
and the same in inlet `ν_t`. **It is not negligible and it is not decisive, and
it is registered rather than argued about after a number exists.**

**`RNGkEpsilon`'s `0.0845` is registered here as NOT USED, and why:** the three
`RNGkEpsilon` cases `M2_c`, `M2_m`, `M2_f` take §3.2's inlet `k` and `ε`
**directly**, in the variables §3.2 already registers them in. **They need no
conversion, and none is applied to them.** `C_lam` is laminar and takes neither.

---

## A4.3 FINDING 3, REPAIRED — the five explicit inlet `omega` values, with the arithmetic shown

**Registered inputs, from §3.2 line 187, unchanged by this amendment:**
`k = 1.25e-3 m²/s²`, `ε = 5.76e-3 m²/s³`. **`I_hi` is §5 line 332's registered
`× 4` on both**, i.e. `k = 5.00e-3 m²/s²`, `ε = 2.304e-2 m²/s³`.

**REGISTERED, 2026-08-25, BEFORE FIRST COMPUTE — the inlet `omega` of every
`kOmegaSST` case in this rung, on the inlet patch `x = 0, y ∈ [1.022, 1.040]`:**

| case | closure | inlet `k` (m²/s²) | inlet `ε` (m²/s³) | `C_mu · k` | **arithmetic** | **registered inlet `omega` (s⁻¹)** |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| `M1_c` | kOmegaSST | 1.25e-3 | 5.76e-3 | `0.09 × 1.25e-3 = 1.125e-4` | `5.76e-3 / 1.125e-4` | **51.2** |
| `M1_m` | kOmegaSST | 1.25e-3 | 5.76e-3 | `0.09 × 1.25e-3 = 1.125e-4` | `5.76e-3 / 1.125e-4` | **51.2** |
| `M1_f` | kOmegaSST | 1.25e-3 | 5.76e-3 | `0.09 × 1.25e-3 = 1.125e-4` | `5.76e-3 / 1.125e-4` | **51.2** |
| `B_hi` | kOmegaSST, floor 35.5 °C | 1.25e-3 | 5.76e-3 | `0.09 × 1.25e-3 = 1.125e-4` | `5.76e-3 / 1.125e-4` | **51.2** |
| `I_hi` | kOmegaSST, inlet `k`, `ε` × 4 | 5.00e-3 | 2.304e-2 | `0.09 × 5.00e-3 = 4.50e-4` | `2.304e-2 / 4.50e-4` | **51.2** |

**The value is exact, not rounded.** `5.76 / 1.125 = 5.12` and
`2.304 / 0.45 = 5.12`; both carry a single factor of ten and land on
**`51.2 s⁻¹` exactly**. A reader can recompute every cell from §3.2's two numbers
and the constant `0.09` without reference to any script.

**`B_hi` takes the same inlet `omega` as `M1_*`, and that is deliberate.**
`B_hi` perturbs the **floor temperature** (§3.3), nothing else; giving it a
different inlet would confound the §3.3 arbitration guard it exists to be.

**Consequences at the inlet, computed and registered so the case can be built
without a second undetermined choice:** inlet `ν_t = k / ω`.

| case | `ν_t` at inlet (m²/s) | `ν_t / ν` at `ν = 1.55e-5` | turbulence intensity `I = √(2k/3)/u_in` | turbulent length scale `ℓ = C_mu^{3/4} k^{3/2} / ε` (m) |
| --- | ---: | ---: | ---: | ---: |
| `M1_c`, `M1_m`, `M1_f`, `B_hi` | `1.25e-3 / 51.2 =` **2.4414e-5** | **1.5751** | **5.0645 %** | **1.2607e-3** |
| `I_hi` | `5.00e-3 / 51.2 =` **9.7656e-5** | **6.3004** | **10.1290 %** | **2.5215e-3** |

`C_mu^{3/4} = 0.09^{0.75} = 0.1643168`. The length scales are **1.26 mm and
2.52 mm** against the registered inlet slot height `h_in = 0.018 m` (§3.1) —
**0.0700 and 0.1401 of the slot height**, both comfortably resolved by the
coarsest level's inlet-slot span of ≥ 10 cells (§4 condition B). *This is stated
as a resolution observation, not as a gate; §4's conditions A–G are unchanged.*

**The mixed boundary-condition types are NOT registered here and are NOT being
registered by stealth.** This amendment registers the inlet **values**. §3.2's
existing outlet clause — *"zero gradient on `U`, `T` and every turbulent
variable"* — already covers `omega` at the outlet, since `omega` is a turbulent
variable of the five `kOmegaSST` cases, and no new outlet rule is created.
Wall treatment for `omega` follows §5's already-registered **wall-resolved,
`y⁺ ≤ 1`** design and is unchanged by this amendment.

---

## A4.4 FINDING 3, SECOND LIMB — DISCLOSED, NOT ALTERED: what the `I_hi` perturbation actually is

**Under the conversion registered in §A4.2, the `I_hi` sweep leaves inlet `omega`
EXACTLY unchanged.** This is arithmetic, not an estimate:

```
ω(I_hi) = 4ε / (C_mu · 4k) = ε / (C_mu · k) = ω(baseline)
        = 2.304e-2 / (0.09 × 5.00e-3) = 51.2 s⁻¹
        = 5.760e-3 / (0.09 × 1.25e-3) = 51.2 s⁻¹
```

The factor of four cancels identically. **Both rows of §A4.3's table read 51.2,
and they read it for that reason.**

**WHAT `I_hi` THEREFORE IS, in the variables the solver actually sees — stated
plainly, because a reader of §5's phrase "inlet `k`, `ε` × 4" would picture
something else:**

| quantity the solver sees at the inlet | baseline | `I_hi` | factor |
| --- | ---: | ---: | ---: |
| `k` | 1.25e-3 m²/s² | 5.00e-3 m²/s² | **× 4** |
| `omega` | 51.2 s⁻¹ | 51.2 s⁻¹ | **× 1 — UNCHANGED** |
| `ν_t = k/ω` | 2.4414e-5 m²/s | 9.7656e-5 m²/s | **× 4** |
| turbulence intensity `I` | 5.0645 % | 10.1290 % | **× 2** |
| turbulent length scale `ℓ` | 1.2607e-3 m | 2.5215e-3 m | **× 2** |

**`I_hi` is a four-fold increase in inlet turbulent kinetic energy and eddy
viscosity at an unchanged specific dissipation rate — equivalently, a doubling of
inlet turbulence intensity at a doubled inlet length scale.** It is a real
perturbation and a substantial one; it is **not** null. It is simply **not the
perturbation the phrase "× 4 on the inlet turbulence" suggests**, and this
document now says which one it is.

**§5 line 332 and §3.2 line 187 ARE NOT ALTERED.** The registered sweep remains
`k` and `ε` × 4. The disclosure changes the reader's understanding of the
perturbation, not the perturbation.

**§11 PREDICTION 6 IS NOT ALTERED, NOT RESTATED AND NOT RESCUED.** It stands
exactly as frozen:

> *"Guard `I` is the one most likely to fire. `I_hi` moves `G5a` (jet-peak
> speed) by 5–15 %. Inlet turbulence is a known sensitivity for wall jets and the
> level is not a measured quantity (§3.2)."*

**Nothing in this amendment touches its number, its band or its direction, and
this amendment offers no revised expectation to replace it.** What changes is
that the prediction is now testable against a perturbation whose composition is
**explicit** rather than one the document never fully specified. **A prediction
is allowed to fail. That is what a registered prediction is for**, and this rung
has already recorded one that did not survive contact with the records
(`AMENDMENT 1` §A1.1, the "18 combinations" figure). **If `G5a` moves less than
5 % under a perturbation that turns out to be `k` × 4 at constant `ω`, prediction
6 is WRONG, the record will say `prediction 6 FAILED` in those words, and it will
not say that the perturbation was misdescribed** — because the perturbation is
described here, before any solver has run.

**Guard `I` itself is unchanged** (§7.5): if `|G5a(I_hi) − G5a(M1_m)|` or
`|G8(I_hi) − G8(M1_m)|` exceeds its own band, rows `G5a`, `G5b` and `G8` are
**REPORTED, not graded**, with the flag *inlet turbulence unmeasured*. That
consequence is untouched.

---

## A4.5 FINDING 2, REPAIRED — the graded station list goes from ELEVEN to THIRTEEN, and `G7`'s false justification is struck

**The defect, restated in one sentence.** §7.2 (line 432) freezes eleven graded
profile stations, `0.25` and `0.75` are not among them, and §7.3's `G7` (line
455) is defined as `Θ(0.75) − Θ(0.25)` while justifying itself as *"a difference
of two graded stations"* — **a justification that is false against §7.2 as
frozen**.

Per rule 6 the frozen text above is **not edited**. Both items are **struck and
replaced here**, at the foot, and this section governs from this amendment's
commit.

**REPLACEMENT 1 — §7.2's station list.**

> ~~`0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95`~~
>
> **REPLACED, 2026-08-25, BEFORE FIRST COMPUTE. The registered graded stations
> of every profile row are THIRTEEN, in the normalised coordinate, fixed now:**
>
> **`0.05, 0.10, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.90, 0.95`**
>
> **The two additions are `0.25` and `0.75` and there are no other changes** —
> the eleven frozen stations are carried across **unchanged, in order, none
> removed and none moved**. The count in §7.2's own sentence, *"graded at eleven
> registered stations"*, reads **thirteen** from this amendment; and the phrase
> *"11 stations"* in the row column of `G1`, `G2`, `G3` and `G4` in §7.3
> (lines 448–451) reads **13 stations** for the same reason. **No band, no scale
> `S`, no relative figure `R` and no reference cell of any of those rows is
> touched.**

**REPLACEMENT 2 — `G7`'s justification sentence.**

> ~~Aisle stratification is the whole point of the spine; a difference of two
> graded stations, so it is not a new measurement~~
>
> **REPLACED, 2026-08-25, BEFORE FIRST COMPUTE:**
>
> **Aisle stratification is the whole point of the spine. `0.25` and `0.75` are
> registered graded stations of the `G1` profile under §7.2 as amended, so `G7`
> is a difference of two graded stations and is not a new measurement — and that
> is true because this amendment registered them, not because it was true when
> `G7` was written.**

**The struck sentence was false and the replacement says why it is now true.**
A justification that is repaired by making itself true is worth more than one
quietly deleted, and the strike is left visible so a reader can see which it was.

**THE `UNMEASURED` MACHINERY NOW COVERS THE TWO NEW STATIONS BY THE SAME RULE AS
THE OTHER ELEVEN, AND THE DERIVED ROW GETS THE RULE IT DID NOT HAVE.** §A3.6
named this precisely: *"the reference addendum has no registered rule for what to
do if Blay tabulates no value at `0.25` or `0.75`."* Registered now, before the
primary is held:

1. **`0.25` and `0.75` are registered stations and take §7.2's existing
   `UNMEASURED` rule verbatim, with no exception**: where the primary supplies
   no value within `± 0.01` of the station, that station is **`UNMEASURED`, is
   named, and the denominator shrinks with the missing station printed**. Nothing
   about that rule is special-cased for the two new stations — that is the point
   of registering them as stations rather than as `G7`-only interpolation
   locations.
2. **`G7` is a DERIVED row and needs its own clause, which §7.2's per-station
   rule does not supply. Registered: if EITHER `0.25` or `0.75` is `UNMEASURED`
   in the primary, `G7` is `UNMEASURED` as a row** — it is **named**, the
   station that was missing is **printed**, the graded-row denominator shrinks
   from `10` to `9` **with `G7` printed as the missing row**, and **no
   interpolated, neighbouring-station or figure-read substitute reference is
   constructed for it.** A reference value that is not in the primary is not a
   reference value (L-144).
3. **This clause cannot rescue a failure, and the reason is structural rather
   than a promise.** An `UNMEASURED` row **grades nothing**: it can never be
   counted as a `PASS`, it never enters the numerator, and §7.4's ladder already
   makes a row with no reference ungradeable at order 4. The clause can only ever
   **remove a row from the tally**, never move one from `GATE FAIL` to `PASS` —
   the same asymmetry `AMENDMENT 2` §A2.5 registered for the smoke test and
   `AMENDMENT 3` §A3.5 for the completion sets.
4. **And it cannot have been chosen to fit an answer, which is the whole reason
   it is legal to register it now.** At this write the primary is **`NOT
   OBTAINED`** (§2), the reference slot
   `verification/runs/F14-cooling-ladder/K0d_runs/K0d_reference_primary.json`
   **does not exist and neither does its parent** (§A4.0), and **no solver has
   run**. Nobody — this lane, this team, this lab — knows what Blay tabulates at
   `0.25` or `0.75`, or what `G7` would grade to either way. **That is what rule
   2's window buys, and it expires the moment the first case starts.**

---

## A4.6 THIS TIGHTENS AND CANNOT LOOSEN — shown for the station change, in a form a reader can refuse

**The claim is not asserted; it is shown, so a reader who thinks it false can
point at the cell where it fails.**

| | stations graded per profile row | rows in the gate | bands | thresholds | reference cells armed |
| --- | ---: | ---: | --- | --- | ---: |
| **before this amendment** | 11 | 10 | `± 1.00 K`, `± 0.0570 m/s`, `± 0.0208 m`, `± 0.104 m`, `± 10 % of \|q_ref\|`, `EXACT MATCH` | §7.2's conversion rule and its anti-widening guard | 0 |
| **after this amendment** | **13** | **10 — unchanged** | **byte-identical** | **byte-identical** | **0 — unchanged** |

**Read the one column that differs.** Four profile rows — `G1`, `G2`, `G3`,
`G4` — are each graded at two more locations. Under §7.2 as frozen, *"the row
PASSES only if every station with a reference value lies inside `BAND(r)`"*.
**Adding a station adds a condition that the row must also satisfy. It cannot
make a failing row pass; it can only make a passing row fail.**

**Counted, because "tighter" should be a number.** Station-level pass conditions
a compliant run must satisfy across the four profile rows:

| | pass conditions across `G1`–`G4` |
| --- | ---: |
| **as frozen** | `4 × 11 =` **44** |
| **as amended** | `4 × 13 =` **52** |

**52 against 44 — an 18 % increase — and not one condition was removed.**

**And it makes an already-registered gate row executable as written.** `G7` was
registered, frozen and gradeable-in-principle at lines 455 and in §7.4's ladder;
what it lacked was two stations at which its own definition could be evaluated
under §7.2's rules. **This amendment does not add `G7`. `G7` was already there.
It adds the two measured locations `G7` was already defined on**, which is why
the graded row count stays at **10** and the tally stays **`0 of 10`**.

**One thing this change is honestly NOT.** It is not free: the comparator now
interpolates the profile at thirteen stations rather than eleven, and the
reference addendum must look for two more values in Blay. **That is work, not
loosening**, and clause 2 of §A4.5 registers in advance what happens if the work
comes back empty.

---

## A4.7 FINDING 4 — DISCLOSED AND CARRIED, DELIBERATELY NOT REPAIRED

**`phi` is depended on by two guards and appears in no completion field set.**
§7.5's guard `HB` computes `Q_adv` *"from the written `phi`"* over inlet and
outlet; guard `MB` reads mass imbalance across the same patches. **`phi` is in
none of the three per-closure completion field sets registered by `AMENDMENT 3`
§A3.4, and it was in none of clause 4's enumeration before that amendment
either.**

**It is recorded here as DISCLOSED AND CARRIED, and the reason it is not repaired
is stated rather than left to inference:**

- **It is an under-specification, not a contradiction.** `AMENDMENT 3`'s
  Finding 1 was a clause **no run of the `RNGkEpsilon` closure could ever
  satisfy** — a guaranteed refusal of three of nine cases, and therefore of the
  whole rung's 829.36 core-min. **This is the opposite shape**: a field the
  guards need, that the completion rule does not demand, on a solver that writes
  it anyway.
- **It blocks nothing.** `buoyantBoussinesqSimpleFoam` writes `phi`, and
  `AMENDMENT 3` §A3.3 inspected completed sibling cases on disk and found `phi`
  present in all of them. **No case is expected to fail on this**, and no case is
  prevented from running, completing or being graded by it.
- **The failure mode if the disclosure is wrong is visible, not silent.** If a
  case somehow completed without `phi`, guards `HB` and `MB` would fail to read
  it and the failure would surface **at guard evaluation with a named missing
  file**, not as a wrong number. **A guard that cannot run is not a guard that
  passes.**
- **And repairing it was not the ruling.** The supervisor ruled Finding 4
  **disclosed, not repaired**. Widening a supervisor's ruling on a lane's own
  authority is rule 9's permission laundering in its quietest form — *an approval
  is only as wide as what was approved* — and the correct move is to say so and
  leave it, which is what `AMENDMENT 3` §A3.6 did and what this amendment does
  again.

**It remains available for repair in any later pre-compute window, and there is
none after first compute.** If the supervisor wants `phi` in the completion sets,
**it must be ruled before the first case starts**, and this sentence is the
notice that the window is the same one this amendment is using.

---

## A4.8 THE SUPERVISOR'S OWN ERROR, RECORDED — and credit to the lane that caught it

**This is recorded at the supervisor's own instruction and is not softened.**

**The error.** The supervisor's `AMENDMENT 3` brief restated the `C_lam`
exemption as *"exempt from `nut` and from the second turbulence field"*. **Clause
4 as frozen exempts `C_lam` from `nut k omega` — ALL THREE FIELDS**, `k`
included:

> **4.** **`T U p_rgh alphat nut k omega` all present** at `endTime` (`C_lam` is
> exempt from **`nut k omega`** and that exemption is registered here, not
> discovered later)

**What the supervisor's narrower wording would have done.** Under *"exempt from
`nut` and from the second turbulence field"*, **`k` would have remained REQUIRED
of a laminar case.** A laminar OpenFOAM case does not solve a `k` equation and
does not write a `k` field. **`verification/runs/F14-cooling-ladder/K0cS_runs/C1_laminar`
on disk writes no `k` and no `nut`.**

**So the supervisor's own wording would have RECREATED, ON `C_lam`, THE EXACT
DEFECT `AMENDMENT 3` WAS WRITTEN TO REPAIR** — a completion clause that no run of
that closure could satisfy, guaranteeing an exit-2 refusal and taking the rung's
`DONE` markers from nine obtainable back to eight. `AMENDMENT 3` §A3.5's own
table would have read `C_lam: satisfiable after — NO`, and the amendment
celebrating **60 checkable assertions and zero unsatisfiable ones** would have
shipped with one.

**What the lane did, and it is the correct behaviour.** The drafting lane
**noticed the discrepancy between the brief and the frozen clause**, **carried
clause 4's three-field exemption verbatim into `AMENDMENT 3` §A3.4's laminar
row** — which reads *"exempt from `nut`, from `k` **and** from the second
turbulence field, which is exactly the exemption clause 4 already registered,
carried across unchanged and no wider"* — and **flagged the discrepancy upward
rather than silently fixing it**.

**All three parts of that are the behaviour this lab wants, and the record says
so explicitly:**

1. **It read the frozen text rather than the brief describing it.** A brief is a
   summary; the frozen clause is the instrument. Where they differ, the
   instrument governs.
2. **It did not widen and it did not narrow.** It carried the exemption *"no
   wider"*, in those words, which is rule 9 applied in the direction people
   forget — an approval is only as wide as what was approved, and a **restatement
   is not a re-authorisation** either.
3. **It flagged rather than silently corrected.** A silent fix would have left
   the supervisor believing the brief was right, and the next brief would have
   carried the same error into a rung with no lane paying attention.

**THE ERROR WAS THE SUPERVISOR'S.** Not the lane's, not the frozen document's,
and not a matter of interpretation: clause 4 names three fields and the brief
named two. **It is recorded here in the pre-registration itself, where it cannot
be lost with a session**, and it is the second consecutive amendment in which the
instrument that caught a defect was **a lane reading a frozen document**
(`AMENDMENT 3` §A3.7: *"This is a document finding, found by reading"*).

**The general lesson this rung has now paid for twice, stated once:** a
supervisor's restatement of a frozen clause is **evidence about the supervisor's
reading, not about the clause**. `SUPERVISION_CHARTER.md` §3's undelegatable
checks exist because a relayed check is a summary; **this is the same failure
running in the other direction — a relayed clause is also a summary**, and a lane
that takes its brief's paraphrase as the text will implement the paraphrase.

---

## A4.9 CHECKED AND FOUND — four items the ruling did not anticipate, DISCLOSED HERE, NOT REPAIRED HERE

Recorded under the practice `AMENDMENT 1` §A1.4 established and `AMENDMENT 3`
§A3.6 continued: **a check that finds something must be recorded, and a check
that finds nothing must be distinguishable from a check never made.** None of
the four below is repaired by this amendment — repairing them was not the ruling,
and rule 9 forbids a lane widening a ruling on its own authority — and all four
are referred while the pre-compute window is still open.

**FINDING 5 — `C_mu` is not one number on this box, and the ruling's wording
assumed it was.** Resolved inside §A4.2 rather than left dangling:
`kOmegaSST`'s `betaStar` is **0.09** and `RNGkEpsilon`'s `Cmu` is **0.0845**, and
they differ by **6.51 %** in the resulting inlet `omega`. §A4.2 registers `0.09`,
because the conversion is applied only to the five `kOmegaSST` cases and `0.09`
is the constant those cases' own solver uses in its own `ε ≡ betaStar·k·ω`
relation (`kOmegaSSTBase.C:163`). **Recorded as a finding, not buried as a
detail**, because a reader of the ruling would expect one constant and the box
has two.

**FINDING 6 — §7.3's pointer to the reference-arming addendum names the wrong
section.** Line 444 reads *"Every cell in it is filled by the dated addendum of
§12, and by nothing else."* **§12 is `The registered alternative: what this rung
does if a case will not converge`** — it says nothing about arming a reference.
The reference-arming addendum is specified at **§7.6** (the reference slot and
its schema) and **§14 step 3** (*"Append the dated reference addendum at the foot
of this file"*). **Checked with a control:** `§12` occurs at lines **444, 877 and
935**; the occurrences at 877 and 935 are correct references to the convergence
alternative, so the reader can plainly see the string used correctly elsewhere
and **line 444's mis-target is a reading, not a search failure.** The consequence
is narrow and stated narrowly: it is a **cross-reference defect, not a
substantive one** — §7.3's binding content (*the reference column is UNARMED, and
only a dated addendum fills it*) is unambiguous, §7.6 and §14 both supply the
procedure, and **no gate, band or threshold depends on which section number the
sentence names.** Referred, unrepaired.

**FINDING 7 — `build_k0d.py`, which §9 registers as the thing that writes the
nine cases, DOES NOT EXIST ON DISK.** §9: *"`build_k0d.py` writes the nine cases;
it does not run and nothing in this commit runs it."* **Checked at this
amendment:** `find` for `build_k0d.py` across the repository returns **nothing**,
against two controls that establish the finder works — the same `find` for
`compute_reference_metrics.py` returns
`./docs/campaigns/F14-cooling-ladder/compute_reference_metrics.py`, and the
pattern `build_*.py` returns five existing scripts. **The script has never been
written.** This is not a defect in the pre-registration — §9 registers what the
builder must do, not that it exists today, and §9's own tooling disclosure says
so — but it has a consequence that is registered here so it cannot be discovered
later: **the dictionaries written for `AMENDMENT 2`'s smoke test are the first
K0d dictionaries to exist anywhere.** Registered: **they are drafts in scratch,
they are NOT the graded case, and the graded run is built by `build_k0d.py` under
§9 with the inlet `omega` of §A4.3** — the smoke test establishes that a
dictionary set of this shape takes a step, and §A2.4 clause 4 already forbids it
being cited for anything else.

**FINDING 8, minor — §3.2 registers no inlet condition for `nut` or `alphat`.**
Both are derived fields that OpenFOAM computes rather than reads as physics, and
`alphat` is fixed by `Pr_t = 0.85` (§3.2, *never tuned*) while `nut` follows from
`k` and `omega` — §A4.3 registers the resulting inlet `ν_t` of every `kOmegaSST`
case explicitly, so the value is now determined by this document rather than by a
build script. **It is an under-specification of a derived field, not of a
physical input, and it blocks nothing.** Recorded for completeness.

**CHECKED AND FOUND SOUND, recorded so it is distinguishable from unchecked.**
§9's tooling disclosure — *"no smoke test, no pilot, no scratch solve and no case
directory was created for this rung, before or during this commit"* — **was true
at the freeze and remains true of that commit.** `AMENDMENT 2` §A2.4 registered a
smoke test afterwards, and running it now **does not contradict §9**, which
speaks about the state at the freeze; the distinction is stated here so no reader
has to resolve it themselves. The rung POINT (`829.36`) and CEILING
(`1 654.23 + 827.11 + 3.50 = 2 484.84`) were re-derived from §10.2 and §10.3 and
reproduce exactly. `AMENDMENT 1` §§A1.1–A1.5, `AMENDMENT 2` §§A2.1–A2.6 and
`AMENDMENT 3` §§A3.0–A3.8 were re-read in full at this amendment and **nothing in
any of them is withdrawn or altered.**

---

## A4.10 WHAT THIS AMENDMENT DID NOT DO — each stated explicitly

- **No GATE moved.** §7.3's ten graded rows `G1, G2, G3, G4, G5a, G5b, G6, G7,
  G8, S1` stand as registered — **ten before, ten after**; §7.4's verdict ladder
  stands; §8.3's Roache triple gating stands; §8.1's planted-zero control stands;
  §7.5's five guards `HB`, `B`, `I`, `DC`, `MB` stand with their consequences
  unchanged.
- **No THRESHOLD and no BAND moved.** `± 1.00 K`, `± 0.0570 m/s`, `± 0.0208 m`,
  `± 0.104 m`, `± 10 % of |q_ref|`, `EXACT MATCH REQUIRED`, §7.2's conversion
  rule and its anti-widening guard, the `0.5 %` heat-balance tolerance, the
  `25 %` discrimination threshold, the `y⁺` windows `≤ 5.0` and `≤ 3.3` — all
  **byte-unchanged**. The station list grew; **no band it is graded against
  did**.
- **No CAP moved.** The registered **POINT of 829.36 core-min** and the
  **CEILING / TOTAL CAP of 2 484.84 core-min** stand exactly, with §10.3's stop
  rules, the 10× per-case hard stop, the 1.6× re-estimate trigger and the
  **827.11 core-min** continuation reserve unchanged. `cost_basis` is unchanged
  and still says the rate is **reported-by-owner, not measured**
  (`COMPUTE_BUDGET_CHARTER.md` §5).
- **No LABEL moved**, and no verdict word outside rule 1's vocabulary is used
  anywhere in this amendment.
- **No PREDICTION moved.** §11's predictions 1–8 stand as registered.
  **Prediction 6 in particular is untouched** — §A4.4 discloses the composition
  of the perturbation it predicts about and offers **no** revised number,
  direction or excuse.
- **The NINE CASES do not change**, the **THREE CLOSURES do not change**
  (`kOmegaSST` × 5, `RNGkEpsilon` × 3, laminar × 1), the mesh family of §4 does
  not change, the `endTime` of **40 000** does not change, and §6's convergence
  criterion does not change.
- **`G6` remains `PENDING` on Blay 1992**, which is still **`NOT OBTAINED`**. All
  ten graded rows remain `BLOCKED` by construction under §7.4 order 4. The rung's
  tally is still **`0 of 10`**.
- **`AMENDMENT 1`, `AMENDMENT 2` and `AMENDMENT 3` stand in full.** Nothing in
  any of them is withdrawn. `AMENDMENT 3` §A3.4's per-closure completion field
  sets are untouched by this amendment, including the laminar row's three-field
  exemption discussed in §A4.8.
- **`AMENDMENT 2`'s pre-flight smoke test remains a registered ABORT CONDITION on
  first compute**, and this amendment does not modify it. **It is run
  immediately after this commit, in scratch outside `verification/runs/`, under
  §A2.4's four registered conditions**, and its result is recorded separately.
- **NO GRADED COMPUTE RAN AT THIS AMENDMENT.**
  `verification/runs/F14-cooling-ladder/K0d_runs/` does not exist at the moment
  of this write (§A4.0), and **this amendment does not create it**. No case
  directory was built under `verification/`, no mesh was generated there, and no
  graded solver was launched. **Zero graded core-seconds.**
- **Nothing was sent** (rule 7). Submissions remain **PARKED**.

**One thing this amendment deliberately does NOT do, stated because a reader
should not have to infer it:** **it does not authorise the launch.** **The
supervisor must read this amendment as a diff before any graded compute** — an
undelegatable check under `SUPERVISION_CHARTER.md` §3 — and the smoke test that
follows it proves **one narrow thing** and may not be cited for physics, mesh,
convergence or any graded quantity.

**K0d remains FROZEN, ARMED AND UNFIRED.**

*Amendment drafted by the heat-transfer lane on the supervisor's ruling,
2026-08-25. Zero graded compute.*
