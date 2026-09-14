# SUBOFF A1h — FULL-DOMAIN MATCHED-REYNOLDS HORIZONTAL-PLANE DRIFT SWEEP, HULL AND SAIL

**STATUS: DRAFT — NOT YET FROZEN.** The freeze is the commit that lands this file. Nothing
in this act may run before that commit exists. Author: cfd lab-lane, 2026-09-13, on the
cfd-supervisor's ruling standing A1f down and directing a successor.

---

## 0. WHAT THIS CASE IS, AND WHY ITS PREDECESSOR WAS STOOD DOWN

**A1f was stood down BLOCKED because its registered mesh could not represent its registered
flow.** `SUBOFF_A1f_MATCHED_RE_DRIFT_SWEEP_PREREGISTRATION.md` (frozen `e7db97605`) registers
a horizontal-plane drift sweep on the A1b `L2` mesh and forbids a new one — §3, verbatim:
"No new mesh is built." That mesh is a **half model split on z = 0**:

| evidence | reading | artifact |
|---|---|---|
| patch `symm` | `type symmetryPlane`, 130,570 faces | `verification/runs/navier_class/SUBOFF_A1/L2/constant/polyMesh/boundary` |
| `symm` bounding box | (−2, −2.9925, **0**) → (9.025, 2.9925, **0**) — a plane at exactly z = 0 | `.../L2/log.checkMesh.FULLFLAG` |
| overall domain | z ∈ **[0, 2.9927629]** | same file |
| `hull` patch | y ∈ [−0.254, +0.254] but z ∈ [**0**, 0.254] — a half body | same file |
| the sail | at top dead centre, **+y** | `cases/navier_class/SUBOFF_A1/build_suboff_a1_geometry.py:168-169` |

The sail at +y makes **z = 0 the port/starboard plane**. A horizontal-plane drift sweep is
the one manoeuvre that breaks it: at β ≠ 0 the free stream is (U cos β, 0, U sin β), whose
z-component the `symmetryPlane` boundary condition forbids, and the lateral force Y acts
along z — the direction the half model annihilates by construction.

**The lab had already written this rule down, in the case where it holds and not in the case
where it fails.** `SUBOFF_A1g_APPENDED_VERTICAL_PLANE_PREREGISTRATION.md` §4.1: *"Sanaa's
sweep is in PITCH, so the free stream lies in that same plane at every α. The symmetry
therefore holds for the whole sweep and the half model is exact, not an approximation."*
A1f's sweep is in **drift**, and the free stream lies in that plane at no β other than zero.
A1g's own reasoning, applied to A1f, refuses it. **A1g is unaffected and stays live.**
**A1e inherits the defect** — same half mesh, same horizontal plane — and is stood down on
the same ground; it never ran, so nothing published rests on it.

**THE PHYSICS WAS NEVER WRONG; ONLY THE MESH WAS.** This case inherits from A1f nothing but
the science. New freeze, new mesh, its own admission, its own cost basis, its own grading
path. It is **NOT a member of the A1b grid family** and may not contribute to its `CT`
triple: A1b's registered condition is `Re_L = 1.2e7` and this case runs at `Re_LBP =
1.42478e7`, a different flow. **Single level, single condition, no observed order, no GCI,
no extrapolation, not a rung of any ladder.**

---

## 1. THE CONDITION — MATCHED TO RODDY, QUOTED FROM HIS PAGE 3

> "The static stability experiments were conducted at a **model speed of 6.5 knots** which
> corresponds to a Reynolds number (based on the length between perpendiculars) of **about
> 14 million**."

| quantity | value | basis |
|---|---|---|
| `U` | **3.343886 m/s** | 6.5 knots exactly, at 0.514444 m/s per knot |
| `nu` | 1e-6 m²/s | unchanged from the A1 family |
| **Re_LBP** | **1.424783e7** | on L_BP = 4.2608602 m — matches Roddy's "about 14 million" |
| `k_inf` | **1.118157e-05** | scales as `U²` from the family's 7.588690e-06 |
| `omega_inf` | **4.658989** | `= k_inf / nut_inf`; the same construction reproduces the family's 3.161954 at the old `U`, which is the check that it is the same rule and not a new one |
| `nut_inf` | 2.4e-06 | unchanged, `nut/nu = 2.4` |

Why the condition must be matched rather than graded across: A1e's solve ran at
`Re_LBP = 1.1738e7` against Roddy's 1.4248e7, **17.6 % low**, and Roddy's page 3 puts both
inside the band where "coefficients vary with Reynolds number". The ±4 % band is his
*measurement* uncertainty and carries no allowance for Reynolds sensitivity. A1e Addendum 4
established the gap **cannot be bounded from Roddy's data**, structurally: every static
derivative, all six configurations, was measured at a single speed — 6.5 knots (Table 3,
report pages 17–18). The four-speed Yawing and Pitching rows are not a Reynolds sweep —
`Omega` is fixed at 2.220 rad/s, so `r' = ωL/U` varies with `U` and Reynolds is confounded
with `r'` by construction. **Matching the condition is the only route to a graded arm.**

---

## 2. THE MESH — FULL DOMAIN, MIRRORED, WITH ITS OWN ADMISSION

The full domain is the admitted `L2` mesh **mirrored about z = 0** with
`/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/mirrorMesh` (verified
present on this box, 75,968 bytes, 2026-06-19), `system/mirrorMeshDict`:

```
planeType       pointAndNormal;
pointAndNormalDict { point (0 0 0); normal (0 0 1); }
planeTolerance  1e-8;
```

**THIS MESH DOES NOT INHERIT `L2`'s ADMISSION.** A1b §2 admitted `L2` as a half model; a
mirrored mesh is a different mesh with a seam the original does not have, and admission is
not transitive across a topological operation. **It is admitted here or the act does not
run.** The mirrored mesh is built ONCE, into `MESH_FULL_L2M/`, and every one of the seven
points takes a copy of it; no point re-mirrors.

### 2.1 MESH ADMISSION GATES — measured on the mirrored result, before any solve

| # | gate | threshold | why |
|---|---|---|---|
| **M-1** | `nCells` | **exactly 18,242,474** = 2 × 9,121,237 | a mirror that dropped or duplicated cells is not a mirror |
| **M-2** | patch `symm` | **nFaces == 0** (retained as a zero-face patch) | the seam must have become interior; a surviving `symm` face means the two halves did not join |
| **M-3** | domain bounding box in z | symmetric about 0 to **1e-6 m**, i.e. z ∈ [−2.9927629, +2.9927629] | the mirror's own arithmetic |
| **M-4** | `checkMesh` topology | **"Mesh OK"**, zero boundary-face errors, mesh closed | |
| **M-5** | max non-orthogonality | **≤ 70°** hard, 65–70 warning band, read from **the reported maximum** and never from `checkMesh`'s verdict line | `docs/standards/MESH_STANDARD.md` §3.1, §14 |
| **M-6** | max skewness, **boundary faces included** | **≤ 4** | `MESH_STANDARD` §3.2 |
| **M-7** | **THE SEAM** — minimum cell volume and maximum non-orthogonality **restricted to cells with any vertex at \|z\| < 1e-6** | min volume **> 0**; seam max non-orthogonality **≤ 70°** and **no worse than the whole-mesh maximum** | **a mirror goes wrong at the seam and nowhere else**; a whole-mesh statistic can hide a thin bad layer at z = 0 among 18.24 M cells |

**M-7 is the gate this case exists to pass.** M-1 to M-6 would be satisfied by a mesh whose
seam is a sheet of slivers. Any of M-1…M-7 failing is **GATE FAIL on the mesh** and the
seven points do not launch.

