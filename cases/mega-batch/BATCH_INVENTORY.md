# Mega-Batch Inventory

Aggregated from ledger.jsonl (207,379 lines); compiled 2026-07-28.

## Total Evaluations

- **207,379 total evaluations**
  - 207,305 ok (99.96%)
  - 74 failed (0.04%)

---

## Per-Solver-Family Breakdown

### 1. openfoam-cylinder

- **Count**: 69,081 evaluations (33.3% of total)
  - 69,019 ok, 62 failed
- **Dimensionality**: 2D
- **Temporal type**: STEADY
- **Reynolds number**: 10 (min) — 27 (median) — 45 (max)
- **Wall time per evaluation**: median 2.4 s, max 16,310 s
- **Flow regime**: Laminar steady flow, incompressible, simpleFoam

### 2. openfoam-cylinder-unsteady

- **Count**: 209 evaluations (0.1% of total)
  - 209 ok, 0 failed
- **Dimensionality**: 2D
- **Temporal type**: UNSTEADY
- **Reynolds number**: 100 (min) — 526 (median) — 1,000 (max)
- **Wall time per evaluation**: median 393.7 s, max 434.2 s
- **Flow regime**: Laminar vortex shedding, 2D circular cylinder, unsteady pimpleFoam

### 3. reduced-order

- **Count**: 68,937 evaluations (33.2% of total)
  - 68,937 ok, 0 failed
- **Dimensionality**: N/A (not a simulation)
- **Temporal type**: N/A (not a simulation)
- **Reynolds number**: not recorded
- **Wall time per evaluation**: median 0.0 s, max 0.4 s
- **Flow regime**: **NOT A SIMULATION** — fitted surrogate / cycle-decomposition orifice screen

### 4. rhosimplefoam-naca0012-transonic

- **Count**: 142 evaluations (0.1% of total)
  - 142 ok, 0 failed
- **Dimensionality**: 2D
- **Temporal type**: STEADY
- **Reynolds number**: 3,003,308 (min) — 4,940,220 (median) — 6,963,719 (max)
- **Mach number**: 0.70 (min) — 0.77 (median) — 0.85 (max)
- **Wall time per evaluation**: median 29.6 s, max 76.3 s
- **Flow regime**: Steady RANS, compressible, transonic shock (M = 0.70–0.85), rhoSimpleFoam kOmegaSST

### 5. vspaero-wing

- **Count**: 69,010 evaluations (33.3% of total)
  - 68,998 ok, 12 failed
- **Dimensionality**: 3D
- **Temporal type**: STEADY
- **Reynolds number**: not recorded (inviscid method, no boundary layer)
- **Wall time per evaluation**: median 5.2 s, max 16,304.6 s
- **Flow regime**: 3D inviscid vortex-lattice panel method (VSPAERO), no viscous boundary layer

---

## Dimensional & Temporal Totals

### Dimensionality

- **2D**: 69,432 (33.5%)
  - openfoam-cylinder: 69,081
  - openfoam-cylinder-unsteady: 209
  - rhosimplefoam-naca0012-transonic: 142
- **3D**: 69,010 (33.3%)
  - vspaero-wing: 69,010
- **N/A** (non-simulation): 68,937 (33.2%)
  - reduced-order: 68,937

### Temporal Type

- **Steady**: 138,233 (66.7%)
  - openfoam-cylinder: 69,081
  - rhosimplefoam-naca0012-transonic: 142
  - vspaero-wing: 69,010
- **Unsteady**: 209 (0.1%)
  - openfoam-cylinder-unsteady: 209
- **N/A** (non-simulation): 68,937 (33.2%)
  - reduced-order: 68,937

---

## Notes

- **Three original families** (openfoam-cylinder, vspaero-wing, reduced-order) are **cheap/thin**: 2–5 s median wall time (or < 0.5 ms for surrogate).
- **Two new hard-physics families**:
  - openfoam-cylinder-unsteady: ~390 s per evaluation (4 minutes), unsteady transient solve
  - rhosimplefoam-naca0012-transonic: ~30 s per evaluation, steady RANS with shock capturing
- **Maximum wall times** (16,300+ s on older families) are outliers; see runner.log for transient convergence failures that exceeded time budget.
