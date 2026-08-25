# `D7-DEF-4` — D7 CARRIES THE D4-DEF-4 UNITS DEFECT. The FD arms are BLOCKED. The optimisation arms are not.

**Date:** 2026-08-25. **Lane:** dafoam `lab-lane`, curriculum item D7.
**Verdict on the FD arms (`F-S`, `F-P`): `BLOCKED`.**
**Verdict on the optimisation arms (`P1`, `P2`, `O`): NOT blocked — see §4 for why the distinction is real and not a convenience.**

**Status when this was written: NO COMPUTE HAD OCCURRED.** This is a finding about frozen
instruments, read from the frozen instruments, before the first container.

## 1. What D4-DEF-4 is

Ruled by the dafoam-supervisor at `dbb88eb4`; lane evidence at `2ecf6ec9`; full text at
`cases/dafoam/ladder-a/A2/curriculum_D4/SUPERVISOR_D4DEF4_REPAIR_RULING.md`.

OpenMDAO applies a design variable's `scaler` **before** pyOptSparse sees the problem, so
pyOptSparse's own scale is `1.0` and `History.getValues(scale=True)` and `(scale=False)` return
**identical** values. `OptView.hst` therefore holds **driver-scaled** values, and an extractor's
`scale=False` argument is **inert** — it cannot do what the instrument was written believing it
does. Re-applying those values through `prob.set_val` then sets the **physical** value, so the
FD table is measured at a design point that is not the optimum. D4's `shape` scaler is `10.0`;
arm F set the wing to ten times its optimised deformation and the mesh died at 15 wall s.

## 2. D7 has it. Read from the frozen files.

`d7_opt_runScript.py:237-241` — **not one design-variable scaler is 1.0**:

| DV | registered | scaler |
|---|---|---|
| `twist` | `lower=-10.0, upper=10.0` | **`0.1`** |
| `shape` | `lower=-1.0, upper=1.0` | **`10.0`** — *the same value that killed D4 arm F* |
| `patchV` | `lower=[U0, 0.0], upper=[U0, 10.0]` | **`0.1`** |

Objective and all five constraints carry `scaler=1.0`; **only the design variables are scaled**,
which is exactly the D4 configuration.

`d7_extract_endpoint.py:40` — `values = h.getValues(major=True, scale=False)`. **The inert
argument.**

**And nothing anywhere converts back.** `grep -c scaler` over both read-path instruments returns
**0** for `d7_extract_endpoint.py` and **0** for `d7_fd_endpoint.py`. The FD producer re-applies
what the extractor handed it through `prob.set_val` at `d7_fd_endpoint.py:144, 221, 224, 253` —
the physical-value setter. **The chain is identical to D4's.**

## 3. THE PINNED WITNESS — a falsifiable prediction, registered BEFORE any compute exists

`d7_opt_runScript.py:241` registers `patchV` with `lower=[U0, 0.0]` and `upper=[U0, 10.0]`, and
`:232` initialises it at `[U0, aoa0]`. With `lower[0] == upper[0] == U0`, **`patchV[0]` is pinned:
its physical value is definitionally `U0` and no optimiser can move it.** `U0 = 291.6` m/s
(`d7_opt_runScript.py:62`).

**A pinned design variable is an unforgeable witness**, and it yields a prediction with no free
parameters:

> **PREDICTION, REGISTERED BEFORE THE FIRST CONTAINER.** When arm `O` produces an `OptView.hst`
> and `d7_extract_endpoint.py` reads it, the extracted `patchV[0]` will be
> **`291.6 × 0.1 = 29.16`**, not `291.6`.
>
> * **If it reads `29.16`** — `D7-DEF-4` is **CONFIRMED to all digits** and the FD arms stay
>   `BLOCKED` until the supervisor rules a repair.
> * **If it reads `291.6`** — D4's mechanism **does not carry to D7**, this note is **REFUTED by
>   its own test**, and that will be recorded as plainly as the finding.
>
> D4's own witness behaved exactly this way: `patchV[0]` pinned at `100.0`, scaler `0.1`,
> extractor returned `10.0` to all digits.

**This prediction is registered here rather than run now because no `OptView.hst` exists yet** —
no arm has run. It is a pre-registered falsification test, not a measurement, and is labelled so.

