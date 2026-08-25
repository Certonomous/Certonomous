# VMFL023 — PRE-REGISTRATION ADDENDUM 01

**Dated 2026-08-25, written AFTER first compute.** Under CLAUDE.md rule 2 the
gates are closed: **this addendum alters NO gate, threshold, cap, window or
label**, and the frozen `PREREGISTRATION.md` is deliberately **left
byte-identical** to the blob committed at `754f4f66` so the launcher's freeze
check keeps verifying against it.

## 1. Geometry is read back, never constructed

`grep` over `grade_vmfl023.py` for constructed cell-centre arithmetic returns
**zero hits**. The case is geometry-free in the relevant sense **by
construction**:

- **St is a FREQUENCY.** It is measured from the *timing* of the lift force on
  the `cylinder` patch — a face-based surface integral by OpenFOAM's `forces`
  function object. **No reference area, no cell centre and no radius enters the
  gate quantity at all.**
- The only length in the comparator is `D_CYL = 2.0`, which is the **manual's own
  stated cylinder diameter** (p.89), used as the reference length in
  `St = D/(T·U)`. It is the definition's D, not a mesh-derived quantity, and it
  would be the same number on any mesh.
- The mesh birth certificate records cell count, patch sizes, bounding box and
  quality metrics **read from `blockMesh`'s and `checkMesh`'s own output** for
  the mesh that ran, and asserts `nCells == 4·NT·NR` per level.
- No selftest fixture in this comparator supplies a geometry. The fixtures are a
  **synthetic time series** (a sinusoid at a known frequency) and a **flat
  signal** — both temporal, neither geometric, so the fixture-shares-the-
  instrument's-assumption trap has no surface to attach to here.

## 2. Budget drawdown cannot starve a later level

`run_vmfl023.sh` computes its budget as the **sum of the caps of the levels the
invocation will actually run**, and grants each level
`timeout_s = min(remaining_total, level_cap) * 60 / RANKS`.

**All three levels were launched as SEPARATE invocations** (`--level L1_96x32`,
`--level L2_192x64`, `--level L3_384x128`), concurrently, one core each.
Consequently **each level's budget is its own cap alone and no cross-level
starvation is possible in this run** — L3 cannot be starved by L2, because they
never shared a budget. The per-level caps are 20 / 70 / 260 core-min.

Each level's `RUN_RC.txt` records `timeout_s_granted`, `level_cap_core_min`,
`total_cap_core_min` and `spent_core_min_after`, so a killed level is
distinguishable as starved or genuinely failed without inference.

**Nothing was silently reduced and nothing will be.** `endTime = 300 s`,
`deltaT = 0.005 s` and the sampling window `[180, 300] s` are as frozen.

## 3. The settling window and the sampling window, stated separately

The frozen registration defines one window explicitly; the supervisor asked that
the two be named separately, so they are named here. **This changes no value.**

- **SETTLING (START-UP) WINDOW: `t ∈ [0, 180) s`.** Not sampled. It contains the
  decay of the frozen symmetry-breaking kick `(1, 0.2, 0)` and the growth of the
  von Karman street. 180 s is ~14.9 shedding periods at the reference
  `T = D/(St·U) = 12.12 s`.
- **SAMPLING WINDOW: `t ∈ [180, 300] s`.** 120 s ≈ **9.9 shedding periods**. This
  is the `WINDOW` constant frozen in the comparator, and St is measured from it
  and from nothing else.

**If the settled state arrives later than predicted, the sampling window is NOT
truncated and no number is reported as if it were.** The comparator carries a
**stationarity control** that splits `[180, 300]` in half, compares the lift
peak-to-peak amplitude of the two halves, and returns **`NOT A RESULT`** if they
differ by more than 5%. A Strouhal number measured over a window that is still
growing is a wrong number, and this case is wired to say so rather than to
report it. Should that fire, it is reported to the supervisor for a decision on a
longer `endTime` under a **new** freeze — never by extending this one.
