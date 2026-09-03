# PRE-REGISTRATION — DIGITIZER re-file R2 (POSITION per §29.3; VALUE separately registered)

> **FROZEN 2026-09-03 by `ansys-verification-supervisor`. Grading path pinned:**
> R2 instrument `digitize_calibrate_r2.py` blob
> **`c1d275a29ad67504b22a9d6b15e16e06a5675f86`**; it imports the frozen R1
> instrument blob `2092c55d…` (verified intact at freeze time, rule 6).
> **§3 check 1 (measurement-script diff) DONE PERSONALLY** — I read all 282 lines
> as the diff (the file imports the frozen module read-only and contains only the
> changed code): §29.3's `term_A = max` for POSITION is taken over the same plate
> set the null control is drawn from (plate 0 is in `perr`), so `u_read ≥` the
> null-control plate's own error **structurally** — the null passes by
> construction, not by luck; the RMS-admissibility refuse (`max < pixel_floor`
> else exit 2) enforces L-461 in code, not a comment; per-quantity grading catches
> each `SystemExit2` for that quantity only, so a POSITION failure cannot drag
> VALUE (separation is real); the sub-pixel locator keeps `term_A = max`, so it
> cannot substitute for the statistic; no code path opens a real plate.
> **§3 check 4 (pre-registration committed before compute) is this commit.**
> `--selftest` re-run by me: **ALL PASS** — SELFTEST 2 shows the exact null that
> refused in R1 (offset 0.0032424) now passing at `u_read = MAX = 0.0032424`.
> **One note for whoever takes the verdict:** the `--calibrate` process exit code
> aggregates (exit 2 if EITHER quantity is `NOT A RESULT`); the **per-quantity
> verdicts in the JSON report are authoritative**, not the exit code — read the
> report, not just `$?`. **`--calibrate` on R2 is now authorised; nothing else is**
> — §25.7 / §28.8 remain unmet, no VMFL case gates on a digitized reference.

**DRAFT by `ansys-lane-opus48`. Frozen by the supervisor per the block above.** The
supervisor read the changed measurement code as a DIFF personally
(`SUPERVISION_CHARTER` §3) and did check 4 (committed before compute); only then
may `--calibrate` run.

- **Task:** re-file the digitized-reference instrument's POSITION quantity so its
  planted null passes **by construction**, per `ANSYS_VERIFICATION_CHARTER` v1.24
  **§29** (esp. §29.3, §29.4), on top of §25/§28.
- **This is a NEW registration.** It **cites** the §25/§28 task's verdict —
  **`NOT A RESULT`** (POSITION PLANT-NULL refused), taken and reproduced by the
  supervisor, `cases/ansys_verification/DIGITIZER/RESULTS.md`, committed
  **`caa6b096`**; charter §29 **`d95af6be`**; lesson **L-461** **`236f982e`** — and
  **does not re-grade it. That `NOT A RESULT` is permanent (§29.4).**
- **Instrument:** `cases/ansys_verification/DIGITIZER/R2/digitize_calibrate_r2.py`.
  It **imports the frozen instrument read-only** (blob
  `2092c55dd59d36c490b5fc3681bfd36c30d5b49b`, freeze `0fab170f`) and **never edits
  it** (rule 6). The R2 file **is the diff**: it contains only the changed
  measurement code, so the reviewer sees exactly what §29 alters.
- **Prediction-first (rule 2):** thresholds below are fixed a-priori from §29.3 and
  pixel geometry. `--selftest` was run during the build (allowed; no committed
  `u_read`); its diagnostic numbers are disclosed in §7. Committed per-quantity
  `u_read` comes only from `--calibrate`, post-freeze.

---

## 1. What changed, and only what changed (§29.3)

§25.4 term A — "the synthetic-control statistic" — was an **RMS**. An RMS
understates a tailed distribution; the POSITION steepest-descent locator's error
**has a tail** (mean 0.843 px, max 1.693 px on 24 clean plates), so a floor-dominated
`u_read` of 1.000 px claimed a precision the reader did not have, and the planted
null refused it (L-461, §29.2).

> **§29.3 change (the required fix):** for any quantity whose per-plate error CAN
> exceed the pixel floor, **term A is a statistic that DOMINATES the worst
> demonstrated per-plate error** — for POSITION, the **MAXIMUM** over the calibration
> set (the 95th percentile is computed and reported beside it). Because that max is
> taken over the same plate set the null control is drawn from, **`u_read` ≥ every
> clean-plate error the calibration measured, the null-control plate included — so
> the planted null passes BY CONSTRUCTION.** The instrument asserts this and refuses
> if it is ever violated.
>
> **RMS stays admissible only where the max per-plate error is below the pixel
> floor** (the floor then binds and dominates the tail). That is where VALUE sits.
> The R2 instrument **enforces this with a refuse**, not a comment: an RMS requested
> for a quantity whose max exceeds the floor is a `refuse()` (exit 2).

This is §28.2's discipline continued: §28.2 fixed *which units* term A is in; §29.3
fixes *which statistic*, so `u_read` is a number the reader can actually back.

