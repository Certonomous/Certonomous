# Ampofo Fig. 11 digitised: the square cavity's turbulent Prandtl number

Campaign F14, gate K0c. Written 2026-08-18. This is experiment **X7** of
`K0c_THERMAL_CLOSURE_SYNTHESIS.md` section 8, costed at **$0** and named as one
of the two zero-cost rows that *"should run first"*.

Data: `reference-data/ampofo_fig11/ampofo_fig11_digitised.dat`.

**Zero compute. Nothing was solved and no verdict moves.** This adds a reference
column that did not exist and bounds a claim the lab has been making without one.

---

## 1. What it settles

`K0cS_RESULTS.md` §9 filed the square cavity's turbulent Prandtl number as **NOT
OBTAINED**. The dated correction D415 established, from the paper's prose, that
Ampofo and Karayiannis p. 3569 report it as *"about unity"*, and recorded that
**the numerical distribution stayed NOT OBTAINED because Fig. 11 was not
digitised.** This digitises it.

---

## 2. Method, and the reading uncertainty carried with it

The figure was rendered from `docs/papers/buoyant_natural_convection/`
`ampofo_karayiannis_2003_ijhmt_46.pdf` page 19 at 300 dpi and read at the
plotted symbols.

`alpha_t/nu` and `nu_t/nu` are on the **left** axis, spanning -2 to 10.
`Prt` is on the **right** axis, spanning -1 to 2, so **`Prt = (left - 2) / 4`**,
fixed by the four coincident tick pairs (10/2, 6/1, 2/0, -2/-1).

**Reading uncertainty, carried per `LITERATURE_CHARTER.md` §2: +/- 0.15 on the
left axis and +/- 0.04 on `Prt`.**

### 2.1 The digitisation checks itself, and does so at four points

`Prt` is plotted **and** is by definition `nu_t / alpha_t`, both of which are
plotted beside it. The reading is therefore falsifiable against itself:

| X | `nu_t/nu` read | `alpha_t/nu` read | ratio | `Prt` read | agree? |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0.0067 | -0.05 | 2.40 | 0.00 | 0.00 | **yes** |
| 0.0095 | 1.50 | 5.15 | 0.291 | 0.30 | **yes**, to 0.01 |
| 0.0133 | 6.90 | 7.80 | 0.885 | 0.89 | **yes**, to 0.005 |
| 0.0333 | -0.10 | -0.10 | 1.00 | 1.02 | **yes**, within uncertainty |

**Where it cannot check itself, that is stated rather than hidden.** For
X > 0.015 the `alpha_t` and `nu_t` symbols and curves **overlap to within the
line width**, so the two cannot be read independently and their ratio cannot
confirm `Prt` there. In that region the plotted `Prt` curve is the primary
reading and the other two are not independent of it.

---

## 3. The measured distribution

| X = x/L | `alpha_t/nu` | `nu_t/nu` | `Prt` |
| ---: | ---: | ---: | ---: |
| 0.0000 | 0.00 | 0.00 | **0.21** |
| 0.0020 | 0.00 | 0.00 | 0.11 |
| 0.0037 | 0.90 | 0.00 | **0.01** |
| 0.0067 | 2.40 | -0.05 | **0.00** |
| 0.0095 | 5.15 | 1.50 | 0.30 |
| 0.0125 | **8.10 peak** | - | - |
| 0.0133 | 7.80 | **6.90 peak** | 0.89 |
| 0.0200 | -0.55 | -0.55 | 0.90 |
| 0.0225 | **-1.40 min** | **-1.40 min** | - |
| 0.0267 | -0.20 | -0.20 | 0.96 |
| 0.0333 | -0.10 | -0.10 | **1.02** |

Rows at X = 0.0125 and 0.0225 are extrema of the authors' own fitted curve
between symbols. **They are not data points** and are recorded because the sign
change is the finding.

---

## 4. Three readings, in increasing order of what they cost the lab

### 4.1 "About unity" is true, and it is true of a third of the profile

The paper's sentence is exact and this digitisation confirms it: over
X = 0.015-0.03, `Prt` reads **0.89 to 1.02**. The text says so and says where —
*"In the comparatively wide region (X = 0:015-0:03 of Fig. 11)"*.

**Outside that region it is not about unity.** From the wall to X = 0.0067,
`Prt` falls from **0.21 to 0.00**. Against the **0.85** that `K0cS` and `K0cT`
imposed as a constant, the measured inner-layer value is low by a factor of four
at the wall and is **zero** at X = 0.0067, where `nu_t` has not yet risen and
`alpha_t/nu` has already reached 2.40.

**This is the region that sets the wall heat flux**, which is the quantity the
gate grades.

### 4.2 The eddy diffusivity and the eddy viscosity are NEGATIVE over a fifth of the profile

Between about X = 0.018 and X = 0.030 **both** `alpha_t` and `nu_t` are below
zero, reaching about **-1.4** at X = 0.0225. That is counter-gradient
transport: heat and momentum moving up their own mean gradients.

**A linear eddy-viscosity model cannot represent this at all.** `nu_t = Cmu k^2 /
epsilon` with `Cmu > 0`, `k >= 0` is non-negative by construction, and every
model this ladder has run — `kOmegaSST`, `kEpsilon`, `LaunderSharmaKE` — is of
that form. The measurement is not merely a value those models get wrong; it is
**outside the range their functional form can produce**.

### 4.3 The sharpest reading, and it inverts how the "unity" sentence is usable

**The region where `Prt` is about unity is the region where both `alpha_t` and
`nu_t` are negative.** `Prt` is near 1 there **because it is a ratio of two
negative numbers of nearly equal size** — the two curves overlap to within the
line width, which is the same fact.

So the measured `Prt = 1` in the outer layer **cannot be quoted as support for
setting `Prt = 1` in a model whose `nu_t` is positive by construction.** Such a
model reproduces the ratio and gets the sign of both transports wrong. **The
agreement would be numerical and not physical**, and it would be reached for a
reason the measurement contradicts.

The paper's own text does not remark on the sign. It says the two profiles are
*"similar"*, which is true, and the similarity is what makes the ratio unity.

---

## 5. What this does to the record

- **`K0cS_RESULTS.md` §9's NOT OBTAINED is now fully answered.** D415 answered
  it with a sentence; this answers it with a distribution, and section 4.3 is a
  statement neither the sentence nor the value alone supports.
- **D415's bound on control C3 is strengthened, and its direction is unchanged.**
  C3 moved `Prt` from 0.85 to 1.28 for **1.75 %** on average Nusselt. Both of
  those values sit **above** the measured inner-layer `Prt` of 0.00-0.21, so C3
  swept a range that does not contain the measurement in the region that sets
  the wall flux. C3 remains a measurement of the integral's insensitivity to
  the **value**, and is not evidence about the **form**.
- **`K0cQ`'s reading gains a second geometry-independent constraint.** The tall
  cavity's measured `Prt` of 1.071 and 1.283 (Betts Table 1, centre-line) and
  the square cavity's 0.00-1.02 (near-wall profile) are **not the same quantity
  at the same place**, and nothing here licenses comparing them directly.
- **It arms no gate row.** No band is proposed and no verdict is claimed. A
  digitised figure carrying +/- 0.04 is a reference for comparison, and this
  document does not turn it into a gate.

---

## 6. What would falsify this document

Obtain the underlying tabulated data, or the authors' Eqs. (19)-(21) evaluated
on their published mean profiles, and exhibit an inner-layer `Prt` that is not
below 0.85, or an outer region in which `alpha_t` and `nu_t` are positive.
Either would overturn section 4, and section 4.3 with it.
