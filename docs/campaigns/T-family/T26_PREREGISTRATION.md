# T26 — motor-in-duct conjugate heat transfer, GENUINELY THREE-DIMENSIONAL: pre-registration

> **STATUS: STAGE 1 (SETUP) DRAFT. NOT FROZEN. NOT COMMITTED AS A FREEZE.
> AUTHORISES NOTHING. ZERO SOLVER COMPUTE HAS BEEN SPENT.**
> The freeze is the supervisor's act, not this lane's. `CLAUDE.md` rule 2:
> once this document is landed as the freeze commit, no gate, threshold, cap or
> label below may change; a departure lands only as a dated addendum appended at
> the foot, and originals are struck, never rewritten.
> §12 lists exactly what is still missing before it CAN be frozen.

Verdict vocabulary fixed by `CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE
FAIL / NOT A RESULT / BLOCKED / PENDING.** No other word appears as a verdict
here. **This document assigns no verdict.** The one measured result it carries —
the geometry gate of §2 — is reported with its instrument and its exit code.

Governing authority: **`docs/charters/CASE_PROTOCOL_CHARTER.md` v1.0**, IN FORCE
2026-09-10, whose scope is *"every 3D case and every Navier-class case"*. This
rung is a 3D case and is registered to that charter's §1, clause by clause.

---

## 0. WHAT THIS RUNG IS, THE ID, AND WHY IT EXISTS

### 0.1 Why it exists — stated first, because it is a correction

Sanaa asked for more 3D industry cases in the demo. The heat-transfer supervisor
surveyed the territory and reported the truth upward: **the entire T23/T24
motor-in-duct spine that Act A films is a 5.0° AXISYMMETRIC WEDGE.**
`T23_PREREGISTRATION.md:132` registers it in those words — *"**2-D axisymmetric
wedge, θ = 5.0°**, one cell thick"* — and `checkMesh` reports two geometric
directions for it. **It cannot honestly be called a 3D simulation, and this lab
does not describe it as one.**

**T26 is the genuinely three-dimensional successor.** Same industry subject —
electric-motor thermal management in a cooling duct — on a full 360° geometry
that carries the physics a wedge structurally cannot represent:

| what a 5° wedge cannot hold | what T26 holds |
|---|---|
| any azimuthal variation whatever | three support struts at 0°, +120°, −120° |
| a conduction path from the motor to the duct wall | the struts ARE that path, conjugate at both ends |
| a three-dimensional wake | three strut wakes convecting onto the hub tail |
| a circumferentially non-uniform `T_max` | `T_max` located in 3-space, not on a ray |

### 0.2 What this rung is NOT — stated before anything is spent

> **T26 registers GRID CONVERGENCE AND CONSERVATION on a 3D geometry. It is
> VERIFICATION, NOT VALIDATION.** It earns nothing about the absolute accuracy
> of `T_max`, because **no reference of any tier exists for this configuration**
> (§5.4). Any later claim that T26 validates a motor temperature is a claim this
> document does not support and may not be cited for.

**T26 does not supersede, amend or re-open T23, T23G, T23G2, T23G2R, T23G2Rn,
T23G2Rn2 or T24.** No number from any of them enters any gate, band, threshold
or referent below. T23 appears in exactly three non-evidentiary roles: as the
**comparability statement** of §2.5, as the **class-default source** for the
region decomposition (§3.1), and as the **negative precedent** of §6.

### 0.3 THE ID — RE-DERIVED FROM THE MAXIMUM, NEVER FROM A COUNT

`CLAUDE.md` rule 11's discipline, applied to rung ids. **The derivation was
taken three ways, and the three do not agree on the SET — only on the MAXIMUM.**
That disagreement is the reason the rule is "from the maximum, never a count",
and it is recorded rather than smoothed over.

| reading | ids found | count | **maximum** | what "count + 1" would return |
|---|---|---:|---:|---|
| **A — disk names only**, `docs/campaigns/T-family/` ∪ `verification/runs/T-family/`, self excluded | {1, 3, 4, 5, 6, 8, 9, 10, 11, 13 … 25} | **22** | **25** | **T23 — TAKEN** |
| **B — `T_FAMILY_INDEX.md` text only** | {1 … 21, 23, 24, 25} | **24** | **25** | T25 — **TAKEN** |
| **C — the union, A ∪ B** | {1 … 25}, contiguous | **25** | **25** | T26 |

- **THE ID IS T26**, taken from the **maximum, 25**, which is the one figure all
  three readings agree on. No file, directory or record named `T26*` exists
  anywhere in the tree (`find -iname 'T26*'`, empty).

**Three precisions the derivation turned up:**

1. **A count DOES collide, on two of the three readings.** Reading A returns
   **T23** and reading B returns **T25**, both of which are taken and both of
   which would have overwritten a live rung's namespace. Reading C returns 26
   only because that set happens to be contiguous — **a coincidence, not a
   method**, and it is stated as a coincidence so nobody promotes it into one.
2. **`T_FAMILY_INDEX.md` alone is not sufficient: it names T22 ZERO times**
   (`grep -c '\bT22\b'` = 0) while `verification/runs/T-family/T22_runs/`
   exists on disk. A derivation from the index alone is taken from a set that is
   missing a member.
3. **Disk names alone are not sufficient either: T2, T7 and T12 appear only in
   the index prose**, never as a file or directory name (6, 4 and 5 hits
   respectively). Neither source is a superset of the other, so **the union is
   the only defensible population** — which is exactly what row C is.

**This derivation must be RE-TAKEN in the committing invocation**, in the same
shell invocation as the write, because peers take numbers constantly and a
derivation taken minutes earlier is a fact about a different tree.

Run root **`verification/runs/T-family/T26_runs/`** (filing charter R6).
Registration at `docs/campaigns/T-family/T26_PREREGISTRATION.md`, on the same
basename pattern `scripts/check_filing.py` accepts for `T23_PREREGISTRATION.md`.

### 0.4 THE RULE-2 PRE-COMPUTE CONDITION, BY NAMING THE DIRECTORIES THAT DO NOT EXIST

**THE CONDITION:** *no compute has run under any T26 registration.*

| directory that must be ABSENT | why it is the right one to name |
|---|---|
| `verification/runs/T-family/T26_runs/` | this rung's own run root. If it exists, this document is being written after its own compute and §1–§9 are closed to change. |
| `verification/runs/T-family/T26_MESH_runs/` | the name a mesh-only arm filed separately would have taken. |
| `verification/runs/F14-cooling-ladder/T26*` | the other root in this team's territory a 3D duct case could plausibly have been filed under. |

**MEASURED 2026-09-10, and TO BE RE-MEASURED in the committing invocation,
under a LIVE PLANTED CONTROL** (`CLAUDE.md` rule 3): all three **ABSENT**, and
the identical predicate run against a directory that **does** exist
(`verification/runs/T-family/T23_runs/`) returned **PRESENT** — so the reader
was shown able to see a non-zero before its zero was believed.

### 0.5 Relationship to the CASE_PROTOCOL §7 fronts — DISCLOSED, NOT ARGUED

CASE_PROTOCOL §7 names heat-transfer's front as **T4e**, and adds **"No new
families."** Both are addressed on the record:

- **"No new families" is complied with.** T26 is a rung of the existing
  T-family, taken from its maximum id, filed under its existing campaign and run
  roots, using its existing instrument conventions.
- **The front.** T26 is a SECOND item alongside T4e, dispatched by the
  heat-transfer supervisor against Sanaa's *"the more 3D industry cases we have
  and can put in the demo the better."* **This lane does not rule on whether a
  second item is inside the front**; it is disclosed here so the supervisor
  rules on it at the freeze rather than after the spend.

---

## 1. THE GEOMETRY — MEASURED, NOT ASSUMED

**Source surface:** `cases/demo-surfaces/motor_in_duct.stl`
**sha256** `131aab8e17242415364d2f1147a76cfbdc7fe5f48287a0996c2318249857db5f`
**Header:** `ACT A motor-in-duct display surface (F28 D=0.25 L=0.2 Dhub=0.075)`
6,288 binary facets, 9,432 unique edges, 3,152 unique vertices, **5 connected
components**.

**Bounding box, MEASURED (metres — see GEO-1 in §2):**

| axis | min | max | extent |
|---|---:|---:|---:|
| x (duct axis) | 0.000000 | 0.200000 | **0.200000** |
| y | −0.130000 | +0.130000 | 0.260000 |
| z | −0.130000 | +0.130000 | 0.260000 |

**The five components, MEASURED:**

| # | name | facets | axial x | radius r | area m² | signed volume m³ |
|---|---|---:|---|---|---:|---:|
| 0 | `hub` (motor nacelle) | 5,376 | 0.037500 → 0.162500 | 0.000000 → 0.037500 | 0.030676 | +4.627164e-04 |
| 1 | `duct` (shell) | 768 | 0.000000 → 0.200000 | 0.125000 → 0.130000 | 0.328391 | +8.005344e-04 |
| 2 | `strutA` | 48 | 0.082500 → 0.112500 | 0.033750 → 0.125079 | 0.006449 | +1.095750e-05 |
| 3 | `strutB` | 48 | 0.082500 → 0.112500 | 0.033750 → 0.125079 | 0.006449 | +1.095750e-05 |
| 4 | `strutC` | 48 | 0.082500 → 0.112500 | 0.033750 → 0.125079 | 0.006449 | +1.095750e-05 |

**Facet resolution, MEASURED:** 96 circumferential segments on both duct and
hub (3.75° arc), confirmed independently by volume: the duct shell's measured
volume is **0.99929 ×** the exact annulus π(0.130²−0.125²)(0.2), and a regular
96-gon's area ratio is (96/2π)sin(2π/96) = **0.99943**. Shortest facet edge
**8.539e-04 m**; longest **2.002e-01 m**. Bore perimeter **0.785258 m**, hub
barrel perimeter **0.235577 m** (both 96-gon, machine-evaluated).

**The hub is a shaped spindle, not a cylinder.** Its measured volume is
**0.8379 ×** a plain cylinder of the same radius and length, and its radius
profile over 30 axial stations rises from 0 at x = 0.0375 to 0.0375 at
x ≈ 0.0625, holds a constant-radius barrel to x ≈ 0.132, and tapers back to 0 at
x = 0.1625. **Registered as: rounded nose 0.025 m, barrel 0.0694 m, tapered tail
0.030 m.** This is recorded because a "cylinder" assumption would misplace both
the separation point and the wake.

**The struts, MEASURED:** three, at azimuths **0°, +120°, −120°**; axial chord
**0.030000 m** (x 0.0825 → 0.1125, centred on x = 0.0975); **constant physical
thickness 4.000 mm** (the ±3.3913° angular half-span is the extreme at the inner
radius, 2 × 0.03375 × sin 3.3913° = 4.000 mm); radial span 0.033750 → 0.125079.

### 1.1 D AND H — the characteristic dimensions this rung uses

| symbol | value | how obtained |
|---|---:|---|
| **D** — duct inner diameter | **0.250000 m** | 2 × measured duct inner circumradius 0.125000 |
| **D_hub** — hub barrel diameter | **0.075000 m** | 2 × measured hub max radius 0.037500 |
| **H** — annulus radial gap | **0.087500 m** | (D − D_hub)/2 |
| **H/D** | **0.350000** | derived |
| **D_h** — annulus hydraulic diameter, ideal | **0.175000 m** | D − D_hub (concentric annulus) |
| **D_h** — annulus hydraulic diameter, **AS FACETED** | **0.174906 m** | 4A/P on the measured 96-gons: A = 0.0490523 − 0.0044147 = 0.0446376 m²; P = 0.785258 + 0.235577 = 1.020835 m |
| **L_body** — STL duct length | **0.200000 m** | measured bbox x-extent |
| **L_hub** — hub length | **0.125000 m** | measured |
| duct wall thickness | **0.005000 m** | 0.130000 − 0.125000 |

**REGISTERED: `D_h = 0.174906 m` is the value every derived quantity below
uses** — the faceted one, not the ideal one, because the faceted surface is what
the solver meshes. The **0.0535 %** difference from the ideal 0.175000 m is
stated so it is never rediscovered as a discrepancy.

> **A CORRECTION THIS LANE MADE TO ITS OWN ARITHMETIC BEFORE THE FREEZE,
> recorded rather than silently fixed.** The first pass evaluated sin(π/96) as
> the RADIAN value 0.0327249 instead of the SINE 0.0327190, giving
> P = 1.020290 and D_h = 0.174994 (0.003 % from ideal). Every quantity
> downstream of D_h — Re, f, C_f, τ_w, u_τ, Δ₁ — was recomputed from the
> machine-evaluated value. **The registered layer counts 18 / 12 / 5 are
> unchanged; the correction lands in the fourth significant figure.** It is
> recorded because a pre-registration is evidence only if its arithmetic is the
> arithmetic that ran.

### 1.2 COMPARABILITY WITH THE AXISYMMETRIC PREDECESSOR — the point of §1.1

`T23_PREREGISTRATION.md:254` registers **D_h = 0.175 m**; `:130` registers the
housing as a hollow cylinder **r_o = 0.0375 m, L = 0.125 m**.

| quantity | T23 (5° wedge) | T26 (3D), measured | agreement |
|---|---:|---:|---|
| annulus D_h | 0.175 m | 0.174906 m | **0.054 %** |
| housing / hub outer radius | 0.0375 m | 0.0375000 m | **exact** |
| housing / hub axial length | 0.125 m | 0.125000 m | **exact** |
| H/D | 0.350 | 0.350000 | **exact** |
| azimuthal extent | 5.0° wedge | 360° | — |
| struts | none | three | — |
| hub shape | cylinder | shaped spindle | **DIFFERENT — §1** |

> **REGISTERED: T26 is dimensionally comparable to T23 on D, D_hub, H/D and D_h,
> and NOT comparable on hub shape, azimuthal extent or strut blockage.** Any
> later cross-reading of a T26 number against a T23 number must carry this row.
> **No T23 number is used as a referent here.**

### 1.3 Blockage, registered before compute

- hub blockage of the duct: (0.075/0.250)² = **9.000 %**
- strut blockage of the annulus: 3 × 0.004000 × (0.125079 − 0.033750) / 0.0446376 = 1.09595e-3 / 0.0446376 = **2.455 %** — unchanged by the D_h correction, which touched the perimeter, not the area

---

## 2. THE GEOMETRY GATE — REGISTERED, INSTRUMENTED, AND ALREADY RUN

**Instrument:** `docs/campaigns/T-family/geometry_gate_t26.py`.
Exit codes: **0** = every check PASS; **2** = REFUSED, deficiency named;
**3** = the gate's own planted control failed, so nothing it printed is
evidence. **The gate never degrades; it refuses** (`CLAUDE.md` rule 4's posture,
applied to admission).

### 2.1 The gates and their thresholds — FROZEN VALUES

| id | check | threshold | MEASURED | verdict |
|---|---|---|---:|---|
| **GEO-1** | units: header-declared dimension vs measured bbox | ≤ 1.0e-6 m | D 0.250000 vs 0.25; L 0.200000 vs 0.2; D_hub 0.075000 vs 0.075 — all **0.0e0** | **PASS** |
| **GEO-2** | closed surface: open edges (multiplicity 1) | **0** | **0** of 9,432 | **PASS** |
| **GEO-3a** | manifold: edges with multiplicity > 2 | **0** | **0** | **PASS** |
| **GEO-3b** | consistent orientation: directed edges seen twice | **0** | **0** | **PASS** |
| **GEO-4** | outward normals: signed volume per component | **> 0** on all 5 | +4.63e-4, +8.01e-4, +1.10e-5, +1.10e-5, +1.10e-5 | **PASS** |
| **GEO-5** | degenerate facets: area < 1.0e-14 m² | **0** | **0** of 6,288 | **PASS** |
| **GEO-6** | self-intersecting non-adjacent facet pairs **WITHIN** a component | **0** | **0** on every one of the 5 | **PASS** |
| **GEO-7** | inter-component intersection | **declared, with the overlap measured** | see §2.3 | **DECLARED** |
| **GEO-8** | feature resolution: surface cell ≤ ⅓ of the smallest named feature | strut thickness 4.000 mm ⟹ cell ≤ **1.333 mm** | see §3.3 | **drives the mesh, §3.3** |

**GATE RESULT: `GEOMETRY GATE: PASS`, exit code 0.**
Cost: **3 wall s × 1 rank = 0.05 core-min, MEASURED** (`date +%s` either side).

### 2.2 THE PLANTED CONTROL — rule 3, and it caught a real reader defect

Every GEO check above can return **zero**, and a broken reader returns the same
zero. `--selftest` therefore drives the SAME production functions in **both
directions** — the clean surface must fire NOTHING, and a mutant with a known
defect must be CAUGHT:

| arm | direction | result |
|---|---|---|
| clean surface, 0 open edges / 0 non-manifold / 0 clashes / 0 degenerate / V > 0 | must NOT fire | **PASS** (5 arms) |
| MUTANT: one facet deleted | open edges 3 > 0 | **PASS** |
| MUTANT: one winding flipped | orientation clashes 3 > 0 | **PASS** |
| MUTANT: zero-area facet appended | degenerate 1 > 0 | **PASS** |
| MUTANT: every normal inverted | signed volume −1.296e-03 < 0 | **PASS** |
| MUTANT: two crossing triangles | self-intersections 1 > 0 | **PASS** |
| CONTROL: two disjoint triangles | self-intersections 0 | **PASS** |
| CONTROL: two **coplanar disjoint** triangles | self-intersections 0 | **PASS** |
| MUTANT: two **coplanar overlapping** triangles | self-intersections 1 > 0 | **PASS** |

**SELFTEST PASS, exit 0, 13 arms.**

> **A DEFECT THE CONTROL FOUND, RECORDED RATHER THAN QUIETLY FIXED.** The gate's
> first run **REFUSED with exit 2**, naming 8,838 self-intersecting pairs on the
> duct and 96 on the three struts. **That refusal was FALSE and the reader was
> at fault.** The Möller axis set {n₀, n₁, e₀ᵢ×e₁ⱼ} is complete only for
> **non-coplanar** triangles; applied to a coplanar pair every one of those
> eleven axes degenerates or lies in-plane, so the test reports "intersecting"
> for every coplanar pair — including two disjoint facets of the same flat end
> cap. The repair adds the six in-plane axes n×e (the 2-D SAT in the shared
> plane) and a positive far-side epsilon; the re-run returns **0 on all five
> components**. Both coplanar selftest arms were added in the same edit, so the
> defect cannot return unnoticed. **The condition was cleared and the gate
> re-run; no "green" was written from an inference.**

### 2.3 GEO-7 — the inter-component intersections, DECLARED with measured overlap

The five components are individually closed and non-self-intersecting. They
**do** intersect each other, **by construction, and it is intended**:

| pair | measured overlap | registered treatment |
|---|---:|---|
| strut ∩ hub | strut inner radius 0.033750 vs hub barrel radius 0.037500 → **3.750 mm radial embedment** | UNION. Both are aluminium and physically continuous; they become ONE solid region `housing` (§3.1). |
| strut ∩ duct | strut outer radius 0.125079 vs duct bore circumradius 0.125000 → **0.079 mm** past the vertices, **0.145 mm** past the 96-gon flats (0.1249331) | UNION into the `duct` solid region. Below every registered cell size at every level, so it is a snap detail, not a geometric feature. |

**REGISTERED: GEO-6's threshold of zero is INTRA-component. Inter-component
intersection is admitted only where declared in this table with its overlap
measured.** An undeclared inter-component intersection is a refusal.

### 2.4 What this gate does NOT check — named, not hidden

- **Curvature-based surface resolution** (CASE_PROTOCOL §1 names it). Not
  applicable as a surface property here: the source surface is already faceted
  at a fixed 3.75°, so curvature is discretised, not continuous. It is handled
  instead as the `resolveFeatureAngle`/`nCellsBetweenLevels` setting of §3.3.
- **Region topology inside snappy** (`locationInMesh` reachability, cellZone
  closure). That is a stage-2 check, not an admission check, and it is listed in
  §8.2.

---

## 3. MESH — PHYSICS-DERIVED, THREE LEVELS, RATIO 1.5

### 3.1 Regions — FOUR, and the reason

| region | material | what it is | source |
|---|---|---|---|
| `fluid` | air | the duct bore, extended axially (§3.2) | duct component minus hub/struts |
| `core` | winding + lamination pack, **k = 40 W/m·K** | hub interior inset 4.000 mm | class default from `T23_PREREGISTRATION.md:131` |
| `housing` | aluminium | hub shell 4.000 mm **∪ the three struts** | GEO-7 union |
| `duct` | aluminium | the 5.000 mm annular shell, x ∈ [0, 0.2] | duct component |

**`housing` and `duct` are separate regions joined only through the struts.
That conjugate path is the physics this rung exists to resolve and the wedge
cannot hold.** The duct's outer surface (r = 0.130) carries an external
convection BC to ambient; it is **not** a conjugate interface.

**Provenance flag, CASE_PROTOCOL §1:** the knowledge base holds no entry for
"3D multi-region CHT with a strut conduction bridge". The four-region
decomposition, the 4 mm housing wall and k = 40 W/m·K are registered
**"class default, first use"**, provenance = `T23_PREREGISTRATION.md:129–131`
extended by this lane. **A missing entry never waits.**

### 3.2 Domain

| item | value | basis |
|---|---:|---|
| inlet plane | x = **−0.175000 m** | **1.0005 × D_h** upstream of the duct entrance |
| outlet plane | x = **+0.900000 m** | **4.0021 × D_h** downstream of the duct exit (0.2 + 0.700000) |
| total axial length | **1.075000 m** | derived |
| cross-section | the measured 96-gon bore, circumradius 0.125000 | the STL itself |

> **REGISTERED MODELLING ASSUMPTION, stated as an assumption and not as a
> result:** a fully developed annular profile at Re_Dh ≈ 2.2e5 needs 10–15 D_h
> of entry length (1.75–2.6 m). **1 D_h is not that**, and the inlet is
> registered as **uniform U with I = 5 %, ℓ = 0.07 D_h**, i.e. a DEVELOPING
> annulus. Its effect on `T_max` is **bounded, not assumed away**, by the
> registered-but-deferred sensitivity arm **S1** of §9.4.

### 3.3 Resolution derived FROM THE PHYSICS — the full arithmetic

**Fluid properties, air at 300 K, 101 325 Pa** (registered; **class default,
first use** for this rung — Sutherland and the standard 300 K table, not a
previous rung's numbers):

| property | value | derivation |
|---|---:|---|
| ρ | 1.176591 kg/m³ | p/(R T), R = 287.058 |
| μ | 1.846002e-05 Pa·s | Sutherland 1.458e-6 T^1.5/(T+110.4) |
| ν | 1.568940e-05 m²/s | μ/ρ |
| k | 0.026240 W/m·K | 300 K table |
| c_p | 1005.0 J/kg·K | 300 K table |
| **Pr** | **0.707024** | μ c_p / k |

**Operating point, REGISTERED (a registration input, not a derived value):**
`U_inf = 20.000 m/s`, `P_loss = 305.0 W`, `T_ambient = 300.0 K`. Both taken from
Sanaa's Case 3 directive set as the single most load-bearing point
(`T23_PREREGISTRATION.md:336`, `:333`); **no T23 SOLVED number is used.**

**Everything below is derived from those inputs, not read off a previous rung:**

| step | formula | value |
|---|---|---:|
| Reynolds number | Re = U D_h/ν = 20 × 0.174906 / 1.568940e-5 | **222 961** |
| Darcy friction factor | Petukhov f = (0.790 ln Re − 1.64)⁻² | **0.0152844** |
| Fanning | C_f = f/4 | **0.00382109** |
| wall shear | τ_w = C_f ½ρU² | **0.899173 Pa** |
| friction velocity | u_τ = √(τ_w/ρ) | **0.874196 m/s** |
| **y at y⁺ = 1** (cell centre) | y = y⁺ν/u_τ | **1.794724e-05 m** |
| **first-cell THICKNESS** | Δ₁ = 2y | **3.589448e-05 m = 35.89 µm** |
| hub BL thickness | δ = 0.37 x Re_x^(−1/5), x = 0.125, Re_x = 159 343 | **4.2135e-03 m** |
| **hub layer count** | Δ₁(rᴺ−1)/(r−1) ≥ δ, r = 1.2 | **N = 18** (delivers 4.5987 mm) |
| strut BL thickness | δ = 0.37 c Re_c^(−1/5), c = 0.030, Re_c = 38 242 | **1.3453e-03 m** |
| **strut layer count** | same, r = 1.2 | **N = 12** (delivers 1.4207 mm) |
| duct-bore Δ₁ at y⁺ = 30 | Δ₁ = 2 y⁺ν/u_τ | **1.07683e-03 m** |
| **duct layer count** | r = 1.2 | **N = 5** (delivers 8.0134 mm) |

**Wall treatment, REGISTERED: `nutUSpaldingWallFunction` +
`alphatJayatillekeWallFunction` on EVERY wall, at every level.** It is
continuous in y⁺, so the hub (y⁺ ≈ 1, resolved) and the duct bore (y⁺ ≈ 30, wall
function) are served by ONE registered choice and the rung never silently
switches treatment between patches or between levels.

**Closure, REGISTERED: `kOmegaSST`**, with its known limit written into the case
as CASE_PROTOCOL §1 requires: *k-ω SST under-predicts separated-flow heat
transfer and is not expected to resolve the strut-wake impingement on the hub
tail to better than order 20 %; this rung does not gate that quantity.*

**GEO-8 satisfied:** smallest named feature = strut thickness 4.000 mm ⟹
surface cell ≤ 1.333 mm. **Struts are refined to 1.000 mm at L1** (surface level
3), so the threshold holds at the COARSEST level and a fortiori at L2 and L3.
`resolveFeatureAngle 30`, `nCellsBetweenLevels 3`, feature edges from
`surfaceFeatureExtract` at 30° included angle.

### 3.4 THE THREE LEVELS

| | L1 | L2 | L3 |
|---|---:|---:|---:|
| base cell Δ₀ | **8.000 mm** | **5.333 mm** | **3.556 mm** |
| duct-bore surface level | 1 (4.000 mm) | 1 (2.667 mm) | 1 (1.778 mm) |
| hub surface level | 2 (2.000 mm) | 2 (1.333 mm) | 2 (0.889 mm) |
| strut surface level | 3 (1.000 mm) | 3 (0.667 mm) | 3 (0.444 mm) |
| layers (hub / strut / duct) | 18 / 12 / 5 | 18 / 12 / 5 | 18 / 12 / 5 |
| Δ₁ on hub and struts | 35.89 µm | 35.89 µm | 35.89 µm |
| **projected cells** | **885,508** | **2,988,590** | **10,086,491** |
| **N ratio** | — | **3.375** | **3.375** |
| **h ratio = N^(1/3)** | — | **1.500** | **1.500** |

**Refinement ratio 1.500 at both steps — inside the CASE_PROTOCOL §1 band of
1.5 to 2.**

**Δ₁ is held FIXED across the three levels, deliberately.** Refining Δ₁ with the
base cell would change the wall treatment's y⁺ regime between levels and the
triple would then measure two things at once. The levels refine the OUTER
discretisation; the near-wall layer is a registered constant.

### 3.5 THE L1 CELL-COUNT ARITHMETIC, OPEN

Bore cross-section A_b = 0.0490523 m²; base face 6.4e-5 m² ⟹ **766 cells/plane**.
Axial: body zone x ∈ [−0.05, 0.30] at 8 mm ⟹ 44 planes; upstream 0.125 m graded
(mean 16 mm) ⟹ 8; downstream 0.60 m graded (mean 24 mm) ⟹ 25. **77 planes.**

| term | arithmetic | cells |
|---|---|---:|
| background in bore | 766 × 77 | 58,982 |
| less hub occupancy | 69/plane × 16 planes | −1,104 |
| hub surface refinement L2 | (0.030676 × 0.006)/8e-9 = 23,007, ×2.2 octree buffer, −360 replaced | +50,255 |
| strut surface refinement L3 | (0.019347 × 0.003)/1e-9 = 58,041, ×2.5 (two transition bands), −113 | +144,990 |
| duct-bore refinement L1, body zone | area 0.785258 × 0.35 = 0.274840 m²; (0.274840 × 0.016)/6.4e-8 = 68,710, −8,589 replaced | +60,121 |
| hub layers | 0.030676/4e-6 = 7,669 faces × 18 | +138,042 |
| strut layers | 0.019347/1e-6 = 19,347 faces × 12 | +232,164 |
| duct-bore layers, body zone | 0.274840/1.6e-5 = 17,178 faces × 5 | +85,890 |
| **`fluid` subtotal** | | **769,340** |
| `core` | 3.400e-4 m³ / 2.7e-8 (3 mm) | 12,593 |
| `housing` shell | 1.2270e-4 m³ / 4e-9 (2×2×1 mm) | 30,675 |
| `housing` struts | 3.2873e-5 m³ / 1e-9 (1 mm) | 32,873 |
| `duct` shell | 8.005344e-4 m³ / 2e-8 (4×4×1.25 mm) | 40,027 |
| **solid subtotal** | | **116,168** |
| **L1 TOTAL** | | **885,508** |

**These are PROJECTIONS and are labelled as such.** CASE_PROTOCOL §2 requires
`checkMesh` on every level at stage 2; **the measured counts replace these, and
the difference is reported, never absorbed.**

**Scale against the wedge, for the record:** T23/T24 ran **8,640 / 34,560 /
138,240** cells. T26's L1 alone is **102.5 ×** the wedge's L1 and **6.4 ×** its
finest level; T26's L3 is **73.0 ×** the wedge's finest level.

### 3.6 Birth certificates

One per level, written by `build_t26.py`, carrying: the STL sha256, the
`snappyHexMeshDict`/`blockMeshDict` sha256, every registered level parameter of
§3.4, the `checkMesh` summary, the measured cell count, the achieved layer
coverage per patch, and the **sha256 of the certificate's own inputs**. Filed at
`verification/runs/T-family/T26_runs/<level>/MESH_BIRTH_CERTIFICATE.json`.
**A level with no certificate is not a level and cannot be graded.**

---

## 4. NUMERICS — AND THE T23G2Rn2 RULE, WITH EVERY MARGIN AS A NUMBER

**Solver: `chtMultiRegionSimpleFoam`** (steady, four regions). `deltaT 1`.
Schemes: `div(phi,U) bounded Gauss linearUpwind grad(U)`;
`div(phi,K)/div(phi,h) bounded Gauss upwind`; `div(phi,k)/div(phi,omega)
bounded Gauss upwind`; `laplacian Gauss linear corrected`; `grad cellLimited
Gauss linear 1`. Relaxation: `p_rgh 0.3`, `U 0.7`, `h 0.3`, `k/omega 0.7`,
solid `h 1.0`.

### 4.1 THE REGISTERED LINEAR SOLVERS

| region | field | solver | **tolerance** | **relTol** | maxIter |
|---|---|---|---:|---:|---:|
| `fluid` | `p_rgh` | GAMG / GaussSeidel | **1e-09** | **1e-03** | 100 |
| `fluid` | `(U\|h\|k\|omega)` | PBiCGStab / DILU | **1e-12** | **1e-03** | — |
| `core`, `housing`, `duct` | `h` | PCG / DIC | **1e-12** | **1e-03** | — |

### 4.2 THE T23G2Rn2 RULE — *solver tolerance strictly tighter than any gate that reads its output*

**The precedent, stated first.** T23G2R was voided because the p_rgh linear
solver's own `tolerance` (1e-8) **EQUALLED** the `G-CONV` gate (1e-8) —
`T23G2Rn2_PREREGISTRATION.md:71–74`. Its successor T23G2Rn2 repaired p_rgh to
one decade below the gate but left `"(U|h|k|omega)"` at **tolerance 1e-9**
(`:198`) against a `G-CONV` criterion of **h ≤ 1e-9** (`:216`).
**MARGIN 1.0 ×. That collision is what voided the rung.**

**Two margins are registered for every gate, because the collision that voided
T23G2Rn2 is visible only in the second one.** A Krylov/GAMG solve stops at
`max(tolerance, relTol × r₀)`, so near convergence the RELATIVE tolerance can
bind far above the absolute one:

- **NOMINAL margin** = gate ÷ absolute `tolerance`.
- **EFFECTIVE margin** = gate ÷ max(`tolerance`, `relTol` × r₀ at the gate).

| gate | criterion | field read | absolute tol | **NOMINAL margin** | effective floor at the gate | **EFFECTIVE margin** |
|---|---|---|---:|---:|---:|---:|
| **G-CONV-h** | outer initial residual `h` ≤ **1e-06**, every region, at `endTime` | `log.solve` | 1e-12 | **1.0e+06** | max(1e-12, 1e-3×1e-6) = 1e-09 | **1.0e+03** |
| **G-CONV-p** | outer initial residual `p_rgh` ≤ **1e-05** | `log.solve` | 1e-09 | **1.0e+04** | max(1e-9, 1e-3×1e-5) = 1e-08 | **1.0e+03** |
| **G-CONV-U** | `Ux`, `Uy`, `Uz` ≤ **1e-05** | `log.solve` | 1e-12 | **1.0e+07** | 1e-08 | **1.0e+03** |
| **G-CONV-t** | `k`, `omega` ≤ **1e-05** | `log.solve` | 1e-12 | **1.0e+07** | 1e-08 | **1.0e+03** |
| **G-CONT** | \|Σφ\|/\|φ_in\| ≤ **1e-05** | `<endTime>/fluid/phi` | 1e-09 (p_rgh) | **1.0e+04** | 1e-08 | **1.0e+03** |
| **G-BAL** | \|ΣQ_wall − P_loss\|/P_loss ≤ **1e-03** | `wallHeatFlux` function object | 1e-12 (h) | **1.0e+09** | 1e-09 | **1.0e+06** |
| **G-ITER** | \|ΔT_max over last 1 000 iters\| ≤ 0.1 × \|T_max(L_k) − T_max(L_{k−1})\| | `T` fields | 1e-12 (h) | ≫1e+03 | 1e-09 K-scale | ≫1e+03 |
| *T23G2Rn2 — the VOIDED row, for contrast* | `h` ≤ 1e-09 | | 1e-09 | **1.0 ×** | 1e-09 | **1.0 ×** |
| *T4e — the posture aimed at* | C6.3 ≤ 2e-04 | | 1e-10 | **2.0e+06** | — (see below) | — |

> **REGISTERED HARD RULE FOR THIS RUNG: no gate may have an EFFECTIVE margin
> below 1.0e+03.** Every gate above clears it; **the minimum on the rung is
> 1.0e+03, three decades.**

**Was T4e's posture reached? Answered honestly rather than claimed.**
T4e's nominal margin is **2.0e+06** (six decades) and this rung's nominal
margins span **1.0e+04 to 1.0e+09** — the same band, and above T4e's on four of
the seven gates. **On the EFFECTIVE basis the two are not comparable**, and this
document will not manufacture a comparison: T4e's 2e-4 is a **field-window
convergence metric**, not a linear residual, so `relTol × r₀` does not map onto
it. **The effective column is reported for T26's own gates because that is the
basis T23G2Rn2 was actually voided on, and it is the column a reader must check
before believing a nominal margin.**

**The price of `relTol 1e-03` is named, not hidden.** T5b — the cost anchor of
§7 — did not run at this relTol, so the registered per-cell rate does **not**
include the extra V-cycles this buys. It is carried as named misprediction risk
in §7.4, not absorbed into the estimate.

### 4.3 endTime, per level

`endTime` **8 000 / 12 000 / 16 000** SIMPLE iterations at L1/L2/L3.
Registered rising with refinement because the outer loop's convergence rate
degrades with cell count. **A level that reaches `endTime` without clearing
`G-CONV` is NOT converged and the triple that contains it is `NOT A RESULT`
(§5.2 ordering) — reaching `endTime` is not convergence.** This is T4e's
measured finding (`T4e_PREREGISTRATION.md:24–25`: the fine level reached
`endTime` 64 000 CLEAN yet at **76 ×** its tolerance) and it is registered here
before the fact so it cannot be argued after.

---

## 5. GATES, GRADING AND THE ROACHE TRIPLE

### 5.1 The graded quantities

| id | quantity | source file |
|---|---|---|
| **Q1** | `T_max` = max(T) over `housing` ∪ `core`, °C | `<endTime>/housing/T`, `<endTime>/core/T` (`internalField`) |
| **Q2** | `T_iface` = area-average of T on the `housing` side of the fluid/housing interface, °C | `<endTime>/housing/T` (`boundaryField`) |
| **Q3** | `Q_strut` = total heat rate leaving `housing` through the three strut→`duct` interfaces, W | `wallHeatFlux` function object |

**Q3 is the 3D quantity and is the reason this rung exists: on the wedge it is
identically zero, because the wedge has no struts.**

### 5.2 ROACHE TRIPLE GATING — `CLAUDE.md` rule 5, ordering registered verbatim

Applied per quantity over (L1, L2, L3) at h-ratio **1.500**, **Fs = 1.25**:

1. **Any level not iteratively converged (G-CONV fails) or not plateaued
   (G-ITER fails) ⟹ `NOT A RESULT`.**
2. **Triple `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` ⟹ `NOT A
   RESULT`**, with the value, both triples and both orders printed beside it.
3. **`CONVERGING` ⟹ `PASS` inside the pre-registered band, else `GATE FAIL`**,
   with the GCI printed.

**The gate can only turn a PASS or GATE FAIL INTO `NOT A RESULT`, never the
reverse. A GCI is never quoted when the three values are not monotone.**

Registered band (CASE_PROTOCOL §5): **observed order p ∈ [0.5, 2.5]**; a p
outside that range **adds a level automatically** rather than being clamped.
**Iterative error must be at least 10 × smaller than the level-to-level
difference** — that is G-ITER, and it is a gate, not a remark.

### 5.3 The rule-4 completion gate — ALL-OR-NOTHING, with the age guard

A level is complete only if **every** clause holds:

| # | clause | this rung |
|---|---|---|
| 1 | `rc = 0` | read from the process, never inferred from a marker |
| 2 | an `End` line | exactly one in `log.solve` |
| 3 | last time == `endTime` | greatest numeric time dir == 8000 / 12000 / 16000 |
| 4 | fields present | `T U p p_rgh alphat nut k omega phi` in `<endTime>/fluid/`; `T p` in `<endTime>/{core,housing,duct}/` |
| 5 | `ExecutionTime` count == round(endTime/deltaT) | == `endTime` at `deltaT 1` |
| 6 | **age guard** | **every field at `endTime` NEWER than that case's own `0/fluid/T`, by `st_mtime`** — the launcher touches it LAST |
| 7 | **launch guard** | the launcher **REFUSES** a case in which `0/` or any numeric time directory already exists (§6) |

**A run failing any clause is not done, and the comparator REFUSES (exit 2)
rather than degrading.** Instrument: `mark_done_t26.py`.

### 5.4 Reference tier — named, and it is the uncomfortable answer

CASE_PROTOCOL §1: *"reference tier named (exact, correlation, measured)."*

| quantity | tier | consequence |
|---|---|---|
| Q1 `T_max` | **NONE** | no exact solution, no correlation, no measured data for this configuration. **Graded on the Roache triple and G-BAL only.** No absolute-accuracy claim is available and none is registered. |
| Q2 `T_iface` | **NONE** | same |
| Q3 `Q_strut` | **NONE** | same |
| annulus `Nu` | **FORMULA, bracket** | Dittus-Boelter on D_h (pessimistic) and flat-plate on L_hub (optimistic), `T23_PREREGISTRATION.md:254–255`. **REPORTED, NOT GATED** — this lab holds no title-page-verified reference (rule 15) establishing either correlation's validity for a strutted annulus. |
| `y+` | — | **REPORTED, NOT GATED**, and this is a lesson applied: **`C-209` records that T5b gated y⁺ at 2.00, measured 2.3100 on the fine level, and every one of its six graded rows became `NOT A RESULT`.** y⁺ is a SOLVED quantity; gating it converts a converged ladder into a non-result on a statistic. Registered as reported. |

> **REGISTERED CONSEQUENCE, before compute: the best verdict available to this
> rung is a Roache-graded, conservation-checked, grid-converged 3D result with
> NO external reference. That is verification. It is not validation, and the
> results record must say so in its first paragraph.**

---

## 6. CLAUSE 7 — THE LAUNCH GUARD, AND ITS CALL SITE

**The finding this section answers**, landed by the heat-transfer supervisor
2026-09-10: **clause 7 is defined in seven K0-family instruments and called by
ZERO launchers**, because every builder created `0/` itself, so the guard's
"refuse if `0/` exists" could never fire on a legitimate launch.

**The registered repair, and it is a design, not a hope:**

1. **`build_t26.py` stages into `0.orig/` and NEVER creates `0/`.** It
   **refuses** (exit 2) if `0/` exists at build time, and refuses if
   `0.orig/fluid/T` was not written — pattern already proved in
   `scripts/build_k0h.py:1100–1147`.
2. **`launch_t26.sh` creates `0` from `0.orig`** (`cp -r 0.orig 0`), writes
   every other field, and **touches `0/fluid/T` LAST** — so the age-guard
   referent dates the run that is allowed to produce the answer.
3. **The guard is `mark_done_t26.py --launch-guard <case>`** and it is the ONLY
   place the rule is written down. It is **called, never reimplemented.**

**CALL SITES — both, because rule 14 says a lesson is not applied until EVERY
call site asserts it:**

| # | call site | why this site specifically |
|---|---|---|
| **CS-1** | inside `launch_t26.sh`, **before** `cp -r 0.orig 0` | the direct path |
| **CS-2** | inside `orchestrate_t26.py`, **synchronously, on this side of the fork, before `Popen`** | the orchestrator sends the launcher's stdout to `DEVNULL` and never waits, so a refusal printed inside the launcher would go to a discarded pipe and the level would be recorded as launched. Pattern from `scripts/orchestrate_k0h.py:310–340`. |

**A refusal STOPS THE LEVEL SET, it does not skip a level** — a level set is
costed as a whole.

**THE SELFTEST, and it drives the LAUNCHER, not the function:**

| arm | what it does | required outcome |
|---|---|---|
| **A** | a clean case (only `0.orig/`), driven **through `launch_t26.sh` as a subprocess** | the guard passes and the launcher proceeds |
| **B** | the same case with a `0/` pre-created, **through the launcher** | launcher **REFUSES**, exit 2, the string `CLAUSE 7` in its output, and **nothing is `Popen`'d** |
| **C** | **NEGATIVE CONTROL** — the guard's verdict forced clear, same dirty case, same launcher | the dirty case **LAUNCHES** |

**Arm C is what makes arm B evidence.** Without it, arm B's refusal could be
caused by anything in the launcher; with it, the refusal is attributable to the
guard and to nothing else. Only the solver `Popen` is intercepted — **the guard
really executes** in all three arms.

---

## 7. COST — CORE-MINUTES, ARITHMETIC OPEN, AND SANAA'S EXEMPTION STATED PRECISELY

### 7.1 The rate basis — MEASURED, and it is the strongest this territory has

`docs/COST_CALIBRATION.md` row **`C-209`**: T5b, `chtMultiRegionSimpleFoam`, 3D
CHT, 5 000 iterations, **1 rank**, three levels, all rule-4 complete:

| level | cells | wall s | **core-s / cell-iteration** |
|---|---:|---:|---:|
| `T5_CUBE_c` | 52,684 | 1,007 | 3.8228e-06 |
| `T5_CUBE_m` | 212,942 | 5,252 | **4.9328e-06** |
| `T5_CUBE_f` | 882,024 | 20,851 | 4.7280e-06 |

**REGISTERED POINT RATE = 4.9328e-06 core-s/cell-iteration** — the **worst** of
the three, so the estimate errs in the conservative direction. The spread
3.82–4.93e-06 is stated so the choice is visible.
*(A second, independent anchor agrees: `T23_PREREGISTRATION.md:606` registers
4.6476e-06 for the three-region wedge. It is quoted for corroboration only and
is NOT the basis.)*

**Parallel efficiency η = 0.75 — registered "class default, first use."** This
territory holds no measured anchor for `chtMultiRegionSimpleFoam` above 1 rank.
Per CASE_PROTOCOL §1 the class default is registered with its provenance marked
and the case proceeds; **it MUST be measured at stage 3 and reported in the
calibration row.**

**Meshing rate 6.0e-03 core-s/cell — registered "class default, first use."**
No measured `snappyHexMesh`-with-layers anchor exists in this territory.

### 7.2 THE COST TABLE

core-min = N_cells × N_iter × 4.9328e-06 ÷ 60 ÷ 0.75

| level | cells | iters | cell-iterations | solve core-min | mesh core-min | **level total** | ranks | **projected wall** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **L1** | 885,508 | 8,000 | 7.08406e+09 | **776.54** | 88.55 | **865.09** | 8 | 1.80 h |
| **L2** | 2,988,590 | 12,000 | 3.58631e+10 | **3,931.23** | 298.86 | **4,230.09** | 16 | 4.41 h |
| **L3** | 10,086,491 | 16,000 | 1.61384e+11 | **17,690.54** | 1,008.65 | **18,699.19** | 16 | 19.48 h |
| geometry gate | — | — | — | — | — | **0.05 (MEASURED)** | 1 | 3 s |
| **RUNG POINT** | | | | **22,398.31** | **1,396.06** | **23,794.42** | | **≈ 25.69 h** |

**RUNG POINT = 23,794.42 core-min = 396.57 core-h.**
**USD = 396.57 × $0.0513/core-h = $20.344 — DERIVED, NOT MEASURED.** The rate is
owner-stated (2026-08-21/22); **the box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5), so `cost_basis` = **reported-by-owner**.

### 7.3 THE CAP, AND SANAA'S EXEMPTION — STATED PRECISELY

CASE_PROTOCOL v1.0 closing clause, Sanaa's own words: *"for all these 3D cases
that still need to run, i dont want to see any budget gates ( time or money).
Bc i want to shoot them so we at least have hard 3D demos to show and then we
can go back to having some restraint."*

> **REGISTERED, exactly and no wider:**
> 1. **NO BUDGET CAP STOPS THIS RUN.** CASE_PROTOCOL §4's *"cap reached: stop,
>    NOT A RESULT"* and `CLAUDE.md` rule 12's *"an overrun stops the run"* are
>    **suspended for this rung** under that clause. A level that exceeds the
>    figures in §7.2 **continues**.
> 2. **THE RUN IS STILL COSTED, AND STILL CALIBRATED.** §7.2 is a full
>    pre-registered cost; §7.4 is the estimate-versus-actual obligation. The
>    exemption removes the STOP, not the ARITHMETIC. **The exemption is not
>    licence to skip the costing and is not used as one here.**
> 3. **A HANG GUARD IS STILL ENACTED, and it is NOT a budget gate.** `timeout_s
>    = 3.0 × POINT × 60 ÷ ranks` per level — **L1 2,595 / L2 12,690 / L3 56,098
>    core-min** — against a wedged or spinning process, not against spend. It is
>    named a hang guard everywhere it appears so no later reader mistakes it for
>    the cap Sanaa suspended. **Whether even this is admitted is the
>    supervisor's call at the freeze; this lane registers it and does not
>    decide it.**
> 4. **The exemption is scoped and ends when she says restraint returns.** This
>    rung is recorded as having run under it.
> 5. **$20.344 is under the $25 pre-authorisation — and a blanket authorisation
>    is not a per-item reading** (`CLAUDE.md` rule 9). The figure is placed here
>    for the supervisor to read as an item, not waved through as covered.

### 7.4 The calibration owed at completion

`CLAUDE.md` rule 12's estimate-versus-actual clause binds this rung. At
completion the results record must carry: **actual core-minutes** read by
`scripts/cost_channel.py` (§8.1), the **ratio actual/predicted**, the
attribution split between **contention, waste and misprediction with waste named
separately and never folded into the ratio**, the **measured** η at 8 and 16
ranks, the **measured** snappy rate, and a row appended to
`docs/COST_CALIBRATION.md`.

**REGISTERED EXPECTED RATIO BAND: 1.00 – 1.60**, with its two causes named
before the fact:
1. **+7.8 %** — `C-209` records T5b overrunning by **1.0781 ×** on *"the
   strongest basis any estimate in this ledger has ever had"*, whose own
   registration declared an expected ratio of 1.00.
2. **the `relTol 1e-03` tightening of §4.2**, which is not in the rate anchor.

**REGISTERED, one-way and before the fact:** a level whose recorded load average
at launch shows a saturated box produces a **COST but NOT a calibration row**.
Each launcher writes `START.<level>` before the solver starts, carrying
`start_utc`, all three `/proc/loadavg` windows and `nproc`.

---

## 8. INSTRUMENTS, PLANTED-ZERO CONTROLS AND THE COMPARATOR PIN

### 8.1 Every reader that can return a zero gets a live planted control (rule 3)

| reader | plants | both-direction selftest |
|---|---|---|
| `T` reader (Q1, Q2) | `PLANT_T = 1.234e-03` K, located **STRUCTURALLY by line index**, never by value | reads it back from disk; **REFUSES (exit 3)** if unseen. Negative arm: plant removed ⟹ the check must fire. |
| `wallHeatFlux` reader (Q3, G-BAL) | a known non-zero flux row | same, both arms |
| `phi` reader (G-CONT) | a known non-zero flux | same, both arms |
| residual reader (G-CONV) | a synthetic residual line at a known value | same, both arms |
| `y+` reader | a known non-zero y⁺ | same, both arms |
| **cost reader** | **`scripts/cost_channel.py`** — `cost_plant_control()` and `assert_cost_channel_armed()`, including its `blind_production_reader=True` negative arm | **MANDATORY.** The heat-transfer supervisor ruled 2026-09-10 that every future heat-transfer rung must use it and that **this is a freeze precondition.** Its docstring records the failure it exists for: a ledger row that recorded **0.00 core-min for a run that cost 34.23**, because `.get(key,"0")` cannot tell an absent key from a measured zero. |
| geometry gate | 13 arms, **already run, PASS** | §2.2 |

**Every one of these refuses rather than degrading.** A comparator that cannot
see its own plant grades nothing.

### 8.2 Stage-2 bug check (CASE_PROTOCOL §2) — registered now, run later

`checkMesh` on every level against the registered quality gates; dictionary and
schema validation; boundary-condition closure on every patch of every field with
**no silent default**; dead-lever audit (every setting this document claims is
present in the files the solver reads); instrument check (every reader sees its
plant through the real path); dry run of one iteration with **rc read from the
process, never inferred from a marker**.

### 8.3 THE COMPARATOR PIN — AND WHY THIS DOCUMENT IS NOT YET FREEZE-READY

CASE_PROTOCOL §1: *"comparator pinned by hash. Nothing below is run until the
freeze check passes."*

| instrument | path | state |
|---|---|---|
| `geometry_gate_t26.py` | `docs/campaigns/T-family/geometry_gate_t26.py` | **WRITTEN, SELFTESTED, RUN** — sha256 to be pinned in the freeze commit |
| `build_t26.py` | `docs/campaigns/T-family/build_t26.py` | **NOT WRITTEN** |
| `launch_t26.sh` | `docs/campaigns/T-family/launch_t26.sh` | **NOT WRITTEN** |
| `mark_done_t26.py` | `docs/campaigns/T-family/mark_done_t26.py` | **NOT WRITTEN** |
| `orchestrate_t26.py` | `docs/campaigns/T-family/orchestrate_t26.py` | **NOT WRITTEN** |
| `analyse_t26.py` (**the comparator**) | `docs/campaigns/T-family/analyse_t26.py` | **NOT WRITTEN** |

> **THIS DOCUMENT CANNOT BE FROZEN UNTIL `analyse_t26.py` EXISTS AND ITS SHA256
> IS PINNED HERE.** Freezing a registration whose comparator does not exist
> would freeze a promise, not a grading path. Stated plainly rather than papered
> over: **§8.3 is the gap.**

---

## 9. THE REGISTERED RUN SET

### 9.1 What runs

Three levels — **L1, L2, L3** — at the single operating point `U_inf = 20.000
m/s`, `P_loss = 305.0 W`, forming ONE Roache triple per graded quantity.

### 9.2 Detached, monitored, survivable (CASE_PROTOCOL §4)

Launched detached; the runner daemon owns it; the process, the autograder and
the monitor are all parented to init. **The fleet dying does not touch the
solver.** Checkpoints at `writeInterval 1000`, so a kill resumes from committed
state.

### 9.3 Monitor actions, fixed and pre-registered

| condition | action |
|---|---|
| residual growth past bound, or a field outside its bounds | **stop** |
| plateau above target with a stalled linear solver | **stop** |
| coherent oscillation with a fixed period in Q1 | **stop**, mark *"physics voting unsteady"* |
| cost per iteration beyond 2 × estimate | **stop**, mark machine or case cause from per-iteration timing and residual decay |
| hang guard reached (§7.3.3) | **stop** — a hang, **not** a budget cap |

One change per stop, from the escalation ladder, never the same action twice on
the same state; two stops on one cause ⟹ climb the ladder; ladder exhausted ⟹
park as `NOT A RESULT` with the full action history and the lesson.

### 9.4 Registered but DEFERRED, with reasons — not silently dropped

| id | what | why deferred | cost if taken |
|---|---|---|---:|
| **S1** | inlet-length sensitivity: one extra L1 with L_up = 3 D_h | bounds §3.2's developing-inlet assumption; not needed to grade the triple | ≈ 950 core-min |
| **S2** | the remaining 15 points of the P_loss × U_inf map in 3D | this rung establishes the ladder first; a 16-point 3D map is a separate registration | ≈ 13 000 core-min at L1 |
| **S3** | `Nu` correlation-tier gate | needs a title-page-verified reference for strutted annular flow (rule 15) that this lab does not hold | acquisition, not compute |
| **S4** | transient/URANS successor if the monitor votes unsteady | a steady solver cannot grade an unsteady state (T4e's D1) | separate registration |

---

## 10. REPORTING (CASE_PROTOCOL §6)

Every stage writes **one status line** to the case record: stage, verdict, one
number, one cause if not green. The supervisor relays those lines and does not
narrate. Anything relayed that was not read from a file carries **VERIFY**.

---

## 11. WHAT THE GEOMETRY CANNOT SUPPORT — stated before the spend

1. **No inlet development length.** §3.2. Bounded by S1, not assumed away.
2. **No reference of any tier for Q1/Q2/Q3.** §5.4. This is verification only.
3. **The hub is a display spindle, not a motor.** Its shape came from a display
   surface (the STL header says so: *"display surface"*). It is geometrically
   valid — the gate proves that — but **nothing establishes it as any real
   motor's outline**, and no claim that it is may be made from this rung.
4. **The struts have no fillets.** They meet the hub and the duct at sharp
   corners, which is a stress and a heat-flux singularity in the solid. `Q_strut`
   is therefore mesh-sensitive at the corner, which is exactly why it is put
   through the Roache triple rather than quoted from one level.
5. **96 facets is 3.75° of azimuthal discretisation on a fixed surface.** It
   cannot be refined by refining the mesh; at L3 the surface cell (0.889 mm on
   the hub) is finer than the facet arc (2.45 mm at the hub radius), so **the
   finest level resolves the faceting itself**. Registered as a known
   discretisation floor, reported with the triple.
6. **The duct outer boundary condition is an assumption.** External convection
   to ambient with a registered h_ext; no measurement supports the value.

---

## 12. WHAT MUST HAPPEN BEFORE THIS CAN BE FROZEN

1. `analyse_t26.py` written, selftested in both directions on all six readers,
   `cost_channel.py` armed, and **its sha256 pinned into §8.3**.
2. `build_t26.py`, `launch_t26.sh`, `mark_done_t26.py`, `orchestrate_t26.py`
   written, with the §6 clause-7 selftest passing all three arms **including
   the negative control**.
3. The §0.3 id derivation and the §0.4 absence condition **re-taken in the
   committing invocation**.
4. The supervisor's **personal** reading of the comparator **as a diff**
   (`SUPERVISION_CHARTER.md` §3.1) — a selftest written by the instrument's
   author is evidence, not the supervisor's read.
5. The supervisor's ruling on **§0.5** (a second front item) and on
   **§7.3.3** (whether a hang guard is admitted under Sanaa's exemption).

---

*Drafted by a heat-transfer lane, 2026-09-10. Zero solver compute. The only
compute spent is the geometry gate's 0.05 core-min, measured. Nothing here has
been sent, filed, uploaded or registered anywhere outside this box
(`CLAUDE.md` rule 7).*

---

## 13. AMENDMENT 1 — 2026-09-10, PRE-FIRST-COMPUTE: THE GRID TRIPLE IS RE-REGISTERED DOWNWARD

**STATUS: this document is STILL NOT FROZEN.** This amendment is taken under
`CLAUDE.md` rule 2's pre-first-compute clause — *"Before first compute,
amendments are legal and must state the condition and how it was checked (name
the run directory that does not exist)"* — and it is legal NOW precisely
because it is legal only now.

### 13.1 THE CONDITION, AND HOW IT WAS CHECKED — under a LIVE PLANTED CONTROL

**THE CONDITION:** *no compute has run under any T26 registration.*

| directory | required | MEASURED 2026-09-10, this invocation |
|---|---|---|
| `verification/runs/T-family/T26_runs/` | ABSENT | **ABSENT** |
| `verification/runs/T-family/T26_MESH_runs/` | ABSENT | **ABSENT** |
| `verification/runs/F14-cooling-ladder/T26*` | ABSENT | **ABSENT** |

**THE PLANTED CONTROL (rule 3), because three absences from a reader never
shown able to see a presence are not evidence:** the IDENTICAL predicate was
run against `verification/runs/T-family/T23_runs/`, which **DOES** exist, and
returned **PRESENT**; and against `verification/runs/T-family/T99_nonexistent`,
which does not, returning **ABSENT**. Both arms fired correctly, so the three
absences above are statements about the disk.

**TO BE RE-TAKEN IN THE COMMITTING INVOCATION** (§12 item 3), in the same shell
invocation as the freeze write. Zero solver compute has been spent on T26; the
only compute on this rung remains the geometry gate's 0.05 core-min.

### 13.2 WHY — A MEASUREMENT, NOT A PREFERENCE

**THE REGISTERED L3 OF §3.4 CANNOT RUN ON THIS BOX.** Measured 2026-09-10 from
`/proc/<pid>/status` `VmHWM` (peak RSS, not current RSS) on two live solvers on
this machine, with cell counts read from each case's own `log.checkMesh`:

| anchor | cells | VmHWM | B/cell incl. fixed |
|---|---:|---:|---:|
| `T4e_IJ_m`, `buoyantBoussinesqSimpleFoam`, 1 rank | 34,560 | 161.8 MiB | 4,910 |
| `T4e_IJ_f`, `buoyantBoussinesqSimpleFoam`, 1 rank | 138,240 | 446.3 MiB | 3,385 |

Two-point fit, same solver, same box, same build, same day:
**marginal 2,877 B/cell; per-rank fixed 67.04 MiB.**

**THE FIT IS OPTIMISTIC AND THE MARGIN IS DISCLOSED, NOT ABSORBED.** Checked
against a third, independent case — `VMFL017-R3/L3`, `rhoCentralFoam`, 368,640
cells, VmHWM 1,184.3 MiB — the fit predicts 1,078.3 MiB and so
**UNDER-PREDICTS BY 9 %.** Every figure below is therefore a **FLOOR**.

**A SECOND, UNQUANTIFIED MULTIPLIER IS NAMED RATHER THAN GUESSED.** The anchors
are SINGLE-REGION incompressible solvers. T26 runs `chtMultiRegionSimpleFoam`
over **four** regions, each carrying its own mesh, fields and interface maps.
That multiplier **μ > 1 is UNMEASURED in this territory** — no
`chtMultiRegionSimpleFoam` peak-RSS anchor exists on this box — and this
amendment does not invent one. **μ MUST be measured at the smoke and reported
in the calibration row** (§7.4), alongside η and the snappy rate.

| level | cells | ranks | FLOOR | μ that exhausts 22 GiB |
|---|---:|---:|---:|---:|
| §3.4 L3 | 10,086,491 | 16 | **28.07 GiB** | **0.78 — it does not fit even at μ = 1** |
| §3.4 L2 | 2,988,590 | 16 | 9.06 GiB | 2.43 |
| §3.4 L1 | 885,508 | 8 | 2.90 GiB | 7.6 |

`MemAvailable` measured **27.21 GiB at 19:12Z** and **22 GiB at 19:42Z** on a
box of 30.64 GiB total. **It moves**, so a ladder sized to the instantaneous
figure is not a ladder; the amended top level is chosen to tolerate μ ≥ 2.4.

> **A triple whose top level cannot run is not a triple.** Sanaa, 2026-09-10
> ~19:45Z: *"we want to have all these complicated cases run and complete, and
> wit their mes convergence ASAAAP."* Mesh convergence means a three-level
> CONVERGING Roache triple with a GCI. §3.4's ladder cannot deliver one on this
> hardware, and no amount of waiting changes that.

### 13.3 THE AMENDMENT — §3.4's CELL COUNTS ARE STRUCK AND REPLACED

**STRUCK** (recorded verbatim so the original stands and the strike is visible;
`CLAUDE.md` rule 2: *"Originals are struck, never rewritten"*):

> ~~L1 **885,508** — L2 **2,988,590** — L3 **10,086,491**~~
> ~~endTime **8,000 / 12,000 / 16,000**; ranks 8 / 16 / 16~~

**REGISTERED IN THEIR PLACE:**

| | L1 | L2 | L3 |
|---|---:|---:|---:|
| **cells** | **262,373** | **885,508** | **2,988,590** |
| **N ratio** | — | **3.375** | **3.375** |
| **h ratio = N^(1/3)** | — | **1.500** | **1.500** |
| **endTime** | **4,000** | **8,000** | **12,000** |
| **ranks** | **4** | **8** | **16** |
| memory FLOOR | 0.96 GiB | 2.90 GiB | **9.06 GiB** |

**THE LADDER IS SHIFTED DOWN EXACTLY ONE RUNG. NOTHING ELSE CHANGES.**
`r = 1.500` at both steps, `N = 3.375 = 1.5³`, so the 3D refinement signature
of §13.5 is preserved exactly. **Two of the three counts — 885,508 and
2,988,590 — are the §3.4 counts unchanged**, already derived by the open
arithmetic of §3.5 and already gate-checked, so this amendment introduces
exactly ONE new count.

**262,373 is DERIVED, not chosen:** 885,508 / 3.375 = 262,372.7 → **262,373**.

**endTime is attached to CELL COUNT, not to ladder position** — so the
registered relationship is PRESERVED rather than re-registered. §4.3 registers
endTime *"rising with refinement because the outer loop's convergence rate
degrades with cell count"*, i.e. it is a function of cells. The registered
pairs 885,508→8,000 and 2,988,590→12,000 therefore travel with their cell
counts. The new bottom level extrapolates the registered +4,000-per-3.375×-step
pattern downward: **262,373 → 4,000.**

**NO GATE, THRESHOLD, BAND OR LABEL IS TOUCHED.** G-CONV-h/p/U/t, G-CONT,
G-BAL, G-ITER, the observed-order band [0.5, 2.5], Fs = 1.25, the verdict
vocabulary, the reference tier NONE of §5.4 and the Roache ordering of §5.2 all
stand exactly as registered. This amendment changes THREE CELL COUNTS, THREE
endTimes, THREE RANK COUNTS and the COST that follows arithmetically from them.

### 13.4 COST, RE-DERIVED — the formula of §7.2 unchanged

`core-min = N_cells × N_iter × 4.9328e-06 ÷ 60 ÷ 0.75`, mesh at
`6.0e-03 core-s/cell`. Both rates are the §7.1 registrations, untouched.

| level | cells | iters | solve core-min | mesh core-min | total | ranks | wall h |
|---|---:|---:|---:|---:|---:|---:|---:|
| L1 | 262,373 | 4,000 | 115.04 | 26.24 | **141.28** | 4 | 0.59 |
| L2 | 885,508 | 8,000 | 776.54 | 88.55 | **865.09** | 8 | 1.80 |
| L3 | 2,988,590 | 12,000 | 3,931.23 | 298.86 | **4,230.09** | 16 | 4.41 |
| geometry gate | — | — | — | — | 0.05 (MEASURED) | 1 | — |
| **RUNG POINT** | | | **4,822.81** | **413.65** | **5,236.51** | | **≈ 6.80 h** |

**RUNG POINT = 5,236.51 core-min = 87.28 core-h.**
**USD = 87.28 × $0.0513/core-h = $4.477 — DERIVED, NOT MEASURED**
(`cost_basis` = reported-by-owner; the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5).

~~**STRUCK: RUNG POINT 23,794.42 core-min = 396.57 core-h = $20.344 derived.**~~

**RATIO amended/registered = 0.2201, a 4.54× REDUCTION** — 18,557.91 core-min
and $15.867 derived not spent. The reduction is larger than cell count alone
would give because `endTime` travels down with the ladder.

**HANG GUARDS, re-derived at 3.0 × POINT** (§7.3.3) — and they are **hang
guards, NOT budget gates**. Sanaa's CASE_PROTOCOL closing clause suspends the
cap-STOP for 3D runs; these numbers exist to catch a wedged or spinning
process, not a spend. **The ambiguity found in T4e is deliberately not
repeated here:** T4e's fine leg carries `timeout 360060`, numerically exactly
**2.0000 ×** POINT, which is its registered CAP wearing a hang guard's name.
Every T26 timeout below is **3.0 ×** POINT and therefore cannot be mistaken for
the 2× cap of any other rung.

| level | POINT core-min | timeout s | = core-min | wall at ranks |
|---|---:|---:|---:|---:|
| L1 | 141.28 | **6,358** | 423.8 | 1.8 h at 4 |
| L2 | 865.09 | **19,465** | 2,595.3 | 5.4 h at 8 |
| L3 | 4,230.09 | **47,589** | 12,690.3 | 13.2 h at 16 |

### 13.5 WHAT WAS CONSIDERED AND REJECTED — the biggest top level that FITS

The instruction was *"the biggest top level that FITS, not the smallest that is
safe"*, so the alternatives were costed rather than waved off. At `r = 1.5` the
ladder is geometric, so admissible top levels are a continuum, not a menu:

| top level | mid | bottom | FLOOR | μ tolerated in 22 GiB | verdict |
|---:|---:|---:|---:|---:|---|
| 2,988,590 | 885,508 | 262,373 | 9.06 GiB | **2.43** | **REGISTERED** |
| 4,000,000 | 1,185,185 | 351,166 | 11.77 GiB | 1.87 | rejected |
| 5,000,000 | 1,481,481 | 438,957 | 14.44 GiB | 1.52 | rejected |
| 6,000,000 | 1,777,778 | 526,749 | 17.12 GiB | 1.28 | rejected |
| 10,086,491 | 2,988,590 | 885,508 | 28.07 GiB | 0.78 | **cannot run** |

**2,988,590 is registered over the larger tops for three stated reasons:**
1. **μ is UNMEASURED.** A top that tolerates only 1.28–1.87× is a bet on a
   number nobody has measured, on a solver with four regions. 2.43× is not.
2. **`MemAvailable` moved 27.21 → 22 GiB inside thirty minutes** while peer
   lanes launched. A ladder sized to the instantaneous figure is not a ladder.
3. **Every larger top requires all three counts to be re-derived** from
   scratch, discarding §3.5's open arithmetic and its gate check. The
   registered ladder reuses two counts already derived and already checked.

**IF μ MEASURES AT OR BELOW 1.5 AT THE SMOKE**, a 5,000,000-cell top becomes
defensible and is the natural successor registration. That is recorded as the
condition, before the fact, so it is a prediction and not a later rescue.

### 13.6 DIMENSIONALITY IS NOW GATED, NOT INFERRED

T4e and the whole T23G2 line (R, Rn, Rn2) were found on 2026-09-10 to be **2-D
axisymmetric wedges**, and the closure team offered three "genuinely 3D"
families that were all **one cell thick with `empty` spanwise patches**. T26's
3D status was, until this amendment, an inference from a GEOMETRY GATE — a
description of an intended shape.

**REGISTERED: gate D-3D.** A level is `NOT A RESULT` unless, on the **BUILT**
mesh: `checkMesh` reports **3** geometric (non-empty/wedge) directions, and
`constant/polyMesh/boundary` carries **zero** `empty` and **zero** `wedge`
patches. Both witnesses are recorded **verbatim, per level**, into
`gate_t26.json` by `analyse_t26.py`, so the 3D claim is carried by the graded
record and can never again be an inference. Dimensionality is **never**
certified from the geometry gate, `blockMeshDict` or `snappyHexMeshDict` —
those are the artifacts that misled closure, and the comparator strips comments
before matching so a commented-out line cannot be read as live.

**Necessary-but-not-sufficient corroboration, available before any mesh
exists:** the registered counts step by **3.375001** and **3.375000**, i.e.
**1.5³** — the 3D signature. A 2-D refinement at r = 1.5 gives **2.250**. This
holds for the amended ladder by construction.

### 13.7 `checkMesh` MUST RUN ITS FULL CHECK SET

**REGISTERED:** every `log.checkMesh` this rung grades from is produced by
`checkMesh -allRegions -allGeometry -allTopology`, and the exact command line
is recorded **into the log itself**. Bare `checkMesh` prints `Mesh OK.` on a
mesh that fails checks which only run under those flags — confirmed against
the binary's own help on this box: `-allGeometry` *"Include bounding box
checks"*, `-allTopology` *"Include extra topology checks"*. cfd spent three
M6CP1 smoke rungs on a mesh its stage-2 gate could never have refused.
`analyse_t26.py` **REFUSES** a log whose recorded command line lacks either
flag: the artifact must prove which instrument produced it.

**REGISTERED: gate G-MINCELL.** Minimum cell dimension, per level, must be
**≥ 0.10 × that level's smallest registered surface cell**. Justification: a
cell an order of magnitude below the intended surface resolution is a snap
artifact, not a resolved feature. The floor is registered as a FRACTION so it
scales with the level rather than being re-chosen per level. **A cusped
trailing edge passes both check sets and still destroyed the M6**, and T26's
three struts have sharp, unfilleted trailing edges (§11 item 4) — this is
exactly that geometry.

### 13.8 What this amendment does NOT do

It does not freeze this document; it does not alter any gate, threshold, band
or label; it does not authorise a launch; and it does not touch §§0–12, whose
line numbers are unchanged — **lines whose number changed above this section:
0** — because `analyse_t26.py`, `mark_done_t26.py`, `launch_t26.sh`,
`build_t26.py` and `orchestrate_t26.py` all cite this document BY LINE, and an
inline strike would have silently broken every one of those citations. That is
why the strikes above are recorded here rather than applied in place.

*Amendment drafted by a heat-transfer lane, 2026-09-10, on the supervisor's
ruling. Zero solver compute. Nothing sent, filed or uploaded (`CLAUDE.md` rule 7).*

---

## 14. AMENDMENT 2 — 2026-09-11, PRE-FIRST-COMPUTE: **THERE IS NO BUILT-MESH SIMILARITY GATE, AND THE `N` RATIO THIS DOCUMENT REGISTERS IS ONE THE BUILD CANNOT DELIVER — BECAUSE IT SHOULD NOT**

**STATUS: this document is STILL NOT FROZEN.** Taken under `CLAUDE.md` rule 2's
pre-first-compute clause. It ADDS a gate and CHANGES no threshold of any gate
that exists; the one registered number it contradicts is contradicted by a
measurement, and the remedy registered here moves the MESH, never the window.

### 14.1 THE CONDITION, AND HOW IT WAS CHECKED — under a LIVE PLANTED CONTROL

**THE CONDITION:** *no compute has run under any T26 registration.*

| directory | required | MEASURED 2026-09-11T16:47:16Z, this invocation |
|---|---|---|
| `verification/runs/T-family/T26_runs/` | ABSENT | **ABSENT** |
| `verification/runs/T-family/T26_MESH_runs/` | ABSENT | **ABSENT** |
| `verification/runs/F14-cooling-ladder/T26*` | ABSENT | **0 matches** |

**THE PLANTED CONTROL (rule 3):** the identical `test -d` predicate was run in
the same invocation against `verification/runs/T-family/T23_runs/` and returned
**PRESENT**, and against `verification/runs/T-family/T99_nonexistent` and
returned **ABSENT**. Both arms fired, so the absences above are statements about
the disk and not about a blind reader.

**Base amended:** commit `0effc11da4bfda432bab7dda0e2c87cc9ce50f50`, blob
`b822113aacf236979bef681e40c437734da4a9f2`. **Zero solver core-minutes have been
spent against this document.** The mesh-development family cited below is NOT a
T26 level, is not graded, and lives outside the repository at
`/home/ubuntu/certonomous-runs/T26_mesh_dev/`.

### 14.2 THE DEFECT — A GATE THAT IS ABSENT, AND A NUMBER THAT CANNOT BE MET

This rung's gate set is `GEO-1…8`, `D-3D`, `G-MINCELL`, `G-CONV-*`, `G-CONT`,
`G-BAL`, `G-ITER`. **None of them reads the BUILT cell count.** §3.4 and §13.3
register `N` ratio **3.375** and `h` ratio `N^(1/3)` = **1.500** at both steps,
and §3.5 labels the counts PROJECTIONS — but **nothing on the grading path ever
compares the projection with what `snappyHexMesh` actually produced.** K2d died
for want of exactly this check and K2f carries `G-MESHSIM` because of it.

**AND THE PROJECTION IS NOT REACHABLE AT `r = 1.5`, WHICH IS A MEASUREMENT.**
§3.4 holds TWO things fixed across the ladder, deliberately and for good reason:
the surface refinement levels (1 / 2 / 3) and the layer counts (18 / 12 / 5,
Δ₁ constant). **A quantity built from a fixed surface refinement and a fixed
layer stack does not scale as Δ₀⁻³.** Measured, from two levels of the
mesh-development family built with THIS rung's approved `snappyHexMeshDict`
(md5 `dec4c99897dd699801ae2faf9b3f1ee9`, byte-identical at every level) and a
division step of exactly ×1.5:

| level | divisions | **BUILT cells**, from that level's own `log.checkMesh` |
|---|---|---:|
| L1ABS | 128 × 36 × 36 | **532,146** |
| L2ABS | 192 × 54 × 54 | **1,409,804** |

**BUILT `N` ratio = 2.649280, against a projected 3.375. The conventional
shortcut `r_eff = N^(1/3)` gives 1.3837 where the base cell Δ₀ refines by
exactly 1.500. Which of those two the CASE_PROTOCOL §1 band of 1.5 to 2 is read
against is REFERRED, not decided — §14.4a.** §3.4's projected `N` column is a
projection this build cannot deliver, and §14.3 explains why it SHOULD not.

The composition, stated so the number is not a surprise: writing the built count
as a volumetric part scaling `k³` and a surface-plus-layer part scaling `k²`,
`2.649280 = f·3.375 + (1−f)·2.25` gives **`f` = 0.3549** — only **35.5 %** of the
mesh refines in three dimensions — **by design, see §14.3.** This is
corroborated INDEPENDENTLY by §3.5's
own arithmetic in this document: layers alone are **456,096 of the 769,340**
projected `fluid` cells.

### 14.3 THE GATE IS KEPT AND ITS QUANTITY IS CHANGED — `G-MESHSIM` GATES `h`, NOT `N`

**A FIRST DRAFT OF THIS AMENDMENT, WRITTEN EARLIER TODAY AND NEVER LANDED OR
COMMITTED, REGISTERED K2f's WINDOW [3.2063, 3.5438] ON THE BUILT `N` RATIO AND
REGISTERED THAT THE DIVISIONS WOULD MOVE UNTIL THEY LANDED INSIDE IT. THAT IS
STRUCK BEFORE IT EVER BOUND ANYTHING, on the supervisor's ruling of 2026-09-11,
and the reasoning is recorded here rather than deleted, because a remedy that
was wrong for a stated reason is worth more to the next reader than a clean
page.** The supervisor's words, which overturn the supervisor's own earlier
ruling: *"Do NOT move the divisions… a family that passes `G-MESHSIM` by that
route passes the gate while being worse."*

**WHY THE FIRST DRAFT WAS WRONG.** The 64.5 % of the mesh that refines as `k²`
rather than `k³` is **not a defect to be corrected — it is the layer stack, and
it refines in two dimensions BY DESIGN.** Refining the surface gives more layer
COLUMNS (`k²`) and the same 18 / 12 / 5 layers per column (`k⁰`). §3.4 registers
that deliberately and says why: *"Δ₁ is held FIXED across the three levels…
Refining Δ₁ with the base cell would change the wall treatment's y⁺ regime
between levels and the triple would then measure two things at once."*
**So `N` can NEVER scale as `k³` on this ladder, and inflating the divisions
until it does would inflate the BULK to compensate for a boundary layer that is
deliberately not refining — changing the proportion of the mesh in each region
between levels, which is the opposite of geometric similarity.**

**K2f's window is correct FOR K2f: K2f has no layers, so its `N` genuinely does
scale as `k³`. Transplanting a gate is not the same as transplanting its
window.** The gate is kept. The window is struck.

**REGISTERED IN ITS PLACE — `G-MESHSIM`, on the quantity that genuinely refines:**

> **`G-MESHSIM` gates the BUILT background cell size.** For each step, the ratio
> `Δ₀(L_k−1) / Δ₀(L_k)` — **verified from the BUILT mesh, never from the
> dictionary** — must lie in **[1.4250, 1.5750]** (1.500 ± 5 %, the same ±5 % K2f
> allows). Δ₀ is read as the level-0 background cell edge from each level's own
> `constant/polyMesh` (`level0Edge`, cross-checked against `checkMesh`'s
> `Overall domain bounding box` divided by the registered divisions).
> **A step outside the window ⟹ every graded row `NOT A RESULT`**, with both
> ratios, all three Δ₀ values and all three BUILT cell counts printed beside
> the verdict.
>
> **REGISTERED ALONGSIDE IT, in the gate's own statement rather than three
> sections away: the near-wall spacing Δ₁ = 35.89 µm is INVARIANT across the
> ladder by design, so the triple measures OUTER discretisation error ONLY.**
> No claim about near-wall discretisation error is available from this ladder
> and none is registered.

**The BUILT cell counts remain REPORTED at every level, beside the ratios, and
are never gated** — `CLAUDE.md` rule 12's discipline that a figure is reported,
not absorbed.

**THE GATE IS MEASURABLE AS WRITTEN, AND THAT IS SHOWN HERE RATHER THAN
ASSUMED — a gate nobody has read an instrument for is an aspiration.** The
reader was run on the two completed mesh-development levels, 2026-09-11:

| level | `constant/polyMesh/level0Edge` `value` | equals |
|---|---:|---|
| L1ABS | **0.0083984375 m** | 1.075 / 128 exactly |
| L2ABS | **0.0055989583 m** | 1.075 / 192 exactly |

**BUILT `h` ratio, measured from the built artifact: 1.5000000089. EXACT
ratio: 192/128 = 1.5, with NO deviation.** The 8.9e-9 is attributable IN FULL to
`level0Edge`'s ten-significant-digit write precision — 1.075/192 is
0.005598958333… and the field stores 0.0055989583 — and it is **not a property
of the mesh.** Both figures are given, and which is which is stated, so that no
later reader spends an hour chasing a deviation that does not exist. Against the
same two meshes `N^(1/3)` reads **1.383702**. **The quantity that genuinely
refines does so exactly as registered; the conventional shortcut does not see
it.**

### 14.4 THE LIVE GRADING DEFECT THIS EXPOSES — `r = N^(1/3)` IS A FICTION ON A LAYERED MESH

**This is the find, and it is larger than T26.** Anyone forming the Roache ratio
as `r = (N_fine / N_coarse)^(1/3)` on these meshes gets **1.3837**. The true
refinement ratio of the quantity actually being refined is **1.5**. A wrong `r`
propagates into the observed order `p = ln|e32/e21| / ln r` and into every GCI,
**and it does so silently, because `N^(1/3)` is the conventional shortcut and
looks entirely reasonable.**

**REGISTERED: this rung's triple is taken on `h`, with `r = 1.500` at both
steps, and on nothing else.** `analyse_t26.py` already does exactly this —
`R_REFINE = 1.5` (`:76`) is a registered h-ratio constant and no cell count
reaches `verdict_t26()` — and **the comparator REFUSES if it is ever handed an
`r` derived from cell counts on this rung.** The comment at `analyse_t26.py:76`
reading *"h ratio = N^(1/3) = 1.500"* states a justification that §14.2 has now
measured to be false; **the VALUE 1.5 is right and the reason given for it is
not**, and that comment is corrected at the freeze commit.

**THE COMMENT IS CORRECTED AT THIS FREEZE AND THE VALUE DOES NOT MOVE.**
`analyse_t26.py:76` now reads `R_REFINE = 1.5   # :424  BUILT base-cell h ratio;
NOT N^(1/3) -- see :14.4`. **1.5 before, 1.5 after. No gate, band, threshold or
label changes, no verdict moves, and no graded number is affected** — the
correction removes a false justification for a correct constant, which would
otherwise survive only until somebody re-derived the constant from the reason
given for it.

**THE SHARED-INSTRUMENT DEFECT, ROUTED AND NOT QUIETLY FIXED HERE.**
`scripts/roache_triple.py:229` — `refinement_ratio(n_coarser, n_finer, dim)`
returns `(N_finer / N_coarser) ** (1/dim)` — and `:217` `representative_h()`
does the same. **Neither carries any statement that this is invalid on a mesh
whose refinement is mixed**, which every layered snappyHexMesh family is. T26
does not call either function (checked: no T26 instrument imports
`roache_triple`), so this is **not a T26 defect and is not repaired from here**;
it goes to **verification** as a shared-instrument finding.

**AND A SECOND ONE INSIDE THIS RUNG'S OWN COMPARATOR, DISCLOSED RATHER THAN
LEFT.** `analyse_t26.py:1179` `cell_count_audit()` discriminates a 3-D from a
2-D ladder by whether `N` = 3.375 or 2.250. **On a layered mesh that
discriminator does not discriminate:** the measured built `N` of a genuinely
3-D T26-dict mesh is **2.649**, which is NEARER the "2-D" signature 2.250 than
the "3-D" one. The audit runs on the REGISTERED projections and is REPORTED in
the output JSON, never gated, and its docstring already says it *"CANNOT prove
the mesh will be 3D — only checkMesh on a BUILT mesh can (D-3D)"*. **REGISTERED:
`cell_count_audit` is REPORTED-ONLY for this rung and is not evidence of
dimensionality; `D-3D`, which reads `checkMesh`'s own
`Mesh has 3 geometric (non-empty/wedge) directions` line, carries that question
alone.**

**FOR THE RECORD, BECAUSE THE TWO DEFECTS IN THIS SECTION ARE ONE DEFECT AT TWO
SCALES: both are a CELL-COUNT PROXY STANDING IN FOR A GEOMETRIC FACT.**
`r = N^(1/3)` proxies for the refinement of `h`; `N = 3.375 vs 2.250` proxies
for the dimensionality of the mesh. Each proxy is exact on a uniformly refined
mesh and each is silently wrong on a layered one. The remedy in both cases is
the same and it is not a better proxy: **read the geometric quantity itself** —
`level0Edge` for `h`, `checkMesh`'s geometric-directions line for dimension.

### 14.4a REFERRED TO SANAA, NOT DECIDED HERE — WHICH RATIO CASE_PROTOCOL §1's BAND IS READ AGAINST

CASE_PROTOCOL §1 requires a refinement ratio in **1.5 to 2**. **Both numbers are
stated here and neither reading is adopted:**

| reading | T26's value | complies with 1.5–2 |
|---|---:|---|
| against `h` (base cell Δ₀, the quantity that refines) | **1.5000** | **yes, exactly at the floor** |
| against `N^(1/3)` (the conventional shortcut) | **1.3837** | **no** |

**This is Sanaa's charter and the reading is not a lane's to fix, nor a
supervisor's where it would widen a gate.** It is flagged, with both numbers,
and the convenient reading is not chosen.

### 14.5 A FALSIFIABLE PREDICTION, FILED BEFORE THE NUMBER EXISTED

The third mesh-development level was still inside `snappyHexMesh`'s
layer-addition phase when the model of §14.2 was written down. Carrying `f`
forward one step (`f(L2)` = 0.4521) predicts **`N(L3)/N(L2)` = 2.7587** and
**3,889,164 built cells**, band ±3 %. The prediction was written to
`/home/ubuntu/certonomous-runs/T26_mesh_dev/L3ABS_BUILT_COUNT_PREDICTION.txt` at
**2026-09-11T16:45:19Z**, before any count for that level existed on disk. **A
count near 4,758,089 would mean the ladder does scale at 3.375 and §14.2 is
wrong.** The outcome is reported either way.

### 14.6 What this amendment does NOT do

It does not freeze this document; it does not authorise a launch; it does not
alter `GEO-*`, `D-3D`, `G-MINCELL`, `G-CONV-*`, `G-CONT`, `G-BAL` or `G-ITER`,
nor any band, floor or label of theirs; **it leaves the registered divisions
where they are** (§14.3 strikes the un-landed proposal to move them); and it
does not touch §§0–13, whose line numbers are unchanged — **lines whose number
changed above this section: 0** — because `analyse_t26.py`, `mark_done_t26.py`,
`launch_t26.sh`, `build_t26.py` and `orchestrate_t26.py` all cite this document
BY LINE.

*Amendment drafted by a heat-transfer lane, 2026-09-11, on the supervisor's
ruling that T26 gets a built-mesh similarity gate before freeze, and revised
the same day on the supervisor's ruling overturning the gated quantity from `N`
to `h`. Zero solver compute.
Nothing sent, filed or uploaded (`CLAUDE.md` rule 7).*

### 14.7 THE TWO SUPERVISOR RULINGS OF 2026-09-11, RECORDED HERE BECAUSE §§0–13 MAY NOT MOVE

**§0.5 — THE FRONT. T26 PROCEEDS.** `[lab-attributed]` The supervisor's ruling,
and what it does NOT do first: **it does not amend CASE_PROTOCOL §7, which is
Sanaa's charter.** It rules on which instruction is operative. §7 named the
front as **T4e** *before 3D became the priority*; since then Sanaa has said
*"since rn the priority for me are these 3D cases"*, *"I want all th 3D cases i
asked for"* and *"the more 3D industry cases we have and can put in the demo the
better"*, and asked heat-transfer for a 3D thermal list on which this rung sits.
**T4e is a 2.5° axisymmetric WEDGE — 2 geometric directions — and cannot satisfy
a 3D instruction at all.** T26 therefore does not compete with the front; it is
the only way to satisfy an instruction the front is structurally incapable of
satisfying. "No new families" is complied with: an existing family, existing
roots, id from the maximum.

**AND THE REVERSAL IS DELIBERATELY KEPT CHEAP, which is why the ruling is
takeable at this level at all.** The launch is blocked by this session's
permission classifier, so **Sanaa necessarily sees this rung before one
core-minute is spent.** Freezing commits no compute. If she reads §7 as admitting
one live item only, **T26 stops on her word and the lab has lost a document, not
a spend.**

**§7.3.3 — THE HANG GUARD IS ADMISSIBLE, WITH ONE CONDITION THAT IS NOT
OPTIONAL.** `[lab-attributed]` **Sanaa suspended budget STOPS, and a hang guard
is a different object: a cap stop fires because a run is COSTING more than
agreed; a hang guard fires because a process is PRODUCING NOTHING.** Suspending
the first says nothing about the second, and a lab with no wedged-process
detector is not cheaper, it is blind. The 3.0 × POINT discriminator stands, and
it earns its ruling by naming the trap it avoids: T4e's fine leg carries
`timeout 360060`, numerically exactly **2.0000 × POINT — a registered CAP
wearing a hang guard's name.**

> **THE CONDITION, REGISTERED AND BINDING: 3 × POINT is a hang guard ONLY IF
> POINT IS RIGHT, and K2d proves that is not automatic.** K2d's §7.3 carried the
> identical rationale while **L2 had ALREADY falsified POINT by 2.62 ×, on disk,
> before L3 launched, and nobody read it.** Therefore: **before each level's
> guard is used, POINT is RE-DERIVED from the MEASURED rate of the preceding
> level, and the re-derivation is RECORDED beside that level's `START.<level>`.**
> A guard computed from a POINT the ladder's own data has already falsified is a
> cap in disguise, whatever multiplier stands in front of it.
>
> **AND A TRIP IS A FINDING REQUIRING TRIAGE, NEVER A LABEL TAKEN FROM `rc`
> ALONE** (§11). K2d wrote `note=HANG_GUARD_TRIPPED` mechanically on a solver
> that was doing work at the instant it died.

### 14.8 THE OBSERVED-ORDER BAND — ASKED AT ITEM 4, ANSWERED FROM THE CODE AND DRIVEN

**`verdict_t26()` DOES band the observed order.** `P_BAND = (0.5, 2.5)`
(`analyse_t26.py:103`, registration `:581`) is applied at `:1298` in **STEP 3**,
returning `NOT A RESULT` outside it, with the registered response being to ADD A
LEVEL rather than clamp. So the flattering-direction hole is closed, and it was
**driven, not reasoned**:

| triple | state | p | verdict |
|---|---|---:|---|
| e21 representable at 9.9476e-14, e32 = 1 | CONVERGING | **+73.838** | **`NOT A RESULT`** — and the GCI it would have quoted is **1.237e-26 %**, the most flattering number the instrument can produce |
| e21 = 1e-18 added to 100.0 | **EXACT** | none | `NOT A RESULT` at STEP 2 |
| e21 = 5e-324 (denormal) added to 100.0 | **EXACT** | none | `NOT A RESULT` at STEP 2 |

**A SECOND DEFENCE WAS FOUND IN THE DRIVING, AND IT IS AN ACCIDENT OF FLOAT64
RATHER THAN A DESIGN, SO IT IS NAMED AS ONE:** at these magnitudes
`100.0 + 1e-18 == 100.0` exactly, so the perturbation is absorbed and the triple
reports `EXACT` before any order is formed. **That protection is
magnitude-dependent and must not be relied on** — a tiny-but-representable `e21`,
as in the first row, reaches the CONVERGING branch and is stopped by `P_BAND`
and by nothing else.

---

## 15. FREEZE — 2026-09-11, AND WHAT IS CLOSED BY IT

**THIS DOCUMENT IS FROZEN AT THE COMMIT THAT CARRIES THIS SECTION.** From this
commit: no gate, threshold, band, floor, cap or label may change. Changes land
only as dated addenda that cannot alter any of those, and originals are struck,
never rewritten (`CLAUDE.md` rule 2).

### 15.1 THE PRE-COMPUTE CONDITION, RE-TAKEN IN THE COMMITTING INVOCATION

**§12 item 3 requires this at the freeze, not before it.** Commands run verbatim
at **2026-09-11T17:11:07Z**, from the repository root, in the same shell invocation that wrote
this section:

```
test -d verification/runs/T-family/T26_runs        -> ABSENT
test -d verification/runs/T-family/T26_MESH_runs   -> ABSENT
test -d verification/runs/T-family/T23_runs        -> PRESENT     [PLANTED CONTROL, positive arm]
test -d verification/runs/T-family/T99_nonexistent -> ABSENT      [PLANTED CONTROL, negative arm]
```

**Both control arms fired**, so the two absences are statements about the disk
and not about a blind reader (`CLAUDE.md` rule 3). **ZERO SOLVER CORE-MINUTES
HAVE BEEN SPENT AGAINST THIS DOCUMENT.** The only compute on this rung remains
the geometry gate's 0.05 core-min.

**Note for a later reader, so the condition cannot go stale the way K2f's §19.7
did:** this rung's instruments live at `docs/campaigns/T-family/` and NOT under
the run root, deliberately — `analyse_t26.py`'s own docstring (`:5`–`:11`)
records that creating `T26_runs/` even only to hold a script would falsify the
condition the freeze rests on. `launch_t26.sh` creates the run root at launch
and not one moment earlier.

### 15.2 THE ID, RE-DERIVED FROM THE MAXIMUM AND NOT FROM A COUNT

```
{ ls docs/campaigns/T-family/ ; ls verification/runs/T-family/ ; } \
  | grep -oE '^T[0-9]+' | grep -oE '[0-9]+' | sort -n | tail -1
