# T5 — the digitisation uncertainty is now **MEASURED**, not estimated, and the control caught two defects that would have made every value wrong

**Written by a `lab-lane` under `heat-transfer-supervisor`, 2026-08-26. ZERO COMPUTE.**
**No pre-registration was written or frozen. No tier was interpreted.** Nothing has been
sent, filed, submitted, uploaded, registered or posted outside this box (rule 7).

Instrument: `verification/runs/T-family/T5_runs/digitise_t5.py`.

---

## 1. THE HEADLINE NUMBER

| | value |
|---|---|
| **digitisation error in `h`, MAX** | **`0.2263 W/m²K`** = **`0.2514 %` of the 0–90 axis span** |
| digitisation error in `h`, RMS | `0.1374 W/m²K` |
| digitisation error in `Re_H`, MAX | `7.07` = `0.1178 %` of the 0–6000 span |
| digitisation error in `Re_H`, RMS | `5.88` |
| points planted / recovered | **6 / 6** |

**Against the draft's estimate.** `T5_PREREGISTRATION_DRAFT.md` §7.3 estimated the
Fig. 5.45 digitisation increment at *"≈ 1.3 W/m²K on h ≈ 55–80 → ≈ 2 %"*, and said in
terms that those were *"estimates made from the figures' axis resolution before any point
was taken"*. **Measured, it is `0.226 W/m²K` — about `0.35 %` of a reading of `h ≈ 65`,
roughly 5.7× smaller than the estimate.** The estimate was conservative in the safe
direction, and it is now replaced by a measurement.

## 2. THE CHANNEL WAS MEASURED, NOT ASSUMED — which is the whole point of the control

A control figure generated as clean vector graphics would exercise a channel the real
artifact does not use. **That is this lab's single most repeated defect**: `blockMesh`
never reads `0/`; a launcher selftest passed with a fake solver on `PATH`; a mesh dry run
never touched `0.orig/`. **Every one exercised the channel its author was thinking about
rather than the channel that consumes the artifact.**

**So the channel was measured on the real page first** (`pdfimages -list`, PDF page 162 =
printed p. 160 = Fig. 5.45, confirmed by rendering the page and reading its caption):

| property | measured |
|---|---|
| embedded image | **1926 × 2816 px** |
| bits per component | **1 — BITONAL, not greyscale** |
| encoder | **CCITT Group 4** |
| resolution | **301 × 300 ppi** |
| distinct grey levels in the render | **3**; **99.988 %** of pixels exactly 0 or 255 |
| blank-margin standard deviation | **0.0** |

**And the degradations were measured on the same page:**

| degradation | measured value | how |
|---|---|---|
| **skew** | **`0.1006°`** | the densest axis line in the figure region drifts `0.001755 px/px` over 1698 px |
| **speckle** | **`4.40 %`** of components are ≤ 4 px | 2478 connected components; 33 are ≤ 1 px, 109 are ≤ 4 px |
| **ink spread** | strokes **4–12 px** | axis-line thickness at five stations, against ~2 px for a vector render |

**The control reproduces all four**: rendered at **300 dpi**, rotated by the measured
**0.1006°**, dilated by 1 px for ink spread, hard-thresholded to **1 bit** at 128,
speckled at the measured density with blob areas 1–4 px from a **fixed seed**, and
round-tripped through **CCITT G4** — the same encoder the thesis PDF uses. G4 is lossless;
**the lossy step is the 1-bit threshold, and that is the step the control had to
reproduce.** Round-trip confirmed: **2 distinct grey levels**, raster **1920 × 1260 px**.

## 3. THE CONTROL CAUGHT TWO DEFECTS, AND BOTH WOULD HAVE CORRUPTED EVERY VALUE

**This is what the control is for, and it earned its cost on the first run.**

### 3.1 A Y-AXIS SIGN INVERSION — every point reflected about the axis midpoint

Tick centres come back in **ascending pixel row** — top first. The anchor values are
registered in **ascending data order** — bottom first. Pairing them as given maps the top
tick to the smallest value and **reflects every extracted point.**

**Measured on the first control run:** planted `28.70` came back as **`61.37`**, and
`90 − 28.70 = 61.30`. **And the x axis, which is not inverted, recovered to `0.097 %` of
span in the same run** — so a control that checked only x, or that checked "did we get
six points", would have reported success on a digitiser that was wrong in y everywhere.

**Repaired with the reversal made explicit, plus a sign guard that refuses on a
non-negative y scale** — so the property is checkable rather than trusted.

### 3.2 AN UNDER-SIZED FRAME MARGIN — the axis lines counted as data

