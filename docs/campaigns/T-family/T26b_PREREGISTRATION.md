# T26b — the motor-in-duct four-region conjugate case, ONE level, with the envelope registered in its own right: pre-registration (FROZEN)

**Version 1.0. Rung `T26b`. Family: T. Team: heat-transfer. Dated 2026-09-12.**
**Status: FROZEN at this commit. NO T26b CASE HAS BEEN BUILT AND NO T26b CASE HAS RUN.**

> **RULE 2, PRE-COMPUTE CONDITION NAMED AND CHECKED.** At this commit
> `/home/ubuntu/certonomous-runs/T26b_mesh/` **does not exist** and
> `verification/runs/T-family/T26b_runs/` **does not exist** — verified on disk
> by this lane immediately before freezing. There is no T26b answer for any gate
> below to have been chosen to fit.

> **T26 IS NOT SUPERSEDED AND IS NOT REPAIRED BY THIS RUNG.** `T26_PREREGISTRATION.md`
> stays frozen with its three-level ladder and every addendum it carries. T26b
> does not amend it, does not grade against it and does not lift any of its
> stops. What T26b does is register **ONE level** that clears `GEO-8` on **both**
> named features and fits this box — which T26's ladder does not.

---

## 1. THE SURFACE — PINNED, NOT INHERITED

The registered geometry is the same binary STL T26 pins, by sha256 of its disk
bytes and never by name:

**sha256** `131aab8e17242415364d2f1147a76cfbdc7fe5f48287a0996c2318249857db5f`

**INDEPENDENT REPRODUCTION OF §1 AND OF GEO-2/3a/3b/4**: facets 5,376 / 768 /
48 / 48 / 48; volumes +4.627164e-04, +8.005344e-04, +1.095750e-05 ×3; areas
0.030676 / 0.328391 / 0.006449 — §1's table to every digit it prints.
All five components watertight and consistently
oriented. Facets are contiguous by component in file order — duct [0, 768), hub
[768, 6144), struts at 6144 / 6192 / 6240.

---

## 2. WHAT T26 ESTABLISHED, AND WHY THIS RUNG IS NECESSARY

Two measured failures, both on record, neither repaired by amending T26:

**FAILURE 1 — the region split.** `splitMeshRegions -cellZones -overwrite`
returned **206 regions** named `domain0…domain205` instead of four, and
`chtMultiRegionSimpleFoam` cannot run on that mesh. Root cause, measured by the
topology probe of 2026-09-11: hub + duct + strutA/B/C were bundled into ONE
`triSurfaceMesh` with the cellZones in its `regions{}` sub-dict, so
`cellZoneInside inside` had no searchable volume, snappyHexMesh reported
**"Found 2 closed, named surfaces"** against three geometry entries supplied,
fell back to the **seed walk**, and the walk leaked into the scaffolding — the
`duct` zone took **172,001 of 199,684 cells**. **Repaired at `d9c2e41af`**: one
geometry entry per closed body, the seed-envelope assert, the region-set check
and the connectivity gate, each with a planted control that fires.

**FAILURE 2 — `GEO-8` at every registered level.** `T26_PREREGISTRATION.md:254`
freezes `GEO-8` as *"surface cell ≤ ⅓ of the smallest named feature"*, and
discharges it as *"strut thickness 4.000 mm ⟹ cell ≤ 1.333 mm"*. §21.4 checks
that bar against the **strut** surface level only. The **duct-bore** surface
sits at level 1 — **9.000 / 6.000 / 4.000 mm** across the three registered
levels — and fails the same bar by **6.75× / 4.50× / 3.00×**. **Every level of
T26's registered ladder violates T26's own frozen gate.** A gate is not widened
and a frozen ladder is not amended, so the ladder is replaced in a successor.

