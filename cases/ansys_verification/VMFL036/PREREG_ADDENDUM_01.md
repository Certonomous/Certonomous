# VMFL036 — PRE-REGISTRATION ADDENDUM 01

**Dated 2026-08-25, written AFTER first compute.** Under CLAUDE.md rule 2 the
gates are closed: **this addendum alters NO gate, threshold, cap or label**, and
the frozen `PREREGISTRATION.md` is deliberately **left byte-identical** to the
blob committed at `ff9e28da` so the launcher's own freeze check keeps verifying
against it. This is a separate dated file for exactly that reason.

## Why it exists

Two standing instructions arrived from `ansys-verification-supervisor` after the
freeze was committed and the solvers were live. Both are recorded here against
**what this case already does**, so a reader can check rather than take it on
trust. **Neither required a change.**

## 1. Geometry is read back, never constructed

**The instruction (final form):** any geometric quantity is read back from
OpenFOAM's `C` field or the written mesh — never constructed from `nr`, `dr`,
`(j+1/2)`, `2/3`, `14/9` or `7/3` — and selftest fixtures are built from real
mesh output, never from an assumed radius.

**What this case does, verified rather than asserted:**

- `grep` over `grade_vmfl036.py` for constructed cell-centre arithmetic
  (`(j+1/2)`, `dr*`, `nr*`, mid-radius forms) returns **zero hits**.
- **The comparator never reads an axis-adjacent cell at all.** Cd is a
  **face-based surface integral** over the `sphere` patch, taken from OpenFOAM's
  own `forces` function object. No cell-centre position enters the gate quantity.
- Every mesh quantity the case uses is read off `constant/polyMesh` — points and
  faces — by `polymesh_area.py`: the sphere's wetted area, its frontal projected
  area, the axis patch's area (asserted **exactly** zero), and the wedge
  half-angle recomputed from actual point coordinates.
- **On the fixture question specifically.** `--selftest`'s
  `control_geometry_identity` compares the closed-form `Aref` against an
  independent 200 000-point quadrature. That is a check of the **algebra**, and
  it is labelled as one — **it is not the geometry check.** The geometry check is
  `mesh_certificate`, which runs **at grade time, on every level**, and compares
  the frozen `Aref` against the frontal projected area **read off the mesh that
  actually ran**, refusing outside `(0.9999, 1.0001)`. Measured on the real L1
  mesh before the freeze: **1.08944678435e-02 analytic against 1.08944678435e-02
  from the written mesh — agreement to 1 part in 1e8.** The instrument is
  therefore validated against real mesh output, not against a fixture that shares
  its assumption.

**Independent confirmation this lane produced, and what it actually showed.** The
supervisor's first message asked that the `7/3` axis-cell ratio be registered;
the second **withdrew it**. This lane had already tested it, on a purpose-built
OpenFOAM v2606 pipe wedge (R = 1, four uniform radial cells, 2.5° half-angle,
cells reaching the axis — the geometry the claim is about, which VMFL036's sphere
wedge does **not** have). Reading OpenFOAM's own `C` field:

| cell | span | `C` radius | mid-radius | ideal sector centroid |
|---|---|---|---|---|
| 0 | [0.00, 0.25] | **0.1665080369** | 0.1250000000 | 0.1666666667 |
| 1 | [0.25, 0.50] | **0.3885187528** | 0.3750000000 | 0.3888888889 |

- The measured ratio `r2/r1` was **2.3333333333** — `7/3` to ten digits, and
  emphatically **not** the mid-radius prediction of 3.
- **But the absolute value is wrong in the fourth digit**: `C` gives
  0.16650804 where the ideal annular-sector centroid `(2/3)dr` gives 0.16666667.
  An OpenFOAM wedge is **flat-sided**, not an annular sector, and the chordal
  factor that biases the absolute radius **cancels in the ratio** — which is
  precisely why the ratio looked exact while the formula was not.

**This measurement supports the withdrawal, not the formula.** It is recorded
here because it is independent evidence for the rule the supervisor kept: the
ideal form is already wrong on the mesh that established it, so no such constant
may be hard-coded. **Nothing in this case registers `7/3`, `2/3`, `14/9` or
`(49*f1 - 9*f2)/40`, and nothing in this case ever did.**

## 2. Budget drawdown cannot starve a later level or the other arm

**The instruction:** a shared running budget can turn one slow level into a false
failure on a later one; two arms sharing a case must not let the diagnostic arm
eat the gate arm's budget; and a killed level must be distinguishable as
*starved* from *genuinely failed*.

**What this case does:**

- **The two arms have SEPARATE budgets and cannot starve each other.**
  `run_vmfl036.sh` takes `--arm` and each arm is its **own invocation** with its
  **own** 120 core-min budget file. Arm B (the `mu = 0.02` diagnostic, Re = 50)
  **cannot** consume any part of Arm A's budget. Arm A carries the primary gate
  and its budget is untouched by Arm B's behaviour. Both arms were launched
  concurrently, one core each.
- **Within an arm**, the three levels do share one drawdown — that is the
  Amendment 3 requirement — so the starvation risk is real in principle. It did
  not bite here, and the margin is on the record: L1 and L2 spent **1.37 + 6.67 =
  8.03 core-min**, leaving **112 core-min** for L3 against a measured L3 need of
  **~55 core-min**, a margin of ~57 core-min.
- **A starved level is already distinguishable from a failed one.** Every level's
  `RUN_RC.txt` records `timeout_s_granted` (the budget remaining at that level's
  launch, in seconds), `cap_core_min`, `spent_core_min_after`, `wall_s` and `rc`.
  An `rc = 124` beside a small `timeout_s_granted` is a starvation; an `rc = 124`
  beside a full grant is a genuine overrun. Nothing needs to be added.
- **Nothing was silently reduced.** `endTime` is 10 000 iterations at every level
  and the tolerance is 0.03 at the finest level, exactly as frozen. No endTime,
  band or label was trimmed to fit a budget, and none will be.