**Mesh quality, disclosed not gated (two-tier standard).** `L2`'s own
`log.checkMesh.FULLFLAG` reports **131,728 concave cells = 1.444 %**; the mirrored mesh
carries 263,456 = the same fraction. `SUBOFF_A1b_CONCAVE_FORCE_SHARE_PREREGISTRATION.md`
(frozen `bc73dc0cae2063477d9d54ee5512b93a68be3249`) applies to this case exactly as to any
other, and `F = max(Q2, Q3)` is unmeasured on this mesh at the time of writing. Nothing
here pre-empts it.

**Geometry.** The hull-and-fairwater body already verified against Liu & Huang page 2 to the
millimetre (A1e §2). No new geometry is generated.

---

## 3. THE SWEEP

- **Drift angles β = −12, −8, −4, 0, +4, +8, +12 degrees**, inside Roddy's tested ±18°.
- The inlet velocity at each point, in **mesh coordinates**, registered as numbers so no
  later reader has to re-derive them:

| β (deg) | `0/U` inlet `internalField uniform` | sin β = v′ |
|---|---|---|
| −12 | (3.270814068 0 −0.695232992) | −0.207911691 |
| −8 | (3.311343531 0 −0.465378984) | −0.139173101 |
| −4 | (3.335740462 0 −0.233257696) | −0.069756474 |
| 0 | (3.343886000 0 0.000000000) | 0.000000000 |
| +4 | (3.335740462 0 +0.233257696) | +0.069756474 |
| +8 | (3.311343531 0 +0.465378984) | +0.139173101 |
| +12 | (3.270814068 0 +0.695232992) | +0.207911691 |

  Each has magnitude exactly `U` = 3.343886 m/s: the sweep yaws the flow, it does not
  change the speed, so **Reynolds number is constant across the seven points by
  construction** and the derivative is not contaminated by a Reynolds gradient.
- `farfield` stays `slip`; `outlet` `inletOutlet`; `hull` and `sail` `noSlip`; **`symm`
  retains a zero-face entry in every field file** (OpenFOAM requires an entry per patch).
- `endTime` 3000, `deltaT` 1, `writeInterval` 15, `purgeWrite` 2 — the A1b family's own
  checkpoint policy. At the rate registered in §6 that is **~10.1 min per checkpoint**,
  inside the directive's 30-minute ceiling.
- **Derivatives `Y_v'` and `N_v'` by linear fit over |β| ≤ 8** — five points, the linear
  range. β = ±12 are solved and **reported**, and are **excluded from the fit**; they exist
  to show where linearity ends, and the comparator prints their residual against the
  |β| ≤ 8 line so a reader can see it.
- Hull/sail force split reported per point. y+ per patch reported per point.

---

## 4. NORMALISATION AND SIGN CONVENTION — DERIVED HERE, NOT INHERITED

A1e Addendum 3 exists because a band was transferred without its normalisation. That defect
is not repeated: the constants are numbers, and **the sign convention is derived in full**,
because a sign error would flip a gated value and is the likeliest way this act goes wrong.

| constant | value | Roddy's words, page 3 |
|---|---|---|
| reference length `L_BP` | **4.2608602 m** | "the length between perpendiculars of 13.9792 feet (4.261 m)" |
| reference area `L_BP²` | **18.154930 m²** | his derivatives are `Y/(½ρU²L²)` |
| `L_BP³` | **77.355617 m³** | the moment normalisation — `N/(½ρU²L³)`; `L²` alone leaves a dimension of length, so the cube is forced, not chosen |
| moment origin (mesh coords) | **(2.013, 0, 0)** | "origin 6.6042 feet (2.013 m) aft of the forward perpendicular (nose) on the hull centerline" |
| `½ρU²L²` (ρ = 1, kinematic) | **101.500341** | |
| `½ρU²L³` | **432.478763** | |

`Aref` is **L_BP², not the wetted area.** A1b's `CT` gate keeps its own wetted-area
normalisation; the two are a **factor of 5.902 apart** and are not interchangeable.

### 4.1 MESH AXES → SNAME BODY AXES, WITH THE DERIVATION SHOWN

Mesh axes, read from the geometry and the `hull` bounding box (x ∈ [0, 4.356], nose at
x ≈ 0): **x_mesh points from bow to stern** (downstream), **y_mesh is up** (the sail is at
+y), **z_mesh is lateral**. The moment origin (2.013, 0, 0) works directly in mesh
coordinates because Roddy measures 2.013 m **aft of the nose** and the nose is at x_mesh ≈ 0.

SNAME body axes are x_b forward, y_b starboard, z_b down. Therefore
`x_b = −x_mesh`, `z_b = −y_mesh`, and right-handedness (`x_b × y_b = z_b`) forces
**`y_b = −z_mesh`**: (−x̂)×(−ẑ) = x̂×ẑ = −ŷ = z_b. ✓

The body's velocity relative to the fluid is −U_inlet, so
- `u_b = (−U_inlet)·x̂_b = U cos β` — forward speed positive ✓
- `v_b = (−U_inlet)·ŷ_b = +U sin β`, hence **`v′ = v_b/U = sin β`**

and therefore, from `force.dat` / `moment.dat` `total_*` columns at `endTime`:

> **`Y′ = −F_z,mesh / 101.500341`**
> **`N′ = −M_y,mesh / 432.478763`**
> **`v′ = sin β`**
> **`Y_v′ = d Y′/d v′`, `N_v′ = d N′/d v′`, least squares over the five points |β| ≤ 8.**

**PHYSICAL CHECK ON THE SIGN, and it agrees.** β > 0 gives `v_b > 0` — the body moving to
starboard relative to the fluid — so the fluid pushes back to port, `Y_b < 0`, hence
`Y_v′ < 0`. Roddy's value is negative. In mesh terms the same statement is: β > 0 puts a +z
component on the inflow, which pushes the body to +z, `F_z > 0`, and `Y_b = −F_z < 0`. ✓
The two readings agree, which is the check that the transform is the same rule read twice
and not a sign chosen to land in the band.

### 4.2 THE SIGN CLAUSE — REGISTERED BEFORE COMPUTE, NOT AFTER

If the fitted `Y_v′` comes out **positive**, the verdict is **`NOT A RESULT`**, not
`GATE FAIL`, and the printed reason is "sign convention or solve is wrong". A positive
`Y_v′` is anti-damping: it is not a bad answer to the physics question, it is evidence the
bookkeeping in §4.1 or the solve itself is inverted. This is registered **now**, before any
number exists, so that it cannot later be reached for as an escape from a failing gate.
Sanaa's ruling of 2026-08-26 and 2026-09-12 — **bookkeeping never voids physics** — is read
here in its other direction: a bookkeeping inversion must not be graded as physics.

### 4.3 THE β = 0 SYMMETRY CHECK — the full mesh's own proof

At β = 0 the flow is in the z = 0 plane and the body is mirror-symmetric about it, so
`F_z` and `M_y` must vanish. **Registered threshold: |Y′(β=0)| ≤ 1e-4 and |N′(β=0)| ≤ 1e-4**,
i.e. ≤ 0.43 % and ≤ 0.64 % of the respective Roddy magnitudes. Failing it is `GATE FAIL`
on the mesh, not on the physics: it means the mirror is not symmetric. This check is the one
thing A1f's half mesh could never have provided — on a half model `F_z` is zero by boundary
condition and proves nothing. **On the full mesh it is a real measurement of the seam.**

---

## 5. THE BANDS

