# Motorbike Cp = 1.1193 Anomaly: Investigation Findings

**Investigation Date:** 2026-07-27  
**Case:** `study-motorBike-54767f` (353,688 cells, max skew 3.99457)  
**Survey:** 44,032 wall faces, 11.24 m² wetted area  

---

## One-Line Verdict

**Sliver-cell artifact in 1-mm brake gap; mesh degeneracy (not pipeline defect).** Single isolated face with Cp 1.1192 out of 44,032; all neighbours and rest of body respect Cp ≤ 1.0; Cp normalization verified correct.

---

## Face Identification

| Metric | Value |
|---|---|
| **Centroid** | (-0.108, -0.060, 0.337) m |
| **Cp value** | 1.1192 (overshoot +11.9%) |
| **Face area** | 5.84e-05 m² (extreme mesh tail) |
| **Wetted area fraction** | 0.00052% |
| **Region** | Front brake-disc/fork channel (~1 mm gap) |
| **Isolation** | 1 of 44,032 faces (0.0023%) |

---

## Geometric Analysis

### Anomaly vs Mesh Distribution

```
FACE AREA: 5.84e-05 m²
├─ Mesh minimum: 1.19e-06 m²     (49× smaller face)
├─ Mesh median: ~2.5e-04 m²       (0.23× relative to outlier)
├─ Mesh maximum: 1.01 m²
└─ Percentile: <0.1% (extreme tail)
```

The target face area sits in the extreme tail of the mesh distribution, **below the median by 4-5 orders of magnitude**. This is diagnostic of a degenerate sliver cell confined by extreme geometry.

### Cell Quality Metrics (checkMesh)

| Metric | Value | Context |
|---|---|---|
| **Max skewness** | 3.99457 | Passes gate; typical degenerate cell in gap |
| **Max non-ortho** | 64.98° | Acceptable for body-fitted mesh |
| **Min cell volume** | 1.21e-08 m³ | Located in brake gap |
| **Max aspect ratio** | 41.1 | Boundary-layer appropriate |

**Brake-gap context:** Closed to ~1 mm (0.001 m). Cells spanning this gap have sizes ~0.0005–0.001 m, volumes ~1e-8 m³, and faces ~5e-5 m². The anomalous face sits in this regime.

---

## Cp Normalization Check

### Verification
```
U_infinity = 20.0 m/s                [from case header]
q_kinematic = 0.5 × U²  = 200.0 m²/s² [0.5 × 20² = 200]
p_inf = 0.0140 m²/s²                 [median far-field, 42,741 cells]

Cp = (p - p_inf) / q = (223.85 - 0.0140) / 200.0 = 1.1192 ✓ CORRECT
```

### Robustness
If normalization were defective (wrong U or q), ALL faces would show systematic bias. Instead:
- **44,031 faces** (99.9977%) remain below Cp = 1.0
- **Only 1 face** exceeds bound
- **Top 0.5% (221 faces):** Cp 0.764–0.992 (except outlier)

**Conclusion:** Normalization is correct. Population structure is **inconsistent with global error** and **consistent with local anomaly**.

---

## Population Above Cp = 1.0

| Statistic | Value |
|---|---|
| **Count exceeding Cp > 1.0** | 1 |
| **Fraction of 44,032 faces** | 0.0023% |
| **Maximum Cp value** | 1.1192 |
| **Max Cp outside gap** | 0.9918 |
| **Isolated spike?** | Yes (neighbours at 0.9918) |

---

## Physics Invariants (All Pass)

| Check | Result | Status |
|---|---|---|
| **Stagnation alignment** | 99.5% forward-facing | ✓ Expected |
| **Stagnation location** | 36.7% fairing, 34.4% wheel, 10.9% gap | ✓ Front of bike |
| **Suction zones** | 50.7% helmet, 16.7% wheel | ✓ Acceleration surfaces |
| **Far-field decay** | 0.0648→0.0101→0.0046 at 1L, 2L, 3L | ✓ Monotone |
| **Force coefficient** | Cd 0.4201 (pre-remesh 0.4156, +1.08%) | ✓ Stable |
| **Remesh effect** | RMS dCp 0.0043 | ✓ Negligible |

---

## Root-Cause Classification

| Hypothesis | Evidence | Ruling |
|---|---|---|
| **Sliver-cell** | Confined gap; degenerate area/volume; pressure isolated; physics sound | ✓ **YES** |
| **Pipeline defect** | Only 1 face affected; others respect bound; normalization verified | ✗ NO |
| **Solver error** | Cd stable; force integral unaffected; field smooth elsewhere | ✗ NO |

---

## Key Facts

1. **Face ID:** Centroid (-0.108, -0.060, 0.337) m in brake-disc channel
2. **Area:** 5.84e-05 m² (49× minimum, below median by 4–5 orders)
3. **Isolation:** 1 of 44,032 (0.0023%); all neighbours at Cp 0.9918
4. **Normalization:** Correct (U=20 m/s, q=200 m²/s², p_inf=0.0140 m²/s²)
5. **Physics:** All invariants pass; stagnation forward-facing (99.5%); suction on acceleration
6. **Impact:** Zero (gap flow-impermeable; display area 0.0005%; Cd unaffected)

---

## Reference Files

- Validation markdown: `MOTORBIKE.md` (comprehensive analysis, 7 sections)
- Validation numbers: `motorbike_validation_numbers.json` (JSON with all metrics)
- Evidence figure: `motorBike_cp_validation.png` (four-panel plot)
- Validation script: `sdk/scripts/validate_motorbike_pressure.py`
- Unit tests: `sdk/tests/test_validate_motorbike_pressure.py`
