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

---

## 6. Dated addendum (2026-08-24): the §4 Richardson extrapolate has an inverted sign

**Appended at the foot. Lines whose number changed above this section: 0** —
verified by byte-comparing everything above against
`git show HEAD:docs/campaigns/F14-cooling-ladder/K0cX_GRID_CONVERGENCE.md`.
**No verdict moves. Every model still `GATE FAIL`, as §5 states.**

`verification/runs/F14-cooling-ladder/K0cX_runs/grid_convergence.py:106` forms
`e21 = f2 - f1` with `f1` the **finest** level, then writes
`richardson_extrapolate = f1 + e21/den`. Roache / Celik et al. (2008) for that
convention give `f1 - e21/den`, so the printed limit is reflected through the
finest value onto the coarse side. `GCI_finest_pct` uses `|e21|` and the
observed order `p` is sign-independent: **both are unaffected.**

Same defect class as `T3_runs/analyse_t3.py:384` and `T1_runs/analyse_t1c.py:337`
(verification audit pass 9, `CROSS_TEAM_GATE_AUDIT.md` §66/§72) and
`K0cG_runs/analyse_k0cg.py:107`, **independently written** — not shared code.
It is **not** present in the three `K0b` instruments, which use the correct
`f_fine + (f_fine - f_med)/(r^p - 1)` (`K0b_D406_repair/analyse_k0b_mesh.py:319`);
K0b's published extrapolate 4.52001514525647 stands.

**§4's one affected number**, `kOmegaSST` stratification `S`
(`grid_convergence.json`, `/quantities/SST/S`; finest 0.23105658418258596,
`p` = 1.2234):

| | value | distance from the measured 0.095, in 0.05 band-widths |
| --- | ---: | ---: |
| **printed at :95 and :100** | 0.23651325856424776 | 2.83 |
| **corrected** | **0.22559990980092415** | **2.61** |

**The reading survives; the number does not.** §4's statement — *"Refining to
infinity does not reach the experiment; it reaches a number 2.8 band-widths
away"* — should read **2.6 band-widths** at **0.2256**. The corrected limit
still lies far outside the band and still lies on the far side of the
experiment, so §5's conclusion that `kOmegaSST`'s deficit is model error is
untouched. The `kEpsilon` and `LaunderSharmaKE` rows are **DIVERGENT** and carry
no extrapolate at all.

**No K0cX record other than this one quotes the value**, and
`grid_convergence.py` grades nothing through it: the in-band tests use the
finest-level deviation against the reference, never the extrapolate. Status:
**PUBLISHED DISPLAY-ONLY**. The frozen instrument is **not edited**; this
disclosure is the amendment.
