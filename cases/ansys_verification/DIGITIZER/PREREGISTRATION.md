# PRE-REGISTRATION — DIGITIZER instrument calibration (per-quantity u_read)

> **FROZEN 2026-09-03 by `ansys-verification-supervisor`. Grading path pinned:**
> instrument `digitize_calibrate.py` blob **`2092c55dd59d36c490b5fc3681bfd36c30d5b49b`**.
> **§3 check 1 (measurement-script diff) DONE PERSONALLY** — I read all 600 lines
> as the diff-against-nothing of a new file: the measurement logic is sound, the
> plants are per-quantity in the correct dimension (VALUE plants a y-offset,
> POSITION an x-displacement of the feature), the slope-sign check is an
> independent third assertion that breaks the fit/held-out agreement a flip would
> otherwise pass, `u_read` has no circular dependency on the plant, and **there is
> no code path that opens a real plate** (every image reaches `digitize()` from
> `render_plate`; `save_png` only writes). **§3 check 4 (pre-registration committed
> before compute) is this commit.** `--selftest` re-run by me: **ALL PASS**, the
> three negative controls (log-as-linear, planted-flip, tick-count) refusing.
> **One flagged weakness, not a blocker:** the two-read-off half-spread is ~1e-7
> on synthetic plates, so term **B never binds on synthetic data** and `u_read`
> rests on **A** (syn_rms) and **C** (pixel floor); B is re-derived larger per
> case on a real target plate (§28.6), where noise and AA make the two read-offs
> actually differ. **`--calibrate` is now authorised; nothing else is** — §25.7 /
> §28.8 remain unmet, no case gates on a digitized reference.

**DRAFT by `ansys-lane-opus48`. Frozen by the supervisor per the block above.** The
supervisor read the instrument as a DIFF personally (`SUPERVISION_CHARTER` §3 —
measurement-script diffs, and check 4, pre-registration committed before compute)
and committed; only then may `--calibrate` run.

- **Task:** build and calibrate the digitized-reference instrument, as its own
  pre-registered, costed task.
- **Specification:** `ANSYS_VERIFICATION_CHARTER` Amendment **v1.23 §28** (commit
  `496394cc` per the supervisor), which adopts as charter law the five holes this
  lane found in §25, read together with §25 (§25.1–§25.8) and the §18/§22.5/§16.4
  constructions they reuse, and the cost clauses **§26.2, §26.3, §27.3**. **Where
  §28 rules, §28 governs.** This revision is the instrument rebuilt to §28.
- **Authority:** Sanaa, 2026-09-03 (~16:00Z), verbatim
  (`etc/sessions/2026-09-03T1600Z_sanaa_five_rulings.md`): *"Digitization approved
  as its own instrumented task; digitized references carry stated read-off
  uncertainty, folded into the gate band."* Authorises **building and calibrating**
  the instrument; **no gate on any case** (§25.0, §25.7, §28.8).
- **Instrument:** `cases/ansys_verification/DIGITIZER/digitize_calibrate.py`
  (grading path; its committed blob sha is frozen with this file, rule 2).
- **This task's verdict** is its own, from the fixed vocabulary. **An instrument
  that fails its plants is a `NOT A RESULT` and unlocks nothing** (§25.7).
- **Prediction-first (rule 2):** every acceptance threshold below is fixed
  **a-priori** from pixel geometry and the §28/§25.4 logic — NOT from calibration
  output. `--selftest` was exercised during the build (the build & self-test step
  allowed pre-freeze); it produced **diagnostic** numbers only (no committed
  `u_read`), disclosed in §7. The **committed** per-quantity `u_read` values come
  only from `--calibrate`, post-freeze.

---

## 1. What the instrument is (§25.1, §28.2)

