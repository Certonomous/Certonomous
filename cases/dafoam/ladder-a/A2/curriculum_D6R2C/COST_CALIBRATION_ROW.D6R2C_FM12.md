# COST CALIBRATION ROW — `D6R2C` arm `FM12` (CLAUDE.md rule 12)

**Item:** `D6R2C-FM12` — the comparison at matched lift, with the extrusion proved instead of assumed.
**Registration:** `PREREGISTRATION_FM12_MATCHED_LIFT_PROVENANCE.md`, frozen at `3bd92d92b`.
**Label:** **`BLOCKED`** at the `Zo` sub-arm's deform phase, cause class **`PRODUCER`**
(`DAFOAM_CHARTER.md` §22.3), recorded in that registration's ADDENDUM 1.

| | core-min | $ (**DERIVED**, not measured) |
|---|---|---|
| predicted | **222.853** | 0.1905 |
| cap (×3.00) | **668.559** | 0.5716 |
| **actual** | **17.933** | **0.0153** |
| **ratio actual / predicted** | **0.080470** | |

**Cap NOT crossed.**

**Actual provenance:** `D6R2C_FM12_ROW … rc=1 wall_s=269 core_min=17.933` in
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM12-a2-wing-matched-lift-provenance/ledger.txt`, read by
`d6r2c_fm13_prefreeze.sh` rather than retyped. **Gross**, not cleaned; no row exceeded 3600 wall s, so
there is no stall to separate.

**Dollars are DERIVED at the owner-stated $0.0513/core-h and are NOT MEASURED** — the box cannot read its
own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

---

## ATTRIBUTION

**The gap is the `Zo` refusal, NOT misprediction.** `Zo` carried **2400.3 s** of the **3342.8 s**
prediction — **72 %** of the whole figure — and never reached a solve, so its terms were never exercised
in either direction. They are carried into `FM13` **unchanged and labelled UNTESTED**. The **204.920
core-min** not spent is **not waste** (`COMPUTE_BUDGET_CHARTER.md` §6): it is compute the arm correctly
declined to start once its input was corrupt, and it is named here rather than absorbed into the ratio.

## NAMED SEPARATELY — GENUINE CALIBRATION INFORMATION, NOT FOLDED INTO THE RATIO ABOVE

`Zb`'s registered term was **676.8 s** (574.5 s DEC7 `STATE B` trim + 88.2 s mesh/deform/stage + 14.1 s
model load) and it ran in **163.413 s** — **4.14× faster**. **Cause, measured:** the trim closed in **2**
evaluations where DEC7 `STATE B` needed **6**, because `Zb` starts from `x0` on a mesh generated at zero
shape.

**Acted on:** `FM13` re-anchors `ZB_TRIM_WALL_S` from **574.5 s → 61.113 s** (163.413 minus the same 88.2
and 14.1 terms the formula already carries), which moves the registered prediction **222.853 → 188.628
core-min**, a **15.4 %** reduction that is **entirely** this one term — asserted, not narrated, in
`d6r2c_fm13_prefreeze.sh`. The 574.5 s DEC7 anchor is **named as known-too-large for this state**, never
quietly dropped.

**SUBMISSIONS PARKED (rule 7).**