At `0.1006°` a straight axis line **drifts 3.4 px across a 1920 px raster**, so a 4 px
exclusion margin let the y-axis line (**area 3002 px**) and part of the x-axis line
(**536 px**) into the marker set. The control refused: **"8 markers recovered, 6
planted."**

**Repaired by DERIVING the margin from the measured skew** — `ceil(tan(skew) × max
dimension) + 4` — rather than choosing a number that happened to work.

### 3.3 And a third, in the control itself

Planting speckle as 4 × 4 blocks (area 16) instead of the measured area ≤ 4 put **17
false markers** through the filter: *"23 markers recovered, 6 planted."* **The control
caught a defect in the control**, which is the right order for that to happen in.

## 4. TWO UNCERTAINTIES, NAMED SEPARATELY AND NEVER MERGED

| source | value | provenance |
|---|---|---|
| **EXPERIMENTAL** | **~5 %** on local `h`, mid-region of the **five** faces; **~10 %** at edges | Meinders p. 59, **read from the rendered page image**, not from OCR. Both figures are **hedged in the source** — *"approximately"*, *"about"* — and are on the **local** `h` |
| **DIGITISATION** | **`0.2263 W/m²K` max, `0.1374` RMS** (`0.2514 %` of span) | **measured** by the planted raster control in §1, not estimated |

**They are reported as two numbers and are not combined here.** The combination rule
belongs to the pre-registration, which already reserves §7.3 for it. **An uncertainty
absorbed into another is an uncertainty nobody can audit later** — the same discipline as
waste-versus-contention in the cost ledger.

## 5. WHAT THE CONTROL DOES **NOT** BOUND — stated at full strength

**The `0.2514 %` is the error of an ISOLATED, WELL-SEPARATED marker.** The control plants
six circles that never touch. **The real Fig. 5.45 does not look like that.** Read from
the rendered page: at low `Re_H` the `+`, `×`, `△` and `□` series **overlap and touch** —
at `Re ≈ 600` and `Re ≈ 2500` several symbols merge into single ink blobs.

> **MARKER OVERLAP IS THE LARGEST UN-MODELLED ERROR SOURCE, AND IT IS UN-MODELLED
> BECAUSE MODELLING IT HONESTLY MEANS DECIDING WHAT A MERGED BLOB'S CENTROID MEANS —
> which is a design decision, not a measurement.**

Also un-modelled: paper texture and show-through, halftone screening of the original
print, and non-uniform platen illumination before thresholding.

**So `0.2514 %` is a FLOOR for the isolated-marker case, not the total for the real
figure**, and the pre-registration must say so where it states the band. **A number
whose limits are not stated beside it invites being read as the total.**

## 6. THE INSTRUMENT'S DISCIPLINE, since it is on the grading path

The digitiser **produces the reference**, so it is a measurement instrument and takes the
full standard:

- **zero `ast.Assert` nodes** — confirmed by `scripts/check_assert_guards.py
  --require-clean`; every refusal is `sys.exit(2)`;
- **five registered refusals**: anchor-count mismatch, non-uniform tick spacing, axis/tick
  non-coincidence, linear-fit residual over 2.0 px, and the planted-control tolerance;
- **selftest: 3 arms, 0 FAILED, rc 0 under BOTH `python3` and `python3 -O`** — and the
  negative arm **drives a mis-anchored figure under `-O` and requires rc 2**, so the
  refusal is shown to *fire*, not merely shown not to crash;
- **T3 is the precedent for what a digitiser is, not for how to guard one.**
  `digitise_t3_secondary.py:190,191` carry T3's axis calibration in two `assert`
  statements — Class A in this territory's `-O` inventory. **They are frozen and are NOT
  repaired here**; the 2026-08-25T22:48Z bound is forward-only. **The pattern is simply
  not reproduced.**

## 7. WHAT IS NOT DONE, AND WHY

**No pre-registration was written or frozen, and no comparator was written.**
`T5_PREREGISTRATION_DRAFT.md` carries **18 labelled INTERPRETATIONs**, and its own header
states that it *"freezes on Sanaa's reading or on the supervisor's promotion of this file
to `T5_PREREGISTRATION.md`, and not before."*

**Promotion is the supervisor's act, not a lane's**, and promoting the draft means
adopting all 18 INTERPRETATIONs — including INTERPRETATION 1, which the draft itself
flags as *"the one most likely to be argued with."* **A lane that froze that on its own
would be taking eighteen design decisions under cover of a build instruction.**

**What is ready for that promotion:** the digitiser exists, its channel is measured, its
error is measured, and §7.3's estimated increment can be replaced by the measured one at
the moment the file is promoted — **in the same commit, so the freeze binds the whole
grading path at once.**