```
**Result: 26.** T26 is that maximum and is this document's own id; it is
taken, by this rung, and by nothing else (`CLAUDE.md` rule 11).

### 15.3 THE INSTRUMENT PINS — §12 item 1's sha256, recorded HERE because §8.3's line numbers may not move

| instrument | sha256 at the freeze |
|---|---|
| `docs/campaigns/T-family/analyse_t26.py` | `c1459612fea9c96c1aa1128ee167dd6dbb91930b4ee0890ad08e54a6d335fa6f` |
| `docs/campaigns/T-family/launch_t26.sh` | `a0887d5b84617f1bf57f1f557250dd4087ea4087f73e6098a9eb5a0b8d161b21` |
| `docs/campaigns/T-family/mark_done_t26.py` | `7b428a65802e66529e97ce38cf0bafcbcfa6686581fd4ecd0a2523e98d91b4b3` |
| `docs/campaigns/T-family/build_t26.py` | `533ca56b1514e0067e6fd7dbcbfcd8ec14e5a4d6c2a6c3ea7310d1c6cf026e72` |
| `docs/campaigns/T-family/orchestrate_t26.py` | `2e79f982463c51efe3c4ef225c0172b73e2481726770d3d3c80dda6aa4fb9868` |

**The grading path is fixed at this commit.** Before grading, each file is
hashed against the blob committed here; a mismatch is a refusal, not a warning.

### 15.4 WHAT THE FREEZE DOES NOT DO

It does not authorise a launch. **No level may start until the §0.5 ruling of
§14.7 has been put in front of Sanaa** — the launch is in any case blocked by
this session's permission classifier, and **no agent works around that.** The
`G-MESHSIM` block of `analyse_t26.py` (`read_level0_edge`, `meshsim_verdict`,
`control_level0_edge_reader`) was written after the supervisor's §12 item-4 diff
read and **has not been read by the supervisor as a diff**; it is pinned by
sha256 above, so any later change to it is detectable, and a read of it can now
be honoured only as a dated addendum.

*Frozen by a heat-transfer lane, 2026-09-11, on the supervisor's rulings of the
same day. Zero solver compute. Nothing sent, filed or uploaded (`CLAUDE.md`
rule 7).*

---

## 16. ADDENDUM 1 TO THE FROZEN DOCUMENT — 2026-09-11T17:14:25Z. THE §12 ITEM-4 READ OF THE `G-MESHSIM` BLOCK, TAKEN AFTER THE FREEZE AND RECORDED AS SUCH

**THIS IS A DATED ADDENDUM UNDER `CLAUDE.md` RULE 2. IT ALTERS NO GATE, NO
THRESHOLD, NO BAND, NO FLOOR, NO CAP AND NO LABEL.** It records a check that
happened, and one disclosure about a frozen reader that is **disclosed and NOT
repaired**, because the file is frozen (rule 6).

### 16.1 WHY THIS ADDENDUM EXISTS AT ALL

§15.4 of the freeze stated that `read_level0_edge()`, `meshsim_verdict()` and
`control_level0_edge_reader()` **were written after the supervisor's §12 item-4
diff read and had NOT been read by the supervisor as a diff.** The freeze pinned
them by sha256 rather than absorbing them silently. **A freeze that quietly
absorbs an unread instrument is the K2d shape: bytes pinned, nobody having
looked.** The read has now been taken, and it is recorded here, dated, rather
than by pretending the freeze covered it.

### 16.2 THE READ, AND WHAT IT FOUND GOOD — supervisor, 2026-09-11T17:14:25Z

- `read_level0_edge()` **calls the existing `strip_foam_comments` rather than
  reimplementing one.** Calling a shared instrument instead of rewriting it is
  what K2d's comparator got right, and it is preserved here.
- **`return v if v > 0.0 else None` — a zero edge is not a value.**
- **An absent file returns `None` and never `0.0`** — the `cost_channel` defect
  class, avoided explicitly and then **mutation-tested on a copy with
  `__pycache__` cleared**, which is the only way that test means anything.
- **`float()` sits inside a `try` returning `None`**, so the K2d
  trailing-period class degrades to a **refusal** rather than an uncaught crash
  at exit 1 — the `read_checkmesh` lesson applied to a reader written the same
  day it was learned.

### 16.3 THE DISCLOSURE — DISCLOSED, NEVER EDITED

> **`read_level0_edge()` returns on the FIRST matching `value` line and does not
> refuse on a second.**

The risk is low: `constant/polyMesh/level0Edge` carries exactly one `value`
entry, and every mesh read by this rung is written by `snappyHexMesh`. **But the
house habit everywhere else in this comparator is to REFUSE ON AMBIGUITY rather
than take the first thing found** — `resolve_unique()` exists for precisely that
— and this one reader does not. **A later reader should see that the divergence
is known and was recorded, not that nobody noticed.**

**It is NOT repaired.** The file is frozen and its sha256 is pinned at §15.3;
editing it would break the pin and the rule-6 prohibition on editing frozen
files. If a case ever presents a second `value` line, this addendum is the
record that the behaviour was known in advance.

### 16.4 WHAT THIS ADDENDUM DOES NOT DO

It does not authorise a launch; it does not alter `G-MESHSIM`'s window
`[1.4250, 1.5750]`, its reader, its refusal on a missing level, or any other
gate; it does not change a single byte of any instrument; and it does not touch
§§0–15, whose line numbers are unchanged — **lines whose number changed above
this section: 0**.

*Recorded by a heat-transfer lane, 2026-09-11, on the supervisor's post-freeze
item-4 read. Zero solver compute. Nothing sent, filed or uploaded
(`CLAUDE.md` rule 7).*

---

## 17. ADDENDUM 2 TO THE FROZEN DOCUMENT — 2026-09-11T17:19:34Z. **A PRE-LAUNCH, FALSIFIABLE PREDICTION ABOUT DELIVERED LAYER COVERAGE — AND A MEASUREMENT THAT PARTLY REFUTES THE MECHANISM WE ADOPTED**

**DATED ADDENDUM UNDER `CLAUDE.md` RULE 2. IT ALTERS NO GATE, NO THRESHOLD, NO
BAND, NO FLOOR, NO CAP AND NO LABEL, AND CHANGES NO BYTE OF ANY INSTRUMENT.**
It registers a prediction **before** this rung's first compute — `T26_runs/`
still does not exist — so it is a test of our understanding rather than a
rationalisation of whatever the ladder returns. **It reports either way.**

### 17.1 THE MEASUREMENT — three mesh-development levels, same dict, same STL

Built with this rung's approved `snappyHexMeshDict` (md5
`dec4c99897dd699801ae2faf9b3f1ee9`, byte-identical at every level) and the same
STL. **These are NOT ladder levels; they are mesh development outside the run
root.** Δ₀ is the mapping variable because everything else is byte-identical.

| level | Δ₀ (mm) | **delivered layer coverage** | layer iterations | stack ÷ Δ₀ |
|---|---:|---:|---:|---:|
| L1ABS | 8.3984 | **44.374 %** | 9 | 1.00 (reference) |
| L2ABS | 5.5990 | **52.902 %** | 24 | 1.50 |
| L3ABS | 3.7326 | **48.042 %** | 28 | 2.25 |

Coverage is `Added N out of M cells` from each level's own `log.snappy`, final
iteration. The layer stack is fixed in metres by registration (`firstLayerThickness`
35.894 µm, `expansionRatio` 1.2, 18/12/5 layers), so **stack ÷ Δ₀ rises by
exactly 1.5 per rung, by construction.**

**AND THE ABSOLUTE NUMBERS ARE STARKER THAN THE RATIO SUGGESTS.** Summing the
geometric series at `expansionRatio` 1.2 gives total stacks of **4.5986 mm on
the hub (18 layers), 1.4207 mm on the struts (12), 0.2671 mm on the duct (5)**.
Against Δ₀: the hub stack is **0.548 × the base cell at L1ABS and 1.232 × it at
L3ABS** — **at the finest level the requested hub stack is THICKER THAN THE
BACKGROUND CELL IT MUST BE INSERTED INTO.** That is a property of holding Δ₁ and
the layer counts fixed while Δ₀ falls, it is registered behaviour and not a
defect, and it is why the medial-axis and thickness-ratio limits bite hardest at
the fine end.

### 17.2 WHAT THE DATA SUPPORTS, AND WHAT IT REFUTES — stated in that order

**SUPPORTED: the relaxation burden rises monotonically.** Layer iterations
**9 → 24 → 28**, strictly increasing, while `nLayerIter` is **50** and no level
hit the cap — so each level ran to stabilisation and each finer level needed
more relaxation than the last. **And iteration count is not a wall-clock
quantity, so machine contention cannot produce it.**

**REFUTED AS A SOLE MECHANISM: that delivered coverage falls monotonically with
refinement.** The reasoning adopted in update 108 — *Δ₁ fixed makes the INPUT
level-invariant but NOT the MESHER'S TASK, because stack ÷ local cell rises 1.5×
per rung and `maxThicknessToMedialRatio 0.3` bites on more faces each rung* —
predicts a monotone decline. **The three-point measurement is NOT monotone:
coverage RISES 8.53 points from L1ABS to L2ABS, then falls 4.86 points to
L3ABS, while stack ÷ Δ₀ rises monotonically throughout.** A single monotone
driver cannot produce a peak.

**THE READING THAT FITS ALL THREE POINTS, offered as a hypothesis and labelled
as one:** two competing effects. At coarse Δ₀ the background cell is poorly
matched to an absolute stack and insertion fails broadly; as Δ₀ falls that
improves. Past a peak — **near Δ₀ ≈ 5.6 mm on this geometry** — the
medial-axis and thickness-ratio limits dominate and coverage falls. **The
update-108 mechanism is real and is visible in the iteration count and in the
L2 → L3 fall; it is simply not the only thing happening.**

### 17.3 THE PREDICTION — direction, magnitude, band, and a NAMED FALSIFIER

**THE T26 LADDER SITS COARSER THAN THE MEASURED FAMILY, AND THEREFORE ON THE
RISING LIMB.** §13.3 shifted the ladder down exactly one rung, so its base cells
are **Δ₀ = 12.000 / 8.000 / 5.333 mm** (arithmetic check: 885,508 ÷ 3.375 =
262,373, §13.3's L1). Mapping onto the measured curve — L2's 8.000 mm sits
beside L1ABS's 8.398 mm, L3's 5.333 mm beside L2ABS's 5.599 mm, and L1's
12.000 mm is coarser than anything measured:

> **PREDICTED, before any T26 level is built:**
>
> 1. **DIRECTION: delivered layer coverage RISES across the T26 ladder,
>    L1 < L2 < L3 — strictly increasing.** This is the OPPOSITE of what the
>    L2ABS → L3ABS fall suggests if that fall is read as a refinement law.
> 2. **MAGNITUDE, with bands: L1 36–44 %, L2 43–47 %, L3 50–55 %.**
> 3. **Layer iterations rise monotonically, L1 < L2 < L3, with L3 in 20–35.**
>
> **NAMED FALSIFIERS — any one of these says this analysis is wrong:**
> - a **strictly DECREASING** coverage sequence across the three T26 levels;
> - **L3 coverage below 45 %**;
> - **L1 coverage above L2's**;
> - coverage flat to within 2 points across all three levels, which would say
>   Δ₀ is not the controlling variable at all.

### 17.4 WHY THIS NEEDED NO NEW GATE — the ladder was already built to catch it

**The freeze already contains the instrument that measures this.** §14's design
reports the **requested** Δ₁ and the **DELIVERED** near-wall height separately,
with the gate on the delivered one; and the BAND × LEVEL 2×2 separates taper
from the rising stack-to-cell burden. **Nothing is added here.** What is added
is the statement, in advance, of what we expect that instrument to show.

**IF IT REPRODUCES ON THE GRADED LADDER it belongs in the results record as a
STATED LIMITATION OF THE FIXED-Δ₁ DESIGN, named by us before the run** — not as
a surprise, and not as a defence constructed afterwards. §3.4 holds Δ₁ fixed so
the near-wall treatment is identical across levels; **delivered coverage varying
by 8.5 points across a 1.5× family says the treatment is NOT identical, and the
triple's claim to measure outer discretisation error alone rests on the
delivered near-wall height, not on the requested one.**

*Recorded by a heat-transfer lane, 2026-09-11T17:19:34Z, on the supervisor's ruling. Zero solver
compute; `T26_runs/` does not exist. Nothing sent, filed or uploaded
(`CLAUDE.md` rule 7).*

---

## 18. ADDENDUM 3 TO THE FROZEN DOCUMENT — 2026-09-11T17:23:39Z. **THE WEAKEST JOINTS IN §17'S PREDICTION, NAMED BEFORE THE NUMBER LANDS**

**DATED ADDENDUM UNDER `CLAUDE.md` RULE 2. ALTERS NO GATE, THRESHOLD, BAND,
FLOOR, CAP OR LABEL, AND CHANGES NO BYTE OF ANY INSTRUMENT.** It is a separate
section rather than an edit to §17 because §17 is committed and this document is
frozen — **a committed record is extended, never rewritten** (rule 6).

**Why it exists:** §17 registered a counter-intuitive prediction with four named
falsifiers. **A prediction that names its own weakest joint is worth more than
one that presents a uniform face**, and §17 presented a uniform face. Two joints
are weak, and they are weak for different reasons.

### 18.1 WEAK JOINT 1 — THE PEAK'S LOCATION IS DETERMINED BY THREE POINTS, AND T26's L3 SITS ESSENTIALLY AT IT

The peak of the coverage–Δ₀ curve is constrained by **exactly three
measurements**, so its location depends on a modelling choice nothing in the
data settles. Fitting the same three points two defensible ways:

| fit | peak Δ₀ | peak coverage |
|---|---:|---:|
| parabola in Δ₀ | **5.7409 mm** | 52.926 % |
| parabola in ln Δ₀ | **5.2964 mm** | 53.028 % |

**The functional form alone moves the peak by 0.44 mm — and T26's L3 sits at
5.333 mm, INSIDE that spread.** Under the log fit L3 is just past the peak;
under the linear fit it is just short of it. Either way the curve is **flat to
first order there**, and the fitted peak is **0.408 mm from L3's Δ₀, which is
15.3 % of the L2 → L3 step.**

> **REGISTERED: the L2 → L3 limb is the LEAST DETERMINED limb of §17's
> prediction.** §17's bands for those two levels — 43–47 % and 50–55 % — do not
> overlap and the margin is real, but **the gap between them is comparable to
> the spread the peak's location introduces**, and a reader should know that
> before the number lands rather than discover it afterwards. §17's
> "flat within 2 points" falsifier covers this only partially.

### 18.2 WEAK JOINT 2 — L1's BAND IS A DIRECTION, NOT A FIT, AND NO CURVE SUPPORTS IT

**This one is not in §17 at all and is disclosed here.** T26's L1 sits at
**Δ₀ = 12.000 mm, coarser than anything measured** — the coarsest measured point
is 8.3984 mm — so its band is an **extrapolation beyond the data**.

**And the fitted curve cannot carry it: evaluated at 12.000 mm the parabola
returns 5.48 % coverage**, which is not credible and is stated here precisely so
nobody later quotes it. **§17's 36–44 % band for L1 therefore rests on
DIRECTION ALONE** — *coarser than 8.3984 mm implies below 44.374 %, on the
rising limb* — **and on no fitted curve whatever.** The band's lower edge, 36 %,
is a judgement about how far the rising limb can plausibly fall, not a
measurement and not an extrapolation of one.

### 18.3 WHAT IS **NOT** WEAKENED

The **direction** claim — coverage rises across the T26 ladder, L1 < L2 < L3 —
does not depend on the peak's location, because **all three T26 base cells lie
on the coarse side of every peak estimate** (12.000, 8.000 and 5.333 mm against
peaks at 5.30–5.74 mm). Only the **magnitude** of the L2 → L3 rise is at risk.
And **§17's falsifiers stand unchanged**: a strictly decreasing sequence, L3
below 45 %, L1 above L2, or flat within 2 points. **No falsifier is widened,
softened or withdrawn by this addendum** — that is the whole point of naming a
weakness rather than adjusting a band to cover it.

*Recorded by a heat-transfer lane, 2026-09-11T17:23:39Z, on the supervisor's instruction to name
the prediction's weakest joint. Zero solver compute; `T26_runs/` does not exist.
Nothing sent, filed or uploaded (`CLAUDE.md` rule 7).*