Reference: **Roddy 1990, DTRC/SHD-1298-08, Table 4, report page 19, "Horizontal Plane",
column printed `Config 4 / B.H. + Sail`** — the hull-with-fairwater body, **named by its
geometry and never by a bare number** (A1e §2's binding rule: `Config 4` in Roddy is not
`Config 4` elsewhere, and `Config 1` names the emptiest body in one report and the fullest
in the other).

| quantity | Roddy | gate |
|---|---|---|
| **`Y_v'`** | −0.023008 | **GATED, ±4 %: [−0.023928, −0.022088]** |
| **`N_v'`** | −0.015534 | **REPORTED, NOT GRADED** — inherited from A1e Addendum 1 |

**THE TWO REFERENCE NUMBERS ABOVE ARE RODDY'S EXPERIMENTAL MEASUREMENTS. THEY ARE NOT
ANYTHING THIS LABORATORY COMPUTED, PREDICTED, OR DERIVED.** `Y_v' = −0.023008` and
`N_v' = −0.015534` were measured on a physical model in a towing facility and read by this
lab out of a printed table in Roddy's report. No reader of this document, now or later, may
cite either number as a Certonomous result. They are the ground the solve is graded
against, and the solve has not run.

**`N_v'` stays ungated for a reason that has nothing to do with Reynolds and is not repaired
by matching it.** A1e Addendum 1 ran the §4.1 extension test and it **splits**: the
transferred ±4 %, stated by Roddy for fully appended submarines, is **17.3 % tighter** than
the rig floor for `Y_v'` (conservative, so `Y_v'` is admitted on a checked ground) and
**13.8 % looser** for `N_v'` — it **errs in our favour**. Gating `N_v'` would be fitting a
gate to a known-favourable ground, and matching the condition does not narrow a band that
is too wide. A tighter gate for `N_v'` is available and is **not** taken by this lane.

±4 % is the **tighter** end of Roddy's stated "4 to 5 percent" (page 105). ±5 % is the outer
reading and does not gate.

---

## 6. COST — THIS CASE'S OWN BASIS, DERIVED FROM THE DOUBLED CELL COUNT

**A1f's 33,180 core-min and its 23.7 s/iteration are NOT carried over.** They price a
9.12 M-cell half mesh. This case prices an 18.24 M-cell full mesh from a rate measured on
this box tonight.

**Rate basis, measured not recalled.** `SOLVE_L2`'s own live log, 9,121,237 cells on 4 ranks
= 2.280 M cells/rank: **20.12 s/iteration** over the run, independently corroborated by this
lane's own last-50 reading of **19.714 s/it** taken at t = 1003 (`ExecutionTime` 21928.43 →
22914.11 over 51 lines). The registered basis is **20.12 s/it at 2.280 M cells/rank**.

Per-iteration time scales with cells per rank. At **7 points × 4 ranks**, 18,242,474 cells
give **4.561 M cells/rank**, exactly 2× the basis, hence **40.24 s/it**:

> **7 × 3000 × 40.24 s × 4 ranks / 60 = 56,336 core-min**
> **$48.17 DERIVED, NOT MEASURED**, at the owner-stated $0.0513/core-h; the box cannot read
> its own billing (`COMPUTE_BUDGET_CHARTER` §5).
> **Wall time: 33.5 h**, one wave.

**No cap is registered.** Sanaa's directive #17 (2026-09-12): no run is stopped by a time or
budget cap. This figure is a **calibration prediction to be scored** under rule 12 at
completion, never a kill. Convergence may arrive before 3000 iterations, in which case the
actual is lower and the ratio is what the calibration row records.

### 6.1 RANK SHAPE — SANAA ALLOCATED 28 RANKS, NOT THE ARITHMETIC

Her 96-core table gives this act **28 ranks for seven points**. The shape within 28 is ours
to justify, so here it is, with the numbers rather than a preference:

| shape | cells/rank | s/it | core-min | waves | wall |
|---|---|---|---|---|---|
| **7 pts × 4 ranks, one wave** | 4.561 M | 40.24 | **56,336** | 1 | **33.5 h** |
| 2 pts × 14 ranks | 1.303 M | 11.50 | 56,336 | 4 | 38.3 h |
| 1 pt × 28 ranks | 0.651 M | 5.75 | 56,336 | 7 | 33.5 h |

Under linear scaling all three cost **identical core-minutes** — the ranks are busy either
way — so the choice turns on wall time, memory and overhead. **7 × 4 in one wave is
registered**: it ties for the shortest wall clock, has the fewest waves and so the least
`decomposePar` overhead, and is exactly the shape Sanaa's table describes. The 14-rank shape
is worse only because 7 does not divide by 2 and the fourth wave idles half the allocation.

**Memory is not the constraint, and this is measured.** The live 4-rank, 9.12 M-cell solve
holds **11.85 GB** resident (3.06 + 2.96 + 2.94 + 2.89), i.e. **1.299 GB per million cells**.
At 18.24 M cells that is **23.7 GB per point**, **166 GB for all seven**, against **670 GB
available** on this 739 GB box — a **4.0× margin**.

### 6.2 THE SHAPE CHECK — a measurement, registered in advance, and NOT a cap

The 2× scaling above assumes per-iteration time is linear in cells per rank. At 4.561 M
cells/rank the solve is far outside cache and that is the right first assumption, but it is
an assumption. **After 100 iterations on the β = 0 point, the measured s/it is recorded. If
it exceeds 48.3 s/it (2.4× the basis), the scaling is materially worse than linear and the
act re-shapes to 1 point × 28 ranks per wave**, which the table above shows costs the same
core-minutes at the same wall time with 7× less memory per rank. This is a **shape
decision**, not a budget stop: directive #17 forbids stopping a run for cost, and nothing
here stops one.

---

## 7. TURBULENCE TREATMENT — MATCHED, AND CHECKED RATHER THAN ASSUMED

Fully-turbulent k-ω SST with `nutUSpaldingWallFunction`, no transition model. **This is the
matched choice, not a disclosed mismatch**: Liu & Huang 1998, page 23, footnote to Table 14,
read as a page image — "Hull, bridge fairwater and four identical stern appendages all have
tripwires installed at 5 percent of chord length." **Both of our patches carried tripwires;
the measured body was fully turbulent by design.** A1e Addendum 2 confirmed the same for
Roddy's rig from his own page.

---

## 8. THE GRADING PATH — FIXED AT THIS COMMIT

> **`cases/navier_class/SUBOFF_A1/grade_suboff_a1h.py`**

This path is fixed from the commit that freezes this file. Rule 2: the frozen file **is** the
file that ran, verified by hashing the comparator against its committed blob before the
grade is believed; `scripts/check_comparator_freeze.py` enforces. No other script grades this
act, and a grade produced by any other path is `NOT A RESULT`.

The comparator **does not write into the cases it grades.** It writes only under `--out` and
`--scratch`, asserts at startup that neither lies inside any graded case directory, and
prints that assertion in its own output.

### 8.1 THE COMPLETION RULE — ENFORCED ON ALL SEVEN BEFORE ANY ONE IS READ

Standing rule 4, all clauses, on every point, **before a single force is read**. A run
failing any clause makes its point `NOT A RESULT`, and **a sweep missing any of the five
fitted points is `NOT A RESULT` entire** — there is no fit over four points and no
degradation to a shorter sweep.

`rc == 0` from `solve_rc`; an `End` line **following the final `Time =` line**; last time ==
`endTime` == 3000; `ExecutionTime` count == 3000 read as **distinct physics steps unioned
across every log segment** via `scripts/solver_log_set.py` (a resumed run double-counts
lines — measured on `SOLVE_L2`, 3,002 lines for 3,000 steps); fields present at `endTime`;
and the **age guard** — every field at `endTime` strictly **newer than the case's own
`0/U`**.

