# `D7-DEF-4` CONFIRMED BY MEASUREMENT. The pinned witness reads `29.16`. The prediction was registered before the artifact existed.

**Date:** 2026-08-25. **Lane:** dafoam `lab-lane`. **Artifact:**
`/home/ubuntu/certonomous-runs/CURRICULUM-D7R-a3-m6-cdmin/D7R_DEF4_WITNESS.txt`, `rc=0`.

## 1. The prediction, and where it was frozen

Registered at `5551db3d` in `../curriculum_D7/D7_DEF4_SCALER_BLOCKER.md` §3 and carried unchanged
into this item's `PREREGISTRATION.md` §6 — **both committed before any `OptView.hst` existed
anywhere on this box:**

> When arm `O` produces an `OptView.hst`, `d7_extract_endpoint.py` will read `patchV[0]` as
> **`291.6 × 0.1 = 29.16`**, not `291.6`.
> **Reads `29.16` → CONFIRMED. Reads `291.6` → REFUTED, recorded as plainly as the finding.**

`patchV[0]` is **pinned**: `d7_opt_runScript.py:241` registers `lower=[U0, 0.0]`,
`upper=[U0, 10.0]`, so `lower[0] == upper[0] == U0 == 291.6`. **Its physical value is
definitionally 291.6 and no optimiser can move it at any iteration.** That is what makes it an
unforgeable witness and what makes the prediction unfittable.

## 2. MEASURED

```
D7R_DEF4_WITNESS patchV[0]=29.16  U0=291.6  predicted_if_defect=29.16
D7R_DEF4_VERDICT CONFIRMED -- the extractor reads the DRIVER-SCALED value
```

Read value: **`29.160000000000004`**. Predicted: **`29.16`**. `291.6 × 0.1 = 29.16` exactly.

**A SECOND, INDEPENDENT CONFIRMATION IN THE SAME VECTOR.** `patchV[1]` is the angle of attack,
`aoa0 = 3.06°`, same scaler `0.1`:

```
patchV  scale=False[0:2] : [29.160000000000004, 0.30600000000000005]
```

**`0.306 = 3.06 × 0.1`.** Both components of `patchV` are scaled by exactly the registered `0.1`.
**The prediction named one component; the artifact confirms two.**

## 3. THE MECHANISM IS NOW MEASURED ON THIS BOX, NOT CITED

This lane's blocker note §8 stated plainly: *"this lane has NOT independently measured that
`getValues(scale=True) == getValues(scale=False)` on this box"* — it was **cited** from the
supervisor's D4 ruling. **That gap is now closed by measurement:**

| DV | `scale=True` == `scale=False`? |
|---|---|
| `patchV` | **True** |
| `twist` | **True** |
| `shape` | **True** |

**pyOptSparse's own scale is `1.0` for every design variable, so the `scale=False` argument in
`d7_extract_endpoint.py:40` is INERT — it cannot do what the instrument was written believing it
does.** OpenMDAO applied the scalers before pyOptSparse ever saw the problem, and `OptView.hst`
holds driver-scaled values with **nothing anywhere converting them back** (`grep -c scaler` is
**0** in both read-path instruments).

**What does NOT discriminate, stated so no one over-reads the table:** `twist` and `shape` both
read `0.0` at this early iteration, and **zero times any scaler is still zero.** They are
consistent with the defect and prove nothing about it. **The entire discriminating power is in
`patchV`, which is exactly why a pinned variable was chosen as the witness** — it is the one
component whose correct value is known independently of the optimiser's progress.

## 4. Consequence

* **`F-S` and `F-P` remain `BLOCKED`.** Any endpoint FD table built through this extractor would be
  measured at a design point that is not the optimum — `shape`'s scaler is **10.0**, the value that
  killed D4 arm F.
* **The §2d.1 bar is now met.** The supervisor declined to authorise a D7 repair on the ground that
  *"condition (1) requires a demonstrable error, not a predicted one"*, and was right to. **It is
  now demonstrable**, on the same evidence class that authorised D4's: a pinned variable returning
  exactly `pinned × scaler` to all digits.
* **This item does NOT author a repair.** Per the ruling, **D7 inherits D4's** — two instruments
  would mean two chances to reintroduce a units error that is invisible to every count-, plant- and
  order-based control. **D4's Limit 1 carries: not frozen until one primal at the corrected point
  reproduces the optimiser's own objective.**
* **Nothing downstream of the extractor is believed** until that repair lands and is verified.

## 5. What this does NOT impugn

**Arm `O`'s optimisation is not affected.** A `scaler` is a legitimate optimiser-conditioning
choice and OpenMDAO applies it correctly inside the driver; `OptView.hst` is a faithful record of
the run **in driver-scaled units**. The defect is entirely in the **read-back** path. `O` continues.

## 6. Honest scope

* The witness ran in a **separate np=1 probe container** on core 6, which is inside arm `O`'s
  registered cpuset `2,3,4,6`. **It therefore contended briefly with `O` on one of four cores.**
  Disclosed rather than omitted; the probe is seconds of work and `O` is a multi-hour arm, but the
  contention was real and is not claimed to be zero.
* The `OptView.hst` read was a **copy taken at 540,672 bytes while `O` was still writing**, at
  IPOPT iteration 2. **`patchV[0]` is pinned at every iteration, so a partial history cannot
  change the witness** — but the `twist`/`shape` rows are early-iteration values and are reported
  as non-discriminating for that reason.