## 4. Why the optimisation arms are NOT blocked, stated as a distinction and not a convenience

A `scaler` is a **legitimate optimiser-conditioning choice**, and OpenMDAO applies it correctly
inside the driver. The optimisation `P1 → P2 → O` therefore solves the intended problem and its
`OptView.hst` is a faithful record of it **in driver-scaled units**. Nothing about D4-DEF-4 makes
the optimisation wrong.

The defect lives **entirely in the read-back path** — extractor → FD producer — which is only
exercised by arms `F-S` and `F-P`.

**Consequence, and it is the operationally useful part:** `P1`, `P2` and `O` may run now, and the
`OptView.hst` that arm `O` produces is exactly what §3's prediction needs in order to be tested.
Running the optimisation therefore *buys the test*. Blocking the whole ladder would delay the
diagnosis it depends on.

## 5. WHAT IS NOT DONE, AND WHY — rule 6

**The frozen extractor has NOT been edited and will not be by this lane.** `CLAUDE.md` rule 6 is
absolute, and the dafoam-supervisor has ruled explicitly that the repair is theirs under
`VERIFICATION_CHARTER.md` §2d.1, not a lane's — exactly as ruled for D4.

The supervisor's precedent is recorded here so it travels with the finding: **a repair is not
frozen until one primal at the corrected point reproduces the optimiser's own objective.** A
diagnosis that authorises a re-freeze buys itself a falsification test.

## 6. Why the fully armed instrument set would NOT have caught this

Recorded because it is the reusable lesson and it indicts controls this lane spent real effort
building and committing earlier today.

Had D7's `shape` scaler been `1.0` by luck, every primal would have converged and the FD arm would
have produced a **complete, well-formed, plausible FD table at a design point that is not the
optimum**. Five components requested, five returned, in registered order. **Every count refusal
would pass. The plant would be seen. The blind reader would be refused. All four `G7` mutations
would raise their named refusals.** `G5`'s `COUNT_EMPTY` / `COUNT_MISMATCH` / `ORDER_MISMATCH` /
`KEY_ABSENT`, the `D7-GRADER-DEF-2` structural validator committed at `0e229a0a`, the planted-zero
control — **not one of them looks at units.**

> **A units error is invisible to every count-, plant- and order-based control. They check THAT
> *n* components were measured. They never check WHERE.**

`d7_extract_endpoint.py` even carries a size assertion — *"a DV vector of the wrong length would
silently move every named component onto a different physical quantity while keeping its label"* —
which is precisely the right worry aimed at the wrong axis. It guards the **length** of the vector
and is blind to the **units** of its entries.

**The control that closes it is a value the optimiser cannot move**, and D7 has one for free.

## 7. What a repair would need, if the supervisor rules one (NOT implemented here)

Recorded as a recommendation to the supervisor, not as an action taken.

1. **Assert the pinned witness.** `patchV[0]` must equal `U0 = 291.6` and the extractor must
   **refuse** by name if it does not. This is the unforgeable check.
2. **Assert every extracted component lies inside its registered bounds.** IPOPT does not violate
   bound constraints, so a component outside `[lower, upper]` is a **units error, not an optimum**.
   Note the diagnostic asymmetry: `shape` at scaler `10.0` and bounds `[-1, 1]` would read
   **outside** its bounds and be caught, while `twist` and `patchV` at scaler `0.1` read
   **inside** theirs and would not be — **the bounds check alone is not sufficient**, which is
   why the pinned witness is the primary control and the bounds check the secondary one.
3. **Divide through by the registered scaler on the read path**, with the scalers named in one
   place shared by producer and extractor so they cannot drift apart.

## 8. Honest scope

* The mechanism in §1 is **cited from the supervisor's committed D4 ruling**, not re-derived by
  this lane. This lane has **not** independently measured that
  `getValues(scale=True) == getValues(scale=False)` on this box.
* This lane has **not** run `d7_extract_endpoint.py`, because **no `OptView.hst` exists** — no arm
  has run. §3 is therefore a **registered prediction, not a measurement**, and the distinction is
  the whole reason it is falsifiable.
* What **is** measured, from the frozen files: the three non-unity scalers, the `scale=False`
  call, the zero occurrences of `scaler` in both read-path instruments, and the pinned bounds on
  `patchV[0]`.
