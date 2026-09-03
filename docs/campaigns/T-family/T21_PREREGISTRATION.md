# T21 — steady 1-D cylindrical conduction through the motor housing wall, flow OFF, EXACT tier: pre-registration

> **STATUS: DRAFT. NOT FROZEN. NOT COMMITTED. AUTHORISES NOTHING.**
> Drafting was **stopped mid-document on the supervisor's instruction**
> (2026-08-31) after Sanaa ruled **feasibility-first**: no freeze is required for
> a feasibility or physics rung, and Case 3's first act is therefore the
> variant-(b) L1 build, not this gate. **This file is preserved in place because
> every number in it was derived and every source claim in it was checked against
> the installed tree; it is intended to become the gated rung's registration
> later.** Nothing below is binding until a supervisor freezes it by commit.
>
> **All sections are now written** — §8 (run set), §9 (selftest spec) and §10
> (omissions) were completed after the initial stop. No verdict from the fixed
> vocabulary is asserted anywhere in this file.
>
> **COST RECONCILIATION — APPLIED, NOT OUTSTANDING.** The draft carried a POINT
> of **8.6 core-min** written before §8 itemised the run set. §8.4 derives
> **9.1901**, and **all three operative sites now read 9.1901**: §1 line 8, §7.2's
> core-minute figure, and §7.2's USD (which was `8.6/60 × $0.0513 = $0.00735` and
> is now `9.1901/60 × $0.0513 = **$0.00786**` — *a derived number inherits its
> input's staleness, which is this lab's own compound-number rule applied to its
> own document*). **CAP is unchanged at 20.0 core-min, hard, = 2.18 × POINT.**
> The remaining mentions of 8.6 in this file are **disclosure notes recording
> that history**, not live figures; §8.4 keeps the account of how the discrepancy
> arose, and that record is meant to survive the freeze.

Verdict vocabulary fixed by `CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE
FAIL / NOT A RESULT / BLOCKED / PENDING.** No other word appears as a verdict here.

---

## 0. WHAT THIS RUNG IS, AND WHY THE ID IS `T21`

### 0.1 What it is

The **V exact tier of Sanaa's CASE 3** (motor-in-duct conjugate heat transfer,
directive `etc/sessions/2026-08-30T2300Z_sanaa_four_new_case_families.md` §3.6,
first bullet, limb (a) and limb (b)): the **flow is OFF**, there is **no fluid
region**, the housing's outer surface is a fixed-temperature boundary, and the
radial temperature drop across the aluminium housing wall is compared against the
closed-form 1-D cylindrical-conduction solution. Limb (b) — the planted +10 %
source — is the balance instrument's positive control and **runs before any
gated point**.

### 0.2 What it is NOT — stated first

> **T21 earns `V` for STEADY RADIAL CONDUCTION IN A SOLID WITH A VOLUMETRIC
> SOURCE AND A REGION-COUPLED INTERFACE, and for NOTHING conjugate.** It earns
> nothing about the annulus flow, nothing about `kOmegaSST`, nothing about a
> heat-transfer coefficient, nothing about the Nusselt correlation tier, and
> nothing about the 16-point P_loss × U_inf map. Those are separate rungs with
> separate registrations and this document may not be cited as covering them.

**No cross-team dependency, and it must not acquire one.** `CASE3-DEP-1` (cfd's
Case 2 centerbody) is PENDING and gates the correlation tier and the Roache
triple of the *map*. **None of that is in this rung**: flow off, no fluid, no
turbulence model, no correlation.

### 0.3 The filing decision — id and folder, with the reasoning

The brief proposed `docs/campaigns/F14-cooling-ladder/`-shaped `K3a` inside
`docs/campaigns/T-family/` and asked that it be checked rather than accepted.
**Both halves are wrong, for the reasons T20 recorded when the same proposal was
made to it** (`T20_PREREGISTRATION.md` §0.3).

**`K3a` is rejected.** `K*` is the rung prefix of campaign **F14**, the
DC-cooling ladder. `docs/campaigns/F14-cooling-ladder/` holds `K0b`, `K0c`,
`K0cG`, `K0cP`, `K0cQ`, `K0cR`, `K0cS`, `K0cT`, `K0cX`, `K0d`, `K0e`, `K0f`,
`K1`, `K2a`, `K2b`, `K2c`, `K2e`, `KV1` — a live campaign whose own numbering
reaches `K2` and will reach `K3`. Filing a motor-housing rung as `K3a` in the
T-family folder puts an F14-shaped id in a T-family directory **and reserves
F14's own next number**. Rejected on both counts.

**`docs/campaigns/T-family/` is the folder, and the number is the next free
top-level `T`.** `FILING_CHARTER.md` §5: *find the nearest existing sibling and
copy its pattern.* The nearest sibling is exact — **T20**, which is Case 4's
EXACT-tier solid-conduction control, registered three days ago in this folder,
solid-only, analytic referent, `chtMultiRegionFoam` family, planted-zero control,
no fluid region. T21 is the same shape for Case 3. T20 §0.3 states the family's
governing practice in terms that read directly onto this rung: *"a new
transient-conduction subject takes the next free top-level `T` number and carries
its lineage in the title, in one folder, so that `T_FAMILY_INDEX.md` — the
register that classifies every rung as EXACT / FORMULA / ACQUIRE — can see it. A
rung filed outside that folder is a rung the tier register cannot classify."*
This rung is **steady** rather than transient, which is a difference of subject
and not of filing.

**The number is 21, taken from the MAXIMUM and never from a count**
(`CLAUDE.md` rule 11 by analogy). Re-derived over
`docs/campaigns/T-family/` ∪ `verification/runs/T-family/`, the maximum existing
`T`-number is **20**; the set present is
{1,3,4,5,6,8,9,10,11,13,14,15,16,17,18,19,20} — **seventeen ids with a maximum of
20, which is exactly why a count is not the rule**. **This derivation is
UNCOMMITTED and must be re-taken in the committing invocation**, in the same
shell invocation as the write; peers take numbers constantly.

**No sub-letter.** `T1b`, `T9aD`, `T10aR` are follow-on *arms of an existing
rung*; a new subject with its own registration takes a plain number.

`scripts/check_filing.py` accepts `T21_PREREGISTRATION.md` under
`docs/campaigns/T-family/`: the basename matches `CAMPAIGN_RECORD_MD`
= `^[A-Z][A-Za-z0-9]*(_[A-Z0-9][A-Z0-9_-]*)?\.md$` (`T21` + `_PREREGISTRATION`).
Run root **`verification/runs/T-family/T21_runs/`** per R6.

**Recorded, not decided by this lane:** whether the *rest* of Case 3 — the
16-point map, the correlation tier, the map's Roache triple — opens its own
campaign folder is a structural question for the supervisor and ultimately
Sanaa. It does not touch T21, which contains no duct, no annulus and no flow.

---

## 1. THE TEMPLATE — the ten registered lines

Sanaa's 10-line form (`docs/LAB_STATE.md:653-655`: *case, reference, quantities,
bands, ladder, decomposition seed, criteria*), plus the cost line rule 12 makes
non-optional and the ABSENT registry rule 2 requires.

**1. CASE.** Solid-only steady conduction. **Two solid regions, zero fluid
regions**: `core` (representative winding/lamination material, ρ 7000, c_p 450,
k 40 W/mK, directive §3.2) carrying a uniform volumetric source, and `housing`
(aluminium, ρ 2700, c_p 900, k 167 W/mK, directive §3.3) as a hollow cylinder
r_i = 0.0335 m → r_o = 0.0375 m, L = 0.125 m. **2-D axisymmetric wedge**,
θ = 5.0°, one cell circumferentially. **The nose and tail cones of directive
§3.2 are REMOVED** — see §2.3. Solver **`chtMultiRegionSimpleFoam`**, OpenFOAM
**v2606** (`api=2606`, `patch=0`, read from
`/usr/lib/openfoam/openfoam2606/META-INFO/api-info`), `regionProperties`
= `fluid ()` / `solid (core housing)`. Run root
`verification/runs/T-family/T21_runs/`.

**2. REFERENCE.** The closed-form steady radial-conduction solution for a
cylindrical shell, **derived in this document (§3) and re-derived independently
in the comparator, never transcribed**. No paper is required and none is cited as
a source of constants. Precedent: T20 §1 line 2, `exact_t18.py`, `exact_t9a.py`.

**3. QUANTITIES.**

| id | quantity | read from |
|---|---|---|
| **Q1** | `dT_wall` = areaAvg(T on `housing_to_core`) − areaAvg(T on `housing_outer`) | `boundaryField` of `<endTime>/housing/T` |
| **Q2** | `dT_cells` = T at the innermost housing cell ring − T at the outermost ring | `internalField` of `<endTime>/housing/T` |
| **Q3** | heat-balance ratio `B` = (power leaving `housing_outer`) / (registered source power) | `wallHeatFlux` functionObject output, housing region |

Q1 and Q2 are **two readers of the same solution on different code paths with
different, pre-derived geometric extents** (§4.4) — the anti-degeneracy control
T20 §4.4 established. Q1 is the **gated** reader; Q2 is gated on its own referent
and its residual **must differ** from Q1's.

**4. BANDS.** All bands are **1 % of the ANALYTIC DROP**, in Kelvin, and the
Kelvin figure is quoted beside the percentage because a percentage of a small
drop is a small absolute number the reader must see:

| P_full (W) | analytic `dT_wall` (K) | **band ±K** | **band ±mK** |
|---:|---:|---:|---:|
| **100 (binding)** | 0.0859974153 | 8.59974e-04 | **±0.8600** |
| 300 | 0.257992246 | 2.57992e-03 | ±2.5799 |
| 600 | 0.515984492 | 5.15984e-03 | ±5.1598 |
| 1000 | 0.859974153 | 8.59974e-03 | ±8.5997 |

**P = 100 W is registered as the binding point**: it has the tightest absolute
band and therefore the least margin against every instrument term. Additional
frozen bands: observed order **p ∈ [1.6, 2.4]**; **GCI_fine < 0.05 %** of
`dT_wall`; wedge-angle invariance per §5.3; unplanted balance **|B − 1| ≤ 0.01**;
planted balance **B_planted − B_unplanted ∈ [0.095, 0.105]**.

**5. LADDER.** Spatial, uniform refinement **r = 2** in both mesh directions:
housing radial 8/16/32 cells, core radial 24/48/96, axial 20/40/80. Roache
classification at **F_s = 1.25** per `CLAUDE.md` rule 5, floors **imported** from
`scripts/roache_triple.py` (`STAGNANT_FLOOR`, `P_MIN`, `FS`, `PLANT`), never
redefined in the comparator — `analyse_t18.py:43` is the pattern.

**6. DECOMPOSITION SEED.** **Serial, 1 rank.** `numberOfSubdomains 1`, no
`decomposeParDict`, `decomposePar` not run, the solver invoked directly and not
through `mpirun`. There is no partitioner, therefore no seed. `ranks = 1` is the
multiplier in every core-minute figure in §7.

**7. CRITERIA.** In this order, and the order is one-way:
(i) **strict completion** (rule 4, steady form, §6) — any case failing any
conjunct gets no marker and the rung is **NOT A RESULT**, the comparator refusing
to grade a partial rung;
(ii) **instrument admission** — the planted-zero control (§5.4) must PASS on
every reader; a refusal is `exit 2`, never a degraded grade; **and the V(b)
planted-source arm must have run and passed BEFORE any gated point is graded**;
(iii) **triple classification** (rule 5) — non-`CONVERGING` ⇒ **NOT A RESULT**
whatever the value says;
(iv) **band** — inside ⇒ PASS, outside ⇒ GATE FAIL, GCI printed beside every row.
No verdict is assigned by this document.

**8. COST.** POINT **9.1901 core-min**, CAP **20.0 core-min** (hard; an overrun
**stops the run** and does not get a new budget) **= 2.18 × POINT**. USD
**$0.00786 point / $0.01710 cap, DERIVED NOT MEASURED**. See §7 for the model and
§8.4 for the per-case itemisation — the rate is **EXTRAPOLATED**, not derived,
and `t_overhead` is **ASSUMED**.

> *This line read **8.6 core-min** in the draft written before §8 itemised the
> run set. It was reconciled to §8.4's derived **9.1901** while the document was
> **unfrozen**, which is the only time such a change is legal; §8.4 keeps the
> record of the discrepancy and how it arose. **CAP is unchanged.***

**9. ABSENT REGISTRY.** `verification/runs/T-family/T21_runs/` and every
registered case directory must be measured **ABSENT under a live planted
control** in the committing invocation. **Not taken here** — this draft is not
the committing invocation and a reading taken now is not transferable.

**10. AUTHORISATION.** This document authorises **no solve**, and in its present
DRAFT state it is not even a candidate for one.

---

## 2. THE CEILING, THE SCOPE LIMITS, AND WHAT WAS CORRECTED IN THE BRIEF

### 2.1 THE CEILING, REGISTERED BEFORE COMPUTE

**An exact analytic referent scores `V` and never `P`.** Under the upheld V/P
ruling this rung can reach **`GATE REACHED` at best and can NEVER reach
`HOLDS`.** `analyse_t18.py`'s own docstring states this for its rung and it is
stated here for the same reason: *the ceiling is registered before compute so
that no later reading of the result can raise it.*

### 2.2 What the brief got right — verified, not accepted

Every scoping figure handed to this lane **reproduces exactly**:

| quantity | brief | this lane, recomputed | agree |
|---|---|---|---|
| `r_o` | 0.0375 m | 0.0375 m (= 0.3 × 0.25 / 2) | yes |
| `r_i` | 0.0335 m | 0.0335 m (= r_o − 0.004) | yes |
| `L` | 0.125 m | 0.125 m (= 0.5 × 0.25) | yes |
| `ln(r_o/r_i)` | 0.11279549 | **0.112795494145** | yes |
| `2 π k L` | 131.16149 W/K | **131.161493287 W/K** | yes |
| `dT` per watt | 8.599742e-04 K/W | **8.59974153376e-04 K/W** | yes |
| `V_core` (full cylinder) | 4.407065e-04 m³ | **4.40706544436e-04 m³** | yes |
| `dT` at 100/300/600/1000 W | 0.085997/0.257992/0.515984/0.859974 K | identical to 9 s.f. | yes |
| wedge chord-vs-arc bias | +0.032 % | **+0.031738 %** at θ = 5° | yes |

All figures **[DERIVED]**, unit K, W, m as stated, referent: the geometry of
directive §3.2 and k = 167 W/mK of §3.3, which are **[REGISTERED-by-owner]** and
flagged by Sanaa herself as to-be-checked.

`V_core` is **not load-bearing** and is recorded as informational only: under
`volumeMode absolute` (§3.3) OpenFOAM divides by the volume **it** measured, so
no hand-computed volume enters the case.

### 2.3 THE NOSE AND TAIL CONES ARE REMOVED — a declared scope limit

Directive §3.2 closes the housing with solid cones of the same aluminium. **They
are removed for this rung and the removal is declared, not silent.** A cone is a
**second conduction path**: with the cones present, part of the source power
leaves the core axially through the cones instead of radially through the wall,
`dT_wall` is no longer `P ln(r_o/r_i)/(2πkL)`, and the referent this rung exists
to test would be **wrong by an unmodelled amount**. With the cones removed and
the axial end planes adiabatic, the geometry's exact solution **is** the 1-D
radial solution — not an approximation of it. This is the same move T20 §3.3
made ("geometric exactness"). **Case 3's map rungs must restore the cones and
may not cite T21 as having verified anything about them.**

### 2.4 THE `writePrecision` TRAP — the band is smaller than the default file quantum

**REGISTERED: `writeFormat ascii`, `writePrecision 12`, `writeCompression off`,
`timePrecision 12`.** The reason is in the document, not in a comment:

OpenFOAM's default `writePrecision` is **6 significant figures**. At T ≈ 288 K
that leaves three decimals — a write quantum of **exactly 1.0 mK**. The binding
band at P = 100 W is **±0.8600 mK**. **The quantum is 116 % of the entire band:
the gate fails on file-format round-off before any physics is wrong.**

**And averaging does not rescue it here, which is the part that is easy to get
wrong.** One might expect a patch-face average over many faces to average the
quantisation away. **It cannot**, because the solution is **exactly uniform on
each cylindrical patch by construction** — every face on `housing_to_core` holds
the same value and therefore rounds the same way. The quantisation error is
**fully correlated across the patch and does not cancel at all.** Worst case on
the difference of two patch averages is ±1.0 mK = **116 % of the band**.

At `writePrecision 12` the quantum is ≈ 1e-9 K, i.e. **≈ 1e-6 of the band**, and
contributes nothing. The lab currently avoids this **by luck rather than by
rule** — `verification/runs/T-family/T5_runs/T5_CUBE_m/system/controlDict:20`
reads `writePrecision 10` with no recorded reason — and T20 §4.4 hit the
identical trap independently and registered 12. **Two rungs in one week is a
pattern, and the general form — every registration whose band is expressible in
absolute units must state the write quantum beside the band in the same units,
and register a precision that puts the quantum at least 100× below it — is
offered upward to verification and is NOT ruled here.**

---

## 3. THE HEAT SOURCE — three defects in the directive's spec, all reproduced

Directive §3.3 states: *"fvOptions scalarSemiImplicitSource on cellZone core in
the solid energy equation, injectionRate = P_loss / V_core (W/m^3)."*
**All three of the brief's charges against that sentence are confirmed against
the installed tree. Every citation below was read at source, not recalled.**

### 3.1 The solid energy equation is in ENTHALPY `h`, not `T` — CONFIRMED, with one correction

`/usr/lib/openfoam/openfoam2606/applications/solvers/heatTransfer/chtMultiRegionFoam/chtMultiRegionSimpleFoam/solid/solveSolid.H`
**lines 4-9**:

```
        fvScalarMatrix hEqn
        (
            -thermo.heatDiffusion(betav, h)
          ==
            fvOptions(rho, h)
        );