#### 8.1.1 THE RESUME FORM, REGISTERED HERE AT THIS COMPARATOR'S OWN FREEZE

Rule 4's `ExecutionTime` clause is **silent on resume**, and a draft docket row —
`verification/runs/navier_class/DRIVAER/DOCKET_D631_DRAFT_rule4_resume_hole.md`, a **draft,
not a landed item** (the highest docket number on disk is 630) — records that five graders
across three territories read it two incompatible ways. **Form A** (`n_exec == endTime`)
*refuses* a completed resume; **Form B** (`n_exec == n_time`) *accepts* it by testing the
log's internal consistency and never comparing to `endTime`. The interim rule that draft
proposes is that a resumed run is either graded by a comparator registering its form **at its
own freeze**, or restarted from zero. **The ruling itself is verification's to propose and
Sanaa's to make**, and nothing here anticipates it.

**This act registers its form now, before compute, so that no later reader mistakes it for a
deviation — and the form is neither A nor B.** It is the **distinct-step-set test**: the set
of `Time =` values, **unioned across every log segment**, must be exactly `{1 … endTime}` —
no step missing, no step outside the registered range, and the right cardinality. It
therefore **accepts a resume, as Form B does**, while **still anchoring to the registered
`endTime`, which Form B does not** — and `endTime` is checked again separately by the
`last time == endTime` clause. `scripts/solver_log_set.py:213-216` calls it "strictly
stronger than `count == N`", and it is: a line count is satisfied by 3,000 lines that skip a
step and log another twice; this is not.

The reason it cannot be a line count is **measured on this family's own solve, not
inferred**: `SOLVE_L2` was killed by the 21:32Z reboot at `Time = 63` and resumed from the
`t = 60` checkpoint, so iterations 61–63 ran twice and the appended log holds **3,002
`ExecutionTime` lines for 3,000 physics steps**. The overlap's size varies with every kill
and is invisible from the log, so no fixed correction exists — the count has to be taken on
the physics. Sanaa's ruling of 2026-08-26 and 2026-09-12: **bookkeeping never voids physics.**
The raw line count is still reported, under a key naming it as bookkeeping, so a reader
**sees** the double-count rather than being protected from it.

**The field list for this case is `p U k omega nut phi`**, the incompressible set, registered
here explicitly. Rule 4's named list `T U p_rgh alphat nut k omega phi` is the **thermal
family's**; this is an incompressible external-flow case with no temperature, and the
substitution is registered **before compute** rather than discovered at grading time. It is
the same list `cases/navier_class/SUBOFF_A1/grade_suboff_a1.py:59` already uses for this
family.

### 8.1a ITERATIVE CONVERGENCE — GATED ON THE GRADED QUANTITY, REPORTED ON THE RESIDUALS

A completed run is not a converged one. Registered **before compute**:

- **GATED, per point: the force plateau.** `forces` writes every timestep
  (`writeControl timeStep; writeInterval 1`), so `Y′(t)` is available at every iteration.
  Over the **final 500 iterations**, the ordinary-least-squares slope of `Y′(t)` multiplied
  by 500 — the total drift across the window — must be **≤ 1 % of |Y′| at `endTime`**. A
  point failing it is **`NOT A RESULT`**, and a sweep missing any of the five fitted points
  is `NOT A RESULT` entire. At β = 0, where `Y′ → 0` and a relative test is meaningless, the
  drift is instead required to be **≤ 1e-4 in absolute terms**, the same floor as §4.3.
- **REPORTED, NOT GATED: the residuals.** Initial residuals for `p U k omega` over the final
  50 iterations are printed, maximum and final. They are **not** gated, and the reason is
  stated rather than hidden: this lane cannot defend a specific residual threshold for this
  body at this condition from anything measured, and **a threshold invented at drafting time
  to look rigorous is worse than an honest report.** The plateau test above gates the
  quantity the act actually grades — the graded force has stopped moving — which is the
  claim a residual threshold would only be a proxy for.

### 8.2 THE PLANTED CONTROL — INTO THE FORCE CHANNEL, AND IT REFUSES

Standing rule 3. The comparator plants a known perturbation, reads it back **from disk**
through **the same code path the real derivative uses**, and **REFUSES with exit 2** if the
reader cannot see it. It refuses **before** touching any real case, and it refuses rather
than degrading on any missing input.

| plant | magnitude | planted into | what it would catch |
|---|---|---|---|
| **P-A** | `total_z = 1.234e-03` at `endTime`, **decoy `5.678e-03` at t = 1** | a synthetic `postProcessing/forces/<t>/force.dat` | a force reader that reads the wrong row, the wrong column, or the wrong time |
| **P-B** | `total_y = −9.876e-04` at `endTime`, decoy `+4.321e-04` at t = 1 | a synthetic `moment.dat` | the same, in the moment channel |
| **P-C** | a case whose `endTime` fields are **older** than `0/U` | a synthetic case tree | an **inert age guard** — it must report FAILED, then PASS once the mtime is corrected |
| **P-D** | a synthetic seven-point sweep with an **exactly known slope placed OUTSIDE the band**, then a second **inside** it | the full force/moment channel, end to end | a **blind fit or a blind gate** — the comparator must return `GATE FAIL` on the first and `PASS` on the second. A gate that cannot fail is not a gate. The sign clause (§4.2) and the symmetry clause (§4.3) are each fired the same way |
| **P-E** | `Y′ = −1.215759464292e-05` and `N′ = +2.283580340844e-06` for the planted `F_z`, `M_y` — **literals computed outside the comparator** from §4's own printed constants | the normalisation and the §4.1 sign transform | a **wrong constant or a flipped sign**, which would move or invert a GATED value. The obvious spelling of this check — compare `nondim(x)` against `−x/Q_AREA` — is self-referential, passes for any constant and any sign, and would have caught nothing |

| **P-F** | a perfectly flat series, a series drifting **10× the ceiling**, and a series **one iteration short** of the 500-window | the plateau gate of §8.1a | a **plateau gate that cannot fail**, or a **missing window guard** that would grade a truncated run as converged |
| **P-G** | a complete **seven-case synthetic run tree on disk** at a known slope, then the same tree with one point's `solve_rc` removed, then with one point's `force.dat` removed | **the whole comparator, end to end**, through the same function the real grade calls | everything the other plants cannot reach, because they never hand it a case tree: it must return `PASS` and recover the planted slope to 1e-9, then `NOT A RESULT` on the broken completion, then **refuse** on the missing file |

**P-D and P-G are the plants this act turns on.** P-A, P-B, P-C and P-E prove the file
readers and the constants see. P-D proves the *derivative and the gate* see. **P-G proves
the comparator sees** — a reader can be blind at any stage, and a comparator exercised only
on an empty directory has not been exercised.

### 8.2a THE PLANTS WERE THEMSELVES MUTATION-TESTED, AND THE TEST ADDED TWO OF THEM

A plant that cannot fail is not a plant, so each was checked by deliberately breaking the
thing it guards — in a copy, never in the comparator — and requiring a refusal. Run against
the file being frozen: **fifteen mutants plus an unmutated control. The control graded
cleanly. Twelve were killed by an explicit `exit 2` refusal naming the plant that caught
them** — blind force reader (P-A), blind moment reader (P-B), inert age guard (P-C), gate
that cannot fail (P-D), missing sign clause (P-D), missing symmetry clause (P-D), wrong `U`
(P-E), wrong `L_BP` (P-E), flipped non-dimensionalisation sign (P-E), missing plateau window
guard (P-F), plateau always-pass (P-F), wrong `endTime` (P-G). **One was killed by a crash**
(a fit that ignores missing points). **Two survived and were verified *equivalent*** — a
removed `lsq` degeneracy guard and a discarded completion list — each driven against a real
synthetic tree and each shown to change **no verdict**, because a second, independent check
carries the same requirement.

