# K0cG results: the square cavity's most-cited rung finally has a discretisation bound, and it is decisive

Campaign F14, gate K0c. Written 2026-08-19, after both cases reported.
Run tree `verification/runs/F14-cooling-ladder/K0cG_runs/`.
Pre-registration `3b454b37`, comparator `9ccfece3`, both committed before any
case produced a result.

**This rung GRADES NOTHING and no K0cS verdict moved.** It reports whether the
square cavity's solutions are in the asymptotic range, which is the precondition
for reading K0cS's deviations as model error.

---

## 1. The gap this closes

D428 established that **the square cavity had two mesh levels only**, so K0cS's
`kOmegaSST` −13.4 % and `kEpsilon` +17.1 / +20.5 % hot-wall Nusselt deviations
**could not be separated into model error and discretisation error at all.**
K0cQ, K0cR and K0cP all measure against K0cS baselines, so that unbounded error
sat underneath every one of those comparisons.

**The third level is now on disk: 307×307 = 94 249 cells, first cell
9.7656e-05 m, continuing the same 1.6 ladder.**

---

## 2. `kOmegaSST` — every quantity converges, and the error is the MODEL by factors of 43 to 722

| quantity | finest | reference | \|deviation\| | GCI (absolute) | **deviation ÷ GCI** | `p` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `Nu_hot` | 55.091 | 63.45 | 8.359 | 0.0992 | **84×** | 2.088 |
| `Nu_cold` | 54.885 | 63.95 | 9.065 | 0.0388 | **233×** | 3.121 |
| `Sp` | 0.76597 | 0.481 | 0.2850 | 0.00255 | **112×** | 4.078 |
| `Vpeak` | 0.25541 | 0.2127 | 0.04271 | 5.91e-05 | **722×** | 3.698 |
| `uv_peak` | 4.830e-04 | 1.080e-03 | 5.970e-04 | 1.387e-05 | **43×** | 1.516 |

**All five are CONVERGING.** The observed orders span 1.5 to 4.1 — three exceed
the formal second order, which is not a virtue and is noted rather than claimed:
an order above the scheme's formal accuracy usually means the coarsest level is
outside the asymptotic range, so **the GCI on those rows should be read as
indicative rather than exact.** It does not change the conclusion, because the
ratios are two to three orders of magnitude.

**`kOmegaSST`'s square-cavity deviations are MODEL ERROR.** Refining the mesh
cannot account for a gap 43 to 722 times the discretisation uncertainty.

---

## 3. `kEpsilon` — nothing converges, and the Nusselt error gets monotonically WORSE

| quantity | state | observed `p` |
| --- | --- | ---: |
| `Nu_hot` | **STAGNANT** | 0.150 |
| `Nu_cold` | **STAGNANT** | 0.239 |
| `Sp` | **DIVERGENT** | −0.786 |
| `Vpeak` | **DIVERGENT** | −1.015 |
| `uv_peak` | **DIVERGENT** | −0.102 |

**No band can be armed for any of them, so no attribution ratio exists.** The
hot-wall Nusselt deviation across the three levels:

**+17.146 % → +20.548 % → +23.719 %**

**Monotonically worse under refinement.** There is no asymptotic limit to
extrapolate to, so **`kEpsilon`'s square-cavity error cannot be bounded at all** —
not "is large", but **unbounded**, in the specific sense that the sequence gives
no value for the mesh-independent answer.

---

## 4. This reproduces D428 on a second geometry

D428 found exactly this split on the **tall** cavity: `kOmegaSST` converging,
`kEpsilon` getting monotonically worse. **The square cavity is a different
geometry, a different Rayleigh number and a different aspect ratio, and it
behaves the same way.** A single-geometry finding has become a two-geometry one.

**What that does NOT license:** it is two geometries of the same flow class —
both are buoyancy-driven cavities. §5 of `THERMAL_CAPABILITY_STATE.md` still
stands: every thermal error this lab has measured on a cavity is confounded by
the momentum and thermal fields being wrong together.

---

## 5. Convergence, and a distinction that had to be made carefully

**Neither case tripped `residualControl`** — consistent with **L-141**, which
established that criterion is unsatisfiable in these cases.

**By the registered criterion for this rung family** — peak-to-peak of the
hot-wall flux over a 400-iteration window — **both cases PASS comfortably**:
`Nu` spans of **0.0024 %** and **0.013 %** against a 0.5 % limit.

**A stricter field-difference test disagreed, and chasing it down mattered.**
The temperature field's local maximum still moved **0.170 K** (SST) and
**0.060 K** (kEpsilon) between iterations 38000 and 40000. **That movement is
interior, not near the wall:** it sits **152 mm and 161 mm** from the nearest
vertical heated wall — about 20 % of the cavity width — while within 5 mm of a
heated wall the movement is only **0.016 K** and **0.033 K**.

**So the graded quantity is stable and the residual drift is slow large-scale
motion in the core**, which is characteristic of a high-Rayleigh buoyant cavity
and is exactly why the registered criterion is placed on the wall flux rather
than on the field. **The stricter test was not ignored; it was located.**

---

## 6. What this rung cannot see

- **the lo-Ra question** — this is the hi-Ra square cavity only;
- **`LaunderSharmaKE`**, which K0cS REFUSED for missing its convergence
  criterion, so it has no two-level baseline for a third level to extend;
- **whether a fourth level would restore monotone behaviour for `kEpsilon`** —
  three levels can report that no asymptotic range has been reached, and cannot
  report that none exists.
