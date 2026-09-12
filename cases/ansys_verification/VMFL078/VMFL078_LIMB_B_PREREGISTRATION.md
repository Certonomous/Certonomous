# VMFL078 — LIMB B PRE-REGISTRATION: agreement with the manual

**Version 1.0 — 2026-09-12 — ansys-verification / ansys-lane-opus**
**Status at writing: NOT YET COMMITTED. Nothing is graded before the commit of this file.**

---

## 0. Why this document exists, and the one thing a reader must weigh

VMFL078 (3-D lid-driven cubic cavity, Re = 1000) graded **`GATE REACHED`** on
2026-09-12 at 05:32Z under the frozen comparator
`cases/ansys_verification/VMFL078/grade_vmfl078.py`, blob
`c749c87d0f465a829a8485556b0c358c55125850`. That verdict covered **limb A only** —
our own $r = 2$ grid-convergence property. **Limb A, its numbers and its verdict are
not touched, not re-graded and not altered by this document.**

**Limb B — agreement with the manual — graded `BLOCKED`, for a reason internal to
the manual: VM2026R1 prints no scalar whatsoever for VMFL078.** Its entire published
result is *Figure .78.2* (printed p. 224 / PDF p. 238), a plot. No per-case digitizer
registration had ever been filed in this lab, so there was nothing to compare to.
This document files one.

### 0.1 The disclosure that governs how much this freeze is worth

**The solver runs for VMFL078 were already complete when this pre-registration was
written.** Under rule 2 a gate frozen after its compute is worth nothing, because the
gate can be chosen to fit the answer. That objection is real and is not waved away
here. What is claimed instead is narrower and checkable:

1. **The compute this document freezes is the DIGITISATION, not the solve.** The
   digitisation had not been performed when the band was specified; the band is a
   property of a bitmap, and the bitmap is an artifact of ANSYS, Inc., not of this lab.
2. **Every number in the band is traceable to the figure alone.** Section 4 derives
   each term of the uncertainty budget from pixel measurements and from two *exact*
   physical data printed in the figure itself. No solver output appears anywhere in
   the derivation. A reader can re-run `figure_78_2/digitize_fig782.py` against the
   committed bitmap and reproduce the band without access to any run directory.
3. **No run output was read before this commit.** The author's declared and auditable
   discipline for this item was: digitise → quantify → write → **commit** → only then
   open the run tree. Specifically, `GRADE_VMFL078.json`, `GRADING_VMFL078.log`,
   every `postProcessing/` output and every field/time directory under
   `verification/runs/ansys_verification/VMFL078/` were left unopened until this
   file was committed. This is a declaration, not a proof; it is recorded so it can
   be contradicted.
4. **The band is conservative, and measurably so** (§4.5). It was not tuned toward
   any value; it is wider than the digitisation's own demonstrated accuracy.

A reader who rejects (3) should read limb B as **a registered comparison of our
solution against the manual's printed reference, with a stated uncertainty**, and
discount the word "pre-registration" accordingly. That is the honest floor, and it is
still worth having: before today there was no band at all.

---

## 1. Source, verified

| | |
|---|---|
| Document | **Ansys Fluid Dynamics Verification Manual** |
| Release | **2026 R1, March 2026** |
| Publisher | ANSYS, Inc. (part of Synopsys), Southpointe, 2600 Ansys Drive, Canonsburg, PA 15317 |
| Verification | **title page read from the PDF** (page 1) and the copyright page (page 2), per rule 15 — not by filename, not by hash, not by manifest |
| File | `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.pdf` |
| Case | **VMFL078: Polyhedral Mesh Accuracy**, printed pp. 223–224 = PDF pp. 237–238 |

### 1.1 What the manual itself cites as the reference

Verbatim from the Overview table, printed p. 223:

> **Reference** — *Parallel Simulation of 3D Lid-driven Cubic Cavity Flows by Finite
> Element Method*, **Jifei Wang and Decheng Wan**. Proceedings of the Twenty-first
> (2011) International Offshore and Polar Engineering Conference, Maui, Hawaii, USA,
> June 19-24, 2011.

**This is Wang & Wan (2011), not Ku/Hirsh/Taylor and not Albensoeder/Kuhlmann.** The
lab's expectation going in was one of the latter two; the manual says otherwise and
the manual is what governs. The series digitised below is the one the figure labels
**"Referance"** *(the manual's spelling)*, i.e. Wang & Wan's FEM data.

### 1.2 What Figure .78.2 actually plots

Caption, verbatim: **"Comparison of X-Velocity along the vertical centerline in the
symmetry plane"**.

* **Abscissa** — *"Position (m)"*, 0.0 → 1.0. The caption fixes this as position
  **along the vertical centerline**, i.e. the height $y$: 0 at the stationary floor,
  1 at the moving lid. Confirmed internally — the curve reaches 1.0 m/s exactly at
  Position 1.0, which is the lid speed, and 0 at Position 0, which is no-slip.
* **Ordinate** — *"X Velocity [m/s]"*, −0.4 → 1.0. Lid speed is 1 m/s, so the plotted
  value **is already** $u_x/U_\mathrm{lid}$; no renormalisation is applied.
* **The line in space** — the vertical centerline of the symmetry plane is
  $x = 0.5$, $z = 0.5$ (the cube's mid-span), $y$ running 0 → 1. The case's
  `centrelineProbe` already samples exactly this line at 201 frozen abscissae
  $y = 0.005 + k\cdot 0.00495$; **no new sampling is introduced by limb B.**
* **Series** — black line + markers *"Ansys Fluent"* (the manual's own solution);
  red round markers *"Referance"* (Wang & Wan).
* **Geometry cross-check** (printed p. 223): half domain, height 1 m, length 1 m,
  breadth 0.5 m with a symmetry boundary → a **unit cube**, matching this case's
  `blockMeshDict` ($z \in [0, 0.5]$, `symmetryPlane` at $z = 0.5$).
  Density 1 kg/m³, viscosity 0.001 kg/m·s, lid 1 m/s → Re = 1000. Laminar, steady.

---

## 2. The digitisation method

**The figure is an embedded raster, not vector art.** `pdfimages -list` on PDF page
238 reports one image, object 2923: **720 × 448 px, RGB, 8 bpc, 96 ppi**. That bitmap
is the information ceiling — re-rendering the PDF at 600 dpi manufactures interpolated
pixels, not data — so the digitiser reads **the native bitmap**, extracted losslessly
with `pdfimages -png`.

**Axis calibration — the anchors, stated as required.** Tick-mark pixel positions were
located as short strokes immediately outside the axis lines (x-axis line at row 358,
y-axis line at columns 215–216), then fitted by least squares:

| | anchor low | anchor high | scale | tick residual (rms) |
|---|---|---|---|---|
| **x** | 0.0 m at **column 215.5** | 1.0 m at **column 647.5** | 432.091 px/m | **0.132 px** over 11 ticks |
| **y** | −0.4 m/s at **row 358.0** | +1.0 m/s at **row 44.5** | 223.988 px per m/s | **0.139 px** over 8 ticks |

**Curve extraction.** Red pixels ($R>110$, $R-G>45$, $R-B>45$) with the legend
swatch masked out. At each plot column the reference series occupies a contiguous run
of rows; its midpoint is taken as the curve and its height as the band. The round
markers **overlap and merge** through the dense part of the figure (one connected
component of 1953 px alongside 14 isolated ~26 px discs), so individual marker centres
**cannot** be resolved there — which is exactly why the uniform-band model of §4.2 is
used rather than a marker-centroid model. The black *Ansys Fluent* series is extracted
the same way and is reported, not gated on.

Digitiser: `cases/ansys_verification/VMFL078/figure_78_2/digitize_fig782.py`
(blob `fc3130c261f140dad5596b5574438064f496200c`)
Bitmap: `figure_78_2/fig_78_2_native_720x448.png` (blob `1c097d555c398fbd92dde8420a86b588889c7e13`)
Output: `figure_78_2/fig_78_2_digitised.json`, 433 columns (blob `fc01abbdf9a8702ec275c76466b65b5fdf3b42c2`)

---

## 3. What precision the figure actually supports

**It does not support three digits.** The reference markers are discs roughly **6 px
across**; the extracted band is 5–12 px tall (median 7 px). At 223.988 px per m/s, one
marker is **0.027 m/s** tall. Any claim to read this figure to ±0.001 m/s would be a
fabrication. The honest statement is: **the figure supports roughly two decimal places
in $u_x$, i.e. ±0.015–0.03 m/s at 95 % coverage**, and that is what is registered.

---

## 4. The uncertainty budget — and how the band follows from it

Each term is a measurement on the bitmap. **None involves any solver output.**

| term | what it is | magnitude |
|---|---|---|
| $u_\mathrm{cal}$ | axis calibration: rms tick residual ÷ scale | 6.2e-4 m/s (y); 3.1e-4 m (x) |
| $u_\mathrm{band}$ | **§4.2** marker/line band, uniform model: (half run height)/√3, floored at 0.5 px/√3 | 5–12 px → **0.0065–0.0155 m/s** |
| $u_\mathrm{thr}$ | colour-threshold sensitivity: half-spread of the value re-extracted at red thresholds 95 / 110 / 130 | ≤ 1 px |
| $u_\mathrm{slope}$ | **§4.3** abscissa error projected through the local slope, $\lvert du/dy\rvert \cdot u_x$, with $u_x = 0.002771$ m | negligible mid-cavity; **dominant in the lid layer** |

$$ U_{95} = 2\sqrt{u_\mathrm{cal}^2 + u_\mathrm{band}^2 + u_\mathrm{thr}^2 + (\lvert du/dy\rvert\, u_x)^2} $$

### 4.2 Why the band model, not a centroid model
A centroid of an isolated disc would be sub-pixel accurate, but through the dense part
of the curve the discs merge into one blob and no individual centre is recoverable.
Treating the run of coloured rows as a **uniform interval** containing the true curve
is the model that is honest *everywhere in the figure* rather than only where the
markers happen to be isolated.

### 4.3 Why the abscissa term exists and why the gate stops at y = 0.90
The markers are discrete, so a sampled column may hold no red pixel and the reader
takes the nearest marker within ±2 columns. That abscissa error projects through the
slope. Mid-cavity $\lvert du/dy\rvert \approx 0.3$–1.5 and the term is ~0.001–0.004 m/s.
**Inside the lid boundary layer $\lvert du/dy\rvert \approx 13$ and the term reaches
0.035 m/s** — the figure simply cannot be read there. **The gate window is therefore
$0.05 \le y \le 0.90$, fixed here, for a reason that is a property of the figure and
of nothing else.** Values outside the window are reported, never gated.

### 4.5 Two exact data in the figure validate the calibration
The figure contains two values known *a priori* and exactly: the floor is no-slip
($u = 0$ at Position 0) and the lid moves at 1 m/s ($u = 1$ at Position 1).

| datum | true | digitised | error | registered $U_{95}$ there |
|---|---|---|---|---|
| floor, no-slip | 0.000000 | **+0.001435** | 1.4e-3 m/s | 0.0202 |
| lid speed | 1.000000 | **+1.001488** | 1.5e-3 m/s | 0.0521 |

**The method recovers a known datum to ~1.5e-3 m/s — about 0.33 px — while the
registered band is ~1.6e-2 m/s.** The band is therefore **conservative by roughly an
order of magnitude** at the two points where it can be checked. It is registered at
the conservative value anyway, because the uniform-band model of §4.2 is the one that
is defensible in the merged region too. **This is disclosed so that a PASS is read as
"inside a deliberately generous reading of the figure", and a GATE FAIL is read as
"outside even that".**

---

## 5. THE FROZEN GATE

**Comparison metric.** $\Delta(y) = u_x^\mathrm{ours}(y) - u_x^\mathrm{ref,dig}(y)$,
in m/s, at the sampling locations of §5.1.

**Graded level: `L3`, the finest of the $r=2$ family (128 × 128 × 64).** The
Richardson extrapolate is **deliberately not used**: it would import limb A's fitted
order $p$ into limb B and the two limbs would stop being independent. L1 and L2 are
reported for trend, never gated.

**Solution reader.** The **frozen limb-A reader**, `grade_vmfl078.py` blob
`c749c87d0f465a829a8485556b0c358c55125850`, imported — not copied, not re-implemented.
The comparator refuses if that blob hashes differently. `grade_vmfl078.py` is **not
edited** (rule 6).

### 5.1 Sampling locations and the band — frozen as literal numbers

The 18 locations are the frozen probe abscissae nearest $y = 0.05, 0.10, \ldots, 0.90$.
$u_\mathrm{ref}$ and $U_{95}$ are the digitised series linearly interpolated to them.

| # | probe idx | $y$ (m) | $u_\mathrm{ref}$ (m/s) | $U_{95}$ (m/s) |
|---|---|---|---|---|
| 1 | 9 | 0.04955 | −0.219074 | 0.026956 |
| 2 | 19 | 0.09905 | −0.268669 | 0.015580 |
| 3 | 29 | 0.14855 | −0.247146 | 0.017144 |
| 4 | 39 | 0.19805 | −0.201566 | 0.021337 |
| 5 | 49 | 0.24755 | −0.151656 | 0.020292 |
| 6 | 60 | 0.30200 | −0.105835 | 0.018298 |
| 7 | 70 | 0.35150 | −0.072230 | 0.015797 |
| 8 | 80 | 0.40100 | −0.049907 | 0.015731 |
| 9 | 90 | 0.45050 | −0.031800 | 0.015849 |
| 10 | 100 | 0.50000 | −0.014191 | 0.015675 |
| 11 | 110 | 0.54950 | −0.000797 | 0.015691 |
| 12 | 120 | 0.59900 | +0.017061 | 0.015696 |
| 13 | 130 | 0.64850 | +0.029707 | 0.016547 |
| 14 | 140 | 0.69800 | +0.048313 | 0.015585 |
| 15 | 151 | 0.75245 | +0.070635 | 0.015744 |
| 16 | 161 | 0.80195 | +0.095123 | 0.018303 |
| 17 | 171 | 0.85145 | +0.124209 | 0.015896 |
| 18 | 181 | 0.90095 | +0.163260 | 0.021784 |

Machine copy: `figure_78_2/limbB_band_table.json` (blob `0fbe690025b11d23ca53106cf69385e2961b3e51`). The same
numbers are duplicated as literals inside the comparator, which refuses if the two
disagree — the gate survives the loss of either file.

### 5.2 The three gates

* **B1 — curve agreement (aggregate).**
  $\mathrm{RMS}_{18}(\Delta) \le U_{\mathrm{RMS}95} = \mathbf{0.017917}$ m/s,
  the RMS of the 18 $U_{95}$ above.
* **B2 — pointwise envelope.** At least **16 of 18** points satisfy
  $\lvert\Delta_i\rvert \le U_{95,i}$. *Why 16:* $U_{95}$ is a $k = 2$
  coverage interval, so ≈ 5 % of points are expected outside even under perfect
  agreement; on 18 points that is ≈ 0.9 points, and tolerating **2** is the threshold
  consistent with the stated coverage. This follows from the uncertainty model, not
  from any measured value.
* **B3 — the extremum.** Over the frozen window $y \in [0.05, 0.20]$:
  $\lvert u_\mathrm{min}^\mathrm{ours} - (\mathbf{-0.2687})\rvert \le \mathbf{0.0156}$ m/s
  **and** $\lvert y_\mathrm{min}^\mathrm{ours} - \mathbf{0.0985}\rvert \le \mathbf{0.0336}$ m.
  The $y$ tolerance is **half the span over which the digitised curve stays within
  $U_{95}$ of its own minimum** (0.0730–0.1401 m) — a flat curve read from pixels
  cannot locate its extremum better than that.

**All three are verdict-bearing.** None is a "diagnostic only" number: a printed
discrepancy annotated non-binding is worse than one never computed.

### 5.3 Label vocabulary and the combination rule

Rule 1 vocabulary only — **`PASS` / `GATE REACHED` / `GATE FAIL` /
`NOT A RESULT` / `BLOCKED` / `PENDING`**.

* **`PASS`** — B1 **and** B2 **and** B3 all hold.
* **`GATE FAIL`** — any of B1, B2, B3 fails. All three numbers are printed and the
  failing gate is named. **A GATE FAIL is reported as a GATE FAIL.** The band is not
  widened, the figure is not re-digitised to fit, and no adjective softens it.
* **`BLOCKED` / `NOT A RESULT`** — only via §5.4. The gate may turn a PASS or a
  GATE FAIL *into* `NOT A RESULT`, never the reverse (rule 5).
* Limb A's **`GATE REACHED`** is untouched by every outcome above.

### 5.4 Refusal conditions — the comparator refuses, it never degrades (exit 2)

1. `grade_vmfl078.py` does not hash to `c749c87d0f465a829a8485556b0c358c55125850`.
2. The band table file disagrees with the comparator's inline literals.
3. A frozen probe index does not sit at its registered abscissa (tol 1e-9).
4. The probe file is absent, has no data row, carries ≠ 201 vectors, or holds NaN/Inf
   — all enforced by the frozen reader.
5. `RUN_RC.L3` does not record `rc=0`.
6. **Planted-zero control fails** (rule 3): a $1.234\times10^{-3}$ m/s plant written
   into the **real bytes** of a **copy** of the probe file must be seen by the gate
   reader at that index at exactly its size (**P1a**), must not leak to any other index,
   and must move the limb-B RMS functional by a non-zero amount (**P1b**). The graded
   tree is never written to.

Grading path, fixed at this commit: `cases/ansys_verification/VMFL078/grade_vmfl078_limbB.py`
(blob `1b0cf8496a4208dd487de1205953b3c216a0fbe8`), invoked as
`grade_vmfl078_limbB.py verification/runs/ansys_verification/VMFL078`.

---

## 6. Cost

**No solver runs.** Limb B is post-processing: one serial pass over a 201-row probe
file plus one `copytree` of `postProcessing/`.

* **Pre-registered estimate: ≤ 2 core-minutes**, 1 rank. Basis: arithmetic on 201
  values; the only I/O is a few-kB file copy.
* At the recorded c7a.4xlarge rate of $0.0513/core-h this is **< $0.002, derived,
  not measured** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5).
* Under the $25 pre-authorisation, and under Sanaa's NO-CAP ruling of 2026-09-12.
* Estimate-versus-actual lands in `docs/COST_CALIBRATION.md` at completion (rule 12).

---

## 7. What this pre-registration does not claim

* It does **not** re-open, re-grade or alter limb A, its triple, its $p$, its GCI or
  its `GATE REACHED` verdict.
* It does **not** claim Wang & Wan (2011) is correct. It claims only that our L3
  solution does or does not sit inside a stated reading of what the manual printed.
* It does **not** claim the figure can be read better than §3 says it can.
* It does **not** convert agreement into validation of the physical model: the manual's
  own solution and its reference differ from each other by an rms of **0.0116 m/s**
  over the gate window (a figure-internal measurement, reported, not gated), which
  bounds how sharp any agreement claim from this figure can ever be.