**Two of the plants above exist only because that test found them missing.** P-F was added
after a mutant that deleted the plateau window guard **survived every other plant and exited
0** — nothing had ever reached `plateau()`. P-G was added after two further mutants survived
for the same reason: **with no cases on disk, the run never reached the code they broke.**
The mutation test is reported here rather than kept as a private reassurance, because this
lane's own test is evidence, not the supervisor's read, and the supervisor reads this
comparator as a diff before its output is believed.

### 8.3 WHY THE PLANT IS NOT A FORMALITY — TWO BLIND READERS, BOTH FOUND TONIGHT

1. **The `yPlus` utility.** On this box, OpenFOAM v2606 build `_481094f-20260618`,
   `postProcess -func yPlus` returned **zero on 53 of 53 patch readings** across two solvers
   and two cases, **exiting clean**, while the solver's own `-postProcess` spelling returned
   real values on identical input. Verified by the cfd-supervisor.
2. **This lane's own `zmin` reader**, found while establishing the §0 finding. A greedy
   `sed` capture returned the bounding box's *maximum* corner, so a sweep of the whole lab
   reported, cleanly and confidently, that **no mesh anywhere had a negative `zmin`**. A
   planted `log.checkMesh` carrying `zmin = −2.9927629` caught it: the reader still said
   "not-negative". **It had never once read a `zmin`.** Repaired, the same reader saw the
   plant, and the re-run found **705 of 1,585 checkMesh logs in this lab with a negative
   `zmin`** — and the three SUBOFF meshes reading exactly 0 against a reader now *proven*
   able to read otherwise.

**That is what a planted control is for, and it is why the §0 finding is evidence rather
than an assertion.** The first sweep's clean zero was false. Assume every reader in this
act is blind until a plant proves otherwise.

---

## 9. THE RUN DIRECTORY — NAMED HERE, AND THE SWEEP LAUNCHES INTO EXACTLY THIS PATH

> **`verification/runs/navier_class/SUBOFF_A1H_DRIFT/`**

| path | contents |
|---|---|
| `SUBOFF_A1H_DRIFT/MESH_FULL_L2M/` | the mirrored full-domain mesh, built once, admitted under §2.1 |
| `SUBOFF_A1H_DRIFT/BETA_m12/` | β = −12 |
| `SUBOFF_A1H_DRIFT/BETA_m08/` | β = −8 |
| `SUBOFF_A1H_DRIFT/BETA_m04/` | β = −4 |
| `SUBOFF_A1H_DRIFT/BETA_p00/` | β = 0 |
| `SUBOFF_A1H_DRIFT/BETA_p04/` | β = +4 |
| `SUBOFF_A1H_DRIFT/BETA_p08/` | β = +8 |
| `SUBOFF_A1H_DRIFT/BETA_p12/` | β = +12 |

### 9.1 THE ABSENCE OF THE NINE REGISTERED PATHS

At draft time, **2026-09-13T04:17:05Z**, each of the nine paths above was tested directly and
each is **ABSENT**, together with `cases/navier_class/SUBOFF_A1/grade_suboff_a1h.py` and this
file itself. **The existence test was run in the same invocation against
`verification/runs/navier_class/SUBOFF_A1/SOLVE_L2`, which it correctly reported EXISTS** —
so the reader is proven able to say EXISTS, and the nine ABSENTs are a measured zero rather
than a blind one.

### 9.2 THE ABSENCE OF ANY COMPUTE AT THIS CONDITION — THREE LIMBS, NAMED SEPARATELY

This is a **different and broader claim** than §9.1 and rests on different evidence, so it is
set out limb by limb rather than compressed into one confident sentence. A later reader who
doubts it can attack whichever limb they doubt.

**LIMB (i) — THE CONDITION, READ OUT OF EVERY SUBOFF `0/U`. THIRTY-ONE FILES, NOT ELEVEN.**

An earlier pass of this census found **eleven** and was wrong — its `find` carried
`-maxdepth 5`, which silently excluded every `processor*/0/U`. **Twenty more sat in
decomposed directories the glob could not see: two thirds of its own corpus.** Re-run with
no depth limit, the corpus is **31 files — 11 reconstructed and 20 per-rank** — and three
distinct values, none of them this act's:

| value | files | family |
|---|---|---|
| 2.7547576 | 20 | A1b, per-rank (`processor*/0/U`) |
| 2.893 | 6 | R1/R1b, reconstructed |
| 2.754757632 | 5 | A1b, reconstructed |
| **3.343886** | **0** | — this act's condition appears in none of them |

**All 31 are purely axial**, `(U 0 0)`, so **no yawed solve exists on either run root** — and
a drift sweep is the only thing that could produce `Y_v'` or `N_v'`.

The axiality reader was **planted on both sides in the same invocation**: a synthetic
`(3.270814068 0 -0.695232992)` — this act's own β = −12 inlet — which it reported **YAWED**,
and a synthetic `(2.893 0 0)` which it reported **AXIAL**. That plant was not decoration: the
first spelling of this reader used `tr -d` to strip the word `uniform`, which left the
letter `r` as the first token and shifted every component one place, so it reported **all 31
files NON-AXIAL** — a reader manufacturing false positives where §8.3's manufactured a false
zero. It was caught by the plant, not by inspection.

**LIMB (ii) — A FIXED-STRING CONTENT SWEEP FOR FIVE REGISTERED CONSTANTS**, over the five
SUBOFF trees (`verification/runs/navier_class/{SUBOFF, SUBOFF_A1,
SUBOFF_HULL_SAIL_4STERNPLANES}`, `cases/navier_class/{SUBOFF, SUBOFF_A1}`). Every pattern
carried a **live control in the same invocation** — the same fixed string planted in a
scratch file, which the sweep found each time:

| constant | meaning | files containing it |
|---|---|---|
| `1.42478e7` | Re_LBP | **0** |
| `1.45663e7` | Re_LOA | **0** |
| `1.118157e-05` | `k_inf` | **0** |
| `4.658989` | `omega_inf` | **0** |
| `3.343886` | `U` | **1 — and it is this act's own comparator**, `grade_suboff_a1h.py`, which defines the constant. No run data anywhere. |

**AND THE METHOD'S OWN WEAKNESS, NAMED RATHER THAN LEFT FOR A READER TO FIND.** `grep -F`
fixes the wildcard defect below and does **not** fix the **substring** defect: *a number is a
prefix of longer numbers.* A separate sweep of every `0/U` on both run roots — 3,338 files,
no depth limit — returned exactly one hit for `3.343886`, at
`/home/ubuntu/certonomous-runs/study-airfoil_blown_slot-medium-4d793a/0/U` line 13842:

```
(3.3438861e-05 -1.8414314e-07 -2.6629451e-05)
```

It is **not a SUBOFF case** — a blown-slot airfoil study, whose `constant/` holds
`triSurface` and `extendedFeatureEdgeMesh` — and the value is a velocity component inside a
`nonuniform List<vector>` **solved field**, not an inlet condition. So the pre-compute
condition holds. But look at *why* it matched: **`3.343886` is a prefix of `3.3438861e-05`.**
Verified directly — `grep -F '3.343886'` matches the line `3.3438861e-05` and does not match
`3.3438859`.

**For a numeric literal, `-F` is necessary and not sufficient.** A defensible search needs
`-F` **and an anchor** — a field boundary, a following non-digit, or a parse of the value
rather than a text match. The zeros tabled above are therefore **upper bounds on absence**
(a substring search is looser than an anchored one, so a zero remains a zero), while **any
non-zero must be run down to a parsed value before it means anything** — which is what was
done to the single hit above.