```

The variable is `h`. An `fvOptions` entry naming `T` is never matched to this
equation and is **never applied**; the solver converges cleanly to a
uniform-temperature solid. **This is a zero source that looks like a converged
run, and it is exactly what `CLAUDE.md` rule 3 exists for.** The trap named in
the brief is real:
`/home/ubuntu/Certonomous/verification/runs/THERMAL_K0_runs/K0a_heated_box_source/constant/fvOptions:31`
reads `T (4.275222401e-06 0);` — **correctly**, because that case runs a
kinematic-`T` solver and its own header (`:19-21`) says so. Transplanted into a
solid region it reproduces the silent zero.

**CORRECTION AGAINST THE BRIEF, recorded rather than absorbed: it is not
literally silent — but the warning is worth almost nothing, and the correction
buys a real check.**
`/usr/lib/openfoam/openfoam2606/src/finiteVolume/cfdTools/general/fvOptions/fvOption.C:134-146`:

```
void Foam::fv::option::checkApplied() const
{
    forAll(applied_, i)
    {
        if (!applied_[i])
        {
            WarningInFunction
                << "Source " << name_ << " defined for field "
                << fieldNames_[i] << " but never used" << endl;
```

so OpenFOAM **does** emit `Source <name> defined for field T but never used`.
**But it fires exactly once**, at
`fvOptionList.C:72` — `if (mesh_.time().timeIndex() == checkTimeIndex_)`, with
`checkTimeIndex_ = startTimeIndex + 2` (`:88`). In a 5 000-iteration log that is
**one non-fatal line near the top**, invisible to any reader who greps the tail,
and it does not stop the run. **The hazard is unchanged. What changes is that a
cheap positive check now exists, and it is registered:**

> **REGISTERED: the comparator greps `log.solve` for the string
> `but never used` and REFUSES (exit 2) if it appears in any region's output.**
> This is an *addition* to the planted-zero control and replaces nothing — a
> warning that fires at one iteration is not an instrument.

### 3.2 The key `injectionRate` DOES NOT EXIST at v2606 — CONFIRMED

`/usr/lib/openfoam/openfoam2606/src/fvOptions/sources/general/semiImplicitSource/SemiImplicitSource.H`
accepts exactly two spellings, and `injectionRate` is neither:
- the **2206-and-newer** form, `sources { <field> (Su Sp); }` (`:59-83`);
- the **legacy 2112-and-older** form, `injectionRateSuSp { … }` (`:86-104`).

`grep -rn injectionRate src/fvOptions/` returns **four hits, all
`injectionRateSuSp`** (`SemiImplicitSource.H:86,118,219`,
`SemiImplicitSource.C:544`). **`injectionRate` appears nowhere.**
**REGISTERED: the `sources` form.**

### 3.3 `volumeMode` is MANDATORY and decides the units — CONFIRMED, and `absolute` is registered

`SemiImplicitSource.C:534` (inside `read()`):

```
        volumeMode_ = volumeModeTypeNames_.get("volumeMode", coeffs_);
```

`get` on a missing key is a **fatal dictionary read error**, so omitting
`volumeMode` kills the run — loudly, which is the benign failure. The
**dangerous** failure is the wrong value: `:537-540`,

```
        if (volumeMode_ == vmAbsolute)
        {
            VDash_ = V_;
        }
```

with `VDash_` initialised to 1 and every source value divided by it
(`:500`, `:516`). So `specific` means W/m³ and `absolute` means the entered value
is **divided by the measured zone volume**. Choosing the wrong one is a **silent
scale error by exactly the zone volume**.

**REGISTERED: `volumeMode absolute`, `selectionMode all`, in the `core` region's
own `constant/core/fvOptions`, with `sources { h (P_sector 0); }`.** Four reasons,
each checked:

1. **The value enters in watts**, so no hand-computed volume appears anywhere in
   the case, and the one number a human types is the one physical quantity the
   directive specifies.
2. **OpenFOAM divides by the volume IT measured** —
   `cellSetOption::setVol()` (`cellSetOption.C:145-157`) sums `mesh_.V()` over
   the selected cells — **which is the same volume the heat-balance instrument
   audits against.** A hand-computed `q'''` would have been divided by a
   *different* volume (the chord-faced wedge sector is 0.1269 % smaller than the
   true arc sector at θ = 5°) and that discrepancy would have entered the gate.
3. **`selectionMode all` inside the split region removes the cellZone-name
   failure mode** entirely, and `cellSetOption.C:177-181` sets
   `cells_ = identity(mesh_.nCells())` for it, so `V_` is the whole core region.
   This is the form `K0a_heated_box_source/constant/fvOptions:26-32` already uses.
4. **The measured volume is PRINTED**: `cellSetOption.C:166-168` emits
   `- selected N cell(s) with volume V`. **REGISTERED: the comparator reads that
   line out of `log.solve` and asserts it against the analytic chord-faced wedge
   volume to 1e-9 relative.** That is a free, independent check that the source
   landed on the region it was meant to land on.

**Dimensional confirmation, so `absolute` is not taken on faith.**
`SemiImplicitSource.C:265` sets `SuDims = eqn.dimensions()/dimVolume`. The
`hEqn` above has dimensions of W (an `fvMatrix` carries the volume integration),
so `SuDims` = W/m³ and the entered scalar divided by `V_` [m³] is exactly
`P/V` [W/m³]. **And `rho` does NOT multiply the source**: `SemiImplicitSource.C:244-249`
shows the `rho`-form `addSup` uses `rho` only as a context object for expression
drivers (`:274-276`), never as a factor. A naive fear that `fvOptions(rho, h)`
scales by density is **checked and false**.

### 3.4 THE WEDGE POWER FACTOR — a fourth trap, not in the brief, and the one most likely to be got wrong

The directive's referent `q ln(r_o/r_i)/(2 π k L)` is the **full 360° cylinder**.
The case is a **θ = 5° wedge**, i.e. **1/72 of it**. The general form, derived
here, is

    P_sector = −k (θ r L) dT/dr   ⇒   **dT_wall = P_sector · ln(r_o/r_i) / (θ k L)**

which reduces to the directive's formula at θ = 2π. **REGISTERED: the number
written into `fvOptions` is `P_sector = P_full × θ/(2π)`**, so that `dT_wall`
equals the directive's tabulated value for `P_full` and the referent in §1 line 4
is literally the directive's formula.

| P_full (W) | **P_sector at θ = 5°, W** |
|---:|---:|
| 100 | **1.388888889** |
| 300 | 4.166666667 |
| 600 | 8.333333333 |
| 1000 | 13.88888889 |

**REGISTERED, and this is the clause that prevents the factor-of-72 error from
being typed twice:** the builder reads θ from the generated `blockMeshDict` and
computes `P_sector` from `P_full` and that θ in one place; the comparator
independently recomputes `θ` from the mesh and asserts the `fvOptions` value
against `P_full × θ/(2π)` to 1e-12 relative, **REFUSING** on mismatch. A wedge
angle that appears as a literal in two files is a defect waiting to happen.

---

## 4. THE ERROR BUDGET, DERIVED BEFORE THE RUN

All figures **[DERIVED]** from a 1-D finite-volume model of the registered mesh
(chord face areas `A(r) = 2 r sin(θ/2) L`, cell centroids at
`r_a + Δ(r_a+2r_b)/(3(r_a+r_b))`, orthogonal `snGrad`), **unit: per cent of the
analytic drop**, referent: the exact sector solution of §3.4. **This is a MODEL
of the discretisation, not a measurement**, and every number below is registered
as a **prediction reported beside the measured value, never as a gate.**

### 4.1 The two terms, and the fact that only one of them vanishes

| housing radial cells N | **chord mesh (the real one)** | arc mesh (pure discretisation) |
|---:|---:|---:|
| 8 | **+0.03673 %** | +0.004985 % |
| 16 | **+0.03298 %** | +0.001246 % |
| 32 | **+0.03205 %** | +0.000312 % |
| 64 | +0.03182 % | +0.0000779 % |

- The **discretisation** term converges at **p = 2.0000** to **zero**.
- The **wedge chord-vs-arc** term does **NOT** converge to zero. It converges to
  **θ²/24 = +0.031738 %** at θ = 5°, and **radial refinement cannot remove it,
  because refining radially does not change the wedge angle.**

### 4.2 THE CONSEQUENCE, REGISTERED IN ADVANCE — this is the T16 situation

**The graded quantity mesh-converges to a NON-ZERO residual of +0.0317 %.**
`T20_PREREGISTRATION.md` §5.2 records verification's ruling on T16 at commit
`df69751b`: *"a quantity that mesh-converges to a non-zero value is a PHYSICAL
FEATURE OF THE SOLUTION, not numerical error, and refining the mesh will never
reduce it"* — and verification **refused any relaxation of the tolerance.**

Here the non-zero limit is **geometric, known in advance, signed, and 31× inside
the band** (0.0317 % against 1 %), so it is a **declared bias**, not a
falsification of the referent. **Registered so that it cannot be discovered
afterwards and read as either an excuse or a defect.** The one-way consequence:
if the measured limit differs from +0.0317 % by more than a factor of 2, **the
geometric model in this section is wrong and the rows are `NOT A RESULT`**, not
`GATE FAIL` — a gate may only turn a PASS or GATE FAIL *into* NOT A RESULT.

### 4.3 THE RULE-5 QUESTION THE BRIEF ASKED, ANSWERED IN ADVANCE

The brief required this rung to state **before compute** whether the triple can
return `EXACT` by construction. **It cannot, and here is why.**

The finite-volume flux between radial neighbours uses `(r_{j+1} − r_j)/A(r_f)`
where the exact resistance needs `ln(r_{j+1}/r_j)/(θL)`. The discrete operator
therefore approximates a logarithm by a ratio and **does not integrate the exact
solution exactly**. The predicted triple at N = 8/16/32 (P_full = 100 W):

| level | `dT_wall` predicted (K) |
|---|---:|
| c (N = 8) | 0.0860289980 |
| m (N = 16) | 0.0860257814 |
| f (N = 32) | 0.0860249773 |

Three **distinct, monotone** values ⇒ classification **`CONVERGING`**, with
**p = 1.99994** and **GCI_fine = 3.895e-06 = 0.000390 % = 0.000335 mK**, against
a band of 0.8600 mK — a margin of **2 566×**. Registered band
**p ∈ [1.6, 2.4]**, **GCI_fine < 0.05 %**.

**The registered contingency, one-way and stated now:** if the measured triple
nevertheless classifies `EXACT`, `STAGNANT`, `OSCILLATORY` or `DIVERGENT`, the
rows are **NOT A RESULT** under rule 5 whatever the values say, and **the
prediction in this section is the thing that was falsified** — which is a
reportable finding about this error model and not a reason to re-read the gate.

### 4.4 Q1 and Q2 carry different pre-derived extents — the anti-degeneracy control

Q1 spans **patch to patch**, r_i → r_o, analytic drop 0.0859974153 K at 100 W.
Q2 spans **cell centre to cell centre**, r_c,0 → r_c,N−1, a strictly shorter
span, and is graded against `P_sector ln(r_c,N−1/r_c,0)/(θ k L)` — a **different
referent number at every level**. **REGISTERED PREDICTION: the two residuals
must DIFFER. If Q1 and Q2 return identical residuals, the two readers are
reading the same object twice**, and that is a finding about the instrument, not
about the solver.

### 4.5 The full budget at the graded level (N = 32, P_full = 100 W)

| term | value | tag |
|---|---:|---|
| wedge chord-vs-arc geometric bias | **+0.0273 mK** | DERIVED (model) |
| radial discretisation | +0.00027 mK | DERIVED (model) |
| write precision at `writePrecision 12` | < 1e-6 mK | DERIVED |
| iterative residual at 1e-10 | ≪ 0.001 mK | ASSUMED |
| **predicted net residual** | **+0.0276 mK** | DERIVED (model) |
| **band** | **±0.8600 mK** | REGISTERED |
| **margin** | **31×** | DERIVED |

---

## 5. THE INSTRUMENTS

### 5.1 The comparator reads PATCH averages, never a core centreline value

**REGISTERED.** With the `core` region coupled at r_i, the core adds its own
radial drop at k = 40 W/mK which is **not part of this gate**. The gated quantity
is the difference of two **housing** patch temperatures. `housing_outer` is a
`fixedValue` at 288 K, so the measured content of Q1 is the interface temperature
on `housing_to_core`; the 288 K is REGISTERED and the comparator asserts the
outer patch average equals it to 1e-9 K rather than trusting it.

**Why the wall drop is independent of the core at all** (stated so the design is
auditable): in steady state with both axial end planes adiabatic and the wedge
planes symmetry, **every watt injected in the core must cross the housing wall
radially**, so `dT_wall = P_sector ln(r_o/r_i)/(θkL)` regardless of the core's
conductivity, mesh or geometry. **This is also why the collapsed-axis core mesh
quality does not touch the gate** — the core need only deliver `P_sector` to the
interface, and Q3 audits exactly that.

### 5.2 THE V(b) PLANTED-SOURCE CONTROL — and it RUNS FIRST

Directive §3.6 limb (b). **REGISTERED ORDER: the V(b) pair runs before any gated
point is graded**, precisely because the §3.1 field-name error is quiet.

    B = (power leaving `housing_outer`) / (P_sector as REGISTERED, never as read from the case)

- **Unplanted:** `|B − 1| ≤ 0.01`.
- **Planted:** an otherwise identical case with `sources { h (1.10 × P_sector 0); }`
  and **nothing else changed**. The instrument, still told `P_sector`, must
  report **B_planted − B_unplanted ∈ [0.095, 0.105]**.

**The instrument's numerator must NOT be derived from the gated quantity.**
Inferring `P` from the measured `dT_wall` through the analytic resistance would
make `B ≡ 1` by construction. **REGISTERED AS REJECTED** so that nobody
implements it later as a convenience.

**A refusal here — the instrument cannot see a planted 10 % — is an instrument
failure and the WHOLE RUNG is `NOT A RESULT`.** An instrument that cannot see a
planted 10 % is not entitled to certify a 1 % agreement.

**What this control does and does not cover, stated honestly.** It runs the plant
through the **entire real path** — `fvOptions` → solver → functionObject → reader
— which is stronger than any file-level plant and is what catches the silent-zero
field-name error (a zero source gives `B = 0` in *both* arms and a difference of
**0**, not 0.10). It does **not** by itself exclude a reader that returns the
right number by an accidental path; the unplanted `|B − 1| ≤ 0.01` limb and the
file-level plant of §5.4 cover that.

**AVAILABILITY, CHECKED:** the `wallHeatFlux` functionObject's `wall` model
resolves a **`solidThermo`** — `wallHeatFlux_wall.cxx:31` includes
`solidThermo.H` and `:254-260` does
`mesh().cfindObject<solidThermo>(solidThermo::dictName)` then
`calcHeatFlux(thermo.alpha(), thermo.he(), …)`, falling through to
`FatalErrorInFunction` at `:278-280` only if no thermo of any kind is found.
**So the instrument exists for a solid region at v2606.**

**AND A SOURCE READ IS NOT A DEMONSTRATED RUN.** The paragraph above is a read of
the installed tree; it establishes that the code path *exists* and reaches a
solid thermo. It does **not** establish that the object constructs inside
`chtMultiRegionSimpleFoam`'s per-region function-object list on this build, and
this document does not claim it does.

### 5.2a **THE BALANCE INSTRUMENT RUNS AS A POST-HOC `postProcess` PASS, NOT AS AN INLINE FUNCTION OBJECT — REGISTERED, with the reason**

**REGISTERED: `wallHeatFlux` is NOT placed in `system/controlDict.functions`. It
is run after the solve, against the written fields, as
`postProcess -func wallHeatFlux -region housing -time <endTime>`.**

The reason is an asymmetry of consequences, and it is the whole argument:

- **An inline function object that fails does so at CONSTRUCTION, before the
  first iteration, and takes the entire solve with it.** The cost of a
  source-read that turns out to be wrong is then the whole run — every
  core-minute, and on a contended box possibly an hour of wall time — thrown away
  for an instrument that is not even part of the gate's critical path.
- **A `postProcess` pass that fails costs nothing.** The fields are already on
  disk, the solve is already complete and gradeable, and the failure is a
  finding about the instrument that can be repaired and re-run for free.

**The general form, offered upward and NOT ruled here:** *an instrument whose
availability rests on a source read rather than a demonstrated run belongs
downstream of the solve, not inside it, until one run has demonstrated it.* Once
a `postProcess` pass has succeeded on a real T21 field, promoting `wallHeatFlux`
to an inline function object becomes a registered option for later rungs — at
which point it is no longer a source read.

**What IS registered inline** are only function objects of a shape this family
has already run: `surfaceFieldValue` and `fieldMinMax`. **Every `operation` name
in them is read out of `surfaceFieldValue.C:77-104` at registration time**, for
exactly the same reason — an unknown `operation` is a construction-time abort.

**A consequence that must not be papered over:** because the balance instrument
is post-hoc, **the V(b) planted-source arm (§5.2) is graded after both runs
complete, not during them.** The registered ordering — *V(b) before any gated
point* — is therefore an ordering of **grading**, not of wall-clock launch: the
unplanted and planted cases may run in either order or together, but **no gated
row may be graded until the V(b) pair has been read and passed.**

### 5.3 THE WEDGE-ANGLE CONTROL — a direct measurement of the §4.2 bias

**REGISTERED: one additional case at θ = 1.0°, everything else identical to the
graded level.** Predicted residuals (DERIVED, model):

| θ | predicted residual at N = 32 |
|---|---:|
| 5.0° | **+0.032050 %** |
| 1.0° | **+0.001581 %** |

a **20.3× reduction**, and the θ² scaling of the geometric term is the thing
being measured. **This converts §4.2's declared bias from an assertion into a
falsifiable measurement for the cost of one ~2 core-min solve**, and it is the
cheapest discriminator in the rung between "the referent is right and the mesh
has a known geometric bias" and "the referent is wrong". Registered band: the
θ = 1° residual must be **below 0.25× the θ = 5° residual**; a failure makes
§4.2's model the falsified object and the rows **NOT A RESULT**.

### 5.4 The planted-zero control — patterned on `analyse_t18.py`, NOT on `analyse_t3.py`

Structure adopted **verbatim in shape** from
`verification/runs/T-family/T18_runs/analyse_t18.py:168-220`:

1. **Copy first, never write into the case.** `shutil.copytree` into a scratch
   directory; **REFUSE** if `os.path.realpath(dst)` resolves inside
   `os.path.realpath(case_dir)` (`analyse_t18.py:178-179`).
2. **NEGATIVE ARM, threshold exactly ZERO.** The reader is run twice on identical
   bytes; `dneg = max|a−b|` must be **bitwise `0.0`**, else REFUSE "the reader is
   NOISY" (`:184-186`). **There is no absolute tolerance anywhere in the negative
   arm.**
3. **POSITIVE ARM, a measured magnitude ladder.** Registered magnitudes
   **(1.0, 1e-1, 1e-2, `PLANT`, `BAND_MIN`, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8) K**,
   `floor` = the smallest magnitude with `d > 0.0`, the comparison exact and
   epsilon-free. **`BAND_MIN` = 8.59974e-04 K is included as an explicit rung so
   that the control demonstrates the reader can see an error exactly the size of
   the thing it is gating** — an addition to T18's ladder.
4. **REFUSE if `floor is None`** — the reader is **BLIND**.
5. **The only sizing tolerance is RELATIVE: REFUSE if `seen[PLANT] < 0.1 ×
   PLANT`** (`:210-212`). **T3's absolute `PLANT − 1e-15` is NOT adopted**: on a
   ~300 K field that window is 0.2082 ULP, 56.8× below one ULP, and the outcome
   is decided by a ~7-ULP wiggle. That defect is not reproduced here.
6. **Plant sized to the reader.** Q1 and Q2 are averages; the plant goes into
   **every face value of the target patch** (Q1) and **every cell of the target
   ring** (Q2), so the expected shift is exactly `PLANT`, not `PLANT/N`. The
   number of values planted is recorded in the output.
7. **`PLANT = 1.234e-03 K`, IMPORTED from `scripts/roache_triple.py:169`**, never
   redefined locally — as are `FS`, `STAGNANT_FLOOR`, `P_MIN`
   (`analyse_t18.py:43`).
8. **The plant is located STRUCTURALLY, by line index from the `boundaryField`
   patch block header, never by value.**
9. **T20's floor-to-band refusal is ADOPTED: REFUSE if `floor > 8.59974e-06 K`**
   — one hundredth of the tightest registered band. *An instrument whose
   demonstrated resolution is not at least 100× finer than the band it decides
   has no business deciding it.* Predicted floor at `writePrecision 12`:
   **≤ 1e-08 K**, a margin of ~860×.
10. **NEW CLAUSE, OFFERED UPWARD AND NOT RULED HERE — THE SIGNED ARM.** Q1 is a
    **difference** of two patch averages, so the positive arm is run on **both**
    patches: a plant on `housing_to_core` must move Q1 by **+PLANT** and a plant
    on `housing_outer` by **−PLANT**. **REFUSE on a sign error.** *A reader that
    takes `abs()` of the difference passes every single-sided plant and is
    blind to exactly the failure that inverts the gate.* Registered as binding on
    T21; adopting it lab-wide is verification's call.
11. Original bytes restored from the in-memory copy; the scratch tree removed in
    a `finally`.

---

## 6. RULE 4 COMPLETION, IN ITS STEADY FORM

`CLAUDE.md` rule 4 is **all-or-nothing**; the comparator **refuses (exit 2)
rather than degrades**.

| # | conjunct | how it is evaluated here |
|---|---|---|
| 1 | `rc = 0` | captured **inside** the detached wrapper and written to `STATUS.<case>`. **Never around a `setsid` line** — `setsid timeout cmd` exits 0 for every outcome |
| 2 | an `End` line | `grep -c '^End$' log.solve` == 1 |
| 3 | last time == `endTime` | the numerically greatest time directory equals the registered iteration count |
| 4 | **fields present** | **`T` and `p` in `<endTime>/core/` and `<endTime>/housing/`.** The thermal family's list `T U p_rgh alphat nut k omega` **does not apply — there is no fluid region and those fields do not and must not exist.** `p` is in the list because a solid region of `chtMultiRegionSimpleFoam` requires it: upstream's own `tutorials/heatTransfer/chtMultiRegionSimpleFoam/cpuCabinet/0.orig/v_CPU/` contains exactly `T` and `p`. `betavSolid` is **optional** — `createSolidFields.H:26-62` falls back to a uniform 1 when absent — and is **not** in the registered list |
| 5 | `ExecutionTime` count == `endTime` | evaluated as `count == endTime` with `deltaT 1` |
| 6 | **age guard** | every field at `endTime` **newer** than the case's own `0/housing/T` by `st_mtime`; the launcher touches it last. A guard refuses a case where `0/` or any time directory already exists |

### 6.1 **`residualControl` IS NOT REGISTERED — and this family has already been killed by it, TODAY**

**REGISTERED: no `residualControl` stopping criterion in any region's `SIMPLE`
dict. The full registered iteration count is run. Convergence is an ASSERTION on
the log — final `h` initial residual < 1e-10 in every region, and `dT_wall`
stationary to 1e-7 K over the last 500 iterations — never a stopping rule.** An
assertion failure is `NOT A RESULT`, **not a longer run without
re-registration.**

**This is not a precaution. It is a post-mortem, and the corpse is this family's
own, from today.**

`b52ed93b` (**2026-08-31T15:36:51Z**, verified by `git log -1 --format=%ad
--date=iso-strict`) freezes **T19b as the successor to T19**, and the defect it
repairs is exactly the construction rejected here. **Every figure below was read
off the artifacts, not off the commit message:**

| what | value | where it was read |
|---|---|---|
| the frozen parent's own builder line | `residualControl { p_rgh 1e-9; U 1e-9; T 1e-9; }` | `build_t19.py:211` at `b52ed93b^` **[TRANSCRIBED]** |
| registered `endTime` | **30000** | `verification/runs/T-family/T19_runs/P_q_c/system/controlDict:14` **[TRANSCRIBED]** |
| `P_q_c` last time directory | **828** | `ls P_q_c` → `0 828` **[MEASURED]**, unit: SIMPLE iterations |
| `P_Ts_c` last time directory | **541** | `ls P_Ts_c` → `0 541` **[MEASURED]**, unit: SIMPLE iterations |
| `P_q_c` exit | **`rc=0`**, `wall_s=3`, `note=clean` | `STATUS.P_q_c` **[MEASURED]** |
| `P_Ts_c` exit | **`rc=0`**, `wall_s=2`, `note=clean` | `STATUS.P_Ts_c` **[MEASURED]** |

**Both cases stopped at under 3 % of their registered duration, and both reported
`rc=0` with `note=clean`. THEY DID NOT CRASH; THEY SUCCEEDED AT THE WRONG
EXPERIMENT.** That is the whole hazard in one sentence, and it is why the
construction is forbidden here rather than merely discouraged: **the failure mode
is a clean exit.** Nothing in `rc`, nothing in the `End` line, and nothing in a
`STATUS` file distinguishes a converged run from a run that quietly answered a
different question.

The mechanism, stated in this rung's own terms:

1. An early residual exit leaves the **last time directory below `endTime`**, so
   `CLAUDE.md` rule 4 conjunct 3 (`last time == endTime`) **cannot hold** — the
   run is not complete no matter how healthy it looks.
2. Worse, **any plateau-style control that compares two late writes loses its
   pair and becomes UNEVALUABLE, not failed.** T19's `C_PLATEAU` compares each
   graded quantity between the writes at 28000 and 30000; with the run stopped at
   828 neither write exists. **An unevaluable control is worse than a failing
   one**, because a failing control is a finding and an unevaluable one is a
   silence.
3. The defect is in the **construction, not the solver**: T19 ran
   `buoyantBoussinesqSimpleFoam` (`STATUS.P_q_c:solver`), T21 runs
   `chtMultiRegionSimpleFoam`. Nothing about it is solver-specific, which is
   precisely why it transfers.

**The related referral stays open and this choice does not depend on it.** Ansys
referred to verification (commit `c03b6eb8`, T20 §8.1) whether rule 4's
`ExecutionTime`-count clause forbids adaptive time-stepping lab-wide. **This
document does not rule on that referral**, and T21 would register no
`residualControl` even if the referral were resolved the other way — because the
reason here is the measured fatality above, not the bookkeeping clause. The
steady form of the reading is recorded and referred alongside ansys's: *a
residual-based early exit is incompatible with a completion rule that requires
the last time to equal `endTime`.*

### 6.1a The cost of this choice, stated rather than hidden

Running the full count is **not free**, and pretending otherwise would be the
same dishonesty in the other direction. T21 pays for every iteration after
convergence. That cost is inside the §7 POINT and is the reason the registered
`endTime` is chosen from the convergence estimate rather than set generously
"to be safe": **a padded `endTime` is paid for in full, every run.**

### 6.2 **`constant/g` IS MANDATORY EVEN THOUGH THIS RUNG HAS NO FLUID REGION**

This is counter-intuitive enough that it would otherwise be discovered as a
first-launch failure, so it is registered here.

`chtMultiRegionSimpleFoam` reads gravity at
**`applications/solvers/heatTransfer/chtMultiRegionFoam/chtMultiRegionSimpleFoam/fluid/createFluidFields.H:26`**:

```
const uniformDimensionedVectorField& g = meshObjects::gravity::New(runTime);
```

**That line sits at FILE SCOPE. The `forAll(fluidRegions, i)` loop does not open
until `:29`.** So it executes whatever `regionProperties` says, and
`regions ( fluid () solid (core housing) )` does not save it. And the read is not
optional: `gravityMeshObject.C:43-57` constructs the field with
**`IOobject::READ_MODIFIED`**, which requires the file to be present.

**REGISTERED: `constant/g` is part of this rung's case tree, with
`value (0 0 0)`.** Zero because there is no fluid, nothing buoyant, and a
non-zero radial gravity would in any case be inconsistent with a wedge's
axisymmetry; the file exists because the solver reads it, and its value is a
declared decision rather than a default.

**Two line numbers, not one — and the second is a correction carried from the
brief.** The figure originally handed to this lane was
`createFluidFields.H:35`, which is correct for the **transient**
`chtMultiRegionFoam` header that **T20** (Case 4) uses. The **SIMPLE** variant
used here has its own copy of that header at **`:26`**, with the loop opening at
**`:29`**. Same defect, two different files, and a record that carries only one
of them will mislead whichever rung reads the other.

**Corroborated on disk, not only in source:** T20's own solid-only feasibility
case — `verification/runs/T-family/T20_runs/T20_LC_FEAS_20260831T151828Z/`, whose
`constant/regionProperties` reads `fluid ( )` / `solid (cellRegion)` — **ships a
`constant/g`**, and that case completed at `rc=0`. So the requirement is
confirmed by a run and not only by a reading.

---

## 7. COST — rule 12

### 7.1 The rate, and its provenance stated at its true strength

The basis is **T5b's**, `verification/runs/T-family/T5b_runs/T5B_CAPS.txt`, and it
is a **better** basis than T20's cross-solver borrow in one respect and **worse**
in another. Better: **it is the same solver** — `T5_CUBE_m/system/controlDict:10`
reads `application chtMultiRegionSimpleFoam` — on the same box, at 1 rank, with
`rc = 0` and `capped = 0`:

| T5 level | wall s | cells | core-min | s per cell-iteration |
|---|---:|---:|---:|---:|
| c | 965 | 52 684 | 16.083 | **3.664e-06** |
| m | 4 539 | 212 942 | 75.650 | 4.263e-06 |
| f | 19 150 | 882 024 | 319.167 | 4.342e-06 |

Worse: **this rung's meshes are 100× to 3 000× smaller**, so the basis is
**EXTRAPOLATED DOWNWARD OUT OF ITS CALIBRATION RANGE**, into the regime where
fixed overhead dominates and per-cell rate is meaningless.
`T11_RESULTS.md` records a ladder landing at **0.41× its POINT** for exactly this
reason (*"overhead-dominated below ~1e3 cells"*).

**And T5's three points cannot supply the overhead term.** A two-term fit
`t_iter = t_overhead + rate × N_cells` over the three rows above returns
`rate` = 4.386e-06 and **`t_overhead` = −0.038 s — NEGATIVE, therefore
unphysical.** The three points are consistent with no measurable fixed overhead
and slightly super-linear scaling. **So the overhead is UNMEASURED and is
ASSUMED**, and it is named here as the weakest figure in the registration rather
than dressed up as a fit.

| term | value | **tag** |
|---|---:|---|
| `rate` | 3.664e-06 core-s per cell-iteration | **EXTRAPOLATED** — MEASURED on `T5_CUBE_c`, same solver, same box; extrapolated ~100× downward in cell count |
| `t_overhead` | 2.0e-03 core-s per iteration | **ASSUMED** — not resolvable from T5's three points (a linear fit returns a negative intercept). Allowance for the two-region loop, `thermo.correct()` and per-iteration `Info` |
| `startup` | 5.0 core-s per case | **ASSUMED** — two-region mesh read, two thermo constructions, first write |
| `ranks` | 1 | **REGISTERED** |

### 7.2 POINT and CAP

    cost_core_s = startup + N_iter × (t_overhead + rate × N_cells)

**POINT 9.1901 core-min** over the registered run set, itemised per case in
**§8.4** (6 cases, 18 000 solver iterations, `ranks` 1). **CAP 20.0 core-min,
HARD = 2.18 × POINT.** The cap is **a runaway guard, not a target** — the same
words `T5B_CAPS.txt` uses of its own 2.0× headroom — and the headroom is
deliberate because the POINT rests on an **EXTRAPOLATED** rate and an **ASSUMED**
overhead. **An overrun stops the run; it does not get a new budget.**

**USD, DERIVED NOT MEASURED**, at the owner-stated **$0.0513/core-h**
(c7a.4xlarge, Sanaa 2026-08-21/22): POINT **$0.00786**, CAP **$0.01710**.
`cost_basis`: **DERIVED, NOT MEASURED** — `COMPUTE_BUDGET_CHARTER.md` §5, the box
cannot read its own billing.

> *These figures also read against a POINT of 8.6 in the draft, and were
> reconciled to 9.1901 in the same unfrozen edit as §1 line 8. **The supervisor
> asked for §1 line 8 alone; §7.2 was corrected with it because reconciling one
> and not the other would have moved the contradiction rather than removed it.**
> CAP, its 20.0 value, and the DERIVED-not-measured basis are all unchanged.*

### 7.3 The calibration owed at completion

Rule 12's estimate-versus-actual clause (Sanaa 2026-08-23) binds this rung. At
completion the results record must carry actual core-minutes from the `STATUS.*`
files as `wall_s × ranks ÷ 60`, the **ratio actual/predicted**, the attribution
split between contention, waste and misprediction with **waste named separately
and never folded into the ratio**, and a row appended to
`docs/COST_CALIBRATION.md`. **`t_overhead` and the downward rate extrapolation
are the two figures this rung exists to calibrate** — this is the lab's first
sub-1 000-cell `chtMultiRegionSimpleFoam` reading. *A completion report without
this comparison is incomplete.*

### 7.4 **A CONTENDED RUN DOES NOT PRODUCE A CALIBRATION FIGURE — REGISTERED BEFORE THE FACT**

**REGISTERED, one-way: `t_overhead` may be calibrated ONLY from a run whose
recorded load average at launch shows the box was not saturated. A reading taken
under contention is reported as a cost and is NOT admissible as a calibration
row in `docs/COST_CALIBRATION.md`.** The registration says this in advance
because after the fact a contended number is indistinguishable from a
mispredicted one, and the temptation is then to attribute the whole gap to
whichever term is under discussion.

**The mechanism, registered rather than asserted:** the launcher writes a
`START.<case>` file **before** the solver starts, carrying `start_utc`,
`loadavg_at_launch` (all three windows from `/proc/loadavg`) and `nproc`. **The
contamination is therefore disclosed at the point of measurement rather than
argued about afterwards**, and a reader of the `STATUS` file has the load figure
beside the wall time without having to reconstruct it from anything.

**Registered admissibility threshold: the one-minute load average at launch must
be below `0.5 × nproc`** (on this box, **< 8.0** against `nproc` = 16). Above
that the row is a cost and not a calibration. *This is a registered convention,
not a measured threshold, and it is labelled **[REGISTERED]** rather than dressed
as derived.*

**Why this rung in particular cannot tolerate a contended reading — the
precedent, measured on this box today.** Case 4's own feasibility probe,
`verification/runs/T-family/T20_runs/T20_LC_FEAS_20260831T151828Z`, ran 750 steps
and recorded:

| quantity | value | tag / referent |
|---|---:|---|
| wall time | **3 s** | **[MEASURED]** `STATUS.T20_LC_FEAS:wall_s` |
| final `ExecutionTime` | **0.28 s** | **[MEASURED]** last `ExecutionTime` line of `log.solve` |
| **fraction of the wall that was NOT solving** | **90.7 %** | **[DERIVED]** `1 − 0.28/3` |

**Nine tenths of that run was startup, mesh read, thermo construction and I/O.**
At T21's cell counts the same regime applies — which is the entire reason
`t_overhead` and `startup` are the registered weak terms of §7.1 — and **a
per-cell rate extracted from a wall time that is 91 % overhead calibrates
nothing.** Contention on top of that makes the reading worse, not merely noisier,
because contention inflates the overhead term preferentially: the solve is one
serial process competing for a core, while the I/O and construction phases
compete for the same disk and memory bandwidth as every other job on the box.

**Consequence, registered:** if no uncontended slot is available, **the rung
still runs and still grades** — the physics does not care about the load average
— **but the calibration row is owed and unpaid, and the results record must say
so in those words** rather than quoting a contended ratio as though it were a
measurement.

---

## 8. THE REGISTERED RUN SET

### 8.1 The six cases

Geometry per §1. **The core carries a 6 mm shaft bore, `r_bore` = 0.006 m, with
an adiabatic wall — it does NOT reach the axis.** That is not a preference; it is
inherited from a **measured** failure on T22's identical wedge construction,
where a collapsed-axis core returned three `checkMesh` failures —
`***Zero or negative face area detected. Minimum area: 0`, `***Max skewness =
9.2966987286e+146, 140 highly skew faces`, and `***Total number of faces on empty
patches is not divisible by nCells` — while the fluid and housing regions on the
same mesh returned `Mesh OK`. The 140 zero-area faces were the degenerate axis
faces of the 140 axial cells. **§5.1's argument is unchanged by the bore**: the
core need only deliver `P_sector` to the interface, and Q3 audits exactly that.

| case | housing N_r | core N_r | N_z | housing cells | core cells | **total cells** | θ | P_full | purpose | graded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `T21_CYL_c` | 8 | 24 | 20 | 160 | 480 | **640** | 5° | 100 W | triple — coarse | triple only |
| `T21_CYL_m` | 16 | 48 | 40 | 640 | 1 920 | **2 560** | 5° | 100 W | triple — medium | triple only |
| **`T21_CYL_f`** | **32** | **96** | **80** | **2 560** | **7 680** | **10 240** | 5° | 100 W | triple — fine; **THE GRADED LEVEL** | **Q1, Q2, Q3** |
| `T21_CYL_W1` | 32 | 96 | 80 | 2 560 | 7 680 | 10 240 | **1°** | 100 W | wedge-angle control (§5.3) | residual only |
| `T21_CYL_P1000` | 32 | 96 | 80 | 2 560 | 7 680 | 10 240 | 5° | **1000 W** | linearity + widest band | Q1, Q2 |
| `T21_CYL_S10` | 32 | 96 | 80 | 2 560 | 7 680 | 10 240 | 5° | 100 W **+10 %** | **V(b) planted source** | **Q3 planted arm** |

Refinement is **r = 2 uniform in both mesh directions**, which is what makes the
triple a Roache triple rather than a radial-only sweep. Axial refinement
contributes **identically zero** error because the solution is exactly
z-uniform, so the observed order is set by the radial direction alone — this is
stated so that a measured `p ≈ 2` is not later credited to the axial ladder.

**`endTime` = 3000 iterations, `deltaT` 1, every case, no `residualControl`
(§6.1).** The count is chosen from the convergence estimate and **not** padded,
because §6.1a's cost is real: every iteration after convergence is paid for.

### 8.2 The linearity row, and why it is nearly free

The problem is **linear**: `dT_wall ∝ P`. `T21_CYL_P1000` therefore carries a
registered prediction that is exact rather than approximate —
**`dT_wall(1000 W) / dT_wall(100 W) = 10.000000` to within reader noise** — and
it is the cheapest possible discriminator against a source that saturates,
clips, or is applied with a magnitude-dependent error. It also supplies the
**widest** absolute band (±8.5997 mK against ±0.8600 mK), so a row that passes at
1000 W and fails at 100 W localises the fault to an absolute-error term rather
than a proportional one. **Registered as a physicality row, not a gate.**

### 8.3 Staging — and the one question source inspection cannot answer

**`T21_CYL_c` alone runs first.** It costs **0.30 core-min** and it answers what
no amount of reading the v2606 tree can: *does `chtMultiRegionSimpleFoam` run to
completion with `regions ( fluid () solid (core housing) )`, with an `fvOptions`
source on `h` in one solid region and a `mappedWall` couple to the other?*

If it does not, **the rung is `BLOCKED` on that finding** and `solidFoam` is
registered as the alternative **in a re-registration, not a silent
substitution** — `solidFoam` is not the solver Case 3's map rungs use, and
swapping to it would quietly convert this from a machinery gate into a different
rung. That is T20 §9's construction and the reason is the same.

Then **the V(b) pair (`f` and `S10`) is graded before any gated row** — an
ordering of **grading**, not of launch (§5.2a).

### 8.4 Cost of the run set, itemised — and a correction to §1 line 8

Model and provenance per §7.1: `cost_core_s = startup + N_iter × (t_overhead +
rate × N_cells)`, `startup` **5.0 core-s [ASSUMED]**, `t_overhead` **2.0e-03
core-s/iteration [ASSUMED]**, `rate` **3.664e-06 core-s/cell-iteration
[EXTRAPOLATED]**, `ranks` **1 [REGISTERED]**.

| case | cells | core-s | **core-min** |
|---|---:|---:|---:|
| `T21_CYL_c` | 640 | 18.03 | **0.3006** |
| `T21_CYL_m` | 2 560 | 39.14 | **0.6523** |
| `T21_CYL_f` | 10 240 | 123.56 | **2.0593** |
| `T21_CYL_W1` | 10 240 | 123.56 | **2.0593** |
| `T21_CYL_P1000` | 10 240 | 123.56 | **2.0593** |
| `T21_CYL_S10` | 10 240 | 123.56 | **2.0593** |
| **TOTAL** | | | **9.1901** |

**POINT 9.1901 core-min. CAP 20.0 core-min (hard) = 2.18× POINT.** 18 000 solver
iterations in total. USD **$0.00786 point / $0.01710 cap, DERIVED NOT MEASURED**
at the owner-stated $0.0513/core-h.

**Fraction of Case 3's family cap** (directive §3.7, **700 core-min**):
**POINT 1.313 %, CAP 2.857 %.** This rung costs a little over one percent of the
family's budget at the point estimate and under three percent at its hard cap —
which is the intended shape: it is the cheapest and most independent thing in
Case 3, and it depends on none of it.

> **THE COST CORRECTION, RECORDED RATHER THAN QUIETLY APPLIED — and this note is
> the history, not an outstanding action.** An earlier draft of this document
> carried **POINT 8.6 core-min** at §1 line 8 and again at §7.2, with a USD
> figure of **$0.0074** derived from it — the draft's own rounding of
> `8.6/60 × $0.0513 = $0.00735`, quoted both ways here so the two historical
> forms cannot be mistaken for two different claims. That 8.6 was written
> **before** the run
> set was itemised; itemising it here gives **9.1901**, and **all three operative
> sites were reconciled while the document was UNFROZEN**, which is the only time
> such a change is legal — after a freeze §1's ten lines are the binding content,
> nothing below may widen them, and a discrepancy of this kind would have to land
> as a dated addendum altering no cap.
>
> **Two things are worth keeping from how this was caught.** First, the stale
> figure had propagated to **three** sites and not one, and the third was a
> **dollar figure derived from the stale core-minutes** — *a compound number
> carries its weakest input's tag, and it also carries its inputs' staleness.*
> Second, the discrepancy existed **only because §1 was written before §8**;
> writing the binding ten lines before the derivation that supports them is the
> mechanism that produced it, and a later rung that drafts in the same order
> should expect the same defect. **CAP was never affected and remains 20.0.**

---

## 9. THE SELFTEST SPECIFICATION

The comparator is **not written** — this document does not authorise it. The
selftest it must carry is registered here **so that it cannot be shaped to the
answer later**. `python3 analyse_t21.py --selftest` must exercise, on
**synthetic forged trees only**:

**S1 — BOTH SIGNS of every drift.** For each gated row, four forged cases:
residual `+1.5 × band`, `−1.5 × band`, `+0.5 × band`, `−0.5 × band`. Required:
**`GATE FAIL`, `GATE FAIL`, `PASS`, `PASS`.** *A one-sided threshold passes a
two-sided band only by luck; T15's `0.5*ref` is the failure this limb prevents.*

**S2 — BLIND-reader mutant must REFUSE.** `read_field` monkey-patched to return a
constant independent of the file bytes. The planted-zero control must **exit 2**
with the **BLIND** message, and the selftest **fails if the comparator emits any
verdict at all**.

**S3 — NOISY-reader mutant must REFUSE.** `read_field` patched to add one ULP of
jitter on the second call. The **negative arm** must fire on a non-zero `dneg`.
*This is the limb T3 did not have.*

**S4 — UNDERSIZED-plant mutant must REFUSE.** The Q1 plant patched to touch one
patch face instead of all of them. Clause 5 (`seen[PLANT] < 0.1 × PLANT`) must
fire. *Proves the sizing test is live, not decorative.*

**S5 — FLOOR-tied refusal must fire.** A forged field written at
`writePrecision 4` must drive the demonstrated floor above **8.59974e-06 K** and
REFUSE under §5.4 clause 9.

**S6 — THE SIGNED ARM (§5.4 clause 10), and it is the limb this rung adds.** A
forged pair in which the plant is applied to `housing_outer` instead of
`housing_to_core` must produce a recovered shift of **−PLANT**, and a comparator
that reports `+PLANT` — i.e. one that took `abs()` of the difference — must
**REFUSE**. *A reader that absolutes the difference passes every single-sided
plant and is blind to exactly the error that inverts the gate.*

**S7 — balance instrument, BOTH DIRECTIONS.** A forged pair differing only by a
+10 % source must return `B_planted − B_unplanted` inside `[0.095, 0.105]`; a
forged pair differing by **0 %** must return a difference **< 0.005**. *Both
directions, so the instrument is shown able to report "no plant" as well as
"plant".*

**S8 — the rule-4 completion limbs, one forged tree per conjunct.** Six trees,
each violating exactly one conjunct of §6: `rc≠0`; no `End` line; last time 2994
≠ 3000; `T` missing from `<endTime>/housing/`; 2999 `ExecutionTime` lines against
a registered 3000; a field older than `0/housing/T`. **Each must produce
`NOT A RESULT` and no graded value.** A seventh tree adds the conjunct this rung
learned from T19b: **a tree whose last time directory is 828 against a registered
`endTime` of 3000 must be `NOT A RESULT` even though its forged `STATUS` says
`rc=0` and `note=clean`** (§6.1).

**S9 — the `but never used` limb.** A forged `log.solve` containing
`Source motorLoss defined for field T but never used` must drive **exit 2**.
*This is the free positive check §3.1 discovered, and a limb is what keeps it
from decaying into a comment nobody runs.*

**S10 — the wedge-power-factor assertion.** A forged case whose `fvOptions` value
is `P_full` rather than `P_full × θ/(2π)` — the **72× error** of §3.4 — must
**REFUSE**, and so must one whose value is right for a 5° wedge while the mesh is
1°. *The two files must agree with each other, not merely each be plausible.*

### 9.1 **S11 — THE INVARIANCE LIMB, adopted from T20 §10.1 unchanged**

**REGISTERED, BINDING: no selftest limb of `analyse_t21.py` may read, `stat`,
`glob` or assert anything whatsoever about
`verification/runs/T-family/T21_runs/` or any other live run tree. Every limb
operates on a synthetic tree it forges in a scratch directory it creates and
removes.**

**And the invariance is MEASURED, not promised.** `--selftest` runs its entire
limb set **twice** in one invocation — **pass A** against an empty synthetic run
root, **pass B** against one fully populated with all six case directories, time
directories through `endTime`, fields, `log.solve`, `STATUS.*` and `DONE.*` — and
**asserts the two limb-result structures are byte-identical**, failing with a
diff of the differing limbs if they are not.

**Why, in one sentence, from T20's own record:** `docs/DOCKET.md` **D574**
records a selftest limb with a built-in expiry keyed to the campaign's own
progress — asserting the live run tree holds no `DONE` marker. **A limb of that
shape is true at freeze and FALSE the moment the campaign succeeds**: it is not a
check on the instrument, it is a check on the calendar, and it passes for exactly
as long as the work has not been done — worthless precisely when the result needs
defending. **No count of that defect class is quoted here**, because T20 §10.1
records three detectors producing three different sets and one of them (its own)
returning an unplanted zero. S11 stands on the argument, not on a census.

### 9.2 Two constructions the comparator is FORBIDDEN to use

1. **The balance instrument's numerator may NOT be inferred from `dT_wall`**
   through the analytic resistance. That makes `B ≡ 1` by construction (§5.2).
   Registered as rejected **before** anyone implements it as a convenience.
2. **Roache floors may NOT be defined locally.** `STAGNANT_FLOOR`, `P_MIN`, `FS`
   and `PLANT` are **imported** from `scripts/roache_triple.py`
   (`analyse_t18.py:43` is the pattern), and a registered JSON copy that differs
   from the import must **REFUSE**. One number, one home.

---

## 10. DECLARED OMISSIONS AND ASSUMPTIONS

Each labelled, per the directive's common deliverable 7 (*"certificate draft per
case listing WHAT WAS NOT CHECKED"*). **Stated at true size, not at a reassuring
one.**

1. **THE NOSE AND TAIL CONES ARE REMOVED** (§2.3). They are a second conduction
   path; with them present `dT_wall ≠ P ln(r_o/r_i)/(2πkL)` by an unmodelled
   amount. **Case 3's map rungs must restore them and may not cite T21 as having
   verified anything about them.**

2. **NO FLUID, THEREFORE NO CONVECTION, NO TURBULENCE MODEL, NO `h`.** The
   housing outer surface is a `fixedValue` at 288 K. **The rung says nothing
   about what heat-transfer coefficient the real annulus produces**, which is
   Case 3's central physics and is deliberately removed here.

3. **NO CONJUGATE FLUID–SOLID COUPLING IS EARNED.** The only couple exercised is
   **solid-to-solid** (`core ↔ housing`). The
   `compressible::turbulentTemperatureRadCoupledMixed` path across a
   fluid/solid interface is **not** exercised, and the map rungs may not cite
   T21 for it.

4. **RADIATION OFF**, `radiationModel none`. The neglected term must be bounded
   in the results record by `εσ(T⁴ − T_inf⁴)A` at the run's **own** maximum
   surface temperature with ε = 0.9, and **the figure that comes out is the
   figure that goes in the record**. *Why the gate is unaffected, stated
   precisely rather than waved:* this is an EXACT-tier verification of code
   against the closed-form solution of the equations the code is solving, and
   radiation is absent from **both sides** — from the case and from the referent.
   The cost is paid in physical realism, not in gate validity.

5. **REPRESENTATIVE CORE PROPERTIES, NOT ANY REAL MOTOR'S.** ρ 7000, c_p 450,
   k 40 W/mK are the directive's own **declared representative** values for
   windings-plus-laminations. No manufacturer's data was consulted and none is on
   this box. **Nothing here is a claim about any real motor.** The core's
   properties are in any case **irrelevant to the gate** (§5.1): every watt must
   cross the housing wall regardless.

6. **THE 6 mm SHAFT BORE IS A DEPARTURE FROM DIRECTIVE §3.2**, which says the
   core fills the housing interior (§8.1). It is taken on a **measured**
   `checkMesh` failure, not a preference, and it changes no registered quantity
   because `volumeMode absolute` means `V_core` is never hand-typed.

7. **STEADY ONLY.** No `ddt`, no thermal mass, no transient. `ρ` and `c_p` appear
   in the case files but **do not enter the steady solution at all** — they are
   registered for completeness and a reader must not infer that this rung
   verifies them. **T20 is the transient control; T21 is not.**

8. **THE COST RATE IS EXTRAPOLATED OUT OF ITS CALIBRATION RANGE** (§7.1), roughly
   100× downward in cell count, and `t_overhead` is **ASSUMED** because T5's three
   points return a **negative** intercept. The §8.4 figures are a **prediction
   with two named weak terms**, not a measurement. **A contended run does not
   discharge the calibration** (§7.4).

9. **THE ERROR BUDGET OF §4 IS A MODEL, NOT A MEASUREMENT.** It is a 1-D
   finite-volume model of the registered mesh with chord face areas and
   geometric centroids. The real solver additionally carries the enthalpy
   formulation, the region-coupling iteration, and the interface treatment at
   r_i. **The predicted residuals are registered as predictions reported beside
   the measured values, and are not gates.**

10. **`writePrecision 12` IS REGISTERED, NOT VERIFIED TO BE SUFFICIENT BY
    MEASUREMENT.** The 1e-9 K quantum is arithmetic from the significant-figure
    count; the **demonstrated** detection floor comes from §5.4's measured ladder
    at run time, and if it exceeds 8.59974e-06 K the instrument refuses.

11. **THE `wallHeatFlux` AVAILABILITY FINDING IS A SOURCE READ, NOT A RUN**
    (§5.2, §5.2a). That it constructs inside `chtMultiRegionSimpleFoam`'s
    per-region function-object list on this build is **not demonstrated**, which
    is exactly why it is registered downstream of the solve.

12. **NOTHING IN THIS RUNG IS VALIDATION.** §2.1: an exact analytic referent
    scores **V and never P**. The ceiling is `GATE REACHED`; `HOLDS` is
    unreachable **by construction**, and no reading of the result can raise it.

---

---

## 11. WHAT THIS DOCUMENT DOES NOT DO

- It **does not authorise a solve**, does not enqueue, and creates no queue entry.
- It **does not write the builder, the comparator or the launcher.** §3, §5 and §6
  are the specification those must meet; the code is a separate act under a
  separate review, and the supervisor reads measurement-script diffs **as diffs**,
  personally.
- It **does not rule** on the steady `residualControl` reading (§6.1), on the
  `writePrecision`-versus-band standard (§2.4), or on the signed-plant clause
  (§5.4 clause 10). All three are **offered upward to verification** and none is
  a request for relief.
- It **does not decide** whether the rest of Case 3 opens its own campaign folder
  (§0.3).
- It **files nothing anywhere.** `CLAUDE.md` rule 7 — submissions are parked.

---

## AMENDMENT 1 — 2026-09-03 — **PRE-COMPUTE. TWO CASE-TREE FILES THE SOLVER READS UNCONDITIONALLY EVEN WITH ZERO FLUID REGIONS: ONE ALREADY REGISTERED AND NOW MEASURED, ONE NOT REGISTERED AT ALL AND NOW REGISTERED.**

**lines whose number changed above this section: 0** — this amendment is a **pure
append**; the assertion was **verified by diff in the committing invocation**, not
recited. Every line citation made elsewhere against this file (§1 lines 126–127,
§1 lines 199–205, §6.2 lines 781–818, §8.1, §8.3) is unaffected.

### A1.0 THE LEGALITY CONDITION, AND HOW IT WAS CHECKED

`CLAUDE.md` rule 2: *before first compute, amendments are legal **and must state
the condition and how it was checked** (name the run directory that does not
exist).*

**THE CONDITION: this rung has had NO FIRST COMPUTE.** How it was checked, in the
committing invocation of this amendment and not earlier:

- **`verification/runs/T-family/T21_runs/` DOES NOT EXIST** — measured absent in
  that invocation.
- **All six registered case directories of §8.1 do not exist**: `T21_CYL_c`,
  `T21_CYL_m`, `T21_CYL_f`, `T21_CYL_W1`, `T21_CYL_P1000`, `T21_CYL_S10`.
- **The reader was shown able to return a positive in the same invocation** on a
  directory that does exist, so the absence is not a zero from a blind reader
  (`CLAUDE.md` rule 3).

**This is NOT the §1 line 9 ABSENT REGISTRY discharge.** That one is owed **in the
committing invocation of the FREEZE** and is taken there. This reading
establishes only that no compute has occurred, which is what makes *this*
amendment legal.

**No gate, threshold, cap or label is altered by this amendment.** POINT
(9.1901 core-min), CAP (20.0 core-min, hard), every band of §1 line 4, the
ladder, the criteria order and the ceiling all stand exactly as written above.
This amendment adds **two file requirements to the case tree** and nothing else.

### A1.1 THE MEASUREMENT THIS RESTS ON

`verification/runs/T-family/T21_FEASIBILITY_PROBE_2026-09-03/` — a five-arm
case–solver feasibility probe run at 1 rank, **under 0.2 core-min as an upper
bound (not a measurement; wall was below `date +%s` resolution)**, drawn against
neither the POINT nor the CAP above. **It is a feasibility probe, not a graded
rung**: no verdict from `CLAUDE.md` rule 1's vocabulary is claimed for it, and
`FEASIBLE` is not offered as a synonym for `PASS`.

| arm | `regions ( … )` | rc | outcome |
|---|---|---:|---|
| A | `fluid () solid (core housing)` | **0** | `Time = 1`, `End`, fields written |
| B | `fluid ()` only | 1 | `solid not found in table.  Valid entries: 1(fluid)` |
| C | `solid (core housing)` only | 1 | `fluid not found in table.  Valid entries: 1(solid)` |
| **D** | as A, **`constant/g` deleted** | **1** | `cannot find file "…/constant/g"` |
| **E** | as A, **top-level `system/fvSolution` deleted** | **1** | `cannot find file "…/system/fvSolution"` |

**Arm A's `rc = 0` is evidence because four sibling arms on the same harness
returned `rc = 1`.** Arm B is the positive discriminator: its error names the
valid entries it *did* find — `1(fluid)` — proving `rp["fluid"]` at
`createFluidMeshes.H:1` **returned an empty list without throwing**, and that only
the later `rp["solid"]` fired. **Present-but-empty and absent are measurably
different**, which is precisely the distinction between this rung's
`regions ( fluid () … )` and the T5 `S_m` arm that was ruled `BLOCKED`.

### A1.2 REGISTERED (NEW): A **TOP-LEVEL `system/fvSolution` IS MANDATORY**

`chtMultiRegionSimpleFoam` reads the **top-level** (non-region) `system/fvSolution`
**unconditionally**, at
**`applications/solvers/heatTransfer/chtMultiRegionFoam/include/createCoupledRegions.H:3`**:

```
fvSolution solutionDict(runTime);
```

`runTime` is the **global** object registry, so this resolves to `system/fvSolution`
and **not** to any `system/<region>/fvSolution`. It executes **before any region
loop opens**, so an empty fluid region list does not save it — exactly the shape
of the `constant/g` trap already registered at §6.2, in a second file. The same
top-level dictionary is read again by
`loopControl looping(runTime, "SIMPLE", "energyCoupling")` at
`chtMultiRegionSimpleFoam.C:121`.

> **REGISTERED: a top-level `system/fvSolution` is part of this rung's case tree.
> A bare `SIMPLE { }` block suffices and is what is registered** — the same
> minimal form v2606's own `jouleHeatingSolid` tutorial ships. The per-region
> `system/core/fvSolution` and `system/housing/fvSolution` are separate files and
> do **not** satisfy this requirement.

**This requirement was registered NOWHERE in this document before this
amendment.** That was verified, not assumed: a grep of all 1,245 lines above for
`fvSolution` and `fvSchemes` returned **zero hits**. It is therefore registered
here for the first time and is **not** a duplicate of any existing clause.

**Why this had to land before the freeze and not after.** Arm E is a
first-launch fatal — `T21_CYL_c` would have died in `createCoupledRegions.H:3`
having consumed its mesh-build cost and produced nothing. Registering a
requirement **after** a freeze would be adding a requirement post-compute-close;
registering it now costs one commit and no compute.

### A1.3 STRENGTHENED (EXISTING, AND IT WAS ALREADY CORRECT): §6.2's `constant/g`

§6.2 (lines 781–818) registers `constant/g` as mandatory despite this rung having
no fluid region, citing `createFluidFields.H:26` — the gravity read at **file
scope**, above the `forAll` that opens at `:29` — and
`gravityMeshObject.C:43-55`'s `IOobject::READ_MODIFIED`. **That registration is
correct and is not changed.** Its evidence base is strengthened:

- **Before:** a source reading, plus a one-solid precedent on disk
  (`verification/runs/T-family/T20_runs/T20_LC_FEAS_20260831T151828Z/`, which
  ships a `constant/g` and completed at `rc = 0`).
- **Now, additionally:** **arm D — a direct fatal on deleting `constant/g` from a
  case with TWO solid regions and zero fluid regions**, which is this rung's own
  shape rather than a neighbouring one.

§6.2's registered value `value (0 0 0)` and its stated reasoning stand unchanged.

### A1.4 WHAT THE PROBE DOES **NOT** DISCHARGE — §8.3 IS ONLY HALF ANSWERED

§8.3 stages `T21_CYL_c` first to answer *"does `chtMultiRegionSimpleFoam` run to
completion with `regions ( fluid () solid (core housing) )`, **with an `fvOptions`
source on `h` in one solid region** and a `mappedWall` couple to the other?"*

**The probe answers the region-list and `mappedWall` halves. It does NOT answer
the `fvOptions` half, which carried no source at all.** §8.3's staging is
therefore **unchanged**, and so is its registered consequence: if `T21_CYL_c`
fails, the rung is **`BLOCKED`** on that finding and `solidFoam` enters only by
re-registration, never by silent substitution.

Also not exercised by the probe, and so not discharged by it: the **2-D
axisymmetric wedge at θ = 5.0°** (the probe was a 3-D hex box), this rung's
registered material properties (the probe used placeholders), and everything
after the first iteration — convergence, the closed-form reference, the Roache
triple, the error budget and every gate.

### A1.5 DECLARED OMISSION ADDED TO §10

**13. THE TWO CASE-TREE FILE REQUIREMENTS ARE MEASURED FOR THEIR *NECESSITY*, NOT
FOR THEIR *SUFFICIENCY*.** Arms D and E each show that the solver **fails without**
the file. Neither shows that the registered minimal content — `value (0 0 0)` for
`g`, a bare `SIMPLE { }` for the top-level `fvSolution` — is **sufficient for this
rung's own case**, which carries an `fvOptions` source and a wedge the probe did
not build. **Sufficiency is demonstrated by `T21_CYL_c` or not at all**, and §8.3
already stages exactly that.

---

## AMENDMENT 2 — 2026-09-03 — **THE FREEZE. THE DOCUMENT LEAVES `DRAFT` AND §1 LINE 10's `AUTHORISATION` IS FLIPPED. §1 LINE 9's ABSENT REGISTRY IS DISCHARGED HERE, IN THE COMMITTING INVOCATION, UNDER A LIVE PLANTED CONTROL.**

**lines whose number changed above this section: 0** — this amendment is a **pure
append**; the assertion was **verified by diff in the committing invocation**, not
recited. Nothing above is rewritten in place: the superseded text is **struck and
quoted verbatim below**, per `CLAUDE.md` rule 6. Every line citation made against
this file elsewhere (§1 lines 126–127, §1 lines 199–205, §6.2 lines 781–818,
§8.1, §8.3) remains valid at its original line number.

**Whose act this is.** The freeze is the **supervisor's own check-4 act** —
`CLAUDE.md`'s roster clause reserves *"pre-registration **committed** before
compute"* to the supervisor personally and forbids its delegation. This lane
executed the **mechanics** of the amendment and the commit; **the judgement that
this document is fit to freeze is the supervisor's, not this lane's**, and is
recorded here as such rather than being quietly absorbed into the paperwork.

---

### A2.1 §1 LINE 9 — **ABSENT REGISTRY: DISCHARGED**

**STRUCK, quoted verbatim** (§1 line 9, document lines 199–202), on the single
ground that its final sentence has been overtaken by events — this **is** now the
committing invocation:

> ~~**9. ABSENT REGISTRY.** `verification/runs/T-family/T21_runs/` and every
> registered case directory must be measured **ABSENT under a live planted
> control** in the committing invocation. **Not taken here** — this draft is not
> the committing invocation and a reading taken now is not transferable.~~

**THE READING — TAKEN FRESH IN THIS AMENDMENT'S OWN COMMITTING
INVOCATION, CONTROL FIRST, AT `2026-09-03T22:59:57Z` (`date -u`, read in that same
invocation).**

**Not one figure is carried across from the preserved copy.** The reading
that appears in `docs/campaigns/T-family/T21_FREEZE_AMENDMENT_PENDING.md`
was taken in a lane invocation that was **denied and never committed**;
that file rules it **not on the record and not transferable**, and §1
line 9 says in terms that *a reading taken now is not transferable*. The
clause is therefore discharged by the rows below and by nothing else.
Every row was produced by one reader — `os.path.isdir` on the repository
path — applied identically to the control and to each registered
directory, in the shell invocation that wrote this commit.

| # | directory | reading |
|---:|---|---|
| **0** | **`verification/runs/T-family/T20_runs/`** | **PRESENT — THE LIVE PLANTED CONTROL, READ FIRST** |
| 1 | `verification/runs/T-family/T21_runs/` | **ABSENT** |
| 2 | `verification/runs/T-family/T21_runs/T21_CYL_c` | **ABSENT** |
| 3 | `verification/runs/T-family/T21_runs/T21_CYL_m` | **ABSENT** |
| 4 | `verification/runs/T-family/T21_runs/T21_CYL_f` | **ABSENT** |
| 5 | `verification/runs/T-family/T21_runs/T21_CYL_W1` | **ABSENT** |
| 6 | `verification/runs/T-family/T21_runs/T21_CYL_P1000` | **ABSENT** |
| 7 | `verification/runs/T-family/T21_runs/T21_CYL_S10` | **ABSENT** |

**The control is what makes the seven absences evidence.** `CLAUDE.md`
rule 3: a zero from a reader not shown able to see a non-zero is not
evidence. The **same reader, in the same invocation, immediately before
the seven negative readings, returned `PRESENT` on `verification/runs/T-family/T20_runs/`**
— a directory that does exist. A reader that could see nothing at all
would have produced the identical seven `ABSENT`s and this discharge
would have been worthless. The guard **refuses with a non-zero exit — and
so aborts the commit — if the control does not read `PRESENT`, or if any
registered directory reads anything but `ABSENT`**; the reading therefore
cannot be recorded without its control.

`verification/runs/T-family/T21_FEASIBILITY_PROBE_2026-09-03/` is a **separate,
dated directory and is deliberately NOT `T21_runs/`**, precisely so that filing
the probe could not destroy the condition this clause asserts.

**The clause is discharged as written and its requirement is not weakened for any
future re-registration.**

---

### A2.2 §1 LINE 10 — **AUTHORISATION: FLIPPED**

**STRUCK, quoted verbatim** (§1 line 10, document lines 204–205):

> ~~**10. AUTHORISATION.** This document authorises **no solve**, and in its present
> DRAFT state it is not even a candidate for one.~~

**REPLACED BY, and this is the operative text from this amendment forward:**

> **10. AUTHORISATION — FROZEN 2026-09-03.** This document is **FROZEN**. Its
> gates, thresholds, bands, ladder, criteria order, cap and label are **CLOSED**
> and may not be altered; from this commit forward changes land only as **dated
> addenda that cannot alter a gate, threshold, cap or label**, and originals are
> **struck, never rewritten** (`CLAUDE.md` rule 2). The registered run set of
> §8.1 is **authorised to be built and run** within the registered **CAP of 20.0
> core-min, hard — an overrun STOPS the run and does not get a new budget.**
>
> **THIS DOCUMENT IS A FROZEN REGISTRATION. IT IS NOT A QUEUE-READY CASE, AND IT
> MUST NOT BE COUNTED TOWARD FREEZE-AHEAD.** T21 has **no builder, no launcher
> and no comparator** — §11 says so in terms, and they are a separate act under a
> separate review in which the supervisor reads measurement-script diffs **as
> diffs**, personally. Nothing may be enqueued or launched against this document
> until those three exist and have been reviewed.

---

### A2.3 THE DOCUMENT'S `STATUS` BLOCK — **SUPERSEDED**

**STRUCK, quoted verbatim** (document lines 3–10):

> ~~**STATUS: DRAFT. NOT FROZEN. NOT COMMITTED. AUTHORISES NOTHING.**
> Drafting was **stopped mid-document on the supervisor's instruction**
> (2026-08-31) after Sanaa ruled **feasibility-first**: no freeze is required for
> a feasibility or physics rung, and Case 3's first act is therefore the
> variant-(b) L1 build, not this gate. **This file is preserved in place because
> every number in it was derived and every source claim in it was checked against
> the installed tree; it is intended to become the gated rung's registration
> later.** Nothing below is binding until a supervisor freezes it by commit.~~

**REPLACED BY:**

> **STATUS: FROZEN 2026-09-03 by commit. Gates CLOSED.** The document is binding
> from that commit. **It authorises the §8.1 run set within the §7.2 cap and
> nothing else**, and it remains a **frozen registration and not a queue-ready
> case** (§A2.2).

**The feasibility-first ruling that stopped this draft is NOT overturned, and
recording that matters.** Sanaa's ruling was that **no freeze is required for a
feasibility or physics rung**. That ruling stands untouched. What changed is
narrower and is a matter of fact rather than of policy: T21 is the **gated
EXACT-tier rung** the stopped draft always said it was *"intended to become"*,
and the one open question about whether it could be gated at all — whether the
registered `regions ( fluid () solid (core housing) )` and the registered solver
were mutually satisfiable — **has now been measured** (Amendment 1 §A1.1;
`verification/runs/T-family/T21_FEASIBILITY_PROBE_2026-09-03/`). **The freeze
follows the feasibility answer; it does not pre-empt it.** That ordering is the
whole point, and it is the ordering the T5 `S_m` arm did not get.

---

### A2.4 WHAT THIS FREEZE DOES **NOT** DO

- It **does not create** `verification/runs/T-family/T21_runs/`, which §A2.1
  measured absent and which remains absent at this commit.
- It **does not build a case, write a builder, a launcher or a comparator, enqueue
  anything, or launch anything.** §11 stands unchanged.
- It **does not add T21 to any team's freeze-ahead count** (§A2.2).
- It **does not resolve** the three questions §11 offers upward to verification —
  the steady `residualControl` reading (§6.1), the `writePrecision`-versus-band
  standard (§2.4), and the signed-plant clause (§5.4 clause 10). All three remain
  open and none is a request for relief.
- It **does not assert any verdict.** No term of `CLAUDE.md` rule 1's vocabulary
  is claimed anywhere in this document, and the feasibility probe's `FEASIBLE`
  finding is **not** a `PASS`.