## 2. Two SEPARATE registrations (§29.4 constraint a)

VALUE and POSITION are registered **separately**, each graded to its **own** verdict
on its **own** frozen bytes. **VALUE is NOT certified by inheriting from the failed
task**, and a `NOT A RESULT` on one quantity does not drag the other down — each
quantity's plant refusal is caught for that quantity only (`_grade_quantity`). This
is rule 1's vocabulary discipline applied to an instrument: a `NOT A RESULT` is not
softened by carving out its clean limb; VALUE stands here on its own calibration.

| registration | quantity | units | term A statistic (§29.3) | pixel floor |
|---|---|---|---|---|
| **R2-VALUE** | value-at-a-station (x=0.517) | y-data | **RMS** (admissible: max < floor, enforced) | 0.0050505 |
| **R2-POSITION** | x-location of a feature (steepest descent) | x-data | **MAX** (95th %ile reported beside) | 0.0027778 |

## 3. Synthetic-plate parameters (frozen; answer-blind format, §28.6)

Identical to the frozen instrument's representative answer-blind format (§2 of the
parent `PREREGISTRATION.md`): 150 DPI, 900×675 px, plot box 720×495 px, x∈[0,2]
linear orient-right, y∈[0,2.5] linear orient-up, blue curve 2 px, gridlines/frame/
ticks as there, one shared family of **24** `nozzle_curve` plates (varied feature
x∈[0.9,1.3] and shape), value station 0.517, log negative control, seed 20260903.
**§28.6 stands: `u_read` is per-target-format, re-derived per case; there is no
lab-wide `u_read`, and R2's representative values do not transfer to any case by
assertion.** The POSITION `u_read` in particular scales with the rendered feature
width, which is part of each target's answer-blind format.

## 4. The plants (§25.3, §28.2, §28.4, §29.3), per quantity

- **PLANT-DETECT**, per quantity: control displaced by **3·u_read in the quantity's
  own dimension** (VALUE y-offset; POSITION feature x-displacement) must read back
  **> u_read**; else REFUSE (blind).
- **PLANT-NULL**, per quantity: undisplaced control **|offset| ≤ u_read**; else
  REFUSE. **For POSITION this now passes by construction** (§29.3): `u_read` = max ≥
  the null-control plate's own error.
- **AXIS PLANT (shared, §28.4):** held-out tick ≤ 1.5 px; orientation declared +
  slope-sign check; **planted-flip** and **log-as-linear** negatives must REFUSE. A
  shared-axis negative failing makes **both** registrations `NOT A RESULT` (axis is
  shared infrastructure).

## 5. `u_read` derivation, per quantity (§25.4, §28.2, §29.3)

`u_read = max(` term A (§29.3: MAX for POSITION, admissible RMS for VALUE), ½·(two
independent read-off spread), pixel floor `)`, **all in the quantity's own units**.
The two-read-off perturbation ranges and their defences are **unchanged from the
frozen instrument** (parent `PREREGISTRATION.md` §5.1, §28.3): colour radius
[0.28,0.42]×√3, drop-one-interior-tick, feature window [1,3] px — pre-registered and
defended; narrowing after a target value is known voids the calibration; wider used
if disputed.

### 5.1 Predicted `u_read` (a-priori, prediction-first)

