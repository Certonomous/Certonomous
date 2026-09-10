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