**FAILURE 3 — the envelope coupling, found while repairing FAILURE 2.** Raising
the duct to level 4 dragged `fluid_env` — a **synthesised 96-gon prism,
r = 0.125000, x ∈ [−0.175000, 0.900000], 0.9425 m² over 1.075 m** — up with it,
because `build_t26.py` wrote `lev["duct"]` for the envelope and **T26 registers
no envelope level at all**. Measured: the env refinement band holds **46,542
cells at level 1 and 2,978,695 at level 4**, while the duct solid occupies
**18.6 %** of that length. The build reached 4,029,680 cells and 6,876 MiB
resident and was stopped on memory. **Repaired at `02c96cd48`** — but the
builder's pin is a *fallback*, and the durable fix is §3.5 below.

---

## 3. MESH — ONE LEVEL

### 3.1 Regions — FOUR, and the reason

| region | material | extent | source |
|---|---|---|---|
| `fluid` | air | the duct bore, extended axially (§3.2) | duct component minus hub/struts |
| `core` | winding + lamination pack, **k = 40 W/m·K** | hub interior inset 4.000 mm | class default from `T23_PREREGISTRATION.md:131` |
| `housing` | aluminium | hub shell 4.000 mm **∪ the three struts** | GEO-7 union |
| `duct` | aluminium | the 5.000 mm annular shell, x ∈ [0, 0.2] | duct component |

**The struts are the conduction path from the motor to the duct wall and are the
entire physical claim of this rung.** They are unioned into `housing`, and a
build in which they are not is a finding, not a level.

### 3.2 Domain

| item | value | basis |
|---|---:|---|
| inlet plane | x = **−0.175000 m** | **1.0005 × D_h** upstream of the duct entrance |
| outlet plane | x = **+0.900000 m** | **4.0021 × D_h** downstream of the duct exit (0.2 + 0.700000) |
| total axial length | **1.075000 m** | derived |
| cross-section | the measured 96-gon bore, circumradius 0.125000 | the STL itself |

### 3.3 `GEO-8` — DISCHARGED AGAINST **BOTH** NAMED FEATURES, WHICH IS WHAT T26 DID NOT DO

`GEO-8`'s bar is unchanged and is **not** widened by a micron: surface cell
**≤ 1.333 mm**, being ⅓ of the **smallest** named feature, the strut at
4.000 mm. The duct wall at 5.000 mm is the *other* named feature and its own ⅓
bar is the looser **1.667 mm**; the binding bar is therefore 1.333 mm and it is
applied here to **every surface that resolves a named feature**:

| named feature | size | ⅓ bar | registered cell | margin |
|---|---:|---:|---:|---|
| strut thickness | 4.000 mm | **1.333 mm** | **1.1250 mm** | **PASS, 15.6 %** |
| duct wall thickness | 5.000 mm | 1.667 mm (1.333 applied) | **1.1250 mm** | **PASS, 15.6 %** |

### 3.4 THE ONE LEVEL

**ONE level is registered, not three, and no triple is claimed.** Sanaa's
standing order is a healthy completed run in band first and the triple second;
one completed level of a four-region conjugate case is what this box can deliver
tonight, and a three-level triple on this case is a successor's work.

```
REGISTERED-LADDER L1 cells=3900000 endTime=5400 ranks=8 delta0_mm=18.000
```

**That line is machine-readable and is the ONLY source of the ladder for any
instrument.** `cells` is a **PROJECTION** and is labelled as one: it is derived
in §4 from a measured trajectory, not multiplied from another level. **The
measured count replaces it at build time and the difference is reported, never
absorbed.**

### 3.5 SURFACE LEVELS — AND THE ENVELOPE IS REGISTERED IN ITS OWN RIGHT

| | L1 |
|---|---:|
| base cell Δ₀ | **18.000 mm** |
| duct-bore surface level | 4 (1.1250 mm) |
| hub surface level | 2 (4.5000 mm) |
| **strut surface level** | **4 (1.1250 mm)** |
| **envelope (`env`) surface level** | **1 (9.0000 mm)** |
| layers (hub / strut / duct) | 18 / 12 / 5 |