**LIMB (iii) — THE SWEEP METHOD ITSELF WAS PLANTED TWICE, AND THE SECOND PLANT FOUND A
DEFECT.**

1. **The ignore-file hazard, cleared by plant.** `grep` on this box is **ugrep 7.8.4**, and
   `.gitignore` line 67 ignores `**/postProcessing/` and line 54 `**/processor[0-9]*/` —
   *exactly* where force histories and decomposed field data live. A content sweep blind to
   ignored files would be blind to the very directories it hunts. Three probes were planted,
   one in a `postProcessing/`, one in a `processor0/`, one in a plain directory; `git
   check-ignore` confirmed the first two IGNORED. **The sweep found all three.** With no
   `GREP_OPTIONS` and no `~/.ugrep` config on this box, this invocation form is not
   ignore-blind. The probes were then removed and the sweep re-run in the same scope,
   returning the zeros above.
2. **THE WILDCARD-DOT DEFECT, found by plant and repaired.** The first pass used the patterns
   unescaped, so every `.` was a **regex wildcard**: `4.658989` matched `4<any>658989`. That
   pass returned **27 "hits" for `omega_inf` and 22 for `U`**, which a reader would then have
   spent effort categorising as mesh connectivity, solved fields at other conditions, and a
   `postProcessing/0/` time directory. **They were not occurrences of those numbers at all.**
   Re-run with `grep -F`, fixed string, the literal count is **zero** for four of the five and
   one for the fifth, as tabled above. The categorisation work was explaining matches that
   never existed.

   Recorded because it is the same failure as §8.3's `zmin` reader with the sign reversed:
   there, a broken reader manufactured a **false zero**; here, a loose pattern manufactured
   **false hits**. Both are cleared the same way — plant a known occurrence and read it back.

**FOUR READER DEFECTS WERE FOUND WHILE ASSEMBLING THIS SECTION AND §8, EVERY ONE BY A PLANT
AND NONE BY INSPECTION.** They are listed together because the pattern is the point, and
because a reader who sees only the final clean numbers would conclude the numbers were easy
to get:

| # | defect | what it produced | caught by |
|---|---|---|---|
| 1 | greedy `sed` capturing the bounding box's **maximum** corner | a false zero: "no mesh in the lab has a negative `zmin`" | a planted `log.checkMesh` with `zmin = −2.9927629` |
| 2 | unescaped `.` read as a **regex wildcard** | false hits: 27 and 22 files "containing" constants they do not contain | re-running with `grep -F` |
| 3 | `find -maxdepth 5` excluding every `processor*/0/U` | a census of 11 that should have been **31** | removing the depth limit |
| 4 | `tr -d` shifting every vector component one place | all 31 `0/U` files reported **NON-AXIAL** | a two-sided plant: a known yawed vector and a known axial one |

Defects 1 and 4 manufactured **false answers about the data**; 2 and 3 manufactured **false
answers about the corpus**. A sweep is only evidence when both are controlled, and neither is
controlled by reading the code.

### 9.3 THE LIMIT OF ALL OF IT, STATED RATHER THAN GLOSSED

The sweep in limb (ii) covers **the five SUBOFF trees, not the whole disk.** A full-disk
content sweep was run separately by another lane and is **not re-verified here**; this
document does not rest on it and does not reproduce its findings as its own. The claim this
registration actually makes is the conjunction of limbs (i)–(iii) at that scope, plus §9.1 —
and **not** "no compute exists anywhere on this box". A registration whose legality rests on
an overclaim is worse than one that states its own limit.

Only three SUBOFF case roots exist. There is no A1e tree and no A1f tree; a `find` for
`*a1f*` returns only `W4-defect-robustness/a1fs_*` and an `S1-fiml` dynamicCode hash — string
collisions on "a1fs", unrelated to this family.

**THE SWEEP LAUNCHES INTO THESE EXACT PATHS.** If the seven points were to run anywhere
else, the absence asserted above would never have been a check — it would have been a
sentence. The comparator takes these seven paths and no others.

---

## 10. WHAT THIS CASE DOES NOT CLAIM

No vertical-plane result: no `Z`, no `M`, no neutral point — that is A1g's, on a body this
one does not have. No hull/fin split: there are no fins on this body. Nothing about the fully
appended configuration, **whose own name means two different bodies in the two source
reports** (A1e Addendum 4 §D: Roddy's "fully appended" includes Ring Wing No. 1; Liu &
Huang's Config 8 does not). No grid convergence, no observed order, no GCI — **single level,
by construction, as §0 states.** No claim about A1b's `CT` gate, which keeps its own
condition, its own normalisation and its own mesh, all untouched by this file.

---

## 11. FREEZE

Frozen at the commit adding this file, before any compute at this condition and before the
mirrored mesh exists. No band, threshold, condition, normalisation, grading path or run path
above may be altered afterwards; departures land as dated addenda that strike the original
legibly and cannot move a gate, a threshold, a cap or a label.

---

# ADDENDUM 1 — 2026-09-13, cfd-supervisor. §2.1's M-1…M-7 CARRY NO DETERMINANT LIMB, AND WOULD HAVE CERTIFIED A MESH THIS LAB HAS REFUSED. DISCLOSED, NOT ALTERED.

**Version 1.0 → 1.1. Lines whose number changed above this section: 0.**

**THIS ADDENDUM ALTERS NO GATE, THRESHOLD, CAP OR LABEL. It adds none and relaxes none.**
Compute has occurred against this registration, so under rule 2 the gate set is closed and
**this addendum may only disclose.** M-1…M-7 stand exactly as frozen.

## A1.1 THE GAP, MEASURED

**`grep -ci determinant` over this document returns 0.** §2.1's seven mesh gates test cell
count, `symm` emptiness, z-symmetry, closure, non-orthogonality, skewness, and the seam —
**and no minimum cell determinant.**

**Consequence, established before it could do harm:** a proposed relocation of the sweep onto a
**mirrored SUBOFF L1** was measured against M-1…M-7 and **passes M-1, M-2, M-3, M-5 (64.95° ≤ 70)
and M-6 (2.913 ≤ 4).** It would have been reported as **"M-gates PASS."**

**`SUBOFF_A1b_PREREGISTRATION.md` line 60, frozen, says otherwise:**
`| L1 | 3,268,613 | 8.6227045e-04 ❌ | … | NOT ADMITTED — GATE FAIL on M-d |`
against a floor of `1.0e-03`. A1b forecloses the escape in its own words: *"L1 is **not**
promoted to admitted by any argument about how small the failure is."*

**And `mirrorMesh` is an isometry, which is why the L2 mirror was admissible and why the L1
mirror is not: the determinant is preserved to ten significant figures — 0.0008622704491 —
and the mirror did not repair the bad cell. It made two of them.**

## A1.2 THE CONSEQUENCE FOR THIS ACT

**Any mesh admitted under §2.1 must ALSO be checked against A1b's M-d floor of 1.0e-03
separately, because §2.1 cannot see it.** The L2 mirror this act actually runs on passes both —
L2's determinant is 1.5198839e-03, above the floor — so **no number already produced by this act
is affected.** The gap is forward-looking and it is disclosed here so a successor cannot walk
into it.

## A1.3 WHOSE FAULT, AND TWO ERRORS OF THE SUPERVISOR'S IN THE SAME EXCHANGE

**The missing limb is the drafting lane's and it reported it unprompted**, having found it only
because it checked A1b before executing an instruction from me. **Its own words: it would
otherwise have reported "M-gates PASS" on a mesh this lab has refused, and the failure would
have been invisible inside its own gate set.**

**Two errors in that exchange are mine and are recorded here rather than in a message:**

**(a) I built a rate table from DEAD LOGS.** I reported six sweep points at 51–63 h against
β = 0 at 7.2 h and called β = 0 "the outlier by seven to nine times." **The six processes had
been stopped ~37 minutes earlier** — logs frozen at 08:49:32Z, zero live ranks — so the
`ExecutionTime` series I differenced was static. **That is the dead-log trap I repaired in
`evaluate_m6i_level.sh` at `0bc8fd09d` seven hours earlier and catalogued as L-585's family.**

**(b) The comparison was also unlike-for-unlike.** β = 0 runs at **28 ranks (0.651 M cells/rank)**;
the six ran at **4 (4.561 M cells/rank)**. **The "anomaly" was the variable I had changed.** A
symmetric-case conditioning effect may exist, but this data cannot see it under a 7× shape
difference; measuring it needs one yawed point at 28 ranks.

## A1.4 WHAT IS NOT DECIDED HERE

Whether Sanaa's *"L1 stall fix and blended-wall arm first"* names **this sweep's mesh level** or
**the A1b `CT` ladder's `SOLVE_L1` stall** (A1b §10.4 quotes her: *"Triage the L1 stall (pinned at
iteration 368)"*). **That is a reading of her words and no agent may make it.** It is on her desk
with both readings and the measurement above, and **the L1 route is barred by A1b's refusal
regardless of which reading is hers.**