A digitized reference is a **measurement of a figure**, carrying `u_read`. The
instrument renders synthetic plates whose truth is known **by construction**
(numpy rasteriser + PIL — not matplotlib, whose transforms/AA would insert an
uncontrolled layer between truth and raster), digitizes them **without being handed
the transform** (it recovers axis calibration from rendered tick marks, given only
the tick data values, the log flags and the orientation declaration), and reports
the error distribution **per gated quantity, in that quantity's own units**.

**Two gated quantities are implemented (§28.2), the two this team needs first:**

| quantity | units | truth by construction | PLANT-DETECT displacement |
|---|---|---|---|
| **VALUE** (value-at-a-station) | y data-units | curve value at the frozen station `X_STATION` | a known **y-offset** of the curve |
| **POSITION** (x-location of a feature) | x data-units | the feature's known x (steepest-descent locator) | a known **x-DISPLACEMENT of the feature** (never a y-offset) |

**§28.2, the wrong-number path, closed:** a y-value `u_read` folded into an
x-location gate is dimensionally meaningless. **Every term of §25.4 is computed on
the gated quantity in its own units.** A value `u_read` never licenses a position
gate. Fig .46.2's quantity is **shock LOCATION** → the POSITION `u_read` (x-units)
is the one that would gate it.

## 2. Synthetic-plate generation parameters (frozen; answer-blind format only, §28.6)

A **representative** answer-blind format, deliberately NOT Fig .46.2's (§28.6):

| parameter | value |
|---|---|
| extraction DPI | **150** |
| raster | **900 × 675 px** (6.0 × 4.5 in); plot box inset 90 px → **720 × 495 px** |
| x axis | linear, **[0, 2]**, ticks {0, 0.4, 0.8, 1.2, 1.6, 2.0}, orient **right** |
| y axis | linear, **[0, 2.5]**, ticks {0, 0.5, 1.0, 1.5, 2.0, 2.5}, orient **up** |
| curve | blue (0.05, 0.10, 0.75), stroke 2.0 px, antialiased |
| gridlines / frame / ticks | gray 0.85 (1 px) / black (2 px) / black 8 px protruding outside |
| family | **24** nozzle-Mach-shock curves, `nozzle_curve`, with per-plate varied feature x∈[0.9,1.3] and shape (peak, lo, post, shock width) — one family serves BOTH quantities |
| value station | `X_STATION = 0.517` (a smooth pre-feature region, off a pixel-centre column) |
| log negative control | one x-log plate ([0.1, 100]) for the AXIS-PLANT log-as-linear arm |
| base seed | 20260903 (deterministic, reproducible) |

**§28.6 consequence, stated as a cost not a detail:** `u_read` is
**PER-TARGET-FORMAT and re-derived per case.** There is **no single lab-wide
`u_read`**, and this calibration does not transfer to any case by assertion. For
each case the synthetic plates are re-matched to that target's **answer-blind
format** (DPI, ranges, scale type, tick density, line width, marker style, gridline
density, aspect — all measurable without reading the plotted curve) and `u_read`
re-derived. `§25.7`'s authorisation is per case.

**Pixel floors (a-priori arithmetic, per quantity, §28.2):**
- VALUE (y-axis): 2.5 / 495 = **0.0050505 y-data-units**.
- POSITION (x-axis): 2.0 / 720 = **0.0027778 x-data-units**.

## 3. The calibration procedure (`--calibrate`)

One family of 24 plates, **each digitized once**, yields both a value error (at
`X_STATION`) and a position error (located feature vs its known x). Then, per
quantity: assemble the three `u_read` floors (§5), run the three plants (§4). Any
plant `refuse()` (exit 2) ⇒ **`NOT A RESULT`**, unlocking nothing. Finally the two
shared AXIS negative controls (log-as-linear, planted-flip) must refuse. Emit the
per-quantity report and the task verdict (§6).

## 4. The plants, per quantity, and what each MUST do (§25.3; §28.2; §28.4; rule 3; §16.4)