> **THE REGISTERED ENVELOPE LEVEL, AND WHY REGISTERING IT IS THE DURABLE FIX.**
> `fluid_env` is a **synthesised meshing boundary**, not a physical body and not
> a named feature: `GEO-8` says nothing about it. Its only named-feature duty is
> the **fluid/duct interface over x ∈ [0, 0.200]**, and **that interface is
> already resolved to 1.1250 mm by the `duct` entry's own `level (4 4)`** —
> established from the geometry rather than inferred: `duct.stl` carries its own
> inner bore at **r = 0.125000** over that span, **1,152 vertices measured
> exactly at that radius**, in a closed annular shell running to r = 0.130000.
> Over that span the env wall is **coincident** with it — same radius, same
> 96-gon, and the builder refuses unless the duct bore and the hub share one
> phase. So the envelope is registered at **level 1**, and the remaining
> **81.4 %** of its length — a 0.6 m downstream tail and a 0.125 m upstream run
> — is not meshed at duct resolution for nothing.
>
> **This is the quantity `build_t26.py` previously chose for itself.** With it
> registered, the builder's pin to the duct-bore row becomes a **fallback**
> rather than the mechanism, and the defect cannot return in the same shape when
> a future rung raises the duct for a real reason. **Registering a quantity is a
> registration act; inventing one inside an instrument is the defect
> `T26_PREREGISTRATION.md` §21.7 records, and it is not done here.**

`env` carries the `inlet` and `outlet` planes as well as `env_wall`. At
Δ₀ = 18.000 mm all three are **9.0000 mm**. They are far-field boundaries, not
named features, and `GEO-8` does not bind them. **Stated rather than buried:
under T26's coupling they would have been 1.1250 mm, and that change is
deliberate.**

| quantity | derivation | value |
|---|---|---|
| **first-cell THICKNESS** | Δ₁ = 2y | **3.589448e-05 m = 35.89 µm** |
| duct-bore Δ₁ at y⁺ = 30 | Δ₁ = 2 y⁺ν/u_τ | **1.07683e-03 m** |

---

## 4. MEMORY — A REGISTERED STOP, BECAUSE THIS WALL WAS HIT ONCE ALREADY

**BASIS — MEASURED on this box 2026-09-12T03:25–03:35Z**, on the stopped
duct-level-4 build, and not modelled:

| quantity | value | how it was obtained |
|---|---:|---|
| refinement trajectory | 95,512 → 280,193 → 637,396 → 1,522,644 → **4,029,680** | `log.snappy`, surface refinement iterations 0–3 |
| resident set at 4,029,680 cells | **6,876 MiB**, 0 MiB of its own swapped | `/proc/<pid>/status VmRSS` |
| **memory rate** | **1.71 kB/cell** | 6,876 MiB ÷ 4,029,680 |
| env band removed by §3.5 | **2,978,695 → 46,542 cells** | 0.9425 m² ÷ cell², band 4 cells deep |

**PROJECTION for this rung, with every factor named:**

| term | value | status |
|---|---:|---|
| castellated cells | **~3.9 M** | 6.8 M measured trajectory **minus** the ~2.93 M env band §3.5 removes |
| final cells after layers | **~5.0 M** | layers 18 / 12 / 5; **an ALLOWANCE, not a measurement** |
| resident at final count | **8.2 GiB** | 5.0 M × 1.71 kB/cell, measured rate |
| layer-addition peak multiplier | **×1.6** | **an ALLOWANCE**; snappy's layer phase runs 1.5–2× the castellated footprint and no measurement on this box isolates it |
| **PROJECTED PEAK** | **≈ 13.7 GiB** | derived from the two rows above |