- **R2-POSITION:** I predict `u_read ≈ the max per-plate error ≈ 1.693 px = 0.004703
  x-data** (1.693 × 0.0027778), i.e. **~1.7× the pixel floor**, term A (max) binding
  over the floor and the half-spread. This is the honest consequence of §29.3: the
  re-filed `u_read` is **larger** than the floor-dominated 0.00278 that refused, and
  that is the point — it is a number the locator can back. **The planted null will
  pass by construction.** With the optional sub-pixel locator (§6) the max shrinks
  modestly (~1.05 px in the 8-plate selftest) but stays above the floor, so max still
  binds.
- **R2-VALUE:** I predict `u_read ≈ pixel floor = 0.0050505 y-data` (max value error
  ~0.001 y-data ≪ floor, so RMS admissible and the floor binds). VALUE verdict
  predicted **PASS**.

### 5.2 §29.5 consequence, stated so no report reads it as a delay

A POSITION `u_read` of ~1.7 px (vs the 1 px floor) means §25.6's **`u_read ≥ tol/3`
cap binds on MORE of the 45 figure-only cases** than the floor-based estimate
assumed. **Fig .46.2 (VMFL046-R2's target) is a POSITION read** — the exact quantity
this re-file governs — so its digitized-shock-location gate is the more likely to be
**capped at `GATE REACHED`** once `u_read` is re-derived on that plate's answer-blind
format. This is the honest cost of reading a position off a picture (§29.5), not a
regression.

## 6. Sub-pixel parabolic locator — OPTIONAL, not the fix (§29.4 constraint b)

`PositionQuantityParabolic` (parabolic fit to the 3 points around the gradient
minimum) is available via `--sublocator`. **It is not the fix and does not replace
§29.3:** term A stays the **MAX** even with it, so a sharper locator can never hide a
tail behind an RMS (L-461). If used, its own max error still dominates `u_read`
(selftest 6 confirms `u_read ≥ max` with the sub-pixel locator). **Default is OFF**;
the required change is the statistic, not the locator.

## 7. Acceptance criteria — per-quantity verdicts (fixed vocabulary)

Each registration is graded independently (§29.4a):

| outcome | condition (per quantity) |
|---|---|
| **`NOT A RESULT`** | any plant `refuse()`s for that quantity (PLANT-DETECT blind; PLANT-NULL false-positive; §29.3 admissibility violated) **or** a shared-axis negative not caught. |
| **`GATE FAIL`** | plants fire but PLANT-DETECT magnitude off by > 1·u_read, or \|bias\| > u_read. Valid, not certified. |
| **`PASS`** | plants fire, PLANT-DETECT magnitude within 1·u_read, \|bias\| ≤ u_read, axis negatives caught. Quantity certified; its `u_read` established. |

**Predicted task outcome:** R2-VALUE **PASS**, R2-POSITION **PASS** (the null now
passes by construction and detection/band are met at the selftest scale). If
`--calibrate` surprises this — a POSITION `GATE FAIL` on the detect band, say — that
is stated plainly, not smoothed (the §29.2 discipline).

## 8. Cost (rule 12; §26.2; §27.3; §28.7) — costed, capped, reconciled

- **Filed estimate 0.1 core-min. Cap 0.3 core-min** (~3× per §26.2/§28.7).
- **Basis / §27.3 reconciliation (filing-time inputs only, re-priced against the R2
  configuration):** R2's `--calibrate` op budget is **identical to the frozen
  instrument's** — one shared 24-plate family + per-quantity plants + 2 axis
  negatives = **32 renders + 34 digitizes** (the per-quantity split reuses the same
  digitizes; `--sublocator` adds no renders). At the measured render 0.1087 s /
  digitize 0.0088 s: `32×0.1087 + 34×0.0088 = 3.78 s = **0.0629 core-min**` per-op
  method. **The frozen R1 run's measured actual was 0.1128 core-min** — the ~0.05
  core-min gap is Python + numpy/PIL import **startup** (a fixed ~1.5 s), not per-op
  misprediction; **filing 0.1 predicts the ACTUAL (with startup) well**, while the
  per-op method (0.063) is the compute component. Filed 0.1 is 1.59× the per-op
  method, disclosed (§27.3), and ≈ the R1 measured actual — the safe direction.
  **R2 runs to completion (no early refuse expected), so unlike R1's partial 0.1128
  this is a full-calibration estimate** — a small upward nudge vs R1's partial actual
  is expected and still far under the 0.3 cap.
- **Dollars (derived):** cap 0.3 core-min = 0.005 core-h × $0.0513 = **$0.000257**.
- **Estimate-vs-actual (rule 12):** at completion, actual `--calibrate` wall × 1 core
  vs 0.1, ratio + attribution → `docs/COST_CALIBRATION.md`.

## 9. Disclosed selftest diagnostics (build step; NOT committed u_read)

`--selftest` ALL PASS. On 8-plate fixtures: POSITION rms 0.00251 / p95 0.00321 /
**MAX 0.00324** vs floor 0.00278 (max > floor → **RMS inadmissible, refused**);
POSITION **max-statistic → u_read 0.00324 ≥ MAX → null passes by construction**
(null_off 0.00324 ≤ u_read); VALUE MAX 0.00102 < floor → RMS admissible, **VALUE
PASS** u_read 0.00505; **separation** confirmed (POSITION-as-RMS `NOT A RESULT` while
VALUE `PASS`, independent); sub-pixel locator MAX 0.00293 with `u_read ≥ MAX` (max
still binds). These are diagnostics, not the committed `--calibrate --n 24` numbers,
and set no threshold above.

---

### Freeze checklist (supervisor)

1. Read `R2/digitize_calibrate_r2.py` as a DIFF personally — it is the changed
   measurement code (imports the frozen module read-only; rule 6 intact).
2. Verify the imported frozen blob is still `2092c55d…` at freeze time.
3. Hash `digitize_calibrate_r2.py`; record its blob sha here (grading path fixed).
4. Commit this file + the R2 instrument via the rule-10 private-index protocol
   (explicit paths only; never `git add -A`). Confirm §3 check 4.
5. Only then: `python3 cases/ansys_verification/DIGITIZER/R2/digitize_calibrate_r2.py
   --calibrate --n 24` (optionally `--sublocator`); grade R2-VALUE and R2-POSITION
   to their separate verdicts (§7); record both `u_read` values and the
   estimate-vs-actual cost row. Cap 0.3 core-min; an overrun stops the run.
6. §25.7 / §28.8 remain unmet until a per-case registration freezes prediction,
   `u_read` (re-derived on that plate's answer-blind format), band arithmetic and
   plate hash — no VMFL case gates on a digitized reference on the strength of this
   re-file alone.