- **PLANT-DETECT (positive control), per quantity.** A control displaced by
  **Δ = 3·u_read IN THE QUANTITY'S OWN DIMENSION** (VALUE: a y-offset of the curve;
  POSITION: an x-displacement of the feature) **must** read back displaced:
  recovered **> u_read**. A blind reader (recovered ≤ u_read) **REFUSES**.
- **PLANT-NULL (negative control, §16.4), per quantity.** An undisplaced control
  **must** read back within u_read: **|offset| ≤ 1·u_read**. A reader reporting
  displacement on a clean control **REFUSES**.
- **AXIS PLANT (§28.4).** (a) fit on a **subset** of ticks, verify a **held-out
  tick**; > **1.5 px** REFUSES. (b) **orientation declared explicitly** in the
  inputs; a **SLOPE-SIGN check** asserts the fitted slope's sign matches the
  declaration. (c) a **PLANTED-FLIP** (pairing reversed vs the declaration) **must
  REFUSE** — the held-out check alone passes a flip (a reversed pairing is a
  self-consistent line; this bit the build, RMS ≈ 1.09 at ~zero bias, `L-436`'s
  class), and the slope-sign check is the independent third assertion that breaks
  that agreement. (d) a **log axis declared linear must REFUSE** (held-out error
  orders of magnitude over floor).
  **Honest scope of the flip guard (disclosed):** from tick positions alone a
  *physically* inverted-and-mislabeled plate is **not** detectable — orientation is
  genuinely an operator declaration, exactly like log. The slope-sign check catches
  a **pairing inconsistent with the declaration** (the implementation class that bit
  the build), not an operator who declares the wrong orientation. This is why
  orientation is a **declared, frozen input**, and the planted-flip arm proves the
  guard fires on the failure the held-out check passed.

Defence-in-depth refusals (all exit 2): tick-count ≠ label-count; < 3 ticks; < 10
curve columns; missing frame; < 7 points to locate a feature.

## 5. `u_read` derivation — three floors, PER QUANTITY, in the quantity's units (§25.4, §28.2, §28.3)

`u_read = max(` **A** synthetic-control statistic, **B** ½·(two-independent-read-off
spread), **C** pixel floor `)` — **all three in the gated quantity's own units.**

- **A — synthetic-control statistic:** quadrature-mean per-plate error over the 24
  plates, computed on the quantity (VALUE: y-error at `X_STATION`; POSITION:
  located-feature x-error). **§28.5:** for VALUE, both a **whole-curve** and a
  **steep-region** statistic are reported; a read in a locally steep region uses the
  steep-region one, and **which is used is frozen before the read, by where the read
  happens.** POSITION is inherently a steep-region read (a feature is where the
  curve is steep), so it uses the feature statistic directly.
- **C — pixel floor:** §2, exact arithmetic, per axis.
- **B — two independent read-offs of the (per-case) target plate, ½ their spread**
  (§25.4, §28.3). Reuses the §18/§22.5 construction: a measured reproduction spread
  is the empirical floor on a quantity's own uncertainty, uncontaminated only if
  measured before the comparison it feeds. **Procedure (real, not a placeholder):**
  the same plate is digitized **twice under independently perturbed, defensible
  operator choices**, neither run seeing the other's numbers; `B = ½·|q_A − q_B|`
  **computed on the quantity**.

### 5.1 Perturbation ranges — FROZEN AND DEFENDED (§28.3)

**§28.3, the loophole closed:** an automated reader can shrink its own uncertainty
by narrowing the perturbation range — that is §25.2's forbidden move through a
parameter. Therefore the ranges are **pre-registered here with a stated defence of
each span**, **a range narrowed after any target value is known voids the
calibration**, and **where a range is disputed the WIDER defensible one is used**
(`u_read` errs large by law; the `u_read ≥ tol/3` cap is the honest consequence).