> **THE REGISTERED MEMORY STOP.** The build **REFUSES** unless, read **FRESH
> from `free` immediately before it starts**, `available − 4 GiB ≥ 13.7 GiB`
> (i.e. **available ≥ 17.7 GiB**). **The stop is a REFUSAL, never a warning, and
> the build is not started to see what happens.** A build stopped by this clause
> is `BLOCKED`, not a failure, and it is re-run unchanged when the box has the
> headroom — the mesh is the right mesh and the box is the constraint.
>
> **THIS CLAUSE EXISTS BECAUSE THE WALL WAS HIT.** On 2026-09-12T03:35:08Z a
> duct-level-4 build was stopped by its own lane at 6,876 MiB resident while the
> box carried 8,925 MiB of swap belonging to four other runs, two of which this
> lane is forbidden to touch. **A registration that does not anticipate a wall
> its own team hit the same night has learned nothing.**

---

## 5. RULE 12 — COST, AT **MEASURED** EFFICIENCY, AND THE SOLVER IS THE SLOW ONE

**THE MEASUREMENT THAT SETS THIS CAP, and it is not the rack's number.**
Measured on this box over a live 60 s window at load 40.6 on 16 cores,
2026-09-12T03:32Z:

| process | ranks | **measured CPU efficiency** |
|---|---:|---:|
| `chtMultiRegionSimpleFoam` (T5f, 1 rank, nice 0) | 1 | **0.288–0.410** |
| `buoyantBoussinesqSimpleFoam` (T4e, 1 rank, nice 0) | 1 | **0.931–0.986** |
| `rhoCentralFoam` (1 rank, nice 0) | 1 | **0.931–0.982** |
| `simpleFoam` (cfd, 6-rank MPI, nice 10) | 6 | **0.558** |

**`chtMultiRegionSimpleFoam` IS THE SLOW SOLVER ON THIS BOX** — ~0.40 under
load where two other single-rank solvers hold 0.93+ in the same window. **T26b's
cap is written for that and not for the rack's numbers**, because a cap written
for a fast solver stops a slow one that is doing nothing wrong.

**WORK BASIS — MEASURED**, from T5f's medium level, the same solver:
**1.30 CPU-s per outer iteration at 216,214 cells** ⟹ **6.01e-06 CPU-s per
cell-iteration**. Scaled to 5.0 M cells × `endTime` 5400 ⟹ **162,270 CPU-s** of
useful work. **The per-cell rate is measured on a TWO-region case and T26b has
FOUR; this is an allowance in the optimistic direction and is named as one.**

| ranks | parallel efficiency (**ALLOWANCE**) | CPU share | **wall** | **core-min charged** |
|---:|---:|---:|---:|---:|
| 4 | 0.85 | 0.40 measured | **33.1 h** | 7,954 |
| **8** | **0.75** | **0.40 measured** | **18.8 h** | **9,015** |
| 8 | 0.75 | 0.90 (box free) | 8.3 h | 4,007 |

**REGISTERED: 8 ranks. POINT = 4,007 core-min. CAP = 9,015 core-min.** The CAP
is the **contended** figure, so that contention cannot stop a legitimate run;
rule 12 charges core-minutes as wall × ranks ÷ 60, so poor CPU share inflates
the **charge** linearly and the cap must absorb it or it is not a cap. **An
overrun STOPS the run; it does not get a new budget.** **$7.71 at CAP, DERIVED
AND NEVER MEASURED**, at $0.0513/core-h — this box cannot read its own billing.

> **THE HONEST SENTENCE ABOUT THE CLOCK.** At tonight's measured contention this
> level needs **18.8 wall-hours**. **It cannot be shot for a demo tomorrow if it
> starts contended.** It reaches 8.3 h only on a box that is substantially free.
> That is a scheduling fact registered in advance, not discovered at hour six.

---

## 6. THE GATE, THE BAND AND THE LABEL — ONE LEVEL, NO TRIPLE

**No Roache triple is claimed and no GCI is quotable from this rung.** Rule 5
needs three levels; T26b registers one. Any row derived from it carries its
level count on its face.

