# T9a. The conjugate ladder's exact-theory entry: composite wall and fin efficiency

Campaign T, tier 4, rung T9a. Written 2026-08-19, **before any case was built.**
Run tree `verification/runs/T-family/T9a_runs/` (not yet created).

---

## 1. Why this rung, and why it can be built today

**T9a is EXACT tier** (`T_FAMILY_INDEX.md`): its references are closed-form
solutions, so **there is nothing to obtain and nothing that can be argued about
the reference.** It is one of only two rungs in the entire T-family with that
property, and it **opens the conjugate ladder** — T9b, T9c, T11 and T13 all rest
on solid-side conduction being right.

**It is built now because T1c taught that the exact-theory members of a class
should be enumerated before the class is called blocked.** The docket recorded
forced convection as reference-limited while T1c — needing no reference at all —
sat unbuilt inside it.

**This rung grades conduction and a convective boundary condition. It grades no
turbulence model and no fluid solution.** Getting the solid side right is a
precondition for every conjugate claim above it, not a substitute for one.

---

## 2. T9a-1 — the composite wall, against series resistances

Three layers in series, fixed temperature on each outer face.

| layer | `L` (m) | `k` (W/mK) | `R = L/k` (m²K/W) |
| --- | ---: | ---: | ---: |
| 1 | 0.05 | 0.8 | 0.062500 |
| 2 | 0.10 | 0.04 | 2.500000 |
| 3 | 0.02 | 16.0 | 0.001250 |
| | | **total** | **2.563750** |

`T_hot = 350 K`, `T_cold = 300 K`. **The closed form is exact:**

- `q″ = ΔT / ΣR =` **19.502682 W/m²**
- interface after layer 1: **348.781082 K**
- interface after layer 2: **300.024378 K**

**The conductivity ratio spans 400×** (0.04 to 16), which is deliberate: a
uniform-conductivity solver bug, or an interface treatment that averages
conductivity where it should average resistance, shows up **only** when the
contrast is large. **A three-layer wall with similar conductivities would pass
while being wrong.**

---

## 3. T9a-2 — fin efficiency, against `tanh(mL)/mL`

Straight rectangular fin, adiabatic tip. `k = 200 W/mK`, `t = 0.002 m`,
`L = 0.05 m`, `h = 50 W/m²K` applied on both faces as a Robin condition.

- `m = √(2h/kt) =` **15.811388 m⁻¹**, `mL =` **0.790569**
- **efficiency `η = tanh(mL)/mL =` 0.8332367**
- **tip excess-temperature ratio `1/cosh(mL) =` 0.7523781**

**`mL ≈ 0.79` is chosen, not inherited.** At `mL → 0` the efficiency tends to 1
and at `mL → ∞` to 0; **either limit would make the row pass for a solver that
had the physics badly wrong.** At `mL = 0.79` the efficiency sits at 0.833, far
from both limits, so the row can actually be failed.

### 3.1 The reference's OWN validity, stated before it is used

**The fin equation is one-dimensional and is valid to `O(Bi)`, where
`Bi = ht/2k` =** **2.5e-04.**

**So the analytic reference carries its own 0.025 % error**, and the comparison
is only meaningful if the armed band exceeds it. **REGISTERED CONDITION: if the
GCI band comes out below 0.025 %, the row is REPORTED and NOT GRADED**, because
below that the disagreement would be measuring the fin equation's
one-dimensionality rather than this lab's solver. **This is the T1c lesson
applied in advance**: there, both arms overshoot the exact constant by an amount
that survives mesh refinement, and the reference's own neglected physics is
still the leading suspect.

---

## 4. Band, controls, and preconditions

**The band is derived, never chosen** — three mesh levels at ratio 1.6, Roache
GCI at `Fs = 1.25` on the finest. **If the triple is oscillatory, stagnant or
divergent, no band is armed and the row is NOT A RESULT.**

**Controls, each a row that MUST fail if the rung is sound:**

- **C1 — wrong resistance rule.** The composite wall graded against the
  **arithmetic mean** conductivity instead of series resistances. With a 400×
  contrast the two differ by orders of magnitude; a band admitting both would be
  measuring nothing.
- **C2 — perfect fin.** The fin graded against `η = 1`, the infinite-conductivity
  limit. **20.0 % away from 0.8332**, so it must fail by a wide margin.
- **C3 — the trivial baseline (Charter §2c).** A uniform-temperature solid.
  **Registered before the rung exists**, because D433 retired four rows across
  two geometries that a trivial solution passed.

**Carried forward from T1c and T1b, because they were paid for once:**

- **Any geometric constant is READ from the mesh, never assumed.** In T1c
  assuming the wall sat at `D/2` cost 9 % of the Nusselt number and produced a
  false DIVERGENT verdict.
- **`writeInterval` strictly less than `endTime`** (L-140).
- **Convergence is judged by comparing written checkpoints, NOT by
  `residualControl`** (L-141), which in the wedge cases proved permanently
  unsatisfiable and never once fired across two rungs.

---

## 5. What this rung cannot do

- **It cannot validate conjugate coupling.** Both cases impose the fluid side as
  a boundary condition rather than solving it. The coupled interface is **T9b**.
- **It cannot validate any turbulence or thermal closure.** There is no fluid.
- **It says nothing about contact resistance, anisotropic conductivity, or
  temperature-dependent `k`**, all excluded by construction.

---

## 6. Status

**NOT BUILT AND NOT RUN. Zero compute spent.** Both references are derived above
and will be re-derived in the rung's own comparator, which will **refuse to run
if its two derivations disagree** — the same discipline as `exact_laminar_pipe.py`
in T1c.

**Ordering note:** `T_FAMILY_INDEX.md` recommends pulling T9a forward, and that
recommendation is **recorded, not applied.** This specification exists so the
rung is ready the moment Sanaa says so; **it does not displace anything in the
registered order of attack.**