| choice | range | defence of the span (why no narrower, and no wider) |
|---|---|---|
| curve-colour selection radius | **[0.28, 0.42]** × √3 | below 0.28 the antialiased curve edge falls outside the selection and the extracted line fragments (biases toward the core); above 0.42 the radius begins to reach gridline-gray / background-blended halos (blue→gray distance ≈ 0.62·√3). The span is the colour tolerance a competent operator could actually pick; not narrower (both edges are real operating limits), not wider (either edge degrades). |
| axis-fit tick subset | **drop any ONE interior tick** | an operator legitimately uses different tick subsets; dropping one interior tick spans that. Endpoint ticks are NOT droppable — dropping one shortens the fit lever arm, which a competent operator would not do — so this is the defensible span, not a narrowing. |
| feature-locator half-window | **[1, 3] px** | the latitude in local smoothing when locating a steep feature: 1 px ≈ raw steepest column, 3 px ≈ a 7-px centroid. Beyond 3 px the window spans a meaningful fraction of a sharp shock and biases the location, so 3 is the defensible upper edge; 1 the lower. |

**Predicted `u_read` (a-priori):** for both quantities I predict **A and B < C**,
so `u_read ≈ pixel floor` — VALUE ≈ **0.00505 y-data**, POSITION ≈ **0.00278
x-data** — because a sub-pixel extractor on a clean synthetic raster reads below the
one-pixel floor. Stated as a prediction to be checked against `--calibrate`.

## 6. Acceptance criteria — this task's own verdict (fixed vocabulary)

Frozen mapping (a-priori), applied to **each** quantity and the shared axis negatives:

| outcome | condition |
|---|---|
| **`NOT A RESULT`** | **any** plant `refuse()`s (exit 2): a PLANT-DETECT blind (recovered ≤ u_read) for either quantity; a PLANT-NULL false-positive (\|offset\| > u_read); an AXIS held-out > 1.5 px; the slope-sign/planted-flip control not caught; the log-as-linear control not caught. Instrument invalid; **unlocks nothing** (§25.7, §28.8). |
| **`GATE FAIL`** | instrument runs, all plants fire, but a quantitative acceptance is missed for either quantity: PLANT-DETECT recovers the displacement's presence but its magnitude off by > 1·u_read (\|recovered − 3·u_read\| > u_read), **or** the quadrature-mean per-plate bias > u_read. Valid instrument, **not certified**. |
| **`PASS`** | both quantities' plants fire **and** PLANT-DETECT magnitude within 1·u_read **and** bias ≤ u_read, **and** both axis negatives caught. Instrument **certified**; per-quantity `u_read` (representative-profile values + per-case method) established. |

**Rationale (§25.7 vs §25.6):** a *blind* instrument is `NOT A RESULT`; a *valid but
biased* instrument is `GATE FAIL`; mere *imprecision* (large but honest `u_read`) is
**neither** — it is reported and folded into per-case bands (§25.6), and a large
`u_read` is a `PASS` for the instrument that simply caps the cases it serves. **A
`PASS` here certifies the reader; it gates no VMFL case.**

## 7. Cost (rule 12; §26.2; §27.3; §28.7) — costed, capped, and reconciled