| gate | quantity | threshold | label if met | label if not |
|---|---|---|---|---|
| **G-REGION** | the built region set | **exactly** `fluid`, `core`, `housing`, `duct`, each **ONE connected piece** | proceed | **`NOT A RESULT`** |
| **G-STRUT** | struts present in `housing` | strut cells > 0 in the `housing` zone | proceed | **`NOT A RESULT`** — the conduction path is the claim |
| **GEO-8** | surface cell on strut and duct | **≤ 1.333 mm** | proceed | **`NOT A RESULT`** |
| **G-T** | `max(T)` in `core` at `endTime` | within **[300 K, 450 K]** | **`PASS`** | **`GATE FAIL`** |

**G-T's band is registered BEFORE any T26b solve exists** (§0). Its basis is the
class default `k = 40 W/m·K` of §3.1 and an aluminium housing; **it is a
plausibility band, not a validation against data, and it is labelled as one.**
No experimental reference is claimed for this geometry.

---

## 7. RULE 4 — COMPLETION, AND RULE 3 — THE PLANTED ZERO

**Completion** is `CLAUDE.md` rule 4 unchanged and is not re-registered here:
`rc=0`; an `End` line; last time == `endTime`; `ExecutionTime` count ==
`round(endTime/deltaT)`; and **every field at `endTime` newer than the case's own
`0/T`** (the age guard). A guard refuses a case where `0` or a time dir already
exists.

> **THE FIELD LIST IS PER REGION, FOR THE REGIONS THAT HAVE THOSE FIELDS.**
> `chtMultiRegionSimpleFoam` writes `T` and `p` for a **solid** region and
> nothing else. The registered fields are therefore the full thermal list in
> **`fluid`**, and **`T` and `p`** in `core`, `housing` and `duct`. **Registered
> this way deliberately**: `T5f_PREREGISTRATION.md` §7 wrote the list as
> required "in both regions" and that clause is unsatisfiable by a correct run
> — see its DATED ADDENDUM 1 at `bd1f9dfad`. The same error is not repeated.

**The planted zero** (rule 3) binds every comparator this rung uses: it plants a
known perturbation, reads it back **from disk**, and **REFUSES rather than
degrades** if the reader cannot see it.

---

## 8. WHERE THINGS LIVE

> **The built `constant/polyMesh` trees live OUTSIDE the repository, under
> `/home/ubuntu/certonomous-runs/T26b_mesh/<level>/`.** §3.6's birth certificates
> stay at their registered path, `verification/runs/T-family/T26b_runs/<level>/MESH_BIRTH_CERTIFICATE.json`.

**A level with no birth certificate is not a level and cannot be graded.**

---

## 9. THE FREEZE SET — sha256 OF THE DISK BYTES (never a git blob SHA-1, L-450)

| file | sha256 |
|---|---|
| `docs/campaigns/T-family/build_t26.py` (at `02c96cd48`) | `44907eb5ab187a94492506af03e89b0c60429a490185c834bd95b0a7740b7912` |
| `docs/campaigns/T-family/analyse_t26.py` | `27e175a0faff77c8ca77db5c13af420fffa7f43a3a8c9f61a575eb12996fa121` |
| `docs/campaigns/T-family/geometry_gate_t26.py` | `8cf4fde2d63a47cb79e2b53f897bcdd3654a8468055b6a92c5120eb62fc13ceb` |
| `docs/campaigns/T-family/mark_done_t26.py` | `7b428a65802e66529e97ce38cf0bafcbcfa6686581fd4ecd0a2523e98d91b4b3` |
| `docs/campaigns/T-family/orchestrate_t26.py` | `bf4158e7c02ff65541f89eb28d6a747ae5ea0f692151a2ecbb0aacc00fd3f8f3` |
| `docs/campaigns/T-family/launch_t26.sh` | `242297a92c1827ee767d87aec7b5ff55a82f454a5c16347a0714ae53448b272b` |
| the registered STL (`cases/demo-surfaces/motor_in_duct.stl`) | `131aab8e17242415364d2f1147a76cfbdc7fe5f48287a0996c2318249857db5f` |

