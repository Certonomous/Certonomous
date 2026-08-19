# The tall cavity's three-level ladder: which thermal errors are physical

Campaign F14, gate K0c. Written 2026-08-19. **Zero compute, zero writes, grades
nothing.** Instrument
`verification/runs/F14-cooling-ladder/K0cX_runs/grid_convergence.py`; every value
read from the committed `gate_k0cx.json`.

---

## 1. Why this was owed

**`K0cX` graded on the FINE mesh of a coarse/fine pair and reported deviations
against the experiment. A deviation becomes MODEL error only once
DISCRETISATION error is bounded**, and that needs three levels and an observed
order. **Three levels exist for the hi-Ra rung — 4 800, 12 288 and 31 314 cells,
refinement ratio 1.60 — and the order was never computed.** Until now every
number in that rung conflated the two.

---

## 2. Only one of six is in the asymptotic range

| Model / quantity | state | observed order |
| --- | --- | ---: |
| `kOmegaSST` / `S` | **CONVERGING** | **p = 1.223**, GCI(finest) **2.95 %** |
| `kOmegaSST` / `Nu_avg` | OSCILLATORY | not reportable |
| `LaunderSharmaKE` / `Nu_avg` | OSCILLATORY | not reportable |
| `kEpsilon` / `Nu_avg` | STAGNANT | p = 0.106 |
| `kEpsilon` / `S` | **DIVERGENT** | p = -0.380 |
| `LaunderSharmaKE` / `S` | **DIVERGENT** | p = -0.168 |

**No order is reported where the sequence is oscillatory, stagnant or
divergent.** `VERIFICATION_CHARTER.md` §3.2 records the two ways an observed
order lies, and printing a number that looks like convergence is one of them.

---

## 3. Where a formal order is unavailable, the mesh spread still bounds the answer

The spread across the three levels is not a GCI and is not labelled one. It is
**what the meshes actually did**, and it is enough to attribute the error.

| Model | `Nu_avg` deviations, coarse -> fine -> finest | mesh spread | deviation / spread |
| --- | --- | ---: | ---: |
| **`kOmegaSST`** | -25.114 %, -24.749 %, -24.847 % | **0.365 pts** | **68.0x** |
| `LaunderSharmaKE` | +4.971 %, +5.503 %, +4.887 % | 0.616 pts | 7.9x |
| `kEpsilon` | **+26.975 %, +29.915 %, +32.712 %** | **5.737 pts** | 5.7x |

### 3.1 `kOmegaSST`'s Nusselt error is model error, by a factor of 68

Across a 6.5-fold increase in cell count the value moves by **0.49 percent**,
against a deviation of **24.8 percent**. The sequence is formally oscillatory,
but the amplitude is negligible: **the solution is grid-independent in practice
even though no order can be extracted.**

**This is the most securely attributable statement the thermal lane owns.** The
tall cavity's `kOmegaSST` heat-transfer error is not a mesh artefact and no
refinement this lab can afford will remove it.

### 3.2 `kEpsilon` gets monotonically WORSE with refinement

**+26.975 -> +29.915 -> +32.712 percent.** Every refinement moves it further
from the experiment, and the observed order of **0.106** says the sequence is
barely responding to refinement at all.

**Refinement is not converging this model toward anything**, so its error cannot
be argued away as under-resolution — and the direction says the coarse mesh was
flattering it. **`K0cX` graded the fine mesh; the finest mesh is worse still.**

### 3.3 `LaunderSharmaKE`'s Nusselt row STRADDLES its band, and the graded mesh is the one it fails

| Mesh | `Nu_avg` | deviation | band 5.41 % | verdict |
| --- | ---: | ---: | --- | --- |
| coarse | 7.946 | **+4.971 %** | inside | **PASS** |
| **fine (the graded mesh)** | 7.987 | **+5.503 %** | outside | **GATE FAIL** |
| finest | 7.940 | **+4.887 %** | inside | **PASS** |

**The row passes on two of three meshes and `K0cX` graded the third.** The
mesh-to-mesh wobble is 0.616 deviation points on a band edge at 5.41 %, so the
row's verdict is **not robust to mesh choice**.

**No model verdict moves.** `LaunderSharmaKE` failed 7 of 14 graded rows; with
hi/R10 read on the finest mesh it fails 6 of 14 and is **still GATE FAIL**,
because R2 and R4 fail on both rungs and R1 fails on the hi rung. **What is
withdrawn is the row, not the verdict**, and the rung's own §2.5 rule — grade the
fine mesh of a registered pair — was followed correctly. **The defect is that a
two-mesh rule cannot see a straddle that only three meshes reveal.**

---

## 4. Stratification: two of three models move AWAY from the experiment under refinement

| Model | `S` coarse -> fine -> finest | reference 0.095 | state |
| --- | --- | ---: | --- |
| `kOmegaSST` | 0.2427 -> 0.2353 -> 0.2311 | all outside 0.05 | converging toward **0.2365**, still 2.8x the band away |
| `kEpsilon` | 0.0198 -> 0.0183 -> 0.0166 | all outside | **DIVERGENT**, p = -0.380 |
| `LaunderSharmaKE` | 0.0203 -> 0.0186 -> 0.0168 | all outside | **DIVERGENT**, p = -0.168 |

**`kOmegaSST`'s stratification is the one quantity in this rung with a clean
observed order, and Richardson extrapolation puts its converged value at 0.2365
— against a measured 0.095.** Refining to infinity does not reach the
experiment; it reaches a number 2.8 band-widths away.

**`K0cX_RESULTS.md` §3 recorded that refinement moved stratification away from
the experiment for the two `k`-`epsilon` models at hi Ra. This measures it: the
sequence is formally divergent for both.**

---

## 5. What this changes and what it does not

- **No verdict in `K0cX` moves.** Every model still GATE FAILs.
- **One row is shown to be mesh-fragile** (§3.3) and is recorded as such.
- **`kOmegaSST`'s 24.8 % heat-transfer deficit is established as model error**,
  which no rung in this campaign had established before.
- **`kEpsilon`'s error is established as not-numerical** in the stronger sense
  that it grows under refinement.
- **It does not say what the model error IS.** That is the closure work in D424,
  D425, D426 and D427.

**Owed, and named rather than performed:** the lo-Ra rung has **two** levels
only, so none of this can be done there; and the **square cavity has two levels
only**, so `K0cS`'s 17-20 % `kEpsilon` deviation and 13-14 % `kOmegaSST`
deviation have **no discretisation bound at all**. A third square-cavity mesh is
the cheapest way to give the campaign's most-cited rung the attribution this one
now has.