- **Filed estimate:** **0.1 core-minutes.** **Cap: 0.3 core-minutes** — **~3× the
  estimate per §26.2 / §28.7** (Sanaa's cap discipline). An overrun stops the run
  (rule 12); a cap-hit here forfeits ~4 s and a re-file (§28.7 notes this tight cap
  is safe *here* precisely because the loss is trivial, and does not generalise).
- **Basis:** measured on this box, single core, warm: **render 0.1087 s**,
  **digitize 0.0088 s** per plate. No GPU, no MPI. Reported-by-owner timing, not
  billed (`COMPUTE_BUDGET_CHARTER` §5).
- **§27.3 / §26.3 freeze-time reconciliation — inputs available at filing only, and
  RE-PRICED against the current (two-quantity) configuration:** the revised
  `--calibrate` op budget is **32 renders + 34 digitizes** (24-plate shared family +
  value plants 3r/4d + position plants 3r/4d + 2 axis negatives 2r/2d):
  `32 × 0.1087 + 34 × 0.0088 = 3.78 s = **0.0629 core-min**`.
  - This equals the charter's pair-count basis (`0.117 s × ~32 ÷ 60 = 0.0624`) to
    within rounding, **confirming the two-quantity structure did not inflate the
    op count** — the shared family is what holds it at ~32 (render dominates;
    digitize is cheap).
  - **Filed 0.1 is 1.59× above its own method (0.0629); the margin is DISCLOSED,
    not silently absorbed** (§27.3). It is in the safe direction and small; the cap
    (0.3) still bounds it.
- **Dollars (derived, not measured):** cap 0.3 core-min = 0.005 core-h ×
  $0.0513/core-h = **$0.00026**. Trivially under the $25 pre-auth; still costed.
- **Estimate-vs-actual (rule 12):** at completion, actual core-min from the
  `--calibrate` wall clock × 1 core is compared to 0.1, ratio + attribution in
  `docs/COST_CALIBRATION.md`.
- **Disclosed selftest diagnostics (build step, not the calibration):** sub-pixel
  reads — VALUE err ~1e-4 y-data at `X_STATION` (whole-curve RMS ~0.0016 ≈ 0.3 px,
  bias −0.28 px·frac); POSITION feature located to ~0.0028 x-data (~1 px);
  held-out axis err ~0 px; log-as-linear and planted-flip both refused;
  PLANT-DETECT recovering 3·u_read for both quantities. **Not committed u_read**,
  **not used to set any threshold** — disclosed so the prediction-first claim is
  auditable.

## 8. §28 status — the five holes are now charter law, and how this build meets each

The five holes this lane raised against §25 are adopted as §28 (v1.23). This
instrument implements all five; recorded here so the diff and the spec line up.

- **§28.2 (wrong-number path):** per-quantity `u_read` in own units; VALUE + POSITION
  implemented; POSITION plants an x-displacement of the feature. **Met.**
- **§28.3 (self-shrinking loophole):** perturbation ranges frozen + defended (§5.1);
  narrowing after a target value is known voids the calibration; wider used if
  disputed. **Met.**
- **§28.4 (axis flip):** orientation declared + slope-sign check + planted-flip arm
  that refuses; honest scope disclosed (§4). **Met.**
- **§28.5 (steep vs whole):** both statistics reported; steep used where the read is
  steep; choice frozen by read location. **Met.**
- **§28.6 (answer-blind format):** synthetic plates matched to answer-blind format
  only; `u_read` per-target-format, re-derived per case; no lab-wide `u_read` (§2).
  **Met.**

**One residual honesty note for the supervisor's diff read (not a new hole, a scope
statement):** the POSITION `u_read` calibrated here is for a **tanh-smoothed shock**
of the synthetic family's width; a real plate's shock is rendered at the manual's
own line width and sharpness, which is part of the **answer-blind format** and so is
re-matched per case (§28.6). The steepest-descent locator's uncertainty scales with
the rendered feature width, so the POSITION `u_read` must be re-derived on
plates matched to the target's feature rendering — it does not transfer from this
representative profile. This is §28.6 applied to the feature, and it means the
number this task commits for POSITION is a **method + representative value**, not
Fig .46.2's `u_read`.

---

### Freeze checklist (supervisor)

1. Read `digitize_calibrate.py` as a DIFF personally (§3 measurement-script check).
2. Hash the script; record its blob sha here (grading path fixed at freeze, rule 2).
3. Commit this file + the instrument via the rule-10 private-index protocol
   (explicit paths only; never `git add -A`).
4. Record the freeze sha; confirm §3 check 4.
5. Only then: run `--calibrate`; grade against §6; record the task verdict, both
   committed `u_read` values, and the estimate-vs-actual cost row.
6. §25.7 / §28.8 remain unmet until a per-case registration freezes prediction,
   `u_read`, band arithmetic and plate hash for that case — no case gates on a
   digitized reference on the strength of this task alone.