---

## 10. WHAT THIS RUNG CANNOT DO

- **It cannot produce a Roache triple or a GCI.** One level.
- **It cannot validate against experiment.** §6's band is plausibility, not data.
- **It cannot settle whether `build_t26.py`'s repaired topology produces four
  connected regions on the REAL geometry** — that has never been run, and §6's
  `G-REGION` exists precisely to refuse the rung if it does not.
- **It does not re-open T26**, whose ladder and addenda stand frozen.
- **It cannot be shot for a demo if it starts on a contended box** (§5).
- **Nothing here is sent, filed, uploaded, registered, posted or commented
  outside this box** (rule 7).

---

## 11. THIS REGISTRATION IS NOT YET READABLE BY ITS OWN INSTRUMENTS — DISCLOSED AT THE FREEZE, NOT DISCOVERED AT THE BUILD

**Every registration reader in `build_t26.py` was DRIVEN against this document
before it was frozen.** Nine of ten pass and return the registered values:

| reader | result against this document |
|---|---|
| `reg_stl_sha256` | `131aab8e…57db5f` |
| `reg_regions` | `['fluid', 'core', 'housing', 'duct']` |
| `reg_domain_x` | `(-0.175, 0.9)` |
| `reg_core_inset` | `0.004` |
| `reg_layers` | `{'hub': 18, 'strut': 12, 'duct': 5}` |
| `reg_delta1` | `{'wall': 3.589448e-05, 'duct': 0.00107683}` |
| `reg_mesh_root` | `/home/ubuntu/certonomous-runs/T26b_mesh/` |
| `reg_certificate_path` | `verification/runs/T-family/T26b_runs/…` |
| `reg_component_measurements` | all five components, facets / volume / area |
| **`read_registered_ladder`** | **REFUSES** |
| **`reg_surface_levels`** | **REFUSES** |

**THE BLOCKER, STATED AS A DEFECT IN THE INSTRUMENTS AND NOT IN THIS DOCUMENT.**
`analyse_t26.py` and `build_t26.py` each carry `LEVELS = ("L1", "L2", "L3")` as a
module constant. `read_registered_ladder` refuses a registration that does not
carry a ladder row for **all three**, and `reg_surface_levels` refuses a levels
table that does not carry **three entries per row**. **A single-level rung is
therefore structurally unreadable by this instrument family**, whatever it
registers.

**THREE ROWS ARE NOT WRITTEN HERE TO GET PAST THAT PARSER.** Registering `L2`
and `L3` rows this rung has no intention of building — with cells, `endTime`,
ranks and caps nobody derived — to satisfy a regex would put numbers on a frozen
document that are not meant, and a later reader could not tell which rows were
real. **The one-level ladder is what is meant and it is what is registered.**

**WHAT MUST HAPPEN BEFORE THIS RUNG CAN BUILD**, named so the sequence is not
discovered at launch:

1. the level vocabulary read **from the registration** rather than held as a
   module constant in two files;
2. `--registration` threaded from `main()` so a build can cite this document at
   all (`build_t26.py:279` hardcodes `T26_PREREGISTRATION.md`);
3. `reg_surface_levels` reading its ladder from the **passed** path — it calls
   `read_registered_ladder(REGISTRATION)` at `build_t26.py:405`, the module
   constant, so it would otherwise validate THIS document's levels table against
   **T26's** Δ₀;
4. a `reg_env_level()` reader, because **§3.5's registered envelope level is not
   read by anything today** — the builder's pin to the duct-bore row is a
   fallback, and until a reader exists the registered value is inert.

**Each is an instrument change, each is a measurement-path diff, and none is
made by this document.** They are proposed separately for the supervisor's
personal read. **Until they land, T26b is `PENDING` on its own instruments and
no T26b build may be started** — a registration whose instruments cannot read it
does not get built around.
