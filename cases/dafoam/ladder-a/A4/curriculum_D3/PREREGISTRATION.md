# Curriculum item D3 — A4 Ahmed body, CONSTRAINED drag minimisation: PRE-REGISTRATION

**Frozen 2026-08-24T17:40:44Z** (`date -u`, read in the invocation that wrote this file).
**Author:** dafoam `lab-lane` (Opus), dispatched by dafoam-supervisor. **PHASE 1 ONLY.**

**ZERO COMPUTE HAS BEEN SPENT. No container was started, no solver ran, and the run root
`/home/ubuntu/certonomous-runs/D3-a4-constrained/` does not exist** — its absence is asserted
inside the commit invocation that freezes this file (§13).

**Curriculum authority:** `cases/dafoam/EXPERTISE_CURRICULUM.md` §3, Tier 1, row **D3** —
*"Ahmed drag min + volume/rear-slant constraints (A4 case) | 3D constraints on separation-dominated
flow | A4 PASS — met | ~70 core-min, $0.06 | as D1; separation-onset monitor registered | wake
bistability making the objective noisy (η measured first, per N-D15's δ_repeat discipline)"*.

**Ratification and the reading that binds it** (`EXPERTISE_CURRICULUM.md` §7, Sanaa 2026-08-23,
verbatim via the chief's session record):

> YOU have my approval also for the heat transfer and dafoam proposals. SO... dafoam team can start
> working on their dafoam tasks from the dafoam proposal. Per usual, each team must formally update
> their respective .md files accordingly with the knowledge, the lessons, the processes, the
> summaries etc, and update the general lab's logic/knowledge and expertise if there is new
> knowledge that the entire lab must have.

The conservative reading that governs this item, quoted from §7 clauses 1–2:

> 1. It authorizes **starting execution** of this curriculum in the recommended sequence, with every
>    item under its own frozen, costed pre-registration, and only **pre-authorised-class items
>    (<$25) run on it**.
> 2. It is **NOT** read as: a per-item cost reading (rule 9 — the blanket is not one); approval of
>    Tier 6 …; the D464 **N=29 gate reading** …; or approval of anything a future prereg finds
>    unusual — **anything unusual, above pre-authorised cost, or outside these pages goes back to
>    Sanaa costed, not read into the blanket.**

§12 applies the "unusual" test item by item and names what is referred and what is not.

**Nothing is filed, sent, uploaded, posted or pushed anywhere** (`CLAUDE.md` rule 7).

---

## 0. What this item is, in four lines

1. The A4 Ahmed body (25° slant, 2,777-cell adjoint mesh, `DASimpleFoam`, np=1) driven by IPOPT
   through pyOptSparse — **now with two design variables and two geometric constraints**, where A4
   had one design variable and **no constraints at all**.
2. It is **phase-split**: the objective's own noise floor δ_repeat is measured **first**, at its own
   price, against a stop rule frozen here. If the noise swamps the signal, **the optimisation is
   never launched** and the item reports the noise floor.
3. Its separation-onset monitor is registered here **together with the measurement, already taken at
   zero compute, that predicts the monitor will refuse on this mesh** (§7). That refusal is the
   registered outcome, not a surprise.
4. Its claim is about **constrained optimisation and gradients**, never about Ahmed-body
   aerodynamics — the 2,777-cell mesh exists only to host a gradient (A4 shipped `RESULTS.md` §8
   limit 4), and §7 now measures exactly how far that limit reaches.

---

## 1. Provenance of every input

| input | value | source, on disk |
|---|---|---|
| case, mesh | Ahmed 25°, **2,777 cells**, np=1 | `/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/base/`, `log.checkMesh:35` reads `cells: 2777` |
| geometry | `ahmed_25.stl`, md5 **`ec3abd312d3e3e9d15340b95365ff62f`**, bbox x[0, 1.044] y[±0.1945] z[0, 0.288] | read at freeze from `base/constant/triSurface/ahmed_25.stl` |
| FFD | `FFD/ahmedFFD.xyz`, **3×2×2 = 12 control points**; i-planes x = {−0.02, 0.80, 1.07}, j = {−0.21, +0.21}, k = {−0.02, 0.31} | read at freeze from the PLOT3D file |
| A4 verdict inherited | **PASS / PASS** two-row; patch **immaterial at the optimum**; CD **−7.4775 %** | `A4/shipped_optimisation_np1/RESULTS.md` §9 |
| A4 optimiser anchor | 6 majors, `EXIT: Optimal Solution Found.`, NLP error `6.9114e-08`, 16 objective / 7 gradient evaluations, **11.583 core-min**, peak RSS **1.007 GiB** | same file §2, §6; `opt/opt_IPOPT.txt` |
| A4 first-major ΔCD | `1.5297473e-01` → `1.5156693e-01` = **1.40780e-03** | same file §2 table, iter 0→1 |
| A4 endpoint FD path-dependence | **0.183 %** between two runs reaching the same point by different paths | same file §3.2 |
| A4 baseline analytic gradient | `dCD/dshape` = **`0.24149949`** (patched), `0.23965` (shipped) | same file §4.2 |
| δ_repeat discipline | **N-D15** — solve-to-solve noise and within-run wobble are different quantities and differed 2.47× on A6; *"which one is the right denominator … is fixed in the pre-registration before the run, never after"* | `docs/NUMERICS_KNOWLEDGE.md:3250-3257` |
| constraint API precedent, 3D blunt body | `nom_addVolumeConstraint`, `nom_addThicknessConstraints2D`, `nom_addLinearConstraintsShape` | `/home/ubuntu/dafoam-tutorials/JBC_Hull/runScript.py:175,180,185,202-205` |
| constraint API precedent, this lab | same three plus `nom_addLERadiusConstraints`, run to **PASS** | `A1/curriculum_D1_Cprime/d1c_runScript.py:152-156, 175-177` |
| toolchain hashes | patched `85f59e87253e0a71a813f64ca6e4c425`; shipped `f0fcb488e0e98156575cd19548e91663` | `A4/shipped_optimisation_np1/RESULTS.md` §1 |

**One provenance limitation, stated:** the two image hashes above are taken **from the A4 record**,
not from a live `docker images` query — the docker socket refused this lane at freeze time
(permission denied). They are therefore **inherited, not re-verified at freeze**. G7 re-verifies them
at run time from **inside the loading process**, which is the check that actually matters.

---

## 2. The problem, exactly

### 2.1 What A4's own runScript contains — read line by line, and what it does NOT contain

Reference file: `/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/opt_runScript.py`,
**md5 `387a09b76d4774186be4b83a80f14e8a`**, 195 lines, the file that produced A4's PASS.

| line | what is there |
|---|---|
| 32–83 | flow parameters, `daOptions` (CD **and** CL functions defined), `meshOptions` |
| **82** | `"symmetryPlanes": []` — IDWarp symmetry auto-detection **disabled**; the mesh is the **full, non-half** body and carries **no symmetry plane** |
| 93 | `OM_DVGEOCOMP(file="FFD/ahmedFFD.xyz", type="ffd")` |
| 101 | `nom_add_discipline_coords("aero", points)` |
| 107 | `pts = self.geometry.DVGeo.getLocalIndex(0)` |
| **109** | `shapes = [{pts[1, 0, 1]: dir_z, pts[1, 1, 1]: dir_z}]` — **one** shape function, pairing the two j control points at i=1, k=1, moved purely in z |
| 110 | `nom_addShapeFunctionDV(dvName="shape", shapes=shapes)` |
| 115 | `add_design_var("shape", lower=-0.05, upper=0.05, scaler=1.0)` |
| 116 | `add_objective("scenario1.aero_post.CD", scaler=1.0)` |
| 129–145 | `pyOptSparseDriver`, IPOPT, `tol 1e-6`, `constr_viol_tol 1e-6`, **`max_iter 15`** |

**What is absent, verified by grep over all 195 lines:** there is **no** `nom_addVolumeConstraint`,
**no** `nom_addThicknessConstraints1D/2D`, **no** `nom_addLERadiusConstraints`, **no**
`nom_addLinearConstraintsShape`, and **no** `add_constraint` of any kind. **A4 is an unconstrained
box-bounded problem in one variable.** Line 115's bounds are the only restriction on the design.

**Consequence registered here:** D3's constraints do not exist in the case and **must be added**. A
one-variable problem also cannot exercise a constraint in any meaningful sense — with one DV, an
active geometric constraint either fixes the design or is inert. **D3 therefore extends the design
space to two variables.** That extension is the item's one substantive departure from A4's frozen
setup and is put on the supervisor's desk by name in §12.

### 2.2 The registered design variables

Both are shape-function DVs moving a **symmetric pair** of FFD control points purely in z, in
exactly A4 line 109's pattern:

| DV | FFD control points | x of the i-plane | role | bounds |
|---|---|---|---|---|
| **`shapeBreak`** | `pts[1,0,1]`, `pts[1,1,1]` | **0.80** | roof height just upstream of the slant break | [−0.05, +0.05] |
| **`shapeRear`** | `pts[2,0,1]`, `pts[2,1,1]` | **1.07** | rear-top height aft of the body's rear edge | [−0.05, +0.05] |

`shapeBreak` **is A4's DV, unchanged**. Nose (i=0) and the entire underbody (k=0) are untouched by
construction. Together the pair sets the **rear-slant angle** (§2.5).

### 2.3 The registered constraints — added, with the API and bounds fixed here

| name | call | bounds | why |
|---|---|---|---|
| **`thickcon_slant`** | `nom_addThicknessConstraints2D("thickcon_slant", LE_AFT, TE_AFT, nSpan=5, nChord=6)` | `lower=0.85, upper=1.15` | the **rear-slant constraint**: the aft body's local thickness may not change by more than ±15 % of baseline, so the optimiser cannot collapse or balloon the slant |
| **`volcon_aft`** | `nom_addVolumeConstraint("volcon_aft", LE_AFT, TE_AFT, nSpan=5, nChord=6)` | `lower=0.98` | the **volume constraint**: the aft body may lose at most 2 % of its enclosed volume — the classic "shrink it to reduce drag" degenerate solution is forbidden |

with the constraint region frozen **inside the body** in all three coordinates (body spans
x[0, 1.044], y[±0.1945], z[0, 0.288]):

```
LE_AFT = [[0.86, -0.17, 0.10], [0.86, 0.17, 0.10]]      # spanwise line just aft of the break
TE_AFT = [[1.03, -0.17, 0.10], [1.03, 0.17, 0.10]]      # spanwise line just forward of the rear face
```

pyGeo normalises both constraint families to **1.0 at the baseline**, which is why the bounds are
written as ratios (JBC_Hull `runScript.py:202-204`; D1-C′ `d1c_runScript.py:175-177`).

### 2.4 Symmetry — enforced by construction, and `nom_addLinearConstraintsShape` DECLINED by name

Every shape function moves its j=0 and j=1 control points **together**, so **no deformation this
parametrisation can express is asymmetric in y**. The JBC_Hull "reflect" pattern
(`nom_addLinearConstraintsShape("reflect", indSetA, indSetB, …)` +
`add_constraint(…, equals=0.0, linear=True)`, that file's lines 124 and 205) is therefore
**declined by name**: it would add an optimiser constraint that is identically satisfied, and it is
a code path this case has never run.

**The decline carries a check, not an assumption.** Stage G measures
`max |z(x, +y) − z(x, −y)|` over the deformed surface at a test DV value and reports it. **Registered
threshold: ≤ 1e-9.** A reading above that falsifies "by construction" and the item says so.

### 2.5 The rear-slant angle — a graded MONITOR, not an optimiser constraint, and why

The slant runs from the break `(x, z) = (0.8428, 0.288)` to the rear-edge top `(1.044, 0.1942)`:
Δz = 0.0938 over Δx = 0.2012, i.e. **tan θ = 0.46620, θ = 25.00°** — the design angle, recovered
from the STL and the FFD independently at freeze.

Under the trilinear FFD, a body point's z-displacement from the k=1 row is
`w·[(1−u)·d_i + u·d_{i+1}]` with `w = (z + 0.02)/0.33` and `u` the local i-fraction. For the two
probe points this gives the **frozen coefficients**

```
d(tanθ·Δx)/d(shapeBreak) = +0.72287        d(tanθ·Δx)/d(shapeRear) = −0.43863
θ(d1, d2) = atan( (0.0938 + 0.72287·d1 − 0.43863·d2) / 0.2012 )
```

**Independent check already run, at zero compute:** the comparator's own control [12] evaluates this
formula at `d = (0, 0)` and returns **24.9951°** against the design 25.00° — the geometry model
reproduces the case's own slant angle to 0.005°. Control [13] evaluates it at A4's optimum
`d = (−0.05, 0)` and returns **15.990°**: A4's PASS reduced the slant angle from 25° to ≈16°.

**Registered band: θ(optimum) ∈ [12.0°, 25.0°].** The upper edge is the baseline itself — an
optimiser that *increases* the slant angle is walking toward the 25–30° critical regime that this
mesh cannot resolve, and that must be caught. **Band exit meaning:** `GATE FAIL` on Gθ, and every
*aerodynamic* reading of the item becomes `NOT A RESULT`; the optimiser, constraint and gradient
verdicts stand on their own gates.

**Why a monitor and not a constraint.** The coefficients above are analytic and unverified against
pyGeo at freeze. A wrong coefficient in an *optimiser constraint* silently wastes the whole buy; a
wrong coefficient in a *monitor* is a finding. **Stage G re-measures both coefficients** and the
comparator substitutes the measured pair when it is present. **Registered agreement threshold:
measured versus frozen within 2 %**; a wider gap means the geometry model is wrong, is reported as
such, and Gθ is `NOT A RESULT`.

---

## 3. Toolchain — two rows (`DAFOAM_CHARTER.md` §6)

| row | image | `libidwarp.so` md5 | stages | graded? |
|---|---|---|---|---|
| **PATCHED** | `dafoam-idwarp-rot:v1` | `85f59e87253e0a71a813f64ca6e4c425` | **G, η, O, T-patched** | **YES — this is the graded row** |
| **SHIPPED** | `dafoam/opt-packages:latest` | `f0fcb488e0e98156575cd19548e91663` | **T-shipped only** | reported as its own row; not the graded row |

**Why the patched image carries the optimisation.** A4 measured the patch **material at the
undeformed baseline** (1.1032 % shipped against 0.33929 % patched — a 3.25× tightening) and
**immaterial at the deformed optimum** (`RESULTS.md` §4.2). The optimisation starts at the baseline,
so the row with the better baseline gradient drives it. R11 adoption stays **case-dependent, not
global** (`EXPERTISE_CURRICULUM.md` §1; N-D18 measured the rotation patch *degrading* an A3 gradient).

### 3.1 What the shipped row buys, what it defers, and both prices

**Bought (Stage T):** the endpoint gradient on **both** images at the **same design vector reached by
the same path**, each from a **cold start** on a pristine staged copy. **Deferred:** a full shipped
optimisation twin.

This is not a cost dodge — it is the arm A4 identified as missing. A4 shipped `RESULTS.md` §8 limit 3:

> **The endpoint comparison is not a toolchain comparison** (§3.2). The two endpoint errors differ
> because their **FD references** differ by 0.18 %, and that difference is path-dependent. **A clean
> toolchain comparison at a deformed design would require running both images' `check_totals` at the
> *same* design point reached by the *same* path** — an arm this item did not register and did not buy.

**Stage T is that arm.** Deferred price of the full shipped twin, stated so the deferral is costed:
**≈ 17 core-min ≈ $0.0145 derived** (Stage O's own prediction). Buying it would put the item at
≈ 47 core-min predicted, whose 100 % contingency exceeds the 70 core-min curriculum ceiling — so it
is deferred **for the ceiling, and the ceiling is the curriculum's own figure**.

### 3.2 The A4 immateriality is a registered prediction to RE-TEST, never an assumption

A4 measured the patch immaterial **at one design variable, at one deformation**, and stated three
limits on that claim (`RESULTS.md` §4.2): one DV moved 0.05 in z; the endpoint pair cannot resolve
below ≈ 4e-06 relative; and it is a statement about this case's gradient, not about the defect.
**D3 has two DVs.** P8 (§5) registers the re-test with a band and a falsifier.

---

## 4. Stages

| stage | what runs | image | flow solves | `-task` |
|---|---|---|---|---|
| **G** | geometry probe: every DVGeo/DVCon call, the FFD z-Jacobian, the symmetry measurement, the constraint values at baseline | patched | **none** | `geom_probe` |
| **η** | δ_repeat of CD at the baseline + the planted perturbation | patched | 3 primals | `eta` |
| **O** | the constrained optimisation + the in-process endpoint FD sweep at the optimum | patched | many | `run_driver` |
| **T** | endpoint gradient at Stage O's frozen design vector, cold, once per image | patched, then shipped | 2 × 5 primals | `endpoint_at` |

**Stage G runs first and is not flow.** It exists because the D1-C′ incident (L-273) cost a graded
row to a defect that a dry run against the frozen inputs would have caught. Stage G exercises the
exact frozen script's setup path — `getLocalIndex`, both `nom_addShapeFunctionDV` calls,
`nom_addThicknessConstraints2D`, `nom_addVolumeConstraint`, `add_constraint` — **without buying a
single primal**. Stage η is the first flow stage and the first gate on a measured quantity.

### 4.1 The frozen executables

| file | md5 at freeze | role |
|---|---|---|
| `d3_runScript.py` | **`af2ce474e7954c03e3937161510f6590`** | producer, all four stages |
| `d3_grade.py` | **`a32f075853e264910ee0a6c2473fd948`** | comparator |
| `d3_sep_monitor.py` | **`cd07d7b8a70627579384f263ba92194e`** | separation-onset monitor |

All three pass `python3 -m py_compile` at freeze. **Honest limitation:** `py_compile` checks syntax
only. `openmdao`, `dafoam`, `pygeo` and `idwarp` exist **only inside the container**, so no import
of `d3_runScript.py` is possible at zero compute and **its API calls are unverified until Stage G
runs them.** That is precisely Stage G's job, and §4.3 says what happens if it fails.

### 4.2 The design vector handoff, and its one deferred value

Stage T reads `{"shapeBreak": …, "shapeRear": …}` from a JSON written by the launcher out of Stage
O's `d3_summary.json`. The **mechanism** is frozen here; the **value** is Stage O's output. Stage T's
first assertion is that its own `run_model` reproduces Stage O's `final_CD` — registered tolerance
**≤ 1e-9 relative** on the patched arm, which is the same code at the same design point. A wider gap
means the handoff did not deliver the design vector and Stage T is `NOT A RESULT`.

### 4.3 Repair policy — no in-place edit of a frozen file, at any stage

If any stage crashes, that stage is **`BLOCKED`**, the crash is a **finding** until triage says
otherwise (`SUPERVISION_CHARTER.md` §3), and **no frozen file is edited**. A repair, if one is
warranted, is a `VERIFICATION_CHARTER.md` §2d.1 four-condition decision **for the supervisor**, and
any re-registered work is a **new mini-item** in the D1-C′ pattern — never an edit that voids the
arms already run. This clause exists because D1's arm C hit exactly this and the frozen file's own
§4.2(c) forbade the in-place repair (L-273).

---

## 5. Predictions, with bands and the basis of each

| id | prediction | band / HIT rule | basis |
|---|---|---|---|
| **P1** | Stage G completes with every DVCon call returning a finite baseline value | `thickcon_slant` and `volcon_aft` both non-empty, all values finite and within 1e-6 of 1.0 (pyGeo normalises to baseline) | JBC_Hull + D1-C′ precedent; pyGeo normalisation |
| **P2** | Stage G's measured FFD Jacobian agrees with §2.5's frozen coefficients | measured `(cB, cR)` within **2 %** of `(+0.72287, −0.43863)` | analytic trilinear FFD; the 24.9951°-vs-25.00° check |
| **P3** | Stage G symmetry residual | `max|z(+y) − z(−y)| ≤ 1e-9` | symmetry by construction (§2.4) |
| **P4** | **δ_repeat at the baseline** | **[0, 1.4e-05]**, point estimate ≈ 1e-06 | N-D15 measured 2.2104e-06 on A6 at CD ≈ 0.0351 (6.3e-05 relative); scaled to CD = 0.153 that is ≈ 9.7e-06, and A4's baseline CD was **bit-identical across two images and two days** (`RESULTS.md` §2.1 P5) |
| **P5** | the η plant is seen | `|ΔCD|` from `shapeBreak = 1e-4` in **[1.0e-05, 4.0e-05]**, point estimate **2.415e-05** | A4's patched baseline gradient `0.24149949` × 1e-4 |
| **P6** | Stage O termination | `EXIT: Optimal Solution Found.`, NLP error < 1e-6, **majors ∈ [7, 14]** | A4 took **6** with 1 DV and no constraints; 2 DVs + 2 constraints adds barrier and feasibility work. **A4's own P2 missed low by anchoring on the wrong quantity** (`RESULTS.md` §2.1) — this band is deliberately wide and its miss direction is expected to be low again |
| **P7** | CD reduction | **≥ 7.478 %**, band **[7.4 %, 16 %]**, point estimate ≈ 9 % | A4 reached −7.4775 % with `shapeBreak` alone; `shapeRear` adds a descent direction, so the constrained 2-DV optimum can only be **at least as good** unless a constraint binds first. D1's 2-DV-plus-AoA analogue overshot its band high (16.310 % vs [2, 12] %), so the upper edge is generous |
| **P8** | **the A4 immateriality re-test** | the two images' **analytic** gradients at Stage T's design point agree to **≤ 1e-4 relative per component** | A4 measured **3.9e-06** at 1 DV (`RESULTS.md` §3.1). The band is 25× looser because D3 has two DVs and A4's own limit (i) says nothing transfers |
| **P9** | endpoint FD | per-component relative error in **[0.1 %, 2.0 %]**, **zero sign flips** | A4 endpoint measured **0.3112 %** (shipped) / **0.4936 %** (patched) |
| **P10** | rear-slant angle at the optimum | **θ ∈ [14°, 22°]** inside the Gθ band [12°, 25°] | A4's optimum computes to **15.990°**; `shapeRear` can move it either way |
| **P11** | **the separation monitor REFUSES** | `n_rev_global = 0` and `n_cells(B) < 20` on Stage η's own baseline field ⇒ **NOT AN INSTRUMENT** | §7 — measured at freeze on three archived A4 fields |
| **P12** | wake momentum ratio | `m_def_global = min(U_x)/U0` at the optimum in **[0.45, 0.75]** | measured 0.5882 / 0.6024 / 0.6021 on three archived A4 fields (§7) |
| **P13** | peak RSS | **≤ 2.5 GiB**, point estimate 1.4 GiB | A4 measured **1.007 / 1.331 GiB** at np=1 |
| **P14** | cost | total **≤ 51.6 core-min** (prediction + 100 % contingency), HARD **≤ 70** | §8 |

---

## 6. Gates — every one with its number

### Gη — the noise-floor stop rule. Stage O does not launch until this passes.

Registered signal reference: **A4's own first-major |ΔCD| = 1.40780e-03**
(`0.15297473 − 0.15156693`, shipped `RESULTS.md` §2, iteration 0→1). Same case, same mesh, same first
design variable; the second DV can only make the first major larger, so this is a **conservative**
reference.

| outcome | condition | consequence |
|---|---|---|
| **REFUSE** | the planted perturbation moves CD by **< 1.0e-05** | the η reader is not shown able to see a non-zero ⇒ **item `BLOCKED`**, Stage O NOT LAUNCHED (`CLAUDE.md` rule 3) |
| **η-PASS** | δ_repeat ≤ **1 % × 1.40780e-03 = 1.4078e-05** | Stage O launches, all gates live |
| **η-MARGINAL** | 1.4078e-05 < δ_repeat ≤ **10 % = 1.4078e-04** | `GATE REACHED`. Stage O launches **under a restriction frozen now**: every major whose accepted \|ΔCD\| < 10·δ_repeat is **`NOT A RESULT`** in advance, and the reported reduction carries ±10·δ_repeat |
| **η-FAIL** | δ_repeat > **1.4078e-04** | `GATE FAIL` on Gη ⇒ **item `BLOCKED`** — the objective's noise floor exceeds 10 % of the registered signal. **Stage O is NOT LAUNCHED**, the item reports the measured noise floor and its ratio to the signal, and **spends nothing further** |

**Which denominator, fixed here as N-D15 requires.** The graded quantity is **δ_repeat — the
solve-to-solve difference between two back-to-back `run_model` calls in one process**, not the
within-run iteration wobble. That is the quantity a central finite difference and an optimiser line
search actually see. The within-run peak-to-peak is **not** graded and is not collected.

**δ_repeat = 0.0 exactly is a legitimate η-PASS *only* with the plant seen**, and is then reported as
"below the write precision", with the plant's own ΔCD quoted as the resolution bound. Without the
plant it is `BLOCKED`.

**Registered second noise figure, disclosed, not graded:** A4 §3.2 measured the endpoint **FD
reference** moving **0.183 %** between two runs reaching the same design point by different paths —
roughly three orders of magnitude above the predicted δ_repeat. **δ_repeat is the floor on the
objective; 0.183 % is the floor on the FD instrument.** They are different quantities with different
jobs and the item never substitutes one for the other.

### G1 — constraint satisfaction at the accepted design

IPOPT's own `Constraint violation....:` ≤ **1e-6** (the `constr_viol_tol` in the frozen opt_settings)
**AND**, re-read independently by the comparator from `d3_summary.json`: every `thickcon_slant` value
in **[0.85 − 1e-6, 1.15 + 1e-6]** and every `volcon_aft` value ≥ **0.98 − 1e-6**. An **empty**
constraint array is **`NOT A RESULT`**, never a pass — nothing was graded.

### G2 — termination (`DAFOAM_CHARTER.md` §9)

`PASS` only on `EXIT: Optimal Solution Found.` **with** Overall NLP error < 1e-6. A stop on
`max_iter 15`, on the `timeout`, or on any external cap is **`GATE REACHED`** where the registered
intermediate threshold (reduction ≥ **7.478 %**, P7's floor) was met and **`NOT A RESULT`** otherwise
— **never `PASS`, and never described by the size of the improvement it reached**.

### G3 — endpoint FD spot-check, per component, at the plateau step

Steps swept **in the same process** at Stage O's optimum: **{1e-1, 1e-2, 1e-3, 1e-4}**, central,
`step_calc=abs`.

**Frozen plateau rule** (`DAFOAM_CHARTER.md` §3 — *"a flat curve is per component or it is not
flat"*): the graded step is the one in **{1e-2, 1e-3, 1e-4}** whose FD value differs from **both**
neighbours by **≤ 25 % of its own value, for every component**. If no step satisfies it, **no plateau
exists and G3 is `NOT A RESULT`** — no step is graded by default.

**Band: per-component relative error ≤ 15 % with zero sign flips.** The **aggregate is never the
graded quantity** — A2's idx46 sign flip hid inside a 0.0506 % aggregate on the *patched* image, and
the comparator recomputes per-component errors from the raw `Jfor`/`Jfd` arrays rather than reading
the printed summary line.

### G4 — trivial baseline (`DAFOAM_CHARTER.md` §4): the same probe at a deliberately wrong step

**Step 1e-1**, two orders off the expected plateau. **It must FAIL the 15 % band or produce a sign
flip.** If the deliberately wrong step also passes, **the gate is not discriminating and G3 is
`NOT A RESULT`** regardless of what the plateau step said.

### G5 — planted-zero control (`CLAUDE.md` rule 3, as sharpened by L-273)

**Already run, at zero compute, before this freeze — output pasted in §14.** Twelve controls, all
SEEN, planted into files the **A4 producer actually wrote** (`opt/opt_IPOPT.txt`, `opt.log`), plus a
**producer/consumer key-set assertion** for the one artifact no producer can have written yet.

### G6 — launch gate, run as its own command before **every** launch

**`free_cores ≥ 4` AND `MemAvailable ≥ 12 GiB`**, where `free_cores := nproc − load1`. The **12 GiB
floor is the lab's standing floor: this item neither touches it nor argues with it**
(`EXPERTISE_CURRICULUM.md` §5 lists it among the untouched holds). The gate is a **separate command**
whose stamped output is appended to `preflight_history.txt` and **read before the launch command is
issued** — never polled by a background process, never inferred. If it is shut, the arm **waits and
the gate is re-run**; it is not launched under a departure on a lane's own authority. Any departure
must be **directed in writing by the supervisor and recorded as a dated amendment before the
launch** (the A4 Amendment-1 precedent, `RESULTS.md` §7).

### G7 — image identity

`IDWARP_SO_MD5`, printed **from inside the process that loaded the library**, equals
`85f59e87253e0a71a813f64ca6e4c425` (G, η, O, T-patched) or `f0fcb488e0e98156575cd19548e91663`
(T-shipped). A mismatch **voids that stage**. `nProcs : 1` is asserted in every log.

### G8 — cold start, verified **before** each launch, never after

No `processor*` directory, no numeric time directory (`0.0001`, `500`, …), `0/` restored from
`0.orig/`, no `reports/` carried over. `DAFOAM_CHARTER.md` §6 records why: **pyDAFoam writes the
primal end state back into the time-0 directory at run end, so a second run of a case directory
silently warm-starts.** Stage η's `eta_call1_CD` reproducing A4's `0.1529738469354696` is the free
check that this held.

### G9 — memory envelope (`DAFOAM_CHARTER.md` §7)

Predicted peak **1.4 GiB**, ceiling **2.5 GiB** (P13). **Kernel cap `--memory=6g --memory-swap=6g`**
— equal, so there is no swap escape — plus `--oom-score-adj=500` and the per-stage `timeout`. **A
container the kernel OOM-killed (`.State.OOMKilled == true`, or exit 137) is recorded as stopped by
memory and is `NOT A RESULT` about convergence.** Equally: **a failure with headroom unused is not a
memory finding either**, and the measured peak is reported beside the cap.

### G10 — cost ceiling

**HARD ceiling 70.0 core-min = $0.0598 DERIVED.** An overrun **stops the run**; it does not get a new
budget (`CLAUDE.md` rule 12). §8.

### Gs — the separation-onset monitor. Registered together with its predicted refusal.

Defined concretely in §7, from fields A4 writes, with its instrument conditions, its band, and what a
band exit means.

### Gθ — the rear-slant angle monitor. §2.5. Band **[12.0°, 25.0°]**.

---

## 7. The separation-onset monitor — definition, band, and the measurement that predicts it refuses

### 7.1 Definition, from fields the case already writes

`DASimpleFoam` writes `U`, `p`, `k`, `omega`, `nut`, `phi` into each time directory; DAFoam writes one
per design point (A4's `opt/` holds `0.0001` … `0.0008` and `500`). No function object, no
`wallShearStress`, no case-file change is needed, and **the monitor costs zero solver time**:
`d3_sep_monitor.py` reads the field and the `polyMesh` in **pure Python**.

Two quantities, with different strengths, both registered:

**Primary — `m_def_global = min over all cells of U_x / U0`.** Exact, whole-domain, 2,777 cells, no
box, **no cell-centre approximation**. This is the graded scalar.
**Registered band: `m_def_global`(optimum) ∈ [0.45, 0.75]** (P12).

**Secondary — `f_sep(B)` = the reverse-flow cell fraction inside the frozen box**
`B = x[0.84, 1.10] × y[−0.20, 0.20] × z[0.10, 0.35]`, the rear slant and its immediate near wake.
Cell centres are the **vertex average of each cell's face vertices** — an approximation used **only
for box membership**, never for a graded number, and registered as such.

**Instrument conditions, frozen:** (i) `n_cells(B) ≥ 20`; (ii) the reader must be shown able to see a
non-zero on a case of this class; (iii) `n_rev_global ≥ 1` on the graded field. **(i) or (iii)
failing ⇒ the monitor prints `NOT AN INSTRUMENT` and exits 3.** Exit 3 is the registered refusal, not
a failure of the run.

### 7.2 The measurement, taken at zero compute before this freeze

Run on three archived A4 fields on the 2,777-cell mesh, with the rule-3 plant supplied:

```
PLANT  file=/home/ubuntu/certonomous-runs/act7-ahmed_25-b14562/154/U ncells=79439 n_rev_global=528 min_Ux=-13.7719
PLANT SEEN: the reader resolves reverse flow on this case class.
FIELD  file=/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/opt/0.0001/U ncells=2777
  n_rev_global = 0
  min_Ux       = 23.526042  m_def_global = min_Ux/U0 = 0.588151
  box B  n_cells=   2 n_rev=   0 f_sep=0.000000
  box Bp n_cells=   6 n_rev=   0 f_sep=0.000000
VERDICT: NOT AN INSTRUMENT -- (i) n_cells(B)=2 < 20; (iii) n_rev_global=0 -- no separated flow exists on this mesh
  m_def_global = 0.588151 is still reported and IS graded (exact, whole-domain, no centre approximation).
exit=3
```

The other two archived fields read the same way: `opt/500` → `n_rev_global = 0`, `min U_x = 24.0952`,
`m_def_global = 0.6024`; `opt/0.0008` → `n_rev_global = 0`, `min U_x = 24.0840`,
`m_def_global = 0.6021`.

### 7.3 What that means, registered in advance

**On the A4 2,777-cell adjoint mesh there is not one cell with reverse axial flow, anywhere in the
domain, at any of three design points. The minimum axial velocity is +23.5 m/s against U₀ = 40 —
59 % of freestream. This mesh carries no separated flow at all.**

The zero is evidence because the **plant was seen**: the identical reader, on an Ahmed-25° case at
**79,439 cells**, finds **528 reverse-flow cells (0.665 %) and min U_x = −13.77 m/s**. *(Disclosed:
that case's STL is md5 `d8026bc2c2e0d4cfda50903c4197202a`, **not** byte-identical to A4's
`ec3abd31…`. The plant is a **reader-capability control**, not a physics comparison, and is used only
as such.)*

**Registered as P11: the separation-onset monitor will report `NOT AN INSTRUMENT` on this item's own
baseline field, and that refusal is the registered outcome.** Stage η re-runs conditions (i)–(iii) on
the run's **own** output, so the prediction is tested on live evidence and not only on archive.

**A refusal does not fail the item.** The optimiser, constraint, gradient and cost gates stand on
their own. What it does do is fix the item's honesty: the curriculum row calls D3 *"3D constraints on
separation-dominated flow"*, and **this mesh's flow is not separation-dominated — it is not separated
at all.** The expertise D3 actually buys is **3D geometric constraints under a 3D adjoint**; the
separation content is **not delivered by this mesh** and the item must not claim it. §12 prices what
would deliver it.

**Band-exit meaning for `m_def_global`:** an exit from [0.45, 0.75] is **not** a `GATE FAIL` of the
optimisation. It converts every *aerodynamic* reading of the item to **`NOT A RESULT`** — the wake's
momentum state moved and this mesh cannot adjudicate it — while the optimiser, constraint and
gradient verdicts stand. With `n_cells(B) = 2`, `f_sep(B)` is registered as a **weak instrument** and
can never carry a `PASS`.

---

## 8. Cost (`CLAUDE.md` rule 12; `DAFOAM_CHARTER.md` §12)

`cost_basis:` **c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER (owner-stated 2026-08-21/22), NOT
MEASURED.** The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so **every dollar
figure below is DERIVED from core-minutes at that rate and is never quoted as measured.**

**Measured anchors used** (A4 shipped `RESULTS.md` §6, np=1): arm S = **11.583 core-min** for a cold
baseline primal + 6 majors + 16 objective evaluations + 7 gradient evaluations + one endpoint
`check_totals`; arm B = **2.033 core-min** for a cold primal + one `check_totals`. Decomposed against
those totals: **adjoint ≈ 50 s, warm primal ≈ 12 s, cold primal ≈ 100 s** — the decomposition
reproduces arm S's 695 s wall to within 1 %.

| stage | work priced | predicted core-min | **stage ceiling** | `timeout` | margin | loss bound if it hangs |
|---|---|---|---|---|---|---|
| **G** | container + setup, no flow | **1.0** | 3.0 | **180 s** | 3.0× | 3.0 core-min |
| **η** | 1 cold + 2 warm + 1 plant primal | **2.5** | 6.0 | **360 s** | 2.4× | 6.0 core-min |
| **O** | cold baseline + 11 adjoints + ≈25 primals + 4-step endpoint sweep (16 primals) | **21.0** | 42.0 | **1900 s** | 1.5× | 31.7 core-min |
| **T** | 2 arms × (1 cold primal + 4-step sweep) | **5.3** | 12.0 | **420 s** ea. | 2.6× | 7.0 core-min ea. |
| **TOTAL** | | **29.8** | **63.0** | **3280 s** | | **54.7 core-min = 78 % of HARD** |

**Predicted 29.8 core-min. With the registered 100 % contingency: 59.6 core-min. HARD ceiling
70.0 core-min** — the curriculum's own D3 figure. Derived dollars: predicted **$0.0255**, HARD
**$0.0598**, against the curriculum's **$0.06**. **Pre-authorised class (< $25).**

### 8.1 L-250 — the `timeout` is the binding instrument, not the ceiling

*"A per-stage timeout cap is both the bound on a hang and the size of the loss."* The caps above sum
to 3,280 s = 54.7 core-min, **78 % of the HARD ceiling** — a hang cannot legally consume the budget.
**Stage O is the one to watch:** if P6's majors land at 14 and per-major cost at the top of its
range, Stage O needs ≈ 33 core-min and the run completes; if anything hangs, the **`timeout` fires
first at 31.7 core-min**, the run is recorded as stopped by the wall clock, and G2 makes it
`GATE REACHED` or `NOT A RESULT`. **That is a registered outcome, not a surprise.**

### 8.2 Estimate-versus-actual calibration — a registered deliverable (`CLAUDE.md` rule 12)

Sanaa's directive, verbatim (2026-08-23): *"for all teams involved once a process is completed, the
estimated costs must be compared with the actual incurred costs so we can improve the lab's
estimates"*. On completion the item reports, **per stage and in total**: predicted core-min, actual
core-min **from the run ledgers**, the **ratio actual/predicted**, and an attribution of the gap
between contention, waste and misprediction — with **waste separately named, never absorbed into the
ratio** (`COMPUTE_BUDGET_CHARTER.md` §6). Dollars are derived at the recorded rate and labelled
**derived, not measured**.

**Contention basis, registered now so it is measured and not asserted:** the like-for-like marker is
the same internal work item in two logs, in A4's own pattern (`RESULTS.md` §6.1 used
`dRdWTPC: 800 of 1087` and measured 1.104× inflation). **Whole-arm wall clocks are NOT an inflation
figure** and are not a cost basis for scaling.

**Who writes the row:** this lane **DRAFTS** the calibration row into the item's `RESULTS.md`; the
**supervisor lands it** in `docs/COST_CALIBRATION.md`. **No lane writes that file** (D1 Amendment
A1.1). Draft row shape:

```
| C-nn | 2026-08-xx | dafoam | curriculum D3 (A4 constrained opt) | 29.8 | <actual> | <ratio> |
      | $0.0255 derived | <attribution: contention / waste / misprediction, named separately> |
```

---

## 9. Environment pinning (L-251) and staging discipline (L-252)

### 9.1 L-251 — uid and directory mode, pinned in the same sentence

*"Copying a prior run's invocation is not copying its environment."* **The container runs as its
image default (root, `mpirun --allow-run-as-root`), with NO `-u` flag — exactly as A4's
`run_arm.sh` ran it — and the run root is created `chmod 0777` by the launching shell before the
first container starts**, so OpenMDAO's `reports/` write cannot hit the `PermissionError` that killed
W4 M2 under L-250's hang. Mount `-v <run root>:/mnt`, `-w /mnt/<stage>`. After each stage the
launcher runs `chown -R ubuntu:ubuntu` over that stage's directory and logs. `--rm` is used (nothing
here needs a post-mortem `docker inspect` of a live container; an OOM is read from exit 137).

### 9.2 L-252 — per-invocation unique names, `test -s`, provenance assert

*"In shared temp, a generic filename IS an accidental handoff."* Every staged artifact carries a
**per-invocation unique suffix** `$(date -u +%s)_$$`; every staged file is `test -s`-checked **and**
asserted to have been produced by **this** chain in **this** invocation before it is used; steps are
chained with explicit `&&`, never on `set -e` alone.

### 9.3 Staging source, fixed here

The base case is copied from `/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/base/` — the pristine
2,777-cell directory A4 ran from — into a fresh per-stage directory under the D3 run root. **The
mesh is inherited byte-for-byte and is NOT regenerated, NOT refined and NOT re-decomposed.** The
frozen `d3_runScript.py` is copied in as `runScript.py`; its md5 is asserted equal to
`af2ce474e7954c03e3937161510f6590` **after** the copy and **before** the launch.

---

## 10. Run root

**`/home/ubuntu/certonomous-runs/D3-a4-constrained/`** — created in **phase 2 only**, with
subdirectories `geom/`, `eta/`, `opt/`, `endpoint_patched/`, `endpoint_shipped/`. **Its absence at
this freeze is asserted inside the commit invocation** (§13). Run outputs live there and never beside
the prose describing them (`CLAUDE.md`, Where things live).

---

## 11. What this item will NOT touch, listed by name

1. **The A4 frozen records.** `A4_ahmed_body.md`, `A4_ahmed_body.json`, `logs_A4/`,
   `first_optimisation_np1/`, `shipped_optimisation_np1/` — read only, never edited (`CLAUDE.md`
   rule 6). A correction owed to any of them is left for the supervisor's desk.
2. **The A4 mesh.** No regeneration, no refinement, no `snappyHexMesh`, no `decomposePar`.
3. **np > 1.** np=1 is required, not merely chosen: the `scotch` decomposition defect this very case
   characterised makes an np>1 A4 adjoint not the transpose Jacobian's solution
   (`A4/DISCRIMINATORS_A4_decomposition_mechanism.md`; A4 `RESULTS.md` §8 limit 4).
4. **The five upstream defect drafts** — all **NOT FILED**, and nothing here files anything.
5. **A6 N=29 and the D464 two-reading gate** (Sanaa's), the GAMG→PBiCGStab ADF sweep, the
   `useMeanStates` arm, B3 Stage 4 fork-adoption, `DAFOAM_CHARTER.md` §13 PROPOSAL — all untouched
   (`EXPERTISE_CURRICULUM.md` §5).
6. **The MemAvailable 12 GiB floor** — used as a gate, never argued with.
7. **`docs/LAB_STATE.md`, `docs/DOCKET.md`, `docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md`,
   `docs/COST_CALIBRATION.md`** — this lane writes none of them; records are drafted here and landed
   by the supervisor.
8. **`A1/curriculum_D2/`** — a sibling lane is freezing D2 concurrently. **No file is shared between
   the two items.**
9. **`cellLimited Gauss linear 1`** on the momentum equation is live on this case and is **not
   varied**; defect **D-B2** reads 92.8 % on A1 with the rotation patch already in place. It could be
   acting on every number this item produces, **on both images equally**, and this item cannot see
   it. Every verdict here is a verdict **for this scheme configuration only**.

---

## 12. The §7 "unusual" test, applied item by item — what goes to Sanaa and what does not

`EXPERTISE_CURRICULUM.md` §7 clause 2: *"anything unusual, above pre-authorised cost, or outside
these pages goes back to Sanaa costed, not read into the blanket."* Applied honestly:

| candidate | reading | referred to Sanaa? |
|---|---|---|
| np = 1 | not np > 4; np=1 is the conservative choice and is required by the decomposition defect | **No** |
| memory | cap 6 GiB, predicted peak 1.4 GiB, host floor 12 GiB untouched; A4 measured 1.007–1.331 GiB | **No — nowhere near the floor** |
| mesh | inherited **byte-for-byte**; no regeneration, refinement or re-decomposition | **No — there is no mesh change** |
| cost | 29.8 core-min predicted, HARD 70, **$0.0598 derived** | **No — pre-authorised class (<$25)** |
| GPU / instance change | none; nothing here leaves this box | **No** |
| **DV extension 1 → 2** | inside the case's own existing FFD, no new geometry, no mesh change. The curriculum row itself specifies *"volume/rear-slant constraints"*, which a one-variable problem cannot express — so the extension is **inside these pages**, not outside them | **No — but it is the item's one substantive design judgement and it is put on the SUPERVISOR's desk by name (§15)** |
| **shipped row bought as endpoint-only** | a §6 two-row deviation: both rows exist, but the shipped row is not a full optimisation twin. Deferral **priced at ≈17 core-min / $0.0145** (§3.1) | **No — but the SUPERVISOR should confirm the deferral before authorising launch (§15)** |
| **the mesh cannot carry the separation content** (§7) | the curriculum row's premise is not met by this mesh. **Buying it would need the 45,760-cell mesh**, whose adjoint has no anchor on this case; the nearest anchor (A3 at 42,120 cells, np=4) cost **85.95 core-min for a single gradient item**, so a constrained optimisation there is plausibly **500–1,500 core-min ≈ $0.43–1.28** — **UNPRICED on this case until its own calibration major**, and it is a **mesh change** | **YES — flagged, costed, NOT run.** §12.1 |

### 12.1 The one item flagged for Sanaa, costed, not run

**A D3 successor on the A4 45,760-cell mesh, which is the only way this lab can honestly claim the
"separation-dominated flow" content the D3 curriculum row names.** It is flagged because it is a
**mesh change** and because its cost is **UNPRICED on this case** (`EXPERTISE_CURRICULUM.md` §2: *"a
price is never invented across case classes"*) — the 500–1,500 core-min figure above is a
cross-anchor scaling, explicitly **not** a costed proposal. **Nothing about it is run, staged or
prepared under this pre-registration.** If it is wanted, it needs its own calibration major, its own
pre-registration and its own cost, and the decision is Sanaa's.

**This item proceeds on the 2,777-cell mesh with the separation content honestly absent**, which is
the whole point of registering the refusal in advance rather than discovering it afterwards.

---

## 13. Freeze assertions made inside the commit invocation

1. `date -u` is re-read in the commit invocation and recorded; the stamp at the head of this file is
   asserted present in the committed blob.
2. **`/home/ubuntu/certonomous-runs/D3-a4-constrained/` is asserted ABSENT.** It read **ABSENT** at
   17:40:44Z when this file was written.
3. The three md5s of §4.1 are re-computed and asserted equal.
4. `python3 scripts/check_filing.py` is run over this directory.
5. `git diff-tree --stat` asserts the tree carries **only** this item's paths, and
   `git diff HEAD~1 HEAD --stat` verifies the same **after** the commit (L-223 — the CAS proves the
   parent, nothing about the tree).

---

## 14. G5 — the planted-zero control, run at zero compute BEFORE this freeze

### 14.1 Twelve controls, planted into files the A4 producer actually wrote

`python3 d3_grade.py --selftest`:

```
=== G5 PLANTED-ZERO CONTROL (zero compute) ===
producer artifacts (written by A4's own runs, not by this control):
  /home/ubuntu/certonomous-runs/P3-a4-opt-shipped/opt/opt_IPOPT.txt
  /home/ubuntu/certonomous-runs/P3-a4-opt-shipped/opt.log

[1] IPOPT reader, UNPLANTED: exit='Optimal Solution Found.' n_iter=6 objective=0.14153425239903014 constr_viol=0.0 nlp_error=6.91140206459383e-08
[2] IPOPT reader, PLANTED (exit -> cap-stop, constr_viol -> 3.7e-03):
    exit='Maximum Number of Iterations Exceeded.' constr_viol=0.0037
    G2 on the planted file -> NOT A RESULT  (EXIT: Maximum Number of Iterations Exceeded. (not a convergence statement))

[3] check_totals reader, UNPLANTED: 1 block(s) in the real A4 log
    wrt=dvs.shape analytic=[0.21410204] fd=[0.21477037] rel=0.3112% flip=False
[4] check_totals grading, PLANTED (FD sign flipped): rel=199.6888% flip=True
[5] check_totals grading, PLANTED (analytic x1.30): rel=29.5955% (band 15.0%)

[6] G-eta, PLANTED unseen perturbation (plant moved CD by 0.0):
    -> BLOCKED  (the planted perturbation was NOT seen: this reader's zero is not evidence (CLAUDE.md rule 3). Stage O NOT LAUNCHED.)
[7] G-eta, PLANTED noisy objective (delta_repeat = 1.0e-3):
    -> BLOCKED  (eta-FAIL: the objective's noise floor exceeds 10% of the registered signal. Stage O is NOT LAUNCHED; the item reports the noise floor and spends nothing further.)
[8] G-eta, quiet objective (delta_repeat = 1.0e-9):
    -> PASS

[9] G1, PLANTED out-of-bound constraint (thickcon 0.5, volcon 0.90):
    -> GATE FAIL  (thickcon_slant[1] = 0.500000 outside [0.85, 1.15]; volcon_aft[0] = 0.900000 below 0.98)
[10] G1, in-bound control:
    -> PASS

[11] G-theta, PLANTED angle outside the band (d=(+0.05, -0.05)):
    -> GATE FAIL  theta=37.047 deg
[12] G-theta, baseline control (d=(0,0)) must read 25.0 deg:
    -> PASS  theta=24.9951 deg
[13] G-theta at A4's own optimum (d=(-0.05, 0)):
    -> PASS  theta=15.990 deg

=== CONTROL SUMMARY ===
  IPOPT exit + constraint violation                    SEEN
  G2 refuses a cap-stop                                SEEN
  check_totals reads a real block                      SEEN
  per-component sign flip is seen                      SEEN
  a 30% error exceeds the 15% band                     SEEN
  G-eta refuses an unseen plant                        SEEN
  G-eta blocks above the noise ceiling                 SEEN
  G-eta passes a quiet objective                       SEEN
  G1 sees an out-of-bound constraint                   SEEN
  G1 passes an in-bound design                         SEEN
  G-theta sees an out-of-band angle                    SEEN
  G-theta reproduces the 25 deg design angle           SEEN

ALL CONTROLS SEEN. The comparator is shown able to produce a non-PASS on planted defects in files the A4 producer actually wrote (L-273).
```
exit status **0**.

Control [3] is the load-bearing one for L-273: the reader is exercised on **A4's real
`check_totals` block**, and it recovers that run's archival `0.3112 %` exactly. Control [12] is the
independent confirmation of §2.5's geometry model.

### 14.2 The producer/consumer key-set assertion, and the defect it caught before the freeze

No producer artifact for `d3_summary.json` can exist before the run, so L-273's second remedy is
used: the freeze invocation asserts the **producer's** key set (parsed out of the frozen
`d3_runScript.py`) equals the **consumer's** (parsed out of `d3_grade.py`).

**Its first run REFUSED — and the defect was in the control's own parser, not in the scripts.** The
producer emits `"%s_CD" % tag`, so the field name is the **suffix**; the parser matched
`"(\w+?)_%s"`, the wrong order, and reported 11 producer keys instead of 47, declaring four real keys
missing. **Fixed before the freeze, when fixing is legal (`CLAUDE.md` rule 2).** After the fix:

```
KEYCHECK producer keys (47): [... 'final_CD', 'final_CL', 'final_shapeBreak', 'final_shapeRear',
 'final_thickcon_slant', 'final_volcon_aft', 'reduction_pct', 'task', ...]
KEYCHECK consumer keys (9): ['G_jac', 'eta_delta_repeat', 'eta_plant_dCD', 'eta_plant_dv',
 'final_shapeBreak', 'final_shapeRear', 'final_thickcon_slant', 'final_volcon_aft', 'reduction_pct']
KEYCHECK consumed-but-never-produced: NONE
KEYCHECK: OK          exit 0
```

**Negative control, because a green check that cannot go red is not a check.** A mutant runScript
with `volcon_aft` renamed in the producer only:

```
KEYCHECK consumed-but-never-produced: ['final_volcon_aft']
KEYCHECK: REFUSE -- L-273 defect present          exit 2
```

**This is exactly the D1-C′ failure — producer writes `CD`, consumer reads `CD_final` — and this
control catches it at zero compute.** L-273's closing sentence asked for precisely this: *"both
defects were findable by dry-running the frozen code against its own frozen inputs before the
freeze."*

---

## 15. Falsifiers, and what is on the supervisor's desk

### 15.1 Falsifiers — named in advance, each with what it would mean

| id | falsifier | what it falsifies |
|---|---|---|
| **F1** | Stage G crashes in any DVCon call | the JBC_Hull/D1-C′ API precedent does not transfer to a 3×2×2 FFD on a blunt body. Stage G `BLOCKED`, §4.3 governs, **no in-place edit** |
| **F2** | Stage G's measured FFD Jacobian differs from §2.5's frozen coefficients by > 2 % | the geometry model is wrong; Gθ becomes `NOT A RESULT` and §2.5's 24.9951° agreement was a coincidence |
| **F3** | symmetry residual > 1e-9 | "symmetric by construction" (§2.4) is false and the decline of `nom_addLinearConstraintsShape` was wrong |
| **F4** | the η plant moves CD by < 1e-05 | the η reader cannot see a non-zero ⇒ item `BLOCKED` (rule 3) |
| **F5** | δ_repeat > 1.4078e-04 | the objective's noise swamps the signal ⇒ item `BLOCKED`, Stage O never launched, noise floor reported |
| **F6** | `eta_call1_CD` ≠ `0.1529738469354696` | the cold start did not hold, or the case is not A4's. G8 fails and every downstream number is suspect |
| **F7** | Stage O reduction < 7.478 % with `EXIT: Optimal Solution Found.` | a constraint binds harder than predicted — the constrained optimum is **worse** than A4's unconstrained one. A legitimate, informative result and a P7 MISS, not a failure |
| **F8** | the deliberately wrong step (1e-1) **passes** the 15 % band | G3 is not discriminating ⇒ `NOT A RESULT` (G4) |
| **F9** | no plateau step exists | the FD instrument has no flat region here ⇒ G3 `NOT A RESULT` |
| **F10** | the two images' analytic gradients differ by > 1e-3 relative at Stage T | **A4's immateriality does not transfer to two DVs** — a finding, and the strongest single result this item could produce |
| **F11** | `n_rev_global ≥ 1` on Stage η's baseline field | **P11 is wrong in the informative direction**: this mesh does carry separation after all, the monitor is an instrument, and `f_sep(B)` is graded |
| **F12** | any stage exceeds its ceiling | the run **stops**; it does not get a new budget (rule 12) |

### 15.2 On the supervisor's desk before launch is authorised

1. **The DV extension 1 → 2** (§2.2, §12). This lane's reading is that it is inside the curriculum's
   own pages; the supervisor's §3 check is what authorises it.
2. **The shipped row bought as endpoint-only** (§3.1), deferral priced at ≈17 core-min.
3. **The separation content is not deliverable on this mesh** (§7.3) — the supervisor decides whether
   D3 proceeds with that content honestly absent, or is re-scoped.
4. **The four §3 checks are the supervisor's and may not be delegated**: this file read as a diff,
   the pre-registration **committed** before any compute, crash triage, and big-claim verification.
   **This lane has launched nothing and will launch nothing without that authorisation.**

---

## 16. Verdict vocabulary

**PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING** — and no synonyms.

- An optimiser stopped by an iteration cap, a wall clock or a budget is **`GATE REACHED`** (registered
  intermediate threshold met) or **`NOT A RESULT`** (not met) — **never `PASS`**, and never described
  by the size of the improvement it reached (`DAFOAM_CHARTER.md` §9).
- A stage the kernel OOM-killed is **`NOT A RESULT` about convergence** (§G9).
- **η-FAIL, an unseen η plant, or a Stage-G crash makes the item `BLOCKED`** — a precondition
  prevented the measurement — not `NOT A RESULT`, which is reserved for a value produced and
  ungradeable.
- The separation monitor's refusal is reported as **`NOT AN INSTRUMENT`**, which is a statement about
  the instrument and is **not** one of the six verdict tokens; the item's own verdicts use only the
  six.
- Shipped and patched are **separate rows** and are never merged into one verdict.
- **`PENDING`** is used only for "not yet run", never to soften a `GATE FAIL`.

---

## 17. Exact launch sequence for phase 2

Run **only** after the supervisor has verified this freeze and authorised launch (§15.2). Every step
is a separate command; G6 is re-read before **each** container start.

```
# 0. verify the freeze is the file that will run (CLAUDE.md rule 2)
git show <freeze-sha>:cases/dafoam/ladder-a/A4/curriculum_D3/d3_runScript.py | md5sum   # af2ce474...
git show <freeze-sha>:cases/dafoam/ladder-a/A4/curriculum_D3/d3_grade.py     | md5sum   # a32f0758...

# 1. run root + staging (L-251 mode, L-252 unique names, G8 cold start)
mkdir -p /home/ubuntu/certonomous-runs/D3-a4-constrained && chmod 0777 ...
cp -a /home/ubuntu/certonomous-runs/P3-a4-opt-shipped/base  <root>/geom   # and eta, opt, endpoint_*
# assert: no processor*, no numeric time dir, 0/ from 0.orig/, no reports/
# copy d3_runScript.py in as runScript.py; assert its md5 AFTER the copy

# 2. G6 as its OWN command, output appended to preflight_history.txt, read before launching
#    free_cores >= 4 AND MemAvailable >= 12 GiB

# 3. STAGE G   -task geom_probe   timeout 180s   patched image   --cpus=1 --memory=6g --memory-swap=6g
#    -> P1/P2/P3. If it crashes: BLOCKED, §4.3, no edit.

# 4. G6 again. STAGE ETA   -task eta   timeout 360s   patched
#    -> d3_grade.py --eta-summary <root>/eta/d3_summary.json
#    -> Geta PASS / GATE REACHED(marginal) / BLOCKED.  BLOCKED => STOP. Nothing further is spent.
#    -> d3_sep_monitor.py --u <eta time dir>/U --mesh <eta>/constant/polyMesh \
#         --plant /home/ubuntu/certonomous-runs/act7-ahmed_25-b14562/154/U   (P11)

# 5. G6 again. STAGE O   -task run_driver   timeout 1900s   patched
#    -> d3_grade.py --summary ... --ipopt <root>/opt/opt_IPOPT.txt --log <root>/opt.log \
#         --row patched --core-min <measured>

# 6. write the design-vector JSON from Stage O's d3_summary.json (§4.2)
# 7. G6 again. STAGE T-patched   -task endpoint_at -dvfile ...   timeout 420s   patched
# 8. G6 again. STAGE T-shipped   -task endpoint_at -dvfile ...   timeout 420s   SHIPPED image
#    -> P8 / F10: the clean toolchain comparison A4 could not make.

# 9. RESULTS.md: six report headings, both toolchain rows, the calibration draft (§8.2),
#    every verdict from the §16 vocabulary. Records drafted here, landed by the supervisor.
```

---

**END OF PRE-REGISTRATION. Frozen by commit. Nothing below this line existed when the gates,
thresholds, caps and labels above were fixed. ZERO COMPUTE SPENT. NOT FILED ANYWHERE.**

---

## 18. ADDENDUM A1 — Supervisor launch authorisation (dated; version bump v1.0 → v1.1)

**Dated 2026-08-24T17:53:21Z** (`date -u`, read in the shell invocation that wrote this addendum, asserted the run root absent, built the tree and landed the commit).

**lines whose number changed above this section: 0** — this addendum is appended at the foot of the
frozen file; nothing above line 856 was touched, re-flowed or re-numbered (`CLAUDE.md` rule 6).

**Version.** The frozen document carried no explicit version token. This addendum designates the
state committed at `0cbf463c` as **v1.0** and this file, with this addendum, as **v1.1**.

**Condition asserted, and how it was checked (`CLAUDE.md` rule 2, before-first-compute clause).**
**ZERO COMPUTE HAS BEEN SPENT WHEN THIS ADDENDUM IS COMMITTED.** The run root
`/home/ubuntu/certonomous-runs/D3-a4-constrained/` **does not exist**: `test ! -d` on that exact path
is executed **inside the same shell invocation** that writes this addendum and that builds and lands
the commit carrying it, and the commit is refused if the path is present. No container has been
started, no image has been run, and no solver has executed. The `date -u` stamp at the head of this
section is read in that same invocation.

**No gate, band, threshold, cap or label is altered by this addendum.** Every number in §5, §6, §7,
§8 stands exactly as frozen. What is recorded here is the supervisor's authorisation, which §15.2
made a precondition of launch.

### 18.1 The four rulings, as directed by the dafoam-supervisor

**(1) The DV extension 1 → 2 is AUTHORISED.** §15.2 item 1 and §12's row put this on the
supervisor's desk as the item's one substantive design judgement. The supervisor's ruling is that the
extension sits **inside the curriculum row's own wording** — the row specifies *"volume/rear-slant
constraints"*, and a rear-slant constraint is **inexpressible with a single design variable**: with
one DV an active geometric constraint either fixes the design outright or is inert (§2.1). The
extension therefore does not go to Sanaa under `EXPERTISE_CURRICULUM.md` §7 clause 2; it is inside
these pages. §12's reading is confirmed, not widened.

**(2) The shipped row bought as endpoint-only is ACCEPTED.** §15.2 item 2, §3.1. Stage T buys the
endpoint gradient on both images at the same design vector reached by the same path — the arm A4's
own `RESULTS.md` §8 limit 3 named as missing. **The full shipped optimisation twin is DEFERRED**, and
the deferral stays priced at **≈ 17 core-min ≈ $0.0145 DERIVED** (§3.1). It is **not bought here**,
and the item's two-row toolchain table (§3) is read with that deviation on its face.

**(3) The item PROCEEDS with the separation content honestly absent.** §15.2 item 3, §7.3. The
supervisor did not take this lane's §7 measurement on relay: as the `SUPERVISION_CHARTER.md` §3
big-claim check, the supervisor **independently counted reverse-flow cells on every 2,777-cell A4
field on disk** — the P2 and P3 optimisation runs, the W4 discriminator runs, baselines and optima
alike. The count is **zero everywhere**, with **min U_x ≈ +23.5 m/s** against U₀ = 40, measured
against **528** reverse-flow cells on the 79,439-cell Ahmed-25 field and **780** on the cfd team's
9,050-cell F5c A4 field. **P11 is expected to HIT.** The A4 2,777-cell adjoint mesh carries no
separated flow, the curriculum row's "separation-dominated flow" premise is **not met by this mesh**,
and the item must not claim that content. **The 45,760-cell successor is a mesh change, goes to
Sanaa's desk unpriced (§12.1), and nothing about it is run, staged or prepared under this
pre-registration.**

**(4) VOCABULARY — `NOT AN INSTRUMENT` is a printed REASON, never a verdict.** §16 already says the
token is a statement about the instrument and is not one of the six. This ruling fixes how it is
rendered in the record: in `RESULTS.md` the **Gs verdict cell reads `NOT A RESULT`**, with
`NOT AN INSTRUMENT` and the failed instrument conditions printed **beside** it as the reason
(`CLAUDE.md` rule 1 — the verdict vocabulary is closed, and honesty is carried by the value and the
reason, never by a new word). The frozen `d3_sep_monitor.py` is **not edited**: it prints what it was
frozen to print and exits 3; the mapping happens in the record.

### 18.2 What this addendum does NOT do

It does not authorise anything Sanaa reserved (`CLAUDE.md` FIRST-ACTION RULE): nothing is sent, filed,
uploaded or posted (rule 7); no mesh is changed; no threshold, band or ceiling moves; no instance or
GPU is touched. **No agent's message is Sanaa's consent** (rule 9) — the supervisor authorises the
launch of an item that already sits in the pre-authorised class (**$0.0598 DERIVED at the HARD
ceiling**, §8), and authorises nothing wider than that.

### 18.3 The launch invocation's own re-verification (§17 step 0)

Independently of the supervisor's 17:50Z check, the invocation that stages and launches re-hashes the
three frozen executables **on disk** against the **committed blobs** at `0cbf463c` and at the
then-current `HEAD`, and refuses to stage on any mismatch. Reading taken before this addendum was
written:

```
d3_runScript.py    disk af2ce474e7954c03e3937161510f6590 == 0cbf463c blob == HEAD blob
d3_grade.py        disk a32f075853e264910ee0a6c2473fd948 == 0cbf463c blob == HEAD blob
d3_sep_monitor.py  disk cd07d7b8a70627579384f263ba92194e == 0cbf463c blob == HEAD blob
PREREGISTRATION.md disk 837794ed3bed9cfc12b2658df754a65c == 0cbf463c blob == HEAD blob
run root /home/ubuntu/certonomous-runs/D3-a4-constrained/   ABSENT
```

**END OF ADDENDUM A1. Nothing below this line existed when the gates, thresholds, caps and labels
above were fixed. ZERO COMPUTE SPENT AT THIS COMMIT. NOT FILED ANYWHERE.**