---

# ADDENDUM 2 — 2026-09-14, cfd lab-lane. THE SEVEN POINTS WERE STOPPED SHORT OF `endTime` BY OWNER RULING. **STRICT COMPLETION THEREFORE FAILS, AND THAT IS DISCLOSED, NOT REDEFINED.**

**Version 1.1 → 1.2. Lines whose number changed above this section: 0.**

**THIS ADDENDUM ALTERS NO GATE, THRESHOLD, CAP OR LABEL. It adds none, relaxes none, and
moves no `endTime`.** Compute has occurred against this registration, so under standing
rule 2 the gate set is closed and **this addendum may only record.** §4.2, §4.3, §5, §8.1a
and the strict completion rule stand exactly as frozen.

## A2.1 THE AUTHORITY

Sanaa's ruling, relayed to this lane, verbatim:

> *"no lets stop them and stop drivaer as well that way we gain 32 ranks. But cfd first
> checks that all residuals are converged"*

The convergence check was treated as a **precondition, not a formality**: a point that did
not satisfy it would have stayed running and been named. **All seven satisfied it**, so all
seven were stopped. The check and its numbers are §A2.3 below.

## A2.2 THE STOP, PER POINT — AND WHAT THE WINDOW IS

Each solver was allowed to reach its **next scheduled checkpoint** and was stopped only
after that write had **provably completed** (the solver had printed a later `Time =` line).
`system/controlDict` in every point carries `runTimeModifiable false`, so a `writeNow`
could **not** be injected; waiting for the scheduled write was the only route to a
checkpoint, and §9's `writeInterval 15` made that wait at most 15 iterations. The stop was
a **`SIGTERM` to the `mpirun`**, identified by `/proc/<pid>/cwd` matching the case
directory and re-verified by `cwd` in the same instant the signal was sent. **`pkill -f`
was not used and is banned on this box** — its pattern matches its own invoking shell.

| point | β | **stop iteration (last written time)** | last `Time =` in log | **the window: last 500 before the stop** | `solve_rc` | mpirun pid |
|---|---|---|---|---|---|---|
| `BETA_m12` | −12 | **2745** | 2746 | **2246 → 2745** | 1 | 1486354 |
| `BETA_m08` | −8 | **2790** | 2791 | **2291 → 2790** | 1 | 1486350 |
| `BETA_m04` | −4 | **2820** | 2821 | **2321 → 2820** | 1 | 1486399 |
| `BETA_p00` | 0 | **2880** | 2881 | **2381 → 2880** | 1 | 1486345 |
| `BETA_p04` | +4 | **2805** | 2806 | **2306 → 2805** | 1 | 1486327 |
| `BETA_p08` | +8 | **2835** | 2836 | **2336 → 2835** | 1 | 1486419 |
| `BETA_p12` | +12 | **2670** | 2671 | **2171 → 2670** | 1 | 1486309 |

**The checkpoints are complete and banner-closed.** Every one of `U p k omega nut phi yPlus`
in each of `processor{0,1,2,3}/<stop>/` — **28 files per point, 196 in all** — ends with the
OpenFOAM closing banner as its last non-blank line; **0 are truncated**. **Standing rule 3:
that zero is planted.** The same checker was handed a deliberately truncated copy of
`BETA_p00/processor0/2880/U` beside an intact `yPlus` and returned **`NOT banner-closed: 1`**,
naming the truncated file and clearing the intact one. A zero from a reader not shown able
to return a non-zero is not evidence; this one was shown.

## A2.3 THE CONVERGENCE CHECK SANAA IMPOSED — ALL SEVEN CONVERGED

**Residuals — REPORTED, NOT GATED (§8.1a says so in advance and this addendum does not
change it).** Maximum initial residual over the **last 500 iterations**, final value in
parentheses, read from each point's **own `log.simpleFoam`**, one named artifact per row:

| point | β | Ux | Uy | Uz | p | k | omega |
|---|---|---|---|---|---|---|---|
| `BETA_m12` | −12 | 8.73e-07 (7.4e-07) | 3.11e-05 (2.3e-05) | 3.89e-06 (2.7e-06) | 2.59e-05 (2.5e-05) | 7.86e-06 (7.7e-06) | 1.67e-07 (1.7e-07) |
| `BETA_m08` | −8 | 1.34e-07 (1.3e-07) | 4.48e-06 (4.2e-06) | 2.03e-06 (2.0e-06) | 1.27e-06 (1.2e-06) | 2.78e-06 (2.7e-06) | 1.79e-07 (1.8e-07) |
| `BETA_m04` | −4 | 1.08e-07 (1.0e-07) | 2.36e-06 (2.3e-06) | 9.79e-07 (9.3e-07) | 6.76e-07 (6.0e-07) | 2.77e-06 (2.7e-06) | 1.85e-07 (1.8e-07) |
| `BETA_p00` | 0 | 9.96e-08 (9.5e-08) | 1.79e-06 (1.7e-06) | 4.94e-06 (4.8e-06) | 9.45e-07 (9.0e-07) | 2.46e-06 (2.4e-06) | 1.61e-07 (1.6e-07) |
| `BETA_p04` | +4 | 1.07e-07 (1.0e-07) | 2.46e-06 (2.3e-06) | 1.02e-06 (9.7e-07) | 6.69e-07 (5.8e-07) | 2.75e-06 (2.6e-06) | 1.86e-07 (1.8e-07) |
| `BETA_p08` | +8 | 1.38e-07 (1.3e-07) | 4.86e-06 (4.6e-06) | 2.35e-06 (2.2e-06) | 1.38e-06 (1.2e-06) | 2.77e-06 (2.7e-06) | 1.80e-07 (1.8e-07) |
| `BETA_p12` | +12 | 8.73e-07 (8.3e-07) | 2.91e-05 (2.9e-05) | 3.70e-06 (3.3e-06) | 2.58e-05 (2.5e-05) | 7.98e-06 (7.8e-06) | 1.67e-07 (1.7e-07) |

**A residual floor is not convergence of the quantity being graded**, and §8.1a already said
so. The test that decides is the **plateau of `Y′`** over the final 500 iterations:
OLS slope × 500 ≤ 1 % of |`Y′`| (≤ 1e-4 absolute at β = 0). Applied at the stop iteration:

| point | β | `Y′` window mean, last 500 | `Y′` window mean, previous 500 | **drift = 500 × slope** | **ceiling** | **verdict** |
|---|---|---|---|---|---|---|
| `BETA_m12` | −12 | −1.946287e-04 | −1.946346e-04 | 4.6334e-08 | 1.9459e-06 | **CONVERGED** |
| `BETA_m08` | −8 | −1.819245e-04 | −1.819278e-04 | 6.9950e-08 | 1.8191e-06 | **CONVERGED** |
| `BETA_m04` | −4 | −9.830079e-05 | −9.829310e-05 | 2.2096e-08 | 9.8340e-07 | **CONVERGED** |
| `BETA_p00` | 0 | +8.494116e-09 | +4.037364e-08 | 1.2056e-08 | 1.0000e-04 | **CONVERGED** |
| `BETA_p04` | +4 | +9.827669e-05 | +9.823346e-05 | 7.8529e-08 | 9.8252e-07 | **CONVERGED** |
| `BETA_p08` | +8 | +1.819195e-04 | +1.819650e-04 | 6.9614e-09 | 1.8193e-06 | **CONVERGED** |
| `BETA_p12` | +12 | +1.944281e-04 | +1.944482e-04 | 2.2076e-08 | 1.9441e-06 | **CONVERGED** |

**The one point that must not be rounded into compliance is β = 0, and it is not.** Its
window-mean **ratio** moves 135 % — but that is the ratio of 8.49e-09 to 4.04e-08, two
numbers that are both essentially zero, and a ratio test at β = 0 is exactly the test §8.1a
refused to register. The registered criterion there is **absolute**, and the absolute change
between the two windows is **3.19e-08** against a floor of **1e-4** — smaller by a factor of
3,100 — with a drift of 1.21e-08. It converges on the criterion this document froze, not on
one chosen tonight.

`N′` window means are reported beside them, ungated (§5 leaves `N_v′` ungated): −12
+5.477412e-04, −8 +3.219319e-04, −4 +1.549161e-04, 0 +7.477132e-09, +4 −1.549230e-04,
+8 −3.219433e-04, +12 −5.477358e-04; the largest `N′` drift over 500 iterations across the
seven is **8.95e-09**.

## A2.4 **STRICT COMPLETION FAILS ON ALL SEVEN. NO ADDENDUM CAN CONVERT THAT INTO A PASS.**

Standing rule 4 requires, among its clauses, **`rc = 0`**, an **`End` line**, and
**last time == `endTime`**. `endTime` is **3000** (§9, frozen). The seven stopped at 2670 –
2880. Measured: **`solve_rc = 1` on all seven; `grep -c '^End$'` returns 0 on all seven; no
`3000` directory exists in any case.** Therefore:

> ### **STRICT COMPLETION: FAILS, all seven points.**

**`endTime` is not free-floating bookkeeping and this addendum does not move it.** A run
stopped at 2,745 of 3,000 is not a completed run, and no dated note can make it one. This
is recorded rather than redefined.

## A2.5 **AND IT COSTS THE ACT NOTHING, FOR A REASON REGISTERED BEFORE COMPUTE**

**The sweep was already `NOT A RESULT` before this stop, on §4.2's own clause.** §4.2,
frozen before any number existed, says: *"If the fitted `Y_v′` comes out **positive**, the
verdict is **`NOT A RESULT`** … and the printed reason is 'sign convention or solve is
wrong'."*

**The fit is positive.** Least squares over the five points |β| ≤ 8, on the window means
above: **`Y_v′ = +1.327616e-03`** (`N_v′ = −2.294674e-03`, ungated). Roddy's experimental
`Y_v′ = −0.023008`. The sign is inverted **and** the magnitude is a factor of 17 small.
**The label was therefore already determined by a clause frozen at `79b4de868`, and the
early stop changes nothing about it.** The sole verdict remains the frozen comparator's.

**The mechanism is measured and it sits inside the freeze, which is why §4.2 fired.**
Line 139 of this document registers **`farfield` stays `slip`**. §2.1's M-3 and §1's table
put those `farfield` walls at **z = ±2.9927629 m** on a body 4.356 m long. A slip wall
carries **zero normal flux**, so the cross-flow `v′ = sin β` injected at the inlet has no
face through which to leave the domain: the registered configuration is a **closed duct in
z**. That the cross-flow cannot pass is a property of the registered boundary set, stated
here as the reading it is; what is **measured** is that the fitted `Y_v′` is positive and
that `|Y′|` at β = ±8 is 1.82e-04 against Roddy's 0.023-scale ground.

## A2.6 THE GRADER — ARMED ON THE RECORDED STOP, NOT REWRITTEN

`verification/runs/navier_class/SUBOFF_A1H_DRIFT/L1M_GRADE/grade_watch_a1h_l1m.sh`, a
sibling lane's detached watcher, was **already running** and waits on `solve_rc` rather than
on a pid. All seven `solve_rc` files now exist; its own log records `ALL SEVEN HAVE solve_rc`
at 2026-09-14T00:15:23Z. **A second grader was not written.** It runs the frozen comparator
`cases/navier_class/SUBOFF_A1/grade_suboff_a1h.py` — blob-pinned to `13ac40d37…` at the
pre-registration commit — with **`--end-time 3000`, the registered value, unchanged.** That
is deliberate: handing it the stop iterations as an `endTime` would be manufacturing a
completion, and this lane will not do it. The comparator will report completion FAILING on
all seven, which is the true state. **The stop iterations of §A2.2 are the record a
successor cites**; the window means of §A2.3 are **REPORTED, NOT GRADED** and are this
lane's reading, not the comparator's verdict.

## A2.7 COST — ESTIMATE VERSUS ACTUAL (standing rule 12)

| point | `ExecutionTime` at stop | ranks | **core-min (gross)** | s/iteration |
|---|---|---|---|---|
| `BETA_m12` | 52478.29 s | 4 | 3498.6 | 19.12 |
| `BETA_m08` | 52577.91 s | 4 | 3505.2 | 18.85 |
| `BETA_m04` | 52418.28 s | 4 | 3494.6 | 18.59 |
| `BETA_p00` | 52590.65 s | 4 | 3506.0 | 18.26 |
| `BETA_p04` | 52439.78 s | 4 | 3496.0 | 18.69 |
| `BETA_p08` | 52573.40 s | 4 | 3504.9 | 18.54 |
| `BETA_p12` | 52617.85 s | 4 | 3507.9 | 19.71 |
| **total** | | **28** | **24,513.2** | **18.82 mean** |

§6 registered **56,336 core-min** for 7 × 3000 iterations at **40.24 s/it on 4 ranks**, i.e.
2.6827 core-min per iteration. The seven actually ran **19,545 iterations**, for which the
registered rate predicts **52,432 core-min**. Actual **24,513.2**. **Ratio actual/predicted
= 0.467.** The gap is **misprediction of the per-iteration rate, not waste and not
contention**: the measured 18.82 s/it against a registered 40.24 s/it is **2.14× faster**,
and no point stalled (no row exceeds 3600 s of wall between checkpoints). Derived cost at
the owner-stated **$0.0513/core-h**: **$20.96 — DERIVED, NOT MEASURED**; the box cannot read
its own billing. This row belongs in `docs/COST_CALIBRATION.md` under that file's append
rules.

*Appended by a cfd `lab-lane`, 2026-09-14. No gate moved. No verdict claimed — the verdict
is the frozen comparator's. No submission, nothing sent, nothing leaves the box.*
